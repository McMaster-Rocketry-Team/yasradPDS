# 2 dof pendulum for shroud line stiffness
import scipy
import numpy as np
# from yasradPDS.systems.system import system  # commented out: "system" does not exist, broke the import
from yasradPDS.systems.system import UnknownValueError
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


def build_simulation_params(parachute, stage: int = 1, *, canopy_mass: float | None = None, line_length: float | None = None) -> SimulationParams:

    ##both these values are unknowns so incase these are not calculated
    if canopy_mass is None:
        try:
            canopy_mass = parachute.get(stage, "canopy_mass")
        except UnknownValueError:
            raise UnknownValueError(
                f"canopy mass is unknown for stage {stage}; provide canopy_mass"
            ) from None

    if line_length is None:
        try:
            line_length = parachute.get(stage, "shroud.length")
        except UnknownValueError:
            raise UnknownValueError(
                f"shroud length is unknown for stage {stage}; provide line_length"
            ) from None

    if canopy_mass <= 0:
        raise ValueError("canopy_mass must be greater than zero")
    if line_length <= 0:
        raise ValueError("line_length must be greater than zero")

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
    

