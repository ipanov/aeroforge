"""
Drawing Orientation Module — SINGLE SOURCE OF TRUTH for coordinate transforms.
================================================================================

EVERY drawing script MUST use this module for coordinate mapping.
No more per-script D() functions. No more sign errors.

Standard engineering drawing conventions:
  - TOP VIEW (planform): FWD=up, LEFT=left, RIGHT=right
  - FRONT VIEW: looking from front, LEFT=left, RIGHT=right, UP=up
  - RIGHT VIEW: looking from right side, FWD=left, UP=up

Coordinate systems:
  - CONSENSUS: X=chordwise (positive aft), Y=spanwise (positive left), Z=vertical (positive up)
  - DXF: X=horizontal (positive right), Y=vertical (positive up)

This module provides tested transforms between consensus and DXF coordinates.
"""

from dataclasses import dataclass


@dataclass
class TopViewMapper:
    """Maps consensus coordinates to DXF for a standard top view.

    In a top view looking DOWN at the aircraft:
      - FWD (consensus -X) maps to DXF +Y (up on paper)
      - LEFT (consensus +Y) maps to DXF -X (left on paper)
      - RIGHT (consensus -Y) maps to DXF +X (right on paper)

    For a LEFT half component (tip extends LEFT):
      - Root is at center, tip extends LEFT (DXF -X direction)

    For a RIGHT half component (tip extends RIGHT):
      - Root is at center, tip extends RIGHT (DXF +X direction)

    For a full assembly:
      - Left half extends LEFT, right half extends RIGHT
    """

    center_x: float  # DXF X position of the root/center
    center_y: float  # DXF Y position of the LE reference line

    def map(self, cons_x: float, cons_y: float) -> tuple[float, float]:
        """Convert consensus (chordwise, spanwise) to DXF (x, y).

        cons_x: chordwise position (0=root LE, positive=aft)
        cons_y: spanwise position (positive=left, negative=right)

        Returns: (dxf_x, dxf_y) where:
          - dxf_x = center_x - cons_y  (left half goes LEFT on paper)
          - dxf_y = center_y - cons_x  (aft goes DOWN, fwd goes UP)
        """
        return (self.center_x - cons_y, self.center_y - cons_x)

    def map_half(self, cons_x: float, cons_y: float, side: str) -> tuple[float, float]:
        """Map a half-span component. side='left' or 'right'.

        For 'left': tip extends LEFT (cons_y positive → DXF -X)
        For 'right': tip extends RIGHT (cons_y positive → DXF +X, mirrored)
        """
        if side == "left":
            return (self.center_x - cons_y, self.center_y - cons_x)
        elif side == "right":
            return (self.center_x + cons_y, self.center_y - cons_x)
        else:
            raise ValueError(f"side must be 'left' or 'right', got '{side}'")


def validate_orientation(
    mapper: TopViewMapper,
    half_span: float,
    root_chord: float,
    side: str = "left",
) -> list[str]:
    """Validate that a mapper produces correct orientation.

    Returns list of errors (empty = all OK).
    """
    errors = []

    # Root LE should be at (center_x, center_y)
    root_le = mapper.map_half(0, 0, side)
    if abs(root_le[0] - mapper.center_x) > 0.01:
        errors.append(f"Root LE X wrong: expected {mapper.center_x}, got {root_le[0]}")
    if abs(root_le[1] - mapper.center_y) > 0.01:
        errors.append(f"Root LE Y wrong: expected {mapper.center_y}, got {root_le[1]}")

    # Tip should be LEFT of root for left half, RIGHT for right half
    tip = mapper.map_half(0, half_span, side)
    if side == "left":
        if tip[0] >= root_le[0]:
            errors.append(f"LEFT tip is RIGHT of root! tip_x={tip[0]}, root_x={root_le[0]}")
    else:
        if tip[0] <= root_le[0]:
            errors.append(f"RIGHT tip is LEFT of root! tip_x={tip[0]}, root_x={root_le[0]}")

    # TE should be BELOW LE (lower DXF Y = more aft)
    root_te = mapper.map_half(root_chord, 0, side)
    if root_te[1] >= root_le[1]:
        errors.append(f"TE is ABOVE LE! te_y={root_te[1]}, le_y={root_le[1]}")

    return errors


# Pre-built mappers for standard sheet sizes
def make_component_mapper(sheet_size: str = "A2", side: str = "left") -> TopViewMapper:
    """Create a mapper for a half-span component drawing.

    Places the root near the center of the sheet, with the half extending
    toward the correct side.
    """
    sheets = {"A4": (297, 210), "A3": (420, 297), "A2": (594, 420), "A1": (841, 594)}
    sw, sh = sheets[sheet_size]

    if side == "left":
        # Root on the right side of the drawing area, tip extends left
        cx = sw * 0.55  # slightly right of center
    else:
        # Root on the left side, tip extends right
        cx = sw * 0.45

    cy = sh * 0.75  # LE near top, leaving room for title block at bottom

    return TopViewMapper(center_x=cx, center_y=cy)


def make_assembly_mapper(sheet_size: str = "A1") -> TopViewMapper:
    """Create a mapper for a full-span assembly drawing.

    Places the fin centerline at the center of the sheet.
    """
    sheets = {"A4": (297, 210), "A3": (420, 297), "A2": (594, 420), "A1": (841, 594)}
    sw, sh = sheets[sheet_size]

    return TopViewMapper(center_x=sw * 0.50, center_y=sh * 0.72)
