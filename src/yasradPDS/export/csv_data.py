# exports analysis results (time series, loads, dispersion points) from a system
# object to CSV files

import numpy as np
from rocketpy import Flight

def descent_csv(descent: Flight, path: str):
    """Writes altitude, vertical velocity and vertical acceleration vs time, one block after another."""
    rows = np.vstack((
        ["Time (s)", "Altitude ASL (m)"], np.array(descent.z),
        ["Time (s)", "Vertical Velocity"], np.array(descent.vz),
        ["Time (s)", "Vertical Accel"], np.array(descent.az),
    ))
    with open(path, "w") as f:
        for row in rows:
            f.write(",".join(map(str, row)) + "\n")

def montecarlo_csv():
    pass
