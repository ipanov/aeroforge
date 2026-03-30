"""Project a 3D shape into standard orthographic views using HLR.

Produces top, front, and right views with visible and hidden edge separation.
All projected edges live in the XY plane (Z=0) and are returned as Edge lists.
"""

from build123d import Shape, Edge
from build123d.exporters import Drawing


# Camera directions for each standard view:
#   look_from  = direction the camera looks FROM (opposite of view direction)
#   look_up    = which world axis points "up" in the resulting 2D image
_VIEW_PARAMS: dict[str, dict] = {
    "top":   {"look_from": (0, 0, 1),  "look_up": (0, 1, 0)},
    "front": {"look_from": (0, -1, 0), "look_up": (0, 0, 1)},
    "right": {"look_from": (1, 0, 0),  "look_up": (0, 0, 1)},
}


def project_standard_views(
    shape: Shape,
) -> dict[str, dict[str, list[Edge]]]:
    """Project shape into top, front, and right orthographic views.

    Args:
        shape: Any Build123d Shape (Part, Compound, etc.)

    Returns:
        {
            "top":   {"visible": [Edge, ...], "hidden": [Edge, ...]},
            "front": {"visible": [Edge, ...], "hidden": [Edge, ...]},
            "right": {"visible": [Edge, ...], "hidden": [Edge, ...]},
        }
    """
    result: dict[str, dict[str, list[Edge]]] = {}

    for view_name, params in _VIEW_PARAMS.items():
        drawing = Drawing(
            shape,
            look_from=params["look_from"],
            look_up=params["look_up"],
            with_hidden=True,
        )
        visible_edges = list(drawing.visible_lines.edges())
        hidden_edges = list(drawing.hidden_lines.edges())
        result[view_name] = {"visible": visible_edges, "hidden": hidden_edges}

    return result


def compute_2d_bounds(
    edges: list[Edge],
) -> tuple[float, float, float, float]:
    """Compute the 2D bounding box of a list of projected edges.

    Args:
        edges: List of Build123d Edge objects (projected, living in XY plane).

    Returns:
        (xmin, ymin, xmax, ymax) in mm.

    Raises:
        ValueError: If edges list is empty.
    """
    if not edges:
        raise ValueError("Cannot compute bounds of empty edge list.")

    xmin = float("inf")
    ymin = float("inf")
    xmax = float("-inf")
    ymax = float("-inf")

    for edge in edges:
        bb = edge.bounding_box()
        xmin = min(xmin, bb.min.X)
        ymin = min(ymin, bb.min.Y)
        xmax = max(xmax, bb.max.X)
        ymax = max(ymax, bb.max.Y)

    return xmin, ymin, xmax, ymax
