from .geometry import Geometry, register
import math
import numpy as np
from yasradPDS.config.defaults import POINTS_PER_METER, SEMI_ELIPSOID_CD



@register("semi_elipsoid")
class SemiElipsoid(Geometry):

    # no __init__: a SemiElipsoid holds no dimensions, it is just the solver for
    # this shape. the dimensions come in through each method call.

    def getCD(self) -> float:
        """
        Returns the drag coefficient (Cd) of a semi-ellipsoid parachute
        """
        return SEMI_ELIPSOID_CD

    def getDXFpoints(self, n: int, chute_diameter: float, chute_height: float, vent_diameter: float) -> np.ndarray:
        """Return a closed loop of (x, y) points (in meters) outlining one gore,
        as an (N, 2) numpy array with one (x, y) point per row.

        Arc-length model: the gore's half-width at canopy radius r is the arc
        length r * pi / n, rather than the chord r * sin(pi / n).

        Naming: r, z are canopy coordinates (distance from the chute axis, and
        height above the bottom edge). x, y are flat-pattern coordinates.

        Starts at the bottom-left of the gore (0, 0), goes up the left edge,
        across the vent, down the right edge, and returns to (0, 0).
        n is the number of gores the chute is sliced into.
        """
        D = chute_diameter
        H = chute_height
        V = vent_diameter
        if n < 3:
            raise ValueError("need at least 3 gores")
            # we need at least 3 gores to make a closed shape, otherwise basically just a flat sheet
        if not (0 <= V < D):
            raise ValueError("vent diameter must be positive or 0, and < chute diameter")

        #t is confusing to understand; it is a parametrized parameter, it is basically for keeping track of how far along the quarter elipse we are.
        #on a normal quarter circle, t would be the polar angle, but since a isnt b, t is just a parameter
        #on a unit, normal quarter circle, r (from the center axis) would be cos(t), and z (height) would be sin(t), but since a != b, we have to use different formulae, r (from the center axis) is a*cos(t), and z (height off the plane) is b*sin(t)

        #this leaves us with:
        # Quarter-ellipse profile: r = a*cos(t), z = b*sin(t), t in [0, t_max]
        # (r = radius from chute axis, z = height above the plane).
        # t is only a curve parameter, not the polar angle, since a != b.
        a, b = D / 2, H

        #t_max found from v/2=a*cos(t_max), so t_max = acos(V/(2*a))
        t_max = math.acos(V / (2*a) )   # point where r = vent radius (V/2)



        # The profile is parametrized by t, but equal steps in t are NOT equal steps
        # along the fabric: near t = 0 the curve is mostly moving in z (steep) and
        # near t_max it is mostly moving in r, so the spacing would bunch up. We want
        # evenly spaced points along the curve itself, so we first build a lookup
        # table of "distance along the curve" versus t, and invert it afterwards.

        # Fine pass: cumulative arc length of the profile as a function of t.
        # 40000 samples is far finer than the output density, so treating each tiny
        # piece of the curve as a straight line is accurate enough for our purposes.
        t_fine = np.linspace(0, t_max, 40000)

        # the (r, z) position on the ellipse at each of those fine t values
        r_fine = a * np.cos(t_fine)
        z_fine = b * np.sin(t_fine)

        # seg[i] is the straight-line length between sample i and i+1 (pythagoras on
        # the r and z steps). a running total of those gives the arc length s from the
        # bottom edge (t = 0) up to each sample, with s = 0 at the start. s_fine ends
        # at total_len, the full length of the canopy profile from edge to vent.
        seg = np.hypot(np.diff(r_fine), np.diff(z_fine))
        s_fine = np.concatenate(([0.0], np.cumsum(seg)))
        total_len = s_fine[-1]

        # Pick the point count from the target density, then space the points
        # evenly along the curve (not evenly in t) by inverting s(t).
        # total_len is in meters, so multiplying by POINTS_PER_METER gives the number
        # of points. max(2, ...) makes sure we always have at least a start and an
        # end point.
        num_pts = max(2, math.ceil(total_len * POINTS_PER_METER))
        
        # np.interp(x, xp, fp) looks up t for each requested arc length: we ask for
        # num_pts evenly spaced distances from 0 to total_len, and it reads off the
        # t that gives each of those distances from the (s_fine -> t_fine) table.
        t = np.interp(np.linspace(0.0, total_len, num_pts), s_fine, t_fine)

        # now the real profile points, evenly spaced along the canopy surface
        r = a * np.cos(t)
        z = b * np.sin(t)

        # Arc-length model: half-width is the arc along the circle at radius r.
        # at radius r the full circle around the chute has circumference 2*pi*r, and
        # one of n gores gets 1/n of it, so its full width is 2*pi*r/n and its
        # half-width is pi*r/n. the gore is widest at the bottom edge (largest r)
        # and narrows toward the vent.
        half_w = r * math.pi / n

        # Pattern height: accumulate slant length, minus the width change.
        # dr, dz are how far the profile moves between consecutive points in radius
        # and height, and dw is how much the half-width changes over that same step.
        # the true distance travelled on the fabric surface is sqrt(dr^2 + dz^2),
        # but part of that "travel" is already accounted for by the edge sliding
        # sideways as the gore narrows (dw). what is left over, sqrt(dr^2+dz^2-dw^2),
        # is the vertical distance in the flat pattern. np.maximum(..., 0.0) guards
        # against tiny negative values from rounding, which would break the sqrt.
        # the cumulative sum turns those steps into a y coordinate for each point,
        # starting at y = 0 at the bottom edge.
        dr, dz, dw = np.diff(r), np.diff(z), np.diff(half_w)
        dy = np.sqrt(np.maximum(dr**2 + dz**2 - dw**2, 0.0))
        y = np.concatenate(([0.0], np.cumsum(dy)))

        # Pattern x: centerline at x = half_w[0] so the bottom-left corner is x = 0.
        # half_w[0] is the half-width at the bottom edge (the widest point), so
        # shifting the centerline to that x value puts the leftmost point of the
        # whole gore at x = 0. each edge then sits half_w to the left or right of
        # the centerline at that height.
        x_left = half_w[0] - half_w
        x_right = half_w[0] + half_w

        # build the closed outline: walk up the left edge from bottom to vent, then
        # come back down the right edge (reverse order, so the loop is continuous
        # across the vent), then repeat the first point to close the polygon.
        # the result is an (N, 2) float array of (x, y) rows, in meters.
        left = np.column_stack((x_left, y))                    # up the left edge
        right = np.column_stack((x_right, y))[::-1]            # down the right edge
        return np.vstack((left, right, [[0.0, 0.0]]))          # close the loop

