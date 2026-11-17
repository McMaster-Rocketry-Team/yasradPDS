# 2 dof pendulum for shroud line stiffness
import scipy
import numpy as np
# from yasradPDS.systems.system import system  # commented out: "system" does not exist, broke the import
from yasradPDS.systems.system import UnknownValueError, System
from dataclasses import dataclass
#this is just a general idea for now simulation Parameters are 100% going to change as we scale things

@dataclass
class SimulationParams:
    # Masses
    canopy_mass: float
    payload_mass: float

    # Geometry
    canopy_diameter: float
    line_length: float

    # Aerodynamics
    drag_area: float
    air_density: float = 1.225

    # Suspension
    spring_constant: float = 0.0
    damping_coefficient: float = 0.0

    # Rotation for later models   
    canopy_inertia: float | None = None
    aerodynamic_stiffness: float | None = None
    rotational_damping: float | None = None

# Helper method to get rid of None type: will likely move this to System later
def get_float(system: System, stage: int, name: str) -> float:
    value = system.get(stage, name) # raises UnknownValueError if None
    if not isinstance(value, (int, float)):
        raise TypeError(f"stage {stage} {name} should be a number, got {type(value).__name__}")
    return float(value)


def build_simulation_params(parachute, stage: int = 1, *, canopy_mass: float | None = None, line_length: float | None = None) -> SimulationParams:
    if canopy_mass is None:
        canopy_mass = get_float(parachute, stage, "canopy_mass") # turn into float
    if line_length is None:
        line_length = get_float(parachute, stage, "shroud.length")
    if canopy_mass <= 0 or line_length <= 0: # "x" is not None is not needed anymore
        raise ValueError("canopy_mass and line_length must be greather than zero.")

    spring_constant = (
        parachute.get(stage, "shroud.count")
        * parachute.get(stage, "shroud.break_strength")
        / parachute.get(stage, "shroud.max_epsilon")
        / line_length
    )
    return SimulationParams(
        canopy_mass=canopy_mass,
        payload_mass=parachute.get(stage, "total_mass"),
        canopy_diameter=parachute.get(stage, "main_diameter"),
        line_length=line_length,
        drag_area=parachute.get(stage, "CD") * parachute.get(stage, "area"),
        spring_constant=spring_constant,
    )
    

