"""Build and preview a laser-cut DXF from an ordered gore point array.

Points, allowances, preview axes, and DXF coordinates are in millimetres.
"""

import ezdxf
import numpy as np
import matplotlib.pyplot as plt


def save_outline_dxf(points: np.ndarray, path: str) -> None:
    """Save ordered (x, y) points in millimetres as a DXF outline."""
    doc = ezdxf.new("R2010")
    doc.units = 4  # millimetres

    doc.modelspace().add_lwpolyline(
        points.tolist(),
        close=True,
    )
    doc.saveas(path)


def add_hem_allowance(points: np.ndarray, allowance_mm: float) -> np.ndarray:
    """Add the same allowance around the entire outline, in millimetres."""
    p = np.asarray(points, dtype=float)
    if np.array_equal(p[0], p[-1]):
        p = p[:-1]  # DXF close=True will close the outline

    edges = np.roll(p, -1, axis=0) - p
    edge_lengths = np.linalg.norm(edges, axis=1)

    # Find whether the points run clockwise or counterclockwise.
    area = np.sum(
        p[:, 0] * np.roll(p[:, 1], -1)
        - p[:, 1] * np.roll(p[:, 0], -1)
    )
    direction = 1 if area > 0 else -1
    normals = direction * np.column_stack((edges[:, 1], -edges[:, 0]))
    normals /= edge_lengths[:, None]

    # Meet the offset of the incoming edge with the offset of the outgoing edge.
    corner_direction = np.roll(normals, 1, axis=0) + normals
    scale = np.sum(corner_direction * normals, axis=1)
    return p + allowance_mm * corner_direction / scale[:, None]


def preview_outline(points: np.ndarray, cut_points: np.ndarray) -> None:
    """Show the original outline and the offset cutting outline together."""
    original = np.vstack((points, points[0]))
    offset = np.vstack((cut_points, cut_points[0]))
    fig, ax = plt.subplots()
    ax.plot(original[:, 0], original[:, 1], color="blue", label="Original outline")
    ax.plot(offset[:, 0], offset[:, 1], "r--", label="Cut outline with allowance")
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.02))
    ax.grid(True)
    plt.show()
    plt.close(fig)


def build_template(
    points: np.ndarray,
    path: str,
    allowance_mm: float = 0.0,
    preview: bool = False,
) -> None:
    """Use millimetres to add an allowance, save the DXF, and preview both outlines."""
    points = np.asarray(points, dtype=float)
    cut_points = points
    if allowance_mm != 0:
        cut_points = add_hem_allowance(points, allowance_mm)

    save_outline_dxf(cut_points, path)
    if preview:
        preview_outline(points, cut_points)

#small test case
if __name__ == "__main__":
    # A 100 mm wide, 200 mm tall rectangle, with points in millimetres.
    test_points = np.array([
        (0.0, 0.0),
        (100.0, 0.0),
        (100.0, 200.0),
        (0.0, 200.0),
    ])

    # Adding 8 mm on every side makes the cut outline 116 mm by 216 mm.
    build_template(
        test_points,
        "outline_test.dxf",
        allowance_mm=8.0,
        preview=True,
    )
    print("Saved outline_test.dxf (expected size: 116 mm by 216 mm)")
