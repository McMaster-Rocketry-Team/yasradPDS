# holds atmosphere math and standards + real world coordinates for weather fetching
#
# NOTE: Environment functions (env.density(h), env.wind_velocity_x(h), ...)
# take height ASL. Stage.deploy_altitude and RocketPy parachute
# trigger heights are AGL. Convert with asl(env, h) before lookups.
# NOTE: Removed RocketPy ensemble since its dataset is disabled. Can make our own ensemble if we have our own dataset.

import math
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable

import pytz
from rocketpy import Environment

WindProfile = float | list[tuple[float, float]]  # constant m/s, or [(h_asl_m, m/s), ...]

@dataclass(frozen=True)
class LaunchSite:
    name: str
    latitude: float   # deg, + north
    longitude: float  # deg, + east
    elevation: float  # m ASL; set explicitly, don't rely on Open-Elevation (RocketPy built-in, not confirmed to be stable)
    timezone: str = "UTC"

    def __post_init__(self):
        pytz.timezone(self.timezone)  # raises UnknownTimeZoneError on a bad name
        if not math.isfinite(self.elevation):
            raise ValueError(f"{self.name}: elevation must be finite, got {self.elevation}")
        if not -90 <= self.latitude <= 90:
            raise ValueError(f"{self.name}: latitude must be in [-90, 90], got {self.latitude}")
        if not -180 <= self.longitude <= 180:
            raise ValueError(f"{self.name}: longitude must be in [-180, 180], got {self.longitude}")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LaunchSite":
        """Build from a config block (cli.py), e.g. defaults.json["launch_site"]."""
        try:
            return cls(**data)
        except TypeError as e:
            raise TypeError(f"launch_site: {e}") from None

def asl(ref: LaunchSite | Environment, h_agl: float) -> float:
    """
    Convert height above ground level to above sea level (m).

    Pass the Environment for lookups: forecast replaces the elevation
    with the weather model's own ground height. Pass the LaunchSite only when
    building a custom wind profile, before the Environment exists.
    """
    return h_agl + float(ref.elevation)

def _base(site: LaunchSite, date: datetime | None = None) -> Environment:
    return Environment(
        date=date,
        latitude=site.latitude,
        longitude=site.longitude,
        elevation=site.elevation,
        timezone=site.timezone,
    )

def standard(site: LaunchSite) -> Environment:
    """ISA, no wind. Offline and deterministic: use for sizing and tests."""
    env = _base(site)
    env.set_atmospheric_model(type="standard_atmosphere")
    return env

def custom_wind(site: LaunchSite, wind_u: WindProfile = 0, wind_v: WindProfile = 0) -> Environment:
    """
    ISA temperature/pressure + design wind profile.

    wind_u is the east component, wind_v the north component. Each is either a
    constant (m/s) or a list of (height ASL m, m/s) points, linearly interpolated.
    """
    env = _base(site)
    # Typed as Any to silence a false type-checker warning: RocketPy's wind_u/wind_v
    # default to 0, so checkers assume int, but a list of points is also valid.
    wind: dict[str, Any] = {"wind_u": wind_u, "wind_v": wind_v}
    # pressure/temperature left unset -> RocketPy uses ISA for both.
    env.set_atmospheric_model(type="custom_atmosphere", **wind)
    return env

def forecast(site: LaunchSite, date: datetime, source: str = "GFS") -> Environment:
    """Real forecast. Needs network; date must be within ~1-2 weeks of today."""
    env = _base(site, date)
    env.set_atmospheric_model(type="Forecast", file=source)
    return env

_MODELS: dict[str, Callable[..., Environment]] = {
    "standard": standard,
    "custom": custom_wind,
    "forecast": forecast,
}

def build(site: LaunchSite, model: str = "standard", **kwargs) -> Environment:
    """Build an Environment by model name; kwargs go to that model's function."""
    factory = _MODELS.get(model)
    if factory is None:
        raise ValueError(f"unknown atmosphere model {model!r}; known: {sorted(_MODELS)}")
    return factory(site, **kwargs)
