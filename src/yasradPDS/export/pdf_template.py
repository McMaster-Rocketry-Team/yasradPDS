# lays out the printable PDF gore pattern / template at true scale from the
# system's canopy geometry
"""
from ..systems.system import System
from ..utils.constants import PdfConstants as consts
"""

import math
import pymupdf as pdf
import numpy as np

#Constants that won't need to be changed
SEAM_LINEWEIGHT : float = 2 #Lineweights are in pdf pixels
ALLOWANCE_LINEWEIGHT : float = 1
BOUNDING_BOX_LINEWEIGHT : float = 0.5


#Use system to generate export
"""
def pdf_export(sys : System, stage : int, name : str): #Remove points post testing
    points : np.ndarray = sys.get(stage, "gore_outline")
    allowance_points = offset_points(sys.get(stage, "gore_outline"), 1)
    pdf = _generate_template_pdf(points, allowance_points, consts.PAGE_SAFE_MARGIN, consts.PAGE_WIDTH, consts.PAGE_HEIGHT)
    pdf.save(name)
    pdf.close()
"""


def _generate_template_pdf(gore_points : np.ndarray, allowance_points : np.ndarray, safe_margin : float = 0.5, page_width : float = 8.5, page_height : float = 11)-> pdf.Document:
    """
    gore_points, allowance_points -> the arrays of points containing info about the gore and allowance outlines
    safe_margin -> how close to the edge of the page can the plot get
    page_width, page_height -> dimensions of the type of paper

    Returns a pymupdf.Document object.
    call .save("String") on this object - See pymupdf Document documentation
    
    Inputs are in inches, internally gets converted to pdf units
    """



    gore_points_pdf = gore_points * 72
    allowance_points_pdf = allowance_points * 72

   


    _page_printable_space_horizontal : float = page_width -2 * safe_margin
    _page_printable_space_vertical : float = page_height - 2 * safe_margin
    vert_space : float = abs(np.max(allowance_points[:, 1]) - np.min(allowance_points[:, 1]) + 3)
    horiz_space : float = abs(np.max(allowance_points[:, 0]) - np.min(allowance_points[:, 0]) + 3)
    

    _pages_horizontal : int = math.ceil(horiz_space / (page_width - 2* safe_margin)) #Number of horizontal pages ---- compute from points/Parameter, tmp set to 3
    _pages_vertical : int  = math.ceil(vert_space / (page_height - 2* safe_margin)) #Number of vertical pages ---- compute from points/Parameter
    _total_pages = _pages_horizontal * _pages_vertical

    
    
    min_x = np.min(allowance_points_pdf[:, 0])
    max_x = np.max(allowance_points_pdf[:, 0])

    min_y = np.min(allowance_points_pdf[:, 1])
    max_y = np.max(allowance_points_pdf[:, 1])

    centerX = (_pages_horizontal * _page_printable_space_horizontal * 72 - (max_x - min_x)) / 2 - min_x
    centerY = (_pages_vertical * _page_printable_space_vertical * 72 - (max_y - min_y)) / 2 - min_y
    
    #Generate blank pdf for document with pages bounded and numbered
    doc = pdf.open()
    for i in range(_total_pages):
        doc.new_page(width=page_width * 72, height=page_height * 72)

    #draw bounding boxes and add numbering text
    for i in range(0, _total_pages):
        doc[i].insert_text(pdf.Point(safe_margin * 72, (safe_margin) * 72 + 11), str(i%(_pages_horizontal)) +","+str(int(i/_pages_horizontal)))
        shape = doc[i].new_shape()
        r = pdf.Rect(safe_margin * 72, safe_margin *72, (page_width - safe_margin) * 72, (page_height - safe_margin) * 72)
        shape.draw_rect(r)
        shape.finish(width = BOUNDING_BOX_LINEWEIGHT, color = pdf.pdfcolor["black"])
        shape.commit()


    #Adds an offset to every point to center it
    correctedCoordToOrgin : np.ndarray = np.ndarray(gore_points_pdf.shape, dtype=float)
    for i in range(gore_points_pdf.shape[0]):
        correctedCoordToOrgin[i, :] = [gore_points_pdf[i, 0] + centerX, gore_points_pdf[i, 1] + centerY] 
    correctedCoordToOrgin = _insert_points_crossing_boundary(correctedCoordToOrgin, _page_printable_space_horizontal * 72, _page_printable_space_vertical * 72, _pages_vertical, _pages_horizontal)
    pageCoord : list = [0, 0]
    index = 0
    shapes_seam : list[pdf.Shape] = []
    
    for i in range(_total_pages):
        shapes_seam.append(doc[i].new_shape())
    
    len = correctedCoordToOrgin.shape[0]

    while index < correctedCoordToOrgin.shape[0]:
        
        pageCoord[0] = math.floor(((correctedCoordToOrgin[index][0] + correctedCoordToOrgin[(index + 1)%len][0])/2) / (_page_printable_space_horizontal * 72))
        pageCoord[1] = math.floor(((correctedCoordToOrgin[index][1] + correctedCoordToOrgin[(index + 1)%len][1])/2) / (_page_printable_space_vertical * 72))
        if(pageCoord[0] < _pages_horizontal and pageCoord[1] < _pages_vertical):
            pg = _page_num_based_on_coords(pageCoord[0], pageCoord[1], _pages_horizontal, _pages_vertical)
            localCurrCoord = _coordinates_to_local_draw_space(pageCoord[0], pageCoord[1], correctedCoordToOrgin[index, :], _page_printable_space_horizontal * 72, _page_printable_space_vertical * 72, safe_margin * 72)
            localNextCoord = _coordinates_to_local_draw_space(pageCoord[0], pageCoord[1], correctedCoordToOrgin[(index + 1)%len, :], _page_printable_space_horizontal * 72, _page_printable_space_vertical * 72, safe_margin * 72)
            shapes_seam[pg].draw_line(pdf.Point(localCurrCoord[0], localCurrCoord[1]), pdf.Point(localNextCoord[0], localNextCoord[1]))
        index += 1

    for i in shapes_seam:
        i.finish(width=SEAM_LINEWEIGHT,closePath= False)
        i.commit()


    
    index = 0
    shapes_allowance : list[pdf.Shape] = []   
          
    for i in range(_total_pages):
        shapes_allowance.append(doc[i].new_shape())
        
    correctedCoordToOrgin : np.ndarray = np.ndarray(allowance_points_pdf.shape, dtype=float)
    for i in range(allowance_points_pdf.shape[0]):
        correctedCoordToOrgin[i, :] = [allowance_points_pdf[i, 0] + centerX, allowance_points_pdf[i, 1] + centerY] 
    pageCoord : list = [0, 0]
    correctedCoordToOrgin = _insert_points_crossing_boundary(correctedCoordToOrgin, _page_printable_space_horizontal * 72, _page_printable_space_vertical * 72, _pages_vertical, _pages_horizontal)
    len = correctedCoordToOrgin.shape[0]
    
    
    while index < correctedCoordToOrgin.shape[0]:
            pageCoord[0] = math.floor(((correctedCoordToOrgin[index][0] + correctedCoordToOrgin[(index + 1)%len][0])/2) / (_page_printable_space_horizontal * 72))
            pageCoord[1] = math.floor(((correctedCoordToOrgin[index][1] + correctedCoordToOrgin[(index + 1)%len][1])/2) / (_page_printable_space_vertical * 72))
            if(pageCoord[0] < _pages_horizontal and pageCoord[1] < _pages_vertical):
                pg = _page_num_based_on_coords(pageCoord[0], pageCoord[1], _pages_horizontal, _pages_vertical)
                localCurrCoord = _coordinates_to_local_draw_space(pageCoord[0], pageCoord[1], correctedCoordToOrgin[index, :], _page_printable_space_horizontal *72, _page_printable_space_vertical *72, safe_margin *72)
                localNextCoord = _coordinates_to_local_draw_space(pageCoord[0], pageCoord[1], correctedCoordToOrgin[(index + 1) % len, :], _page_printable_space_horizontal * 72, _page_printable_space_vertical*72, safe_margin*72)
                shapes_allowance[pg].draw_line(pdf.Point(localCurrCoord[0], localCurrCoord[1]), pdf.Point(localNextCoord[0], localNextCoord[1]))
            index += 1
    for i in shapes_allowance:
            i.finish(width= ALLOWANCE_LINEWEIGHT, closePath= False)
            i.commit()
    
    return doc

