# dual deployment drogue and main system, holds knowns and unknowns
# canopy/shroud line dimensioning is handled here upon init
# passed as an arg to all exports/analyses as source of truth for
# system data
 
from system import System, Stage, register
from geometries.geometry import Geometry

@register("dual_deploy")
class DualDeploySystem(System):
    _stages = {"drogue": Stage, "main": Stage} # Ordered stages, must be defined

    def _solve(self) -> None:
        """Solves for unknowns upon initialization"""

        drogue = self._stage_list[0]
        main = self._stage_list[1]
