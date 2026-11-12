# all physics lives here
from .constants import PhysicalConstants as const

class Physics:
    def drag_force(rho: float, v: float, Cd: float, A: float) -> float:
        return 0.5*rho*v**2*Cd*A;

    def air_density(h: float):
        """Based on ISA model"""
        return const.BASE_RHO*(1 - h*const.LAPSE_RATE/const.BASE_TEMP)**(const.G*const.MM_AIR/(const.R*const.LAPSE_RATE) - 1)