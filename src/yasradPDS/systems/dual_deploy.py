# dual deployment drogue and main system, holds knowns and unknowns
# canopy/shroud line dimensioning is handled here upon init
# passed as an arg to all exports/analyses as source of truth for
# system data
 
import math
from .system import System, Stage, register
from yasradPDS.geometries.geometry import Geometry, new_geometry
from yasradPDS.utils.atmosphere import LaunchSite

SPILL_HOLE_RATIO =  0.2

@register("dual_deploy")
class DualDeploySystem(System):
    _stages = {"drogue": Stage, "main": Stage} # Ordered stages, must be defined

    @property
    def _drogue(self):
        return self._stage_list[0]

    @property
    def _main(self):
        return self._stage_list[1]

    def _solve(self) -> None:
        """Solves for unknowns upon initialization"""
        
        
        # Code goes here, add extra helper methods as needed

        # 1) Size main based on landing velocity

        # 2) Size drogue based on main's lowest max opening shock (upper/lower)

        # 3) Find all unknown values

        # Cd should be a constant value, not a function of dimensions
        # Forget trying to alter the vent hole diam, just use the ratio provided
        # Shroud line lengths should be a ratio of main diam