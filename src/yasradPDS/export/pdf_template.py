# lays out the printable PDF gore pattern / template at true scale from the
# system's canopy geometry

from yasradPDS.systems.system import System
from yasradPDS.utils.constants import PdfConstants as consts
from yasradPDS.config.defaults import FILE_PATH

import math
import pymupdf as pdf
import numpy as np

#Constants that won't need to be changed
SEAM_LINEWEIGHT : float = 2 #Lineweights are in pdf pixels
ALLOWANCE_LINEWEIGHT : float = 1
BOUNDING_BOX_LINEWEIGHT : float = 0.5


#Use system to generate export

def pdf_export(sys : System, stage : int, file_name : str | None = None): #Remove points post testing
    """Generates the parachute PDF stitching templates for the stage in system. if a file_name is provided, it is saved to default path with that name """
    points : np.ndarray = sys.get(stage, "gore_outline")*39.3700787 #Meter to inches conversion
    allowance_points = offset_points(points, consts.ALLOWANCE)
    pdf = _generate_template_pdf(points, allowance_points, consts.PAGE_SAFE_MARGIN, consts.PAGE_WIDTH, consts.PAGE_HEIGHT)
    if file_name:
        pdf.save(FILE_PATH + file_name + ".pdf")
    pdf.close()



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
    """Converts a set of coordinates to the local draw area.
    """
    x : np.ndarray
    y : np.ndarray
    x = coords[0] - page_x * drawable_width_per_page + safe_margin
    y = coords[1] - page_y * drawable_height_per_page + safe_margin
        

    return([x, y])

def _insert_points_crossing_boundary(points: np.ndarray, bounds_width: float, bounds_height: float, number_vertical: int, number_horizontal: int) -> np.ndarray:
    """Returns an array such that If a point is to cross a boundary between pages, add a point at the boundary"""
    
    
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
    Offsets a closed polygon by dist in whatever units the polygon was created in
    """
    if np.allclose(points[0], points[-1]):
        points = points[:-1]

    n = len(points)

    #Determine +ive/-ive area to determine which normal vector we use
    signed_area = 0.5 * np.sum(points[:, 0] * np.roll(points[:, 1], -1) - np.roll(points[:, 0], -1) * points[:, 1])

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

    result = np.vstack((result, result[0]))

    return result
