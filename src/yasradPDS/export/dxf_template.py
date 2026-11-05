"""Build and preview a laser-cut DXF

Points and allowances are in metres; DXF coordinates are in millimetres
"""

import ezdxf
import numpy as np
import matplotlib.pyplot as plt

##

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
    doc = ezdxf.new("R2010")
    doc.units = 4  # millimetres

    doc.modelspace().add_lwpolyline(
        (points * 1000).tolist(),
        close=True,
    )
    doc.saveas(path)


def add_hem_allowance(points: np.ndarray, allowance_m: float) -> np.ndarray:
    """Add the same allowance around the entire outline, in metres."""
    p = np.asarray(points, dtype=float)
    if np.array_equal(p[0], p[-1]):
        p = p[:-1]  # DXF close=True will close the outline

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
    return p + allowance_m * corner_direction / scale[:, None]


def preview_outline(points: np.ndarray) -> None:
    """Show the supplied outline at its real proportions."""
    closed = np.vstack((points, points[0]))
    fig, ax = plt.subplots()
    ax.plot(closed[:, 0], closed[:, 1])
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.grid(True)
    plt.show()
    plt.close(fig)


def export_dxf(points: np.ndarray, path: str, allowance_m: float = 0.0, preview: bool = False,) -> None:
    """Add an optional allowance, save the DXF, and optionally preview it."""
    cut_points = np.asarray(points, dtype=float)
    if allowance_m != 0:
        cut_points = add_hem_allowance(cut_points, allowance_m)
    if preview:
        preview_outline(cut_points)
        decision = input(print("Enter 1 to Save 2 to cancel"))
        if(decision == '1'):
            save_outline_dxf(cut_points, path)
        else: return

    save_outline_dxf(cut_points, path)

#test case
if __name__ == "__main__":
    from yasradPDS.geometries.semi_elipsoid import SemiElipsoid

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
        allowance_m=0.008,    # 8 mm
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