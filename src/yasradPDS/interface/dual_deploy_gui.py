# takes all knowns for dual deploy system creation,
# must support existing parachutes with togglable field
# if a parachute is marked as existing, it cannot be resized
# in dual_deploy.py, only the unmade parachute is varaible
# if both are existing, dual_deploy.py runs no solver for
# unknowns, instead it just stores the data to run analyses/exports

# use tkinter library
import json
import math
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

FONT = 'Calibri'
FONT_SIZE = 10
TITLE = "yasradPDS Dual Deploy GUI"
WINDOW_HEIGHT = 700
WINDOW_WIDTH = 1100

class WholeNumberVar(tk.Variable):
    """Like tk.IntVar, but rejects doubles instead of casting as an int"""
    def get(self) -> int:
        try:
            return int(str(super().get()))
        except ValueError:
            raise tk.TclError("expected a whole number") from None


# FIELDS (key, label text, tk variable class)
GENERAL_FIELDS = [
    ("name", "NAME", tk.StringVar),
]

CANOPY_FIELDS = [
    ("geometry",       "GEOMETRY",                tk.StringVar),
    ("gore_count",     "GORE COUNT",              WholeNumberVar),
    ("fabric_density", "FABRIC DENSITY (kg/m^2)", tk.DoubleVar),
    ("porosity",       "POROSITY (0 to 1)",       tk.DoubleVar),
]

DEPLOYMENT_FIELDS = [
    ("deploy_altitude", "DEPLOY ALTITUDE (AGL, m)",   tk.DoubleVar),
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
    ("max_epsilon",    "MAX EPSILON (0-1)",        tk.DoubleVar),
]

# optional: left blank, the system solves them
EXISTING_FIELDS = [
    ("main_diameter",       "MAIN DIAMETER (m)",       tk.DoubleVar),
    ("spill_hole_diameter", "SPILL HOLE DIAMETER (m)", tk.DoubleVar),
]

class InputFrame(tk.LabelFrame):
    """A labelled box of label + entry pairs that owns its variables.

    Args:
        parent: tk.Tk object
        title: String
        fields: tuples
        optional: keys that may be left blank (left out of get())
    
    Attributes:
        vars: dict
        entries: dict of the tk.Entry for each key

    """
    def __init__(self, parent, title, fields, optional=()):
        super().__init__(parent, text=title, font=(FONT, FONT_SIZE, "bold")) # Inherit the tk.LabelFrame attributes
        self.vars = {}
        self.entries = {}
        self.optional = set(optional)
        for row, (key, label, var_type) in enumerate(fields):
            self.vars[key] = var_type()
            if key in self.optional:
                label += " (optional)"
                self.vars[key].set("") # DoubleVar starts at 0.0, optional boxes should start empty
            tk.Label(self, text=label, font=(FONT, FONT_SIZE, "bold")).grid(
                row=row, column=0, sticky="w", padx=5, pady=2)
            self.entries[key] = tk.Entry(self, textvariable=self.vars[key], font=(FONT, FONT_SIZE, "normal"))
            self.entries[key].grid(row=row, column=1, padx=5, pady=2)

    def get(self) -> dict:
        """Current values as {key: value}, skipping blank optional entries. Raises tk.TclError on bad number input."""
        return {key: var.get() for key, var in self.vars.items()
                if key not in self.optional or self.entries[key].get().strip()}

    def set(self, values: dict):
        """Fill entries from {key: value}. Keys this frame doesn't have are ignored.
        Optional keys missing from values are cleared, so an import doesn't keep stale sizes."""
        for key, var in self.vars.items():
            if key in values:
                var.set(values[key])
            elif key in self.optional:
                var.set("")


