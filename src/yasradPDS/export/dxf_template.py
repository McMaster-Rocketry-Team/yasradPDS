"""Build and preview a laser-cut DXF

Points and allowances are in metres; DXF coordinates are in millimetres
"""

import ezdxf
import numpy as np
import matplotlib.pyplot as plt
from yasradPDS.geometries.semi_elipsoid import SemiElipsoid
##



#had to change inital way of doing it as if there was a bug when you had a vent diameter of zero there was some points that had nan cordinates
#and for some reason it wasnt crashing the program so the clean outline function just checks that the points make a closed geometry
def clean_outline(points: np.ndarray) -> np.ndarray:
    """Validate coordinates and remove consecutive and closing duplicates."""
    p = np.asarray(points, dtype=float)

    #just makes sure that the points at in a np array that is (x,y)
    if p.ndim != 2 or p.shape[1] != 2:
        raise ValueError("Outline must be an (x, y) array.")
    #checks every point to make sure no nan or infinities
    if not np.isfinite(p).all():
        raise ValueError("Outline contains invalid coordinates.")

    # Keep the first point and remove the next if its the same if not use it
    keep = np.ones(len(p), dtype=bool)
    keep[1:] = np.any(p[1:] != p[:-1], axis=1)
    p = p[keep]

    # DXF close=True connects the last point back to the first.
    if len(p) > 1 and np.array_equal(p[0], p[-1]):
        p = p[:-1]

    if len(p) < 3:
        raise ValueError("Outline needs at least three vertices.")

    return p


def build_system_template(
        system,
        stage: int,
        path: str,
        allowance_m : float,
        preview: bool = False,) -> None:
    
    points = system.get(stage , "gore_outline")
    export_dxf(points, path , allowance_m, preview)

##important this assumes geometry uses a np.ndarray with ordered (x,y)
def save_outline_dxf(points: np.ndarray, path: str) -> None:
    """Save ordered (x, y) gore points, supplied in metres, as a DXF outline."""
    points = clean_outline(points)
    doc = ezdxf.new("R2010")
    doc.units = 4  # millimetres

    doc.modelspace().add_lwpolyline(
        (points * 1000).tolist(),
        close=True,
    )
    doc.saveas(path)


def add_hem_allowance(points: np.ndarray, allowance_m: float) -> np.ndarray:
    """Add the same allowance around the entire outline, in metres."""
    p = clean_outline(points)

    edges = np.roll(p, -1, axis=0) - p
    edge_lengths = np.linalg.norm(edges, axis=1)

    #this is needed as it figures out if a corner is inwards or outwards
    area = np.sum(
        p[:, 0] * np.roll(p[:, 1], -1)
        - p[:, 1] * np.roll(p[:, 0], -1)
    )
    #now we just check the sign and based on this we know its direction
    direction = 1 if area > 0 else -1
    normals = direction * np.column_stack((edges[:, 1], -edges[:, 0]))
    normals /= edge_lengths[:, None]

    # Meet the offset of the incoming edge with the offset of the outgoing edge.
    corner_direction = np.roll(normals, 1, axis=0) + normals
    scale = np.sum(corner_direction * normals, axis=1)
    result = p + allowance_m * corner_direction / scale[:, None]

    if not np.isfinite(result).all():
        raise ValueError("Allowance produced invalid coordinates.")

    return result


def preview_outline(original_points: np.ndarray , cut_points : np.ndarray) -> None:
    """Show the original outline and its cut outlines at their real proportions."""
    origional_closed = np.vstack((original_points, original_points[0]))
    cut_closed = np.vstack((cut_points , cut_points[0]))

    fig, ax = plt.subplots()

    ax.plot(
        cut_closed[:,0],
        cut_closed[:,1],
        color="blue",
        linestyle='-',
        label = "Cut outline",
    )
    ax.plot(
        origional_closed[:,0],
        origional_closed[:,1],
        color="black",
        linestyle=":",
        label = "Origional outline"
    )

    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.grid(True)
    ax.legend()

    plt.show()
    plt.close(fig)

def export_dxf(points: np.ndarray, path: str, allowance_m: float = 0.0, preview: bool = False,) -> None:
    """Add an optional allowance, save the DXF, and optionally preview it."""
    cut_points = np.asarray(points, dtype=float)
    if allowance_m != 0:
        cut_points = add_hem_allowance(cut_points, allowance_m)
    if preview:
        preview_outline(points,cut_points)
        decision = input("Enter 1 to Save 2 to cancel: ").strip()
        if(decision != '1'):
            return
    
    save_outline_dxf(cut_points, path)

#test case
if __name__ == "__main__":
    geometry = SemiElipsoid()

    test_points = geometry.getDXFpoints(
        n=8,                  # Number of gores
        chute_diameter=2.0,   # Metres
        chute_height=1.0,     # Metres
        vent_diameter=0.1,    # Metres
    )

    export_dxf(
        test_points,
        "gore_test.dxf",
        allowance_m=0.1,  
        preview=True,
    )    
"""
#small test case
if __name__ == "__main__":
    # A 100 mm wide, 200 mm tall rectangle, with points in metres.
    test_points = np.array([
        (0.00, 0.00),
        (0.10, 0.00),
        (0.10, 0.20),
        (0.00, 0.20),
    ])

    # Adding 8 mm on every side makes the cut outline 116 mm by 216 mm.
    export_dxf(
        test_points,
        "outline_test.dxf",
        allowance_m=0.008,
        preview=True,
    )
    print("Saved outline_test.dxf (expected size: 116 mm by 216 mm)")
"""
