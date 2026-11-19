# 2 dof pendulum for shroud line stiffness
import scipy
import numpy as np
import math
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
    

def Line_Lengths_Attachments(canopy_center : tuple , 
canopy_tilt : float , attachment_spacing: float , rocket_position : tuple) -> tuple:
    left_attachment = (canopy_center[0] - attachment_spacing * 0.5 * math.cos(canopy_tilt),
    canopy_center[1] - attachment_spacing * 0.5 * math.sin(canopy_tilt))

    right_attachment = (canopy_center[0] + attachment_spacing * 0.5 * math.cos(canopy_tilt),
    canopy_center[1] + attachment_spacing * 0.5 * math.sin(canopy_tilt))

    # Left then right line
    line_lengths = (math.dist(rocket_position, left_attachment),
    math.dist(rocket_position, right_attachment))

    return left_attachment , right_attachment , line_lengths

def line_stretch(current_length: float, unstretched_length: float) -> float:
    return current_length - unstretched_length

def line_tension(stretch: float, stiffness: float) -> float:
    return stiffness * max(0.0, stretch)

def line_force(rocket_position: tuple,attachment_point: tuple,tension: float) -> tuple:
    # Vector pointing from the rocket toward the attachment point
    dx = attachment_point[0] - rocket_position[0]
    dz = attachment_point[1] - rocket_position[1]

    length = math.hypot(dx, dz)

    if length == 0:
        raise ValueError("Cannot calculate line direction: length is zero")

    # Unit direction vector multiplied by tension
    force_x = tension * dx / length
    force_z = tension * dz / length

    return force_x, force_z

def rocket_acceleration(mass: float , left_force: tuple , right_force: tuple, gravity: float = 9.81)->tuple:
    if(mass<=0):
        raise TypeError("Mass cannot be less than or equal zero")

    net_force_x = left_force[0] + right_force[0]
    net_force_z = left_force[1] + right_force[1] - mass * gravity
    acceleration_x = net_force_x / mass
    acceleration_z = net_force_z / mass

    return acceleration_x, acceleration_z


def simulation(
    system: System,
    stage: int,
    rocket_position: tuple,
    rocket_velocity: tuple,
    duration: float,
    dt: float):

    rocket_mass = system.get(stage, "total_mass")
    canopy_diameter = system.get(stage, "main_diameter")
    line_length = system.get(stage, "shroud.length")
    total_shroud_stiffness = system.get(stage, "shroud.k")