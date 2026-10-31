# takes all knowns for dual deploy system creation,
# must support existing parachutes with togglable field
# if a parachute is marked as existing, it cannot be resized
# in dual_deploy.py, only the unmade parachute is varaible
# if both are existing, dual_deploy.py runs no solver for
# unknowns, instead it just stores the data to run analyses/exports

# use tkinter library
import tkinter as tk
from tkinter import messagebox, ttk

FONT = 'Calibri'
FONT_SIZE = 10
TITLE = "yasradPDS Dual Deploy GUI"
WINDOW_HEIGHT = 1100
WINDOW_WIDTH = 700

# FIELDS (key, label text, tk variable class)
GENERAL_FIELDS = [
    ("name", "NAME", tk.StringVar),
]

CANOPY_FIELDS = [
    ("geometry",       "GEOMETRY",                tk.StringVar),
    ("gore_count",     "GORE COUNT",              tk.IntVar),
    ("fabric_density", "FABRIC DENSITY (kg/m^2)", tk.DoubleVar),
    ("porosity",       "POROSITY (0 to 1)",       tk.DoubleVar),
]

DEPLOYMENT_FIELDS = [
    ("deploy_altitude", "DEPLOY ALTITUDE (m)",   tk.DoubleVar),
    ("deploy_velocity", "DEPLOY VELOCITY (m/s)", tk.DoubleVar),
    ("target_velocity", "TARGET VELOCITY (m/s)", tk.DoubleVar),
]

LOADS_FIELDS = [
    ("mass_upper",      "MASS UPPER (kg)",     tk.DoubleVar),
    ("mass_lower",      "MASS LOWER (kg)",     tk.DoubleVar),
    ("max_shock_upper", "MAX SHOCK UPPER (N)", tk.DoubleVar),
    ("max_shock_lower", "MAX SHOCK LOWER (N)", tk.DoubleVar),
]

LINE_FIELDS = [
    ("length",         "LENGTH (m)",         tk.DoubleVar),
    ("density",        "DENSITY (kg/m)",     tk.DoubleVar),
    ("break_strength", "BREAK STRENGTH (N)", tk.DoubleVar),
    ("max_epsilon",    "MAX EPSILON",        tk.DoubleVar),
]

class InputFrame(tk.LabelFrame):
    """A labelled box of label + entry pairs that owns its variables.

    Args:
        parent: tk.Tk object
        title: String
        fields: tuples
    
    Attributes:
        vars: dict

    """

    """A labelled box of label + entry pairs that owns its variables.

    fields is a list of (key, label text, tk variable class).
    """
    def __init__(self, parent, title, fields):
        super().__init__(parent, text=title, font=(FONT, FONT_SIZE, "bold")) # Inherit the tk.LabelFrame attributes
        self.vars = {}
        for row, (key, label, var_type) in enumerate(fields):
            self.vars[key] = var_type()
            tk.Label(self, text=label, font=(FONT, FONT_SIZE, "bold")).grid(
                row=row, column=0, sticky="w", padx=5, pady=2)
            tk.Entry(self, textvariable=self.vars[key], font=(FONT, FONT_SIZE, "normal")).grid(
                row=row, column=1, padx=5, pady=2)

    def get(self) -> dict:
        """Current values as {key: value}. Raises tk.TclError on bad number input."""
        return {key: var.get() for key, var in self.vars.items()}


class LineFrame(InputFrame):
    """InputFrame for a _Line. The shroud leaves length out (the system solves it)."""
    def __init__(self, parent, title, include_length=True):
        fields = [f for f in LINE_FIELDS if include_length or f[0] != "length"]
        super().__init__(parent, title, fields)


