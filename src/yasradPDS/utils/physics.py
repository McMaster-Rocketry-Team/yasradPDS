# all physics lives here

import math

def drag_force(drag_coefficient : float, area : float, fluid_density : float, flow_velocity : float) -> float:
    """
    drag_coefficient - unitless
    area - m^2 - reference area for drag equation, not surface area
    fluid_density - kg/m^3 - density of fluid
    flow_velocity - m/s - relative velocity between object and fluid

    Return:
    Drag force - newtons
    """
    
    return drag_coefficient * area * (fluid_density * math.pow(flow_velocity, 2)) / 2