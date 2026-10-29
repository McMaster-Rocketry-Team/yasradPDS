# takes all knowns for dual deploy system creation,
# must support existing parachutes with togglable field
# if a parachute is marked as existing, it cannot be resized
# in dual_deploy.py, only the unmade parachute is varaible
# if both are existing, dual_deploy.py runs no solver for
# unknowns, instead it just stores the data to run analyses/exports

# use tkinter library
import tkinter as tk

FONT = 'Calibri'
FONT_SIZE = 10

def prompt_inputs() -> dict | None:
    """Open the input window for dual deploy GUI. Returns the entered values, or None if closed."""
    results = {}

    root = tk.Tk()
    root.geometry("1200x800")
    root.title("yasradPDS Dual Deploy GUI")

    name_var = tk.StringVar()
    geometry_var = tk.StringVar()
    gore_count_var = tk.IntVar()
    deploy_altitude_var = tk.DoubleVar()
    deploy_velocity_var = tk.DoubleVar()
    target_velocity_var = tk.DoubleVar()
    mass_upper_var = tk.DoubleVar()
    mass_lower_var = tk.DoubleVar()
    
    # Find a way to input _Line
    cord_upper_var = 0
    cord_lower_var = 0
    shroud_var = 0

    max_shock_upper_var = tk.DoubleVar()
    max_shock_lower_var = tk.DoubleVar()
    fabric_density_var = tk.DoubleVar()
    porosity_var = tk.DoubleVar()

    # Functions
    def save():
        results["name"] = name_var.get()
        results["geometry"] = geometry_var.get()
        results["gore_count"] = gore_count_var.get()
        results["deploy_altitude"] = deploy_altitude_var.get()
        results["deploy_velocity"] = deploy_velocity_var.get()
        results["target_velocity"] = target_velocity_var.get()
        results["mass_upper"] = mass_upper_var.get()
        results["mass_lower"] = mass_lower_var.get()
        results["max_shock_upper"] = max_shock_upper_var.get()
        results["max_shock_lower"] = max_shock_lower_var.get()
        results["fabric_density"] = fabric_density_var.get()
        results["porosity"] = porosity_var.get()

        root.destroy() # close window after saving

    # Widgets
    # Name Input
    name_label = tk.Label(root, text='NAME', font=(FONT, FONT_SIZE, "bold"))
    name_entry = tk.Entry(root, textvariable=name_var, font=(FONT, FONT_SIZE, "normal"))

    # Geometry Input
    geometry_label = tk.Label(root, text='GEOMETRY', font=(FONT, FONT_SIZE, "bold"))
    geometry_entry = tk.Entry(root, textvariable=geometry_var, font=(FONT, FONT_SIZE, "normal"))

    # Gore Count Input
    gore_count_label = tk.Label(root, text='GORE COUNT', font=(FONT, FONT_SIZE, "bold"))
    gore_count_entry = tk.Entry(root, textvariable=gore_count_var, font=(FONT, FONT_SIZE, "normal"))

    # Deploy Altitude Input
    deploy_altitude_label = tk.Label(root, text='DEPLOY ALTITUDE (m)', font=(FONT, FONT_SIZE, "bold"))
    deploy_altitude_entry = tk.Entry(root, textvariable=deploy_altitude_var, font=(FONT, FONT_SIZE, "normal"))

    # Deploy Velocity Input
    deploy_velocity_label = tk.Label(root, text='DEPLOY VELOCITY (m/s)', font=(FONT, FONT_SIZE, "bold"))
    deploy_velocity_entry = tk.Entry(root, textvariable=deploy_velocity_var, font=(FONT, FONT_SIZE, "normal"))

    # Target Velocity Input
    target_velocity_label = tk.Label(root, text='TARGET VELOCITY (m/s)', font=(FONT, FONT_SIZE, "bold"))
    target_velocity_entry = tk.Entry(root, textvariable=target_velocity_var, font=(FONT, FONT_SIZE, "normal"))

    # Mass Upper Input
    mass_upper_label = tk.Label(root, text='MASS UPPER (kg)', font=(FONT, FONT_SIZE, "bold"))
    mass_upper_entry = tk.Entry(root, textvariable=mass_upper_var, font=(FONT, FONT_SIZE, "normal"))

    # Mass Lower Input
    mass_lower_label = tk.Label(root, text='MASS LOWER (kg)', font=(FONT, FONT_SIZE, "bold"))
    mass_lower_entry = tk.Entry(root, textvariable=mass_lower_var, font=(FONT, FONT_SIZE, "normal"))

    # TODO: cord_upper, cord_lower, shroud (_Line) widgets go here

    # Max Shock Upper Input
    max_shock_upper_label = tk.Label(root, text='MAX SHOCK UPPER (N)', font=(FONT, FONT_SIZE, "bold"))
    max_shock_upper_entry = tk.Entry(root, textvariable=max_shock_upper_var, font=(FONT, FONT_SIZE, "normal"))

    # Max Shock Lower Input
    max_shock_lower_label = tk.Label(root, text='MAX SHOCK LOWER (N)', font=(FONT, FONT_SIZE, "bold"))
    max_shock_lower_entry = tk.Entry(root, textvariable=max_shock_lower_var, font=(FONT, FONT_SIZE, "normal"))

    # Fabric Density Input
    fabric_density_label = tk.Label(root, text='FABRIC DENSITY (kg/m^2)', font=(FONT, FONT_SIZE, "bold"))
    fabric_density_entry = tk.Entry(root, textvariable=fabric_density_var, font=(FONT, FONT_SIZE, "normal"))

    # Porosity Input
    porosity_label = tk.Label(root, text='POROSITY (0 to 1)', font=(FONT, FONT_SIZE, "bold"))
    porosity_entry = tk.Entry(root, textvariable=porosity_var, font=(FONT, FONT_SIZE, "normal"))

    save_button = tk.Button(root, text="Save", command=save)

    # Layout
    name_label.grid(row=0, column=0)
    name_entry.grid(row=0, column=1)
    geometry_label.grid(row=1, column=0)
    geometry_entry.grid(row=1, column=1)
    gore_count_label.grid(row=2, column=0)
    gore_count_entry.grid(row=2, column=1)
    deploy_altitude_label.grid(row=3, column=0)
    deploy_altitude_entry.grid(row=3, column=1)
    deploy_velocity_label.grid(row=4, column=0)
    deploy_velocity_entry.grid(row=4, column=1)
    target_velocity_label.grid(row=5, column=0)
    target_velocity_entry.grid(row=5, column=1)
    mass_upper_label.grid(row=6, column=0)
    mass_upper_entry.grid(row=6, column=1)
    mass_lower_label.grid(row=7, column=0)
    mass_lower_entry.grid(row=7, column=1)
    # TODO: _Line widgets get their own rows here
    max_shock_upper_label.grid(row=8, column=0)
    max_shock_upper_entry.grid(row=8, column=1)
    max_shock_lower_label.grid(row=9, column=0)
    max_shock_lower_entry.grid(row=9, column=1)
    fabric_density_label.grid(row=10, column=0)
    fabric_density_entry.grid(row=10, column=1)
    porosity_label.grid(row=11, column=0)
    porosity_entry.grid(row=11, column=1)
    save_button.grid(row=12, column=1)

    root.mainloop()
    return results or None

if __name__ == "__main__":
    prompt_inputs()