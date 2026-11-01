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


    #any chute design will have area implemented the same, a diameter, and a vent diameter (could change for torroidal chute, but )
    @property
    def chuteDiameter(self) -> float:
        """Canopy diameter in m."""
        pass
    
    @property
    def chuteHeight(self) -> float:
        """Canopy height in m."""
        pass
    
    
    @property
    def ventDiameter(self) -> float:
        """vent hole diameter in m."""
        pass
    
    @property
    def area(self) -> float:
        """Canopy area in m^2."""
        """the reason this is in the base class is that the canopy area basically just reffers to the collumn(ish shape) of air underneath the chute."""
        return (self.chuteDiameter**2 * math.pi) - (self.ventDiameter**2 * math.pi)
    # ---------------------------------------------------------------------

    # per-geometry interface goes here: one @abstractmethod for each thing
    # a system needs to ask any geometry
    
    
    @abstractmethod
    def getCD(self) -> float:
        """Return the drag coefficient for this geometry."""
        pass
    #get cd baseline fropm config defaults
    
    
    
    
    
    @abstractmethod
    def getDXFpoints(self, n: int) -> list[tuple[float, float]]:
        """Return a list of (x, y) points for the geometry's outline. n is number of gores the chute is sliced into."""
        pass
    


class Toroidal(Geometry):
    def area(self) -> float:
        pass # if we want to ever do torroidal, we can implement it here,
             #but for now we don't need it cz we just doing semi-elipsoids

class SemiElipsoid(Geometry):
    
    def __init__(self, chute_diameter: float, chute_height: float, vent_diameter: float):
        self.chuteDiameter = chute_diameter
        self.chuteHeight = chute_height
        self.ventDiameter = vent_diameter
        
    


    def getDXFpoints(self, n: int) -> list[tuple[float, float]]:
        """Return a closed loop of (x, y) points (in meters) outlining one gore.

        Arc-length model: the gore's half-width at canopy radius r is the arc
        length r * pi / n, rather than the chord r * sin(pi / n).

        Naming: r, z are canopy coordinates (distance from the chute axis, and
        height above the bottom edge). x, y are flat-pattern coordinates.

        Starts at the bottom-left of the gore (0, 0), goes up the left edge,
        across the vent, down the right edge, and returns to (0, 0).
        n is the number of gores the chute is sliced into.
        """
        PTS_PER_INCH = 30          # target density; spec says 20-50
        METERS_PER_INCH = 0.0254

        D = self.chuteDiameter
        H = self.chuteHeight
        V = self.ventDiameter
        if n < 3:
            raise ValueError("need at least 3 gores")
            # we need at least 3 gores to make a closed shape, otherwise basically just a flat sheet
        if not (0 <= V < D):
            raise ValueError("vent diameter must be positive or 0, and < chute diameter")

        #t is confusing to understand; it is a parametrized parameter, it is basically for keeping track of how far along the quarter elipse we are. 
        #on a normal quarter circle, t would be the polar angle, but since a isnt b, t is just a parameter
        #on a unit, normal quarter circle, r (from the center axis) would be cos(t), and z (height) would be sin(t), but since a != b, we have to use a different formule, r (from the center axis) is a*cos(t), and z (height off the plane) is b*sin(t) 
        
        #this leaves us with: 
        # Quarter-ellipse profile: r = a*cos(t), z = b*sin(t), t in [0, t_max]
        # (r = radius from chute axis, z = height above the plane).
        # t is only a curve parameter, not the polar angle, since a != b.
        a, b = D / 2, H
        
        #t_max found from v/2=a*cos(t_max), so t_max = acos(V/(2*a))
        t_max = math.acos(V / (2*a) )   # point where r = vent radius (V/2)



        ### BELOW IS UNCOMMENTED ###
        
        # Fine pass: cumulative arc length of the profile as a function of t.
        t_fine = np.linspace(0, t_max, 4000)
        r_fine = a * np.cos(t_fine)
        z_fine = b * np.sin(t_fine)
        seg = np.hypot(np.diff(r_fine), np.diff(z_fine))
        s_fine = np.concatenate(([0.0], np.cumsum(seg)))
        total_len = s_fine[-1]

        # Pick the point count from the target density, then space the points
        # evenly along the curve (not evenly in t) by inverting s(t).
        num_pts = max(2, math.ceil(total_len / METERS_PER_INCH * PTS_PER_INCH))
        t = np.interp(np.linspace(0.0, total_len, num_pts), s_fine, t_fine)

        r = a * np.cos(t)
        z = b * np.sin(t)

        # Arc-length model: half-width is the arc along the circle at radius r.
        half_w = r * math.pi / n

        # Pattern height: accumulate slant length, minus the width change.
        dr, dz, dw = np.diff(r), np.diff(z), np.diff(half_w)
        dy = np.sqrt(np.maximum(dr**2 + dz**2 - dw**2, 0.0))
        y = np.concatenate(([0.0], np.cumsum(dy)))

        # Pattern x: centerline at x = half_w[0] so the bottom-left corner is x = 0.
        x_left = half_w[0] - half_w
        x_right = half_w[0] + half_w

        points = [(float(x_left[i]), float(y[i])) for i in range(num_pts)]                # up the left edge
        points += [(float(x_right[i]), float(y[i])) for i in range(num_pts - 1, -1, -1)]  # down the right edge
        points.append((0.0, 0.0))                                                          # close the loop
        return points
        
    
    

    

        
        
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


