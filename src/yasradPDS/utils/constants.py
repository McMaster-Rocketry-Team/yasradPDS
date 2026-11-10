# fixed physical constants (gravity, gas constant, standard sea level values)

class PhysicalConstants:
    G = 9.81
    BASE_RHO = 1.225 # kg/m^3 air density at sea level
    BASE_TEMP = 228.15 # K at sea level

"""PDF Export Constants"""
class PdfConstants:
    ALLOWANCE = 1
    PAGE_SAFE_MARGIN = 0.5 #In Inches
    PAGE_WIDTH = 8.5 #In Inches
    PAGE_HEIGHT = 11 #In Inches