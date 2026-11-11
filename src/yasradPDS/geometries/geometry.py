# geometry objects are stateless solvers, they do not hold on to values.
# values should be taken as needed in method parameters, specific implementations
# can import their geometry-specific constants from defaults.py,
# any universal constants may be imported here from constants.py

from abc import ABC, abstractmethod
import math
import numpy as np

# interface
class Geometry(ABC):

    # common math shared by every geometry goes here as ordinary methods
    # that build on the abstract ones below

    # the only thing an instance "is" is its geometry type (the subclass). every
    # dimension (chute diameter, chute height, vent diameter) is passed into each
    # method as a parameter, so the same instance can be reused for any chute size.

    #any chute design will have area implemented the same, a diameter, and a vent diameter (could change for torroidal chute, but )
    def getArea(self, chute_diameter: float, vent_diameter: float) -> float:
        """Canopy area in m^2. Diameters in m."""
        """the reason this is in the base class is that the canopy area basically just reffers to the collumn(ish shape) of air underneath the chute."""
        
        return (chute_diameter/2)**2 * math.pi - (vent_diameter/2)**2 * math.pi
    # ---------------------------------------------------------------------

    # per-geometry interface goes here: one @abstractmethod for each thing
    # a system needs to ask any geometry


    @abstractmethod
    def getCD(self) -> float:
        """Return the drag coefficient for this geometry. Dimensions in m."""
        pass
    #get cd baseline fropm config defaults





    @abstractmethod
    def getDXFpoints(self, n: int, chute_diameter: float, chute_height: float, vent_diameter: float) -> np.ndarray:
        """Return an (N, 2) numpy array of (x, y) points for the geometry's outline. n is number of gores the chute is sliced into. Dimensions in m."""
        pass



'''
class Toroidal(Geometry):
    def getArea(self, chute_diameter: float, vent_diameter: float) -> float:
        pass # if we want to ever do torroidal, we can implement it here,
             #but for now we don't need it cz we just doing semi-elipsoids
'''





# don't touch
_REGISTRY: dict[str, type[Geometry]] = {}

def register(name: str):
    def decorator(cls: type[Geometry]) -> type[Geometry]:
        _REGISTRY[name] = cls
        return cls
    return decorator

def new_geometry(geometry_type: str) -> Geometry:
    cls = _REGISTRY.get(geometry_type)
    if cls is None:
        raise ValueError(
            f"unknown geometry type {geometry_type!r}; known: {sorted(_REGISTRY)}"
        )
    return cls()