class LineFrame(InputFrame):
    """InputFrame for a _Line."""
    def __init__(self, parent, title, optional=()):
        super().__init__(parent, title, LINE_FIELDS, optional)


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
        self.existing = InputFrame(self, "EXISTING PARACHUTE", EXISTING_FIELDS,
                                   optional=[key for key, _, _ in EXISTING_FIELDS])
        self.frames = [canopy, deployment, loads, self.existing]

        # _Line frames sit inside one container
        lines_container = tk.LabelFrame(self, text="LINES", font=(FONT, FONT_SIZE, "bold"))
        self.lines = {
            "cord_upper": LineFrame(lines_container, "CORD UPPER"),
            "cord_lower": LineFrame(lines_container, "CORD LOWER"),
            "shroud":     LineFrame(lines_container, "SHROUD", optional=["length"]),
        }

        # Layout
        self.columnconfigure(0, weight=1, uniform="col")
        self.columnconfigure(1, weight=1, uniform="col")

        # left column stacks top to bottom
        canopy.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        deployment.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        loads.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        self.existing.grid(row=3, column=0, sticky="ew", padx=10, pady=5)

        # right column: lines spans the left stack, centered vertically
        lines_container.grid(row=0, column=1, rowspan=4, sticky="ew", padx=10, pady=5)

        lines_container.columnconfigure(0, weight=1)
        for row, frame in enumerate(self.lines.values()):
            frame.grid(row=row, column=0, sticky="ew", padx=5, pady=5)

    def get(self) -> dict:
        """Stage inputs as a dict. Raises tk.TclError on bad number input."""
        values: dict = {}
        for frame in self.frames:
            values.update(frame.get())

        # each _Line goes out as a dict, Stage turns it into a _Line
        for key, frame in self.lines.items():
            values[key] = frame.get()

        # both known sizes given means the parachute is already made
        values["is_existing"] = "main_diameter" in values and "spill_hole_diameter" in values
        return values

    def set(self, values: dict):
        for frame in self.frames:
            frame.set(values)
        for key, frame in self.lines.items():
            frame.set(values.get(key, {}))


def stage_error(stage: dict) -> str | None:
    """What's wrong with one stage's values, or None if they pass."""
    lines = [v for v in stage.values() if isinstance(v, dict)]
    numbers = [v for group in (stage, *lines) for v in group.values() if isinstance(v, float)]
    if any(math.isinf(v) for v in numbers):
        return "Cannot use inf as an input."
    if not all(0 < line["max_epsilon"] <= 1 for line in lines):
        return "MAX EPSILON must be above 0 and at most 1 (20% = 0.2)."
    if ("main_diameter" in stage) != ("spill_hole_diameter" in stage):
        return "Fill in both MAIN DIAMETER and SPILL HOLE DIAMETER, or leave both empty."
    return None


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
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
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
    def valid_inputs() -> dict | None:
        """Read and check every field. Returns the values, or None after showing the error."""
        values = general.get()
        for key, frame in stages.items():
            notebook.select(frame) # show the tab being checked if it fails
            try:
                stage = frame.get()
            except tk.TclError:
                # a number box was empty or held text, or gore count wasn't whole
                messagebox.showerror("Invalid input", "Number fields must contain numbers, and gore count a whole number.")
                return None

            error = stage_error(stage)
            if error:
                messagebox.showerror("Invalid input", error)
                return None

            values[key] = stage
        return values

    def save():
        values = valid_inputs()
        if values is None:
            return
        path = filedialog.asksaveasfilename(initialfile="system.json", defaultextension=".json",
                                            filetypes=[("JSON", "*.json")])
        if not path:
            return # cancelled, keep the window open
        try:
            with open(path, "w") as f:
                json.dump(values, f, indent=2)
        except OSError as e:
            messagebox.showerror("Save failed", f"Could not write {path}:\n{e}")
            return

        results.update(values)
        root.destroy() # close window after saving

    def import_json():
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not path:
            return
        try:
            with open(path) as f:
                values = json.load(f)
            general.set(values)
            for key, frame in stages.items():
                frame.set(values.get(key, {}))
        except (OSError, ValueError, AttributeError) as e:
            messagebox.showerror("Import failed", f"Could not read {path}:\n{e}")

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
