# dual deployment drogue and main system, holds knowns and unknowns
# canopy/shroud line dimensioning is handled here upon init
# passed as an arg to all exports/analyses as source of truth for
# system data
 
import math
from .system import System, Stage, register
from yasradPDS.geometries.geometry import Geometry, new_geometry

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
