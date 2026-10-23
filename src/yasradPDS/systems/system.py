# system objects hold knowns and unknowns
# they define what the variables are, and keep them all in 
# one place so that exports and analyses can be performed by
# passing just a single system object

from math import isclose
from abc import ABC, abstractmethod
from dataclasses import dataclass, fields
from typing import Any, ClassVar


class UnknownValueError(Exception):
    pass

@dataclass(kw_only=True)
class Line:
    # knowns, manufacturer supplied
    density: float # kg/m
    break_strength: float # N
    max_epsilon: float # elongation at break %/100

    # unknowns
    length: float | None = None  
    count: int = 1 # lines in parallel

    def __post_init__(self):
        for f in fields(self):
            v = getattr(self, f.name)
            if isinstance(v, (int, float)) and v <= 0:
                raise ValueError(f"Line.{f.name} must be > 0, got {v}")

    @property
    def k(self) -> float:
        """Stiffness of the whole element, N/m."""
        if self.length is None:
            raise UnknownValueError("line length is unknown")
        return self.count * self.break_strength / self.max_epsilon / self.length

@dataclass(kw_only=True)
class Stage():
    # knowns
    name: str
    geometry: str
    gore_count: int
    deploy_altitude: float # m
    deploy_velocity: float # m/s
    target_velocity: float # m/s
    mass_upper: float # kg
    mass_lower: float # kg
    cord_upper: Line
    cord_lower: Line
    shroud: Line
    max_shock_upper: float # N
    max_shock_lower: float # N
    fabric_density: float # kg/m^2
    porosity: float

    # unknowns
    main_diameter: float | None = None # m
    spill_hole_diameter: float | None = None # m
    area: float | None = None # m^2
    fill_time: float | None = None # s
    
    _NON_ZERO_PARAMS = ("target_velocity", "mass_upper", "mass_lower",
                    "max_shock_upper", "max_shock_lower", "fabric_density")

    def __post_init__(self):
        for f in fields(self):
            v = getattr(self, f.name)
            if isinstance(v, (int, float)) and v < 0:
                raise ValueError(f"{self.name}: {f.name} must be >= 0, got {v}")
        for name in self._NON_ZERO_PARAMS:
            if getattr(self, name) == 0:
                raise ValueError(f"{self.name}: {name} must be > 0")
        for name in ("cord_upper", "cord_lower", "shroud"):
            v = getattr(self, name)
            if isinstance(v, dict):
                try:
                    setattr(self, name, Line(**v))
                except (ValueError, TypeError) as e:
                    raise type(e)(f"{self.name}.{name}: {e}") from None
        for name in ("cord_upper", "cord_lower"):
            if getattr(self, name).length is None:
                raise ValueError(f"{self.name}.{name}: length is required")
        if self.gore_count < 3:
            raise ValueError(f"{self.name}: gore_count must be >= 3")
        if self.shroud.count == 1:
            self.shroud.count = self.gore_count
        elif self.shroud.count < 3:
            raise ValueError(f"{self.name}: shroud.count must be >= 3")
        if not 0 <= self.porosity <= 1:
            raise ValueError(f"{self.name}: porosity must be in [0, 1]")

    @property
    def total_mass(self) -> float:
        return self.mass_upper + self.mass_lower


# interface
class System(ABC):
    _stages: ClassVar[dict[str, type[Stage]]]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "_stages"):
            raise TypeError(f"{cls.__name__} must define stages")

    def __init__(self, **stage_info: dict):
        if extra := stage_info.keys() - self._stages.keys():
            raise TypeError(f"no such stage(s): {sorted(extra)}")
        if missing := self._stages.keys() - stage_info.keys():
            raise TypeError(f"missing info for stage(s): {sorted(missing)}")

        self._stage_list = [
            stage_cls(name=name, **stage_info[name])
            for name, stage_cls in self._stages.items()
        ]
        for a, b in zip(self._stage_list, self._stage_list[1:]):
            if not isclose(a.total_mass, b.total_mass):
                raise ValueError(
                    f"total mass differs between {a.name!r} and {b.name!r}: "
                    f"{a.total_mass} vs {b.total_mass} kg"
                )
        self._solve()

    @property
    def stage_count(self) -> int:
        """Returns the number of deployment stages."""
        return len(self._stage_list)

    def get(self, stage: int, name: str) -> Any:
        """
        Value of any field on any stage. Raises if the value is still unknown.
        
        Stage is an int representing the deployment stage in order of occurrence
        (i.e. 0 = drogue, 1 = main). Throws IndexError if out of bounds.
        """
        if not 0 <= stage < self.stage_count:
            raise IndexError(
                f"stage {stage} out of range (0 to {self.stage_count - 1})"
            )
        value = self._stage_list[stage]
        for part in name.split("."):
            try:
                value = getattr(value, part)
            except AttributeError:
                raise KeyError(f"stage {stage} has no field {name!r}") from None
        if value is None:
            raise UnknownValueError(f"{name} is unknown for stage {stage}")
        return value

    @abstractmethod
    def _solve(self) -> None:
        pass 


_REGISTRY: dict[str, type[System]] = {}
    
def register(name: str):    
    if name in _REGISTRY:
        raise ValueError(f"system type {name!r} is already registered")

    def decorator(cls: type[System]) -> type[System]:
        _REGISTRY[name] = cls
        return cls
    return decorator

def new_system(system_type: str, **kwargs) -> System:
    cls = _REGISTRY.get(system_type)
    if cls is None:
        raise ValueError(
            f"unknown system type {system_type!r}; known: {sorted(_REGISTRY)}"
        )
    return cls(**kwargs)