def _page_num_based_on_coords(x : int, y : int, num_pages_horizontal : int, num_pages_vertical : int) -> int:
    """
    Returns the page number (0 indexed) of the page that coordinates (x, y) refer to in pages
    num_pages_horizontal -> how many pages are in the template horizontally
    """
    return x + y * num_pages_horizontal

def _coordinates_to_local_draw_space(page_x : int, page_y : int, coords : np.array, drawable_width_per_page : float, drawable_height_per_page : float, safe_margin : float):
    """Converts a set of coordinates to the local draw area, if the point goes out of bounds, adds multiples of truncate_vector until it returns in bounds
    
    Needs checking to see if a solve is even possible using truncate vector, otherwise the point gets moved to the corner
    """
    x : np.ndarray
    y : np.ndarray
    x = coords[0] - page_x * drawable_width_per_page + safe_margin
    y = coords[1] - page_y * drawable_height_per_page + safe_margin
        

    return([x, y])

def _insert_points_crossing_boundary(points: np.ndarray, bounds_width: float, bounds_height: float, number_vertical: int, number_horizontal: int) -> np.ndarray:
    numpts = len(points)
    newpts = []

    xbounds = [i * bounds_width for i in range(1, number_horizontal)]

    ybounds = [i * bounds_height for i in range(1, number_vertical)]

    for j in range(numpts):
        x1, y1 = points[j]
        x2, y2 = points[(j + 1) % numpts]
        dx = x2 - x1
        dy = y2 - y1
        intersections = []
        if abs(dx) > 1e-12:
            for xb in xbounds:
                ratio = (xb - x1) / dx
                if 0 < ratio < 1:
                    y = y1 + ratio * dy
                    intersections.append((ratio, [xb, y]))

        if abs(dy) > 1e-12:
            for yb in ybounds:
                ratio = (yb - y1) / dy
                if 0 < ratio < 1:
                    x = x1 + ratio * dx
                    intersections.append((ratio, [x, yb]))

        # Sort intersections along the edge
        intersections.sort(key=lambda item: item[0])

        newpts.append(points[j])

        for _, intersection in intersections:
            newpts.append(intersection)

    return np.array(newpts, dtype=float)

