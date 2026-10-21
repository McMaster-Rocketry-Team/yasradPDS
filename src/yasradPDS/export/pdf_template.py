# lays out the printable PDF gore pattern / template at true scale from the
# system's canopy geometry
import pymupdf as pdf
import numpy as np
import math 




'''
all code beyond this line is temporary and will need to be updated for yasradPDS
'''
#Printer Settings:
seamLineWeight : float = 2 #Line weight assigned to seam lines on the template
allowanceLineWeight : float = 1 #Line weight assigned to seam allowance 
boundingBoxLineWeight : float = 0.5 #Line weight assigned to bounding box



#Parachute Parameters
seam_allowance : float = 2.5 #Excess material added to seam lines
hem_allowance : float = 2.5 #Excess material added to top and bottom open edges that require hemming

#Plot Parameters
print_overall_width : float = 16 #How wide the overall plot should be in inches
print_overall_height : float = 16 #How tall the overall plot should be in inches

#Print Parameters 

#E.g. letter size is 8.5" by 11"
page_width : float = 8.5
page_height : float = 11


#The margins on the page (How far from the edge of the page can the printer print)
page_left_margin : float = 0.5
page_right_margin : float = 0.5
page_top_margin : float = 0.5
page_bottom_margin : float = 0.5


#Dots per inch 
dpi : float = 600 



#Compute other variables related to page layout
printable_width_per_page : float = page_width - page_left_margin - page_right_margin
printable_height_per_page : float = page_height - page_top_margin - page_bottom_margin

num_pages_vertical : int = (int(print_overall_height / printable_height_per_page) + 1)
num_pages_horizontal : int = (int(print_overall_width / printable_width_per_page) + 1) 
number_of_pdf_pages =  num_pages_vertical * num_pages_horizontal

#Generate new blank pdf
doc = pdf.open()
for i in range(number_of_pdf_pages):
    doc.new_page(width=page_width * 72, height=page_height * 72)

#draw bounding boxes and add numbering text
for i in range(0, number_of_pdf_pages):
    doc[i].insert_text(pdf.Point(page_left_margin * 72, (page_top_margin) * 72 + 11), str(i%(num_pages_horizontal)) +","+str(int(i/num_pages_horizontal)))
    shape = doc[i].new_shape()
    r = pdf.Rect(page_left_margin * 72, page_top_margin *72, (page_width - page_right_margin) * 72, (page_height - page_bottom_margin) * 72)
    shape.draw_rect(r)
    shape.finish(width = 0.5, color = pdf.pdfcolor["black"])
    shape.commit()


#Test function
def line(x):
    return ((x/72)**2)*72

line = np.frompyfunc(line, 1, 1)

#Defining pymupdf coordinate width and height of the printable area on each page 
coord_height_per_page = printable_height_per_page * 72
coord_width_per_page = printable_width_per_page * 72


#Returns the page number (0 indexed) of the page that coordinates (x, y) relate to
def find_page_num_based_on_coords(x, y) -> int:
    pageNum : int
    pageNum = x + y*num_pages_horizontal
    return pageNum

def coordinates_to_local_draw_space(page_x, page_y, coords):
    newCoord = [coords[0] - page_x * coord_width_per_page + page_left_margin*72, coords[1] - page_y * coord_height_per_page + page_top_margin * 72]
    return newCoord


def plot_coordinates_on_pdf_2array(file : pdf.Document, x_coords : list, y_coords : list, orgin_x : int, orgin_y : int, lineweight : float):
    """Plots coordinates onto the pdf based on x_coords and y_coords"""
    curCoord : list = [x_coords[0], y_coords[0]]
    prevCoord : list = [x_coords[1], y_coords[1]]
    pageCoord : list = [0, 0]
    for i in range(0, len(x_coords)):
        curCoord = [x_coords[i], y_coords[i]]
        pageCoord[0] = int(x_coords[i] / (printable_width_per_page * 72))
        pageCoord[1] = int(y_coords[i] / (printable_height_per_page * 72))
        if(pageCoord[0] < num_pages_horizontal and pageCoord[1] < num_pages_vertical):
            pg = find_page_num_based_on_coords(pageCoord[0], pageCoord[1])
            localCurrCoord = coordinates_to_local_draw_space(pageCoord[0], pageCoord[1], curCoord)
            localPrevCoord = coordinates_to_local_draw_space(pageCoord[0], pageCoord[1], prevCoord)
            shape = file[pg].new_shape()
            shape.draw_line(pdf.Point(localCurrCoord[0], localCurrCoord[1]), pdf.Point(localPrevCoord[0], localPrevCoord[1]))
            shape.finish(width = lineweight, color = pdf.pdfcolor["black"])
            shape.commit()
            prevCoord = curCoord

def plot_coordinates_on_pdf_ndarray(file : pdf.Document, coords : np.ndarray, orgin_x : int, orgin_y : int, lineweight : float):
    """plots a set of points x, y. the coordniates array must come in size [n, 2] 
    (any number of rows, 2 columns (for x, y)). Additonally the points MUST be in order of connection.
    Coordinates are in pdf coordinates (72 units/inch)"""
    correctedCoordToOrgin : np.ndarray = np.ndarray(coords.shape, dtype=float)
    for i in range(coords.shape[0]):
        correctedCoordToOrgin[i, :] = [coords[i, 0] + orgin_x, coords[i, 1] + orgin_y] 
    pageCoord : list = [0, 0]
    index = 0
    while index < coords.shape[0] - 1:
        pageCoord[0] = int(correctedCoordToOrgin[index, 0] / (printable_width_per_page * 72))
        pageCoord[1] = int(correctedCoordToOrgin[index, 1] / (printable_height_per_page * 72))
        if(pageCoord[0] < num_pages_horizontal and pageCoord[1] < num_pages_vertical):
            pg = find_page_num_based_on_coords(pageCoord[0], pageCoord[1])
            localCurrCoord = coordinates_to_local_draw_space(pageCoord[0], pageCoord[1], correctedCoordToOrgin[index, :])
            localPrevCoord = coordinates_to_local_draw_space(pageCoord[0], pageCoord[1], correctedCoordToOrgin[index + 1, :])
            shape = file[pg].new_shape()
            shape.draw_line(pdf.Point(localCurrCoord[0], localCurrCoord[1]), pdf.Point(localPrevCoord[0], localPrevCoord[1]))
            shape.finish(width = lineweight, color = pdf.pdfcolor["black"])
            shape.commit()
        index += 1