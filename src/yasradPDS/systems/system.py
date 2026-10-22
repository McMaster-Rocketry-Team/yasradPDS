# system objects hold knowns and unknowns
# they define what the variables are, and keep them all in 
# one place so that exports and analyses can be performed by
# passing just a single system object

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, ClassVar

class InvalidStageError(Exception):
    pass

class UnknownValueError(Exception):
    pass

@dataclass(kw_only=True)
class Stage():
    # knowns
    name: str
    geometry: str
    gore_count: int
    deploy_altitude: float # m
    deploy_velocity: float # m/s
    target_velocity: float # m/s
    max_shock: float # N
    max_epsilon: float # shroud line % elongation at break
    porosity: float

    #  unknowns
    main_diameter: float | None = None # m
    spill_hole_diameter: float | None = None # m
    area: float | None = None # m^2
    line_length: float | None = None # m
    fill_time: float | None = None # s

# interface
class System(ABC):
    _stages: ClassVar[dict[str, type[Stage]]]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "_stages"):
            raise TypeError(f"{cls.__name__} must define stages")

    def __init__(self, *, dry_mass: float, **stage_info: dict):
        if extra := stage_info.keys() - self._stages.keys():
            raise TypeError(f"no such stage(s): {sorted(extra)}")
        if missing := self._stages.keys() - stage_info.keys():
            raise TypeError(f"missing info for stage(s): {sorted(missing)}")

        self.dry_mass = dry_mass
        self._stage_list = [
            stage_cls(name=name, **stage_info[name])
            for name, stage_cls in self._stages.items()
        ]
        self._solve()

    @property
    def stage_count(self) -> int:
        """Returns the number of deployment stages."""
        return len(self._stage_list)

    def get(self, stage: int, name: str) -> Any:
        """
        Value of any field on any stage. Raises if the value is still unknown.
        
        Stage is an int representing the deployment stage in order of occurance
        (i.e. 0 = drogue, 1 = main). Throws InvalidStageError if out of bounds.
        """
        if not 0 <= stage < self.stage_count:
            raise InvalidStageError(
                f"stage {stage} out of range (0 to {self.stage_count - 1})"
            )
        value = getattr(self._stage_list[stage], name)
        if value is None:
            raise UnknownValueError(f"{name} is unknown for stage {stage}")
        return value

    @abstractmethod
    def _solve(self) -> None:
        pass
    


_REGISTRY: dict[str, type[System]] = {}
    
def register(name: str):
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
