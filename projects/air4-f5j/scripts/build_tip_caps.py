"""Build ROUNDED tip caps for stab and elevator."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from build123d import *
from src.cad.airfoils import blend_airfoils, scale_airfoil

HALF_SPAN=215.0; ROOT_CHORD=115.0; N_EXP=2.3; REF_FRAC=0.45
REF_X=ROOT_CHORD*REF_FRAC; X_HINGE=60.0; N_PTS=60
Y_CAP_START=210.0; Y_CAP_END=214.0

def _se(y):
    if abs(y)>=HALF_SPAN or y<0: return 0.0
    return ROOT_CHORD*(1-(y/HALF_SPAN)**N_EXP)**(1/N_EXP)
_c0=_se(Y_CAP_START); _sl=(_se(Y_CAP_START)-_se(Y_CAP_START-0.001))/0.001
_ca,_cb=_c0,_sl; _cd=(_ca+2*_cb)/32; _cc=(-_cb-48*_cd)/8

def chord_at(y):
    y=abs(y)
    if y<=Y_CAP_START: return _se(y)
    if y>=Y_CAP_END: return 0.0
    t=y-Y_CAP_START; return max(0,_ca+_cb*t+_cc*t**2+_cd*t**3)

def le_x(y): return REF_X-REF_FRAC*chord_at(abs(y))

def get_section(y, x_min=None, x_max=None):
    c=chord_at(abs(y)); lx=le_x(abs(y))
    blend=min(abs(y)/HALF_SPAN,1.0)
    af=blend_airfoils("ht13","ht12",blend,N_PTS); sc=scale_airfoil(af,c)
    le_idx=int(np.argmin(sc[:,0]))
    upper=sc[:le_idx+1][::-1]; lower=sc[le_idx:]
    upper_abs=[(lx+float(p[0]),float(p[1])) for p in upper]
    lower_abs=[(lx+float(p[0]),float(p[1])) for p in lower]

    if x_max is not None:
        upper_abs=[p for p in upper_abs if p[0]<=x_max+0.1]
        lower_abs=[p for p in lower_abs if p[0]<=x_max+0.1]
        if upper_abs and upper_abs[-1][0]<x_max:
            upper_abs.append((x_max,upper_abs[-1][1]))
        if lower_abs and lower_abs[-1][0]<x_max:
            lower_abs.append((x_max,lower_abs[-1][1]))
    if x_min is not None:
        upper_abs=[p for p in upper_abs if p[0]>=x_min-0.1]
        lower_abs=[p for p in lower_abs if p[0]>=x_min-0.1]

    return upper_abs, lower_abs

def build_rounded_tip(y_start, y_end, n_stations, n_ring, x_min=None, x_max=None, label="tip"):
    """Build a rounded tip cap that blends from airfoil to ellipse."""
    ys = np.linspace(y_start, y_end, n_stations)

    # Get reference section at start
    uc_ref, lc_ref = get_section(y_start, x_min, x_max)
    if len(uc_ref)<3 or len(lc_ref)<3:
        print(f"  {label}: reference section too small")
        return None

    all_ref = uc_ref + list(reversed(lc_ref))
    cx = np.mean([p[0] for p in all_ref])
    cz = np.mean([p[1] for p in all_ref])
    rx = (max(p[0] for p in all_ref) - min(p[0] for p in all_ref)) / 2
    rz = (max(p[1] for p in all_ref) - min(p[1] for p in all_ref)) / 2

    sections = []
    for y in ys:
        t = (y - y_start) / (y_end - y_start)
        scale = math.cos(t * math.pi / 2)  # 1.0 -> 0.0 cosine
        if scale < 0.08:
            continue

        blend_t = min(1.0, t * 1.5)  # rounding increases with span

        pts = []
        for i in range(n_ring):
            theta = 2 * math.pi * i / n_ring

            # Ellipse
            ex = cx + rx * math.cos(theta) * scale
            ez = cz + rz * math.sin(theta) * scale

            # Airfoil (map theta to reference section)
            if theta <= math.pi:
                frac = theta / math.pi
                idx = min(int(frac * (len(uc_ref)-1)), len(uc_ref)-1)
                ax, az = uc_ref[idx]
            else:
                frac = (theta - math.pi) / math.pi
                idx = min(int(frac * (len(lc_ref)-1)), len(lc_ref)-1)
                ax, az = lc_ref[idx]

            ax_s = cx + (ax - cx) * scale
            az_s = cz + (az - cz) * scale

            px = ax_s * (1 - blend_t) + ex * blend_t
            pz = az_s * (1 - blend_t) + ez * blend_t
            pts.append((px, pz))

        pts.append(pts[0])
        sections.append((y, pts))

    if len(sections) < 2:
        return None

    print(f"  {label}: {len(sections)} sections, y=[{sections[0][0]:.1f},{sections[-1][0]:.1f}]")

    with BuildPart() as bp:
        for y, pts in sections:
            plane = Plane(origin=(0, y, 0), x_dir=(1, 0, 0), z_dir=(0, 1, 0))
            with BuildSketch(plane):
                with BuildLine():
                    Polyline(*pts)
                make_face()
        loft()
    return bp.part


def main():
    print("=" * 60)
    print("ROUNDED Tip Caps")
    print("=" * 60)

    # Stab tip: LE to hinge (X < 60), y=208 to 214
    print("\nStab tip cap:")
    stab_tip = build_rounded_tip(208.0, 214.0, 8, 60, x_max=X_HINGE, label="Stab")
    if stab_tip:
        bb = stab_tip.bounding_box()
        print(f"  Vol: {stab_tip.volume:.1f} mm3  Y=[{bb.min.Y:.1f},{bb.max.Y:.1f}]")

    # Elevator tip: hinge to TE (X > 60), y=208 to 212
    print("\nElevator tip cap:")
    elev_tip = build_rounded_tip(208.0, 212.0, 6, 60, x_min=X_HINGE, label="Elev")
    if elev_tip:
        bb = elev_tip.bounding_box()
        print(f"  Vol: {elev_tip.volume:.1f} mm3  Y=[{bb.min.Y:.1f},{bb.max.Y:.1f}]")

    # Export
    for part, folder, fname in [
        (stab_tip, "cad/components/empennage/HStab_Tip_Cap", "HStab_Tip_Cap"),
        (elev_tip, "cad/components/empennage/Elevator_Tip_Cap", "Elevator_Tip_Cap"),
    ]:
        if part is None:
            continue
        os.makedirs(folder, exist_ok=True)
        export_step(part, f"{folder}/{fname}.step")
        export_stl(part, f"{folder}/{fname}.stl", tolerance=0.005, angular_tolerance=0.1)
        print(f"  {fname}: {os.path.getsize(f'{folder}/{fname}.step')/1024:.0f}KB")

    # Show
    from ocp_vscode import show
    hl = import_step("cad/components/empennage/HStab_Left/HStab_Left_MainBody.step")
    hr = import_step("cad/components/empennage/HStab_Right/HStab_Right.step")
    el = import_step("cad/components/empennage/Elevator_Left/Elevator_Left.step")
    er = import_step("cad/components/empennage/Elevator_Right/Elevator_Right.step")
    spar = import_step("cad/components/empennage/HStab_Main_Spar/HStab_Main_Spar.step")
    wire = import_step("cad/components/empennage/Hinge_Wire/Hinge_Wire.step")

    parts = [hl, hr, el, er, spar, wire]
    names = ["Stab_L", "Stab_R", "Elev_L", "Elev_R", "Spar", "Wire"]
    colors = ["mediumorchid", "mediumorchid", "hotpink", "hotpink", "dimgray", "silver"]
    alphas = [0.4, 0.4, 0.4, 0.4, 1.0, 1.0]

    if stab_tip:
        stab_tip_r = stab_tip.mirror(Plane.XZ)
        parts.extend([stab_tip, stab_tip_r])
        names.extend(["StabTip_L", "StabTip_R"])
        colors.extend(["mediumorchid", "mediumorchid"])
        alphas.extend([0.7, 0.7])

    if elev_tip:
        elev_tip_r = elev_tip.mirror(Plane.XZ)
        parts.extend([elev_tip, elev_tip_r])
        names.extend(["ElevTip_L", "ElevTip_R"])
        colors.extend(["hotpink", "hotpink"])
        alphas.extend([0.7, 0.7])

    show(*parts, names=names, colors=colors, alphas=alphas)
    print("ROUNDED tip caps displayed in OCP Viewer")


if __name__ == "__main__":
    main()
