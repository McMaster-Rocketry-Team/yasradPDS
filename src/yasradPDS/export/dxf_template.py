# Builds the DXF gore pattern for cutting, using geometry output from the
# system's canopy geometry object.
#
# Proof of concept: create a small layered DXF template and preview it with
# matplotlib via ezdxf's
import math

import ezdxf
import matplotlib.pyplot as plt
from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend

'''Temporary Code To create a predetermined gore'''

GORE_LENGTH = 120.0     
GORE_HALF_WIDTH = 50.0   
CENTER_X = 50.0          
SEAM_ALLOWANCE = 8.0     
HEM_ALLOWANCE = 8.0      
TIP_EXPONENT = 0.7

LAYERS = {
    "CUT": 1,   # Red
    "SEW": 3,   # Green
    "FOLD": 5,  # Blue
}



def parabola_half(length, half_width, offset=0.0, hem=0.0, samples=60,power=TIP_EXPONENT):
    L, W = length, half_width
    k = 1.0 / power
    pts = []

    for i in range(samples + 1):
        t = i / samples
        dx = W * t
        y = L - L * t**k

        if offset:
            nx, ny = L * k * t ** (k - 0.001), W
            n = math.hypot(nx, ny)
            dx += offset * nx / n
            y += offset * ny / n

        pts.append((dx, y))

    if hem:
        dx, y = pts[-1]
        s = (y + hem) / (L * k)
        pts.append((dx + s * W, -hem))

    return pts

def create_gore_geometry():
    """
    Gore outline shaped like sqrt(x)

    Returns:
        sew_outline: Closed finished gore outline.
        cut_outline: Closed cutting outline (true offset + hem).
    """

    def assemble(half):
        right = [(CENTER_X + dx, y) for dx, y in half]
        left = [(CENTER_X - dx, y) for dx, y in reversed(half)]
        return left + right[1:]

    sew_half = parabola_half(GORE_LENGTH, GORE_HALF_WIDTH)
    cut_half = parabola_half(
        GORE_LENGTH,
        GORE_HALF_WIDTH,
        offset=SEAM_ALLOWANCE,
        hem=HEM_ALLOWANCE,
    )

    return assemble(sew_half), assemble(cut_half)


def build_template_example(path="drogue_example.dxf"):
    """Generate the gore DXF."""

    doc = ezdxf.new("R2010")
    doc.units = 4  # Millimetres

    msp = doc.modelspace()

    # Create drawing layers.
    for name, color in LAYERS.items():
        if name not in doc.layers:
            doc.layers.new(name=name, dxfattribs={"color": color})

    # Generate the geometry.
    sew_outline, cut_outline = create_gore_geometry()

    msp.add_lwpolyline(
        cut_outline,
        close=True,
        dxfattribs={"layer": "CUT"},
    )

    # Finished sewing outline.
    msp.add_lwpolyline(
        sew_outline,
        close=True,
        dxfattribs={"layer": "SEW"},
    )

    # Centre fold / alignment line.
    msp.add_line(
        (CENTER_X, 0),
        (CENTER_X, GORE_LENGTH),
        dxfattribs={"layer": "FOLD"},
    )

    doc.saveas(path)

    return path


def preview_dxf(path, show=True, save_path=None):
    """Display a DXF drawing using Matplotlib."""

    doc = ezdxf.readfile(path)
    msp = doc.modelspace()

    fig, ax = plt.subplots()

    context = RenderContext(doc)
    backend = MatplotlibBackend(ax)

    Frontend(context, backend).draw_layout(msp, finalize=True)

    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    ax.set_title("Example Gore Template")
    ax.grid(True)

    if save_path is not None:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")

    if show:
        plt.show()

    plt.close(fig)

    return fig


output = build_template_example("drogue_example.dxf")
print(f"Wrote {output}")
preview_dxf(output, show=True)