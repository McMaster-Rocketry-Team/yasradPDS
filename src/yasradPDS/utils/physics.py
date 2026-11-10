# all physics lives here
<<<<<<< HEAD
from .constants import PhysicalConstants as const

class Physics:
    def drag_force(rho: float, v: float, Cd: float, A: float) -> float:
        return 0.5*rho*v**2*Cd*A;

    def air_density():
        """Based on ISA model"""
        
=======

import math
>>>>>>> origin/main