class StageFrame(tk.Frame):
    """One tab's worth of inputs for a single Stage (drogue or main).

    Args:
        parent: tk widget (the notebook)

    Attributes:
        frames: list of InputFrames merged flat into the stage dict
        lines: dict of LineFrames, each sent out as its own dict
    """
    def __init__(self, parent):
        super().__init__(parent)
        canopy = InputFrame(self, "CANOPY", CANOPY_FIELDS)
        deployment = InputFrame(self, "DEPLOYMENT", DEPLOYMENT_FIELDS)
        loads = InputFrame(self, "MASSES AND SHOCK LIMITS", LOADS_FIELDS)
        self.frames = [canopy, deployment, loads]

        # _Line frames sit inside one container
        lines_container = tk.LabelFrame(self, text="LINES", font=(FONT, FONT_SIZE, "bold"))
        self.lines = {
            "cord_upper": LineFrame(lines_container, "CORD UPPER"),
            "cord_lower": LineFrame(lines_container, "CORD LOWER"),
            "shroud":     LineFrame(lines_container, "SHROUD", include_length=False),
        }

        # Layout
        self.columnconfigure(0, weight=1, uniform="col")
        self.columnconfigure(1, weight=1, uniform="col")

        # left column stacks top to bottom
        canopy.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        deployment.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        loads.grid(row=2, column=0, sticky="ew", padx=10, pady=5)

        # right column: lines spans the left stack, centered vertically
        lines_container.grid(row=0, column=1, rowspan=3, sticky="ew", padx=10, pady=5)

        lines_container.columnconfigure(0, weight=1)
        for row, frame in enumerate(self.lines.values()):
            frame.grid(row=row, column=0, sticky="ew", padx=5, pady=5)

    def get(self) -> dict:
        """Stage inputs as a dict. Raises tk.TclError on bad number input."""
        values = {}
        for frame in self.frames:
            values.update(frame.get())

        # each _Line goes out as a dict, Stage turns it into a _Line
        for key, frame in self.lines.items():
            values[key] = frame.get()
        return values


def prompt_inputs() -> dict | None:
    """ Opens the input window for dual deploy GUI.

        Args:
            None
        
        Returns:
            dict: Inputted values, {"name": ..., "drogue": {...}, "main": {...}}
            None: No inputted values
    """
    results = {}

    root = tk.Tk()
    root.geometry(f"{WINDOW_HEIGHT}x{WINDOW_WIDTH}")
    root.title(TITLE)

    # Frames (each one holds its own variables)
    general = InputFrame(root, "GENERAL", GENERAL_FIELDS)

    # one tab per stage, keys match DualDeploySystem stages
    notebook = ttk.Notebook(root)
    stages = {
        "drogue": StageFrame(notebook),
        "main":   StageFrame(notebook),
    }
    for key, frame in stages.items():
        notebook.add(frame, text=key.upper())

    # Functions
    def save():
        try:
            results.update(general.get())
            for key, frame in stages.items():
                notebook.select(frame) # show the tab being read if it fails
                results[key] = frame.get()
        except tk.TclError:
            # a number box was empty or held text
            results.clear()
            messagebox.showerror("Invalid input", "Number fields must contain numbers.")
            return

        root.destroy() # close window after saving

    def import_json():
        pass

    save_button = tk.Button(root, text="Save", command=save)
    import_button = tk.Button(root, text="Import", command=import_json)

    # Layout
    root.columnconfigure(0, weight=1, uniform="col")
    root.columnconfigure(1, weight=1, uniform="col")
    root.rowconfigure(1, weight=1)

    general.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
    notebook.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)

    # bottom row: buttons side by side, stretched across the window
    save_button.grid(row=2, column=0, sticky="sew", padx=10, pady=10, ipady=6)
    import_button.grid(row=2, column=1, sticky="sew", padx=10, pady=10, ipady=6)

    root.mainloop()
    return results or None
    # NOTE: results will return {"name": ..., "drogue": {...}, "main": {...}} and when creating a new system, .pop("name") and input **results

if __name__ == "__main__":
    print(prompt_inputs())
