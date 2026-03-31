"""
HStab Drawing Validation Suite
================================
Validates ALL H-Stab drawings against the v5 Design Consensus.

Three validation phases:
  1. PRE-GENERATION: Spec consistency (catches impossible geometry)
  2. POST-GENERATION: DXF content checks (catches drawing script bugs)
  3. CROSS-COMPONENT: Assembly includes all component features

Run standalone:  cd D:/Repos/aeroforge && PYTHONPATH=. python scripts/validate_hstab_drawings.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from hstab_geometry import *
from src.cad.drawing.spec_validator import SpecValidator
from src.cad.drawing.dxf_validator import DxfValidator


def validate_spec_consistency():
    """Phase 1: Check that the design consensus is internally consistent."""
    v = SpecValidator()

    # --- Basic dimension sanity ---
    v.check_dimension_positive("HStab", "root_chord", ROOT_CHORD)
    v.check_dimension_positive("HStab", "half_span", HALF_SPAN)
    v.check_range("HStab", "superellipse_exponent", N_EXP, 1.5, 4.0)
    v.check_range("HStab", "te_truncation", TE_TRUNC, 0.90, 1.0)

    # --- Rod fit checks ---
    def half_thickness(frac, y):
        tr = t_ratio(y)
        c = chord_at(y)
        return naca4_yt(frac, tr) * c

    # Main spar: 3mm tube needs 3.1mm bore
    v.check_rod_fits_airfoil(
        "HStab_Left", "Main spar (3mm CF tube)",
        rod_x=X_MAIN_SPAR, rod_diameter=D_MAIN,
        y_range=(0, Y_MAIN_END),
        le_x_fn=le_x, chord_fn=chord_at,
        thickness_fn=half_thickness, te_trunc=TE_TRUNC,
    )

    # Rear spar: 1.5mm rod needs 1.6mm bore
    v.check_rod_fits_airfoil(
        "HStab_Left", "Rear spar (1.5mm CF rod)",
        rod_x=X_REAR_SPAR, rod_diameter=D_REAR,
        y_range=(0, Y_REAR_END),
        le_x_fn=le_x, chord_fn=chord_at,
        thickness_fn=half_thickness, te_trunc=TE_TRUNC,
    )

    # Hinge wire: 0.5mm wire needs 0.6mm bore (1.2mm with PETG sleeve)
    v.check_rod_fits_airfoil(
        "HStab_Left", "Hinge wire (0.5mm + 1.2mm sleeve)",
        rod_x=X_HINGE, rod_diameter=1.2,  # sleeve OD, not wire OD
        y_range=(0, Y_HINGE_END),
        le_x_fn=le_x, chord_fn=chord_at,
        thickness_fn=half_thickness, te_trunc=TE_TRUNC,
    )

    # Stiffener: 1mm rod
    v.check_rod_fits_airfoil(
        "Elevator_Left", "Stiffener (1mm CF rod)",
        rod_x=X_STIFF, rod_diameter=1.0,
        y_range=(0, Y_STIFF_END),
        le_x_fn=le_x, chord_fn=chord_at,
        thickness_fn=half_thickness, te_trunc=TE_TRUNC,
    )

    # --- Tungsten pocket vs horn envelope ---
    pocket_fwd = POCKET_FWD_OF_HINGE + POCKET_CHORD / 2   # 11.25mm fwd of hinge
    pocket_aft = POCKET_FWD_OF_HINGE - POCKET_CHORD / 2   # 4.75mm fwd of hinge
    pocket_y_min = POCKET_Y_CENTER - POCKET_SPAN / 2       # y=195
    pocket_y_max = POCKET_Y_CENTER + POCKET_SPAN / 2       # y=205

    v.check_containment_along_span(
        component="Elevator_Left",
        feature_name=f"Tungsten pocket ({POCKET_SPAN}×{POCKET_CHORD}mm, {POCKET_FWD_OF_HINGE}mm fwd hinge)",
        span_range=(pocket_y_min, pocket_y_max),
        feature_bounds_fn=lambda y: (pocket_fwd, 0),  # forward extent, no aft extent
        envelope_bounds_fn=lambda y: (horn_fwd_offset(y), 999),  # horn forward limit
        step=1.0,
    )

    # --- Hinge wire sleeve clearance at tip ---
    # Check that airfoil is thick enough for 1.2mm sleeve at hinge X
    from src.cad.drawing.spec_validator import ValidationIssue
    sleeve_od = 1.2  # mm
    for y in range(195, int(Y_HINGE_END) + 1):
        c = chord_at(y)
        if c < 1:
            continue
        lx = le_x(y)
        frac = (X_HINGE - lx) / c
        if not (0 < frac < TE_TRUNC):
            continue
        tr = t_ratio(y)
        thickness = 2 * naca4_yt(frac, tr) * c
        if thickness < sleeve_od:
            v.issues.append(ValidationIssue(
                severity="WARNING",
                component="Elevator_Left",
                check_name="hinge_sleeve_clearance",
                message=f"Hinge sleeve (Ø{sleeve_od}mm) won't fit at y={y}: airfoil thickness={thickness:.2f}mm",
            ))

    return v


def validate_dxf_elevator_left():
    """Phase 2: Check Elevator_Left DXF against spec."""
    path = "cad/components/empennage/Elevator_Left/Elevator_Left_drawing.dxf"
    if not os.path.exists(path):
        print(f"  SKIP: {path} not found")
        return None

    v = DxfValidator(path)

    # Required layers
    for layer in ["OUTLINE", "CENTERLINE", "SPAR", "SECTION", "TEXT", "DIMENSION"]:
        v.check_layer_has_entities(layer)

    # Required text labels
    v.check_text_present("HINGE LINE")
    v.check_text_present("HORN")
    v.check_text_present("TUNGSTEN")
    v.check_text_present("STIFFENER")
    v.check_text_present("PUSHROD")
    v.check_text_present("TIP CAP")

    # Dimensions
    v.check_dimension_value(214.0, tolerance=1.0, label="span_214mm")

    return v


def validate_dxf_hstab_left():
    """Phase 2: Check HStab_Left DXF against spec."""
    path = "cad/components/empennage/HStab_Left/HStab_Left_drawing.dxf"
    if not os.path.exists(path):
        print(f"  SKIP: {path} not found")
        return None

    v = DxfValidator(path)

    for layer in ["OUTLINE", "CENTERLINE", "SPAR", "TEXT", "DIMENSION"]:
        v.check_layer_has_entities(layer)

    v.check_text_present("MAIN SPAR")
    v.check_text_present("REAR SPAR")
    v.check_text_present("HINGE")
    v.check_text_present("LEADING EDGE")
    v.check_text_present("TRAILING EDGE")
    v.check_text_present("ROOT")
    v.check_text_present("TIP")

    return v


def validate_dxf_assembly():
    """Phase 2: Check HStab_Assembly DXF against spec."""
    path = "cad/assemblies/empennage/HStab_Assembly/HStab_Assembly_drawing.dxf"
    if not os.path.exists(path):
        print(f"  SKIP: {path} not found")
        return None

    v = DxfValidator(path)

    for layer in ["OUTLINE", "CENTERLINE", "SPAR", "TEXT", "DIMENSION"]:
        v.check_layer_has_entities(layer)

    v.check_text_present("LEFT TIP")
    v.check_text_present("RIGHT TIP")
    v.check_text_present("MAIN SPAR")
    v.check_text_present("HINGE WIRE")
    v.check_text_present("LE")
    v.check_text_present("TE")
    v.check_text_present("FWD")
    v.check_text_present("VStab")

    # CRITICAL: Assembly must show horn geometry
    v.check_text_present("HORN", partial=True)

    return v


def validate_cross_component():
    """Phase 3: Cross-component consistency checks."""
    issues = []

    # Check: assembly must show horn forward extension
    assy_path = "cad/assemblies/empennage/HStab_Assembly/HStab_Assembly_drawing.dxf"
    if os.path.exists(assy_path):
        import ezdxf
        doc = ezdxf.readfile(assy_path)
        msp = doc.modelspace()

        # The horn extends forward of the standard planform LE at the tip.
        # Check if any OUTLINE entity has coordinates forward (higher Y in drawing)
        # of where the standard LE would be at tip stations.
        # This is a simplified check — a full check would trace the outline.
        texts = [e.dxf.text for e in msp if e.dxftype() == "TEXT"]
        horn_mentioned = any("horn" in t.lower() for t in texts)
        if not horn_mentioned:
            issues.append("Assembly drawing does not mention HORN — tip horn geometry likely missing from planform")

    # Check: elevator sections must show horn at horn stations
    elev_path = "cad/components/empennage/Elevator_Left/Elevator_Left_drawing.dxf"
    if os.path.exists(elev_path):
        import ezdxf
        doc = ezdxf.readfile(elev_path)
        msp = doc.modelspace()
        texts = [e.dxf.text for e in msp if e.dxftype() == "TEXT"]
        horn_section = any("horn" in t.lower() and ("sec" in t.lower() or "section" in t.lower()) for t in texts)
        # At y=200 (horn zone), the section label exists but doesn't indicate horn geometry
        # This is a simplified check
        if not horn_section:
            issues.append("Elevator SEC C (horn zone) doesn't indicate horn forward extension in cross-section")

    return issues


def main():
    print("=" * 70)
    print("H-STAB DRAWING VALIDATION SUITE")
    print("=" * 70)
    print()

    # Phase 1
    print("PHASE 1: Spec Consistency (pre-generation)")
    print("-" * 50)
    spec_v = validate_spec_consistency()
    print(spec_v.report())
    print()

    # Phase 2
    print("PHASE 2: DXF Content Checks (post-generation)")
    print("-" * 50)

    for name, validator_fn in [
        ("Elevator_Left", validate_dxf_elevator_left),
        ("HStab_Left", validate_dxf_hstab_left),
        ("HStab_Assembly", validate_dxf_assembly),
    ]:
        print(f"\n  {name}:")
        v = validator_fn()
        if v:
            print(v.report())

    # Phase 3
    print("\nPHASE 3: Cross-Component Consistency")
    print("-" * 50)
    cross_issues = validate_cross_component()
    if cross_issues:
        for issue in cross_issues:
            print(f"  ✗ {issue}")
    else:
        print("  ✓ All cross-component checks passed.")

    print()
    print("=" * 70)
    if spec_v.has_critical:
        print("⛔ CRITICAL SPEC ISSUES — consensus needs revision before drawing.")
        return 1
    print("Validation complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
