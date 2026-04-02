"""Export projected views to DXF with standard engineering drawing layers.

Takes projected views + layout and writes a single DXF file with
all views positioned on the sheet using the computed scale and offsets.
"""

from build123d import Compound, Location, ExportDXF, LineType, Unit
from build123d.exporters import ColorIndex


def export_drawing(
    views: dict[str, dict[str, list]],
    layout: dict,
    output_path: str,
) -> str:
    """Export projected views to a DXF file.

    Args:
        views: {view_name: {"visible": [Edge], "hidden": [Edge]}}
        layout: from calculate_layout() — scale + per-view offsets
        output_path: path to write the DXF file

    Returns:
        The output path.
    """
    scale = layout["scale"]

    exporter = ExportDXF(unit=Unit.MM)
    exporter.add_layer("VISIBLE", line_weight=0.5)
    exporter.add_layer(
        "HIDDEN",
        color=ColorIndex.GRAY,
        line_type=LineType.ISO_DASH,
        line_weight=0.25,
    )

    for view_name in ["top", "front", "right"]:
        if view_name not in views or view_name not in layout:
            continue

        ox, oy = layout[view_name]
        vis = views[view_name]["visible"]
        hid = views[view_name]["hidden"]

        vis_moved = _scale_and_translate(vis, scale, ox, oy)
        hid_moved = _scale_and_translate(hid, scale, ox, oy)

        if vis_moved:
            exporter.add_shape(vis_moved, layer="VISIBLE")
        if hid_moved:
            exporter.add_shape(hid_moved, layer="HIDDEN")

    exporter.write(output_path)
    return output_path


def _scale_and_translate(
    edges: list, scale: float, ox: float, oy: float
) -> list:
    """Scale edges by factor, then translate so bounding box min lands at (ox, oy).

    Args:
        edges: List of Build123d Edge objects (projected, in XY plane).
        scale: Uniform scale factor.
        ox: Target X coordinate for the left edge of the bounding box.
        oy: Target Y coordinate for the bottom edge of the bounding box.

    Returns:
        List of translated Edge objects, or empty list if input is empty.
    """
    if not edges:
        return []

    c = Compound(edges)

    # Scale about the world origin
    scaled = c.scale(scale)

    # Compute post-scale bounding box and translate so its min = (ox, oy)
    bb = scaled.bounding_box()
    dx = ox - bb.min.X
    dy = oy - bb.min.Y
    moved = scaled.moved(Location((dx, dy, 0)))

    return list(moved.edges())
