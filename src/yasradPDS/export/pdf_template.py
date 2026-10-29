# lays out the printable PDF gore pattern / template at true scale from the
# system's canopy geometry

#from ..systems.system import System
#from yasradPDS.utils.constants import PdfConstants as consts

import pymupdf as pdf
import numpy as np
#import math 
#import geometries

UNITS_PER_INCH = 72

#Printing Variables, determines the properties of the export
SEAM_LINEWEIGHT : float = 2
ALLOWANCE_LINEWEIGHT : float = 1
BOUNDING_BOX_LINEWEIGHT : float = 0.5


#Use system to generate export
"""
def system_pdf_export(sys : System, stage : int, pts): #Remove points post testing
    points : np.ndarray = sys.get(stage, "gore_outline")
    allowance_points = offset_points(pts, 72)
    _generate_template_pdf(points, allowance_points, consts.PAGE_SAFE_MARGIN, consts.PAGE_WIDTH, consts.PAGE_HEIGHT)

    
    pass

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



    _pages_horizontal : int = 3 #Number of horizontal pages ---- compute from points/Parameter, tmp set to 3
    _pages_vertical : int  = 3#Number of vertical pages ---- compute from points/Parameter
    _total_pages = _pages_horizontal * _pages_vertical

    centerX = (_page_printable_space_horizontal * _pages_horizontal * 72) / 2
    centerY = (_page_printable_space_vertical * _pages_vertical * 72 / 2)
    
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
        shape.finish(width = 0.5, color = pdf.pdfcolor["black"])
        shape.commit()


    #Adds an offset to every point to center it
    correctedCoordToOrgin : np.ndarray = np.ndarray(gore_points_pdf.shape, dtype=float)
    for i in range(gore_points_pdf.shape[0]):
        correctedCoordToOrgin[i, :] = [gore_points_pdf[i, 0] + centerX, gore_points_pdf[i, 1] + centerY] 
    pageCoord : list = [0, 0]



    index = 0
    shapes_seam : list[pdf.Shape] = []
    
    for i in range(_total_pages):
        shapes_seam.append(doc[i].new_shape())

    while index < gore_points_pdf.shape[0] - 1:
        pageCoord[0] = int(correctedCoordToOrgin[index, 0] / (_page_printable_space_horizontal * 72))
        pageCoord[1] = int(correctedCoordToOrgin[index, 1] / (_page_printable_space_vertical * 72))
        if(pageCoord[0] < _pages_horizontal and pageCoord[1] < _pages_vertical):
            pg = _page_num_based_on_coords(pageCoord[0], pageCoord[1], _pages_horizontal, _pages_vertical)
            localCurrCoord = _coordinates_to_local_draw_space(pageCoord[0], pageCoord[1], correctedCoordToOrgin[index, :], _page_printable_space_horizontal, _page_printable_space_vertical, safe_margin)
            localPrevCoord = _coordinates_to_local_draw_space(pageCoord[0], pageCoord[1], correctedCoordToOrgin[index + 1, :], _page_printable_space_horizontal, _page_printable_space_vertical, safe_margin)
            shapes_seam[pg].draw_line(pdf.Point(localCurrCoord[0], localCurrCoord[1]), pdf.Point(localPrevCoord[0], localPrevCoord[1]))
        index += 1

    for i in shapes_seam:
        i.finish(closePath= False)
        i.commit()


    shapes_allowance : list[pdf.Shape] = []
        
    for i in range(_total_pages):
        shapes_allowance.append(doc[i].new_shape())

    index = 0
    correctedCoordToOrgin : np.ndarray = np.ndarray(allowance_points_pdf.shape, dtype=float)
    for i in range(allowance_points_pdf.shape[0]):
        correctedCoordToOrgin[i, :] = [allowance_points_pdf[i, 0] + centerX, allowance_points_pdf[i, 1] + centerY] 
    pageCoord : list = [0, 0]

    while index < allowance_points_pdf.shape[0] - 1:
            pageCoord[0] = int(correctedCoordToOrgin[index, 0] / (_page_printable_space_horizontal * 72))
            pageCoord[1] = int(correctedCoordToOrgin[index, 1] / (_page_printable_space_vertical * 72))
            if(pageCoord[0] < _pages_horizontal and pageCoord[1] < _pages_vertical):
                pg = _page_num_based_on_coords(pageCoord[0], pageCoord[1], _pages_horizontal, _pages_vertical)
                localCurrCoord = _coordinates_to_local_draw_space(pageCoord[0], pageCoord[1], correctedCoordToOrgin[index, :], _page_printable_space_horizontal, _page_printable_space_vertical, safe_margin)
                localPrevCoord = _coordinates_to_local_draw_space(pageCoord[0], pageCoord[1], correctedCoordToOrgin[index + 1, :], _page_printable_space_horizontal, _page_printable_space_vertical, safe_margin)
                shapes_allowance[pg].draw_line(pdf.Point(localCurrCoord[0], localCurrCoord[1]), pdf.Point(localPrevCoord[0], localPrevCoord[1]))
            index += 1
    for i in shapes_allowance:
            i.finish(closePath= False)
            i.commit()
    
    return doc

def _page_num_based_on_coords(x : int, y : int, num_pages_horizontal : int, num_pages_vertical : int) -> int:
    """
    #Returns the page number (0 indexed) of the page that coordinates (x, y) refer to in pages
    num_pages_horizontal -> how many pages are in the template horizontally
    """
    if not (0 <= x < num_pages_horizontal and
            0 <= y < num_pages_vertical):
        raise ValueError(f"Page coordinates out of bounds: ({x}, {y})")

    return x + y * num_pages_horizontal

def _coordinates_to_local_draw_space(page_x, page_y, coords, drawable_width_per_page, drawable_height_per_page, safe_margin):
    """"""
    return [
        coords[0] - page_x * drawable_width_per_page * 72
        + safe_margin * 72,
        coords[1] - page_y * drawable_height_per_page * 72
        + safe_margin * 72
    ]

def offset_points(points: np.ndarray, dist: float) -> np.ndarray:
    newpts = []

    for i in range(len(points) - 1 ):
        delta = points[i + 1] - points[i]

        perp = np.array([-delta[1], delta[0]])
        norm = perp / np.linalg.norm(perp)

        newpts.append(points[i] + norm * dist)

    return np.array(newpts)

'''
all code beyond this line is temporary and will need to be updated for yasradPDS CDR, Temporary Testing
'''
def generate_circle_points(
    radius: float = 5,
    center_x: float = 0,
    center_y: float = 0,
    num_points: int = 1000
) -> np.ndarray:
    
    theta = np.linspace(0, 2 * np.pi, num_points, endpoint=True)

    x = center_x + radius * np.cos(theta)
    y = center_y + radius * np.sin(theta)

    return np.column_stack((x, y))


# Generate test geometry
points = generate_circle_points(
    radius=5,
    center_x=0,
    center_y=0,
    num_points=1000
)

# Test your PDF generator

doc = _generate_template_pdf(points, offset_points(points, 1))
doc.save("Circle Test.pdf")
doc.close()


