# dual deployment drogue and main system, holds knowns and unknowns
# canopy/shroud line dimensioning is handled here upon init
# passed as an arg to all exports/analyses as source of truth for
# system data
 
import math
from system import System, Stage, register
from geometries.geometry import Geometry, new_geometry

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

        # Check to ensure that both stages report the same total mass
        if not math.isclose(self._drogue.total_mass, self._main.total_mass):
            raise ValueError(
                f"total mass differs between stages: "
                f"{self._drogue.total_mass} vs {self._main.total_mass} kg"
            )
        
        # Code goes here, add extra helper methods as needed
