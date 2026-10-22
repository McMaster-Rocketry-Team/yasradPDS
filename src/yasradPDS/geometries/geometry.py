# geometry objects are stateless solvers, they do not hold on to values.
# values should be taken as needed in method parameters, specific implementations
# can import their geometry-specific constants from defaults.py, 
# any universal constants may be imported here from constants.py

from abc import ABC, abstractmethod

# interface
class Geometry(ABC):

    # common math shared by every geometry goes here as ordinary methods
    # that build on the abstract ones below

    # ---------------------------------------------------------------------

    # per-geometry interface goes here: one @abstractmethod for each thing
    # a system needs to ask any geometry

    @property
    @abstractmethod
    def area(self) -> float:
        """Canopy area in m^2."""
        pass


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