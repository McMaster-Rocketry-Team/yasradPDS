# dual deployment drogue and main system, holds knowns and unknowns
# canopy/shroud line dimensioning is handled here upon init
# passed as an arg to all exports/analyses as source of truth for
# system data

import math
from .system import System, Stage, register
from yasradPDS.geometries.geometry import Geometry, new_geometry
from yasradPDS.utils.atmosphere import LaunchSite
from yasradPDS.utils.constants import PhysicalConstants
from yasradPDS.utils.physics import Physics

g = PhysicalConstants.G
SPILL_HOLE_RATIO =  0.2
OPENING_SHOCK_CX = 1.6

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
        
        # an existing drogue sets how fast the main opens, so it goes first.
        # otherwise the main's shock limit sets the drogue size, so main goes first.
        if self._drogue.is_existing:
            self._solve_drogue()
            self._solve_main()
        else:
            self._solve_main()
            self._solve_drogue()

        for stage in self._stage_list:
            stage.fill_time = self.get_fill_time(stage.main_diameter, stage.deploy_velocity)
            stage.actual_shock_upper = stage.actual_shock_lower = self._opening_shock(stage, stage.deploy_velocity)

        if self._opening_shock(self._main, self._main.deploy_velocity) > self._shock_limit(self._main):
            raise ValueError("main opening shock exceeds its limit, drogue is descending too fast")

        # Cd should be a constant value, not a function of dimensions
        # We're using vent ratio provided
        # Shroud line lengths should be a ratio of main diam

    def _solve_main(self) -> None:
        main = self._main
        self._set_area(main, main.target_velocity, 0)

        if self._drogue.is_existing:
            rho = Physics.air_density(main.deploy_altitude)
            main.deploy_velocity = self.get_terminal_velocity(main.total_mass, self._drogue.area, self._drogue.CD, rho)
        else:
            main.deploy_velocity = self._max_deploy_velocity(main)

    def _solve_drogue(self) -> None:
        # drogue should be slowed to the main's deploy velocity by the time it gets there
        self._set_area(self._drogue, self._main.deploy_velocity, self._main.deploy_altitude)

    def _set_area(self, stage: Stage, velocity: float, altitude: float) -> None:
        """Area from the diameters if the canopy exists, else sized to descend at `velocity` at `altitude`"""
        if stage.is_existing:
            stage.area = stage._geometry.getArea(stage.main_diameter, stage.spill_hole_diameter)
            return
        rho = Physics.air_density(altitude)
        stage.area = self.get_area(stage.total_mass, velocity, stage.CD, rho)
        stage.main_diameter = self.get_diameter(stage.area)
        stage.spill_hole_diameter = SPILL_HOLE_RATIO * stage.main_diameter

    def _opening_shock(self, stage: Stage, velocity: float) -> float:
        rho = Physics.air_density(stage.deploy_altitude)
        fill_time = self.get_fill_time(stage.main_diameter, velocity)
        x1 = self.get_X1_param(stage.total_mass, velocity, stage.area, stage.CD, rho, fill_time)
        return self.get_opening_shock(stage.CD, stage.area, rho, velocity, x1)

    def _shock_limit(self, stage: Stage) -> float:
        
        return min(stage.max_shock_upper, stage.max_shock_lower) / stage.FOS

    def _max_deploy_velocity(self, stage: Stage) -> float:
        """Fastest the stage can open at without passing its shock limit (shock rises with velocity).
        Uses a binary search to find the max velocity that doesn't exceed the shock limit, because
        velocity is all tangled up in the X1 parameter and can't be solved for directly, so we iteratite 
        between the guesses of 0.1m/s and 500m/s until we find the max velocity that doesn't exceed the shock limit.
        we could probably do it in like 20, but 50 is round and why not."""
        limit = self._shock_limit(stage)
        low, high = 0.1, 500.0
        for _ in range(50):
            mid = (low + high) / 2
            if self._opening_shock(stage, mid) > limit:
                high = mid
            else:
                low = mid
        return low

    @staticmethod
    def get_terminal_velocity(mass: float, area: float, cd: float, air_density: float) -> float:
        """
        Terminal (steady descent) velocity in m/s, where drag balances weight.
        mass is total descending mass, kg
        area is the projected canopy area, m^2
        cd is drag coefficient (constant, from the geometry)
        air_density is air density in kg/m^3 at a given altitude
        """
        return math.sqrt((2 * mass * g) / (air_density * area * cd))

    @staticmethod
    def get_area(mass: float, velocity: float, cd: float, air_density: float) -> float:
        """
        Canopy area in m^2 needed to descend at `velocity` (inverse of
        _get_terminal_velocity).
        """
        return (2 * mass * g) / (air_density * cd * velocity**2)

    @staticmethod
    def get_diameter(area: float) -> float:
        """
        Canopy diameter in m for a given area (inverse of Geometry.getArea
        with the spill hole at SPILL_HOLE_RATIO of the diameter).
        """
        return math.sqrt(4 * area / (math.pi * (1 - SPILL_HOLE_RATIO**2)))

    @staticmethod
    def get_fill_time(diameter: float, velocity: float) -> float:
        """
        from p33 of http://mae-nas.eng.usu.edu/MAE_6530_Web/New_Course/launch_design/Section3.5.pdf
        also p32 of http://mae-nas.eng.usu.edu/MAE_5900_Web/5900/USLI_2010/Recovery/Section7.1.pdf
        """
        return 4*diameter / (velocity**0.85)



    @staticmethod
    def get_X1_param(mass: float, initial_velocity: float, area: float, cd: float, air_density: float, inflation_time: float) -> float:
        """
        returns X1 parameter by finding balistic parameter
        """

        balistic_param = (2 * mass)/(cd * air_density * area * initial_velocity * inflation_time)
        return balistic_param/(balistic_param +0.35)

    @staticmethod
    def get_opening_shock(cd: float, area: float, air_density: float, velocity: float, x1: float) -> float:
        """
        Peak opening force in N, max_shock = Cd * area * q * Cx * X1
        where q = 1/2 * air_density * velocity^2
        """
        q = 0.5 * air_density * velocity**2
        return cd * area * q * OPENING_SHOCK_CX * x1