def offset_points(points: np.ndarray, dist: float) -> np.ndarray:
    """
    Offset a closed polygon by dist.
    Returns a closed loop, with the first point repeated at the end.
    """

    # Remove duplicate closing point, if present
    if np.allclose(points[0], points[-1]):
        points = points[:-1]

    n = len(points)

    # Determine polygon orientation
    signed_area = 0.5 * np.sum(
        points[:, 0] * np.roll(points[:, 1], -1)
        - np.roll(points[:, 0], -1) * points[:, 1]
    )

    orientation = 1 if signed_area > 0 else -1

    # Calculate offset lines for each edge
    directions = np.roll(points, -1, axis=0) - points
    lengths = np.linalg.norm(directions, axis=1)

    if np.any(lengths < 1e-12):
        raise ValueError("Polygon contains zero-length edges")

    directions = directions / lengths[:, None]

    normals = orientation * np.column_stack((
        directions[:, 1],
        -directions[:, 0]
    ))

    offset_starts = points + dist * normals

    result = []

    for i in range(n):
        prev = (i - 1) % n

        p1 = offset_starts[prev]
        d1 = directions[prev]

        p2 = offset_starts[i]
        d2 = directions[i]

        cross = d1[0] * d2[1] - d1[1] * d2[0]

        if abs(cross) < 1e-10:
            # Parallel edges: use a midpoint fallback
            result.append((p1 + p2) / 2)
            continue

        delta = p2 - p1

        t = (
            delta[0] * d2[1] - delta[1] * d2[0]
        ) / cross

        intersection = p1 + t * d1

        result.append(intersection)

    result = np.array(result)

    # Explicitly close the polygon
    result = np.vstack((result, result[0]))

    return result
'''
all code beyond this line is for temp testing
'''
POINTS_PER_METER = 1181
def getDXFpoints(n: int, chute_diameter: float, chute_height: float, vent_diameter: float) -> np.ndarray:
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
        # 4000 samples is far finer than the output density, so treating each tiny
        # piece of the curve as a straight line is accurate enough for our purposes.
        t_fine = np.linspace(0, t_max, 4000)

        # the (r, z) position on the ellipse at each of those fine t values
        r_fine = a * np.cos(t_fine)
        z_fine = b * np.sin(t_fine)

        # seg[i] is the straight-line length between sample i and i+1 (pythagoras on
        # the r and z steps). a running sum of those gives the arc length s from the
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



points = np.array(getDXFpoints(12, 0.5, 0.5, 0.05)) * 39
import matplotlib.pyplot as plt

offset_pts = offset_points(points, 1)
plt.plot(points[:, 0], points[:, 1], label="Gore")
plt.plot(offset_pts[:, 0], offset_pts[:, 1], label="Allowance")
plt.axis("equal")
plt.legend()
plt.show()
doc = _generate_template_pdf(points, offset_pts)
doc.save("Square Test.pdf")
doc.close()
