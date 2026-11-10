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

        if (self.main.exists):
            terminal_velocity = self.get_terminal_velocity(self.main.mass_upper + self.main.mass_lower, self.main.area, self.main.CD, LaunchSite.air_density(self.main.deploy_altitude))
        
        
        
        if (self.drogue.exists):
            pass
        
        if (self._main.is_existing):
            # know diameters, shroud line lengths
            pass
        
        # Code goes here, add extra helper methods as needed
        
        # 1) Size main based on landing velocity

        # 2) Size drogue based on main's lowest max opening shock (upper/lower)

        # 3) Find all unknown values

        # Cd should be a constant value, not a function of dimensions
        # Forget trying to alter the vent hole diam, just use the ratio provided
        # Shroud line lengths should be a ratio of main diam


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
    def get_fill_time(diameter: float, velocity: float) -> float:
        """
        from p33 of http://mae-nas.eng.usu.edu/MAE_6530_Web/New_Course/launch_design/Section3.5.pdf
        also p32 of http://mae-nas.eng.usu.edu/MAE_5900_Web/5900/USLI_2010/Recovery/Section7.1.pdf
        """
        return 4*diameter / (velocity**0.85)

    
    
    @staticmethod
    def get_balistic_param(mass: float, initial_velocity: float, area: float, cd: float, air_density: float, inflation_time: float) -> float:
        """
        returns the balistic parameter
        """
        
        return (2 * mass)/(cd * air_density * area * initial_velocity * inflation_time)
    
    

    