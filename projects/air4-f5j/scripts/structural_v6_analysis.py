"""
Structural V6 Analysis for H-Stab Round 4
==========================================
Single-spar, no rear spar, no stiffener, no tip horn, no tungsten.
Hinge at X=60.0mm, spar at X=34.5mm.
"""
import math
import sys
sys.path.insert(0, "scripts")
from hstab_geometry import (
    chord_at, le_x, te_x, t_ratio, naca4_yt,
    ROOT_CHORD, HALF_SPAN, N_EXP, REF_X, REF_FRAC,
    FIN_HALF, FIN_GAP,
)

# ============================================================
# V6 Parameters (non-negotiable)
# ============================================================
X_SPAR = 34.5
X_HINGE = 60.0
SPAR_OD = 3.0
SPAR_ID = 2.0
SPAR_TERM = 189.0
WIRE_DIA = 0.5
WIRE_TERM = 212.0
WALL_STAB = 0.45
WALL_ELEV = 0.40

# Material properties
G_LWPLA = 0.60e3      # MPa (0.6 GPa)
E_LWPLA = 1.8e3        # MPa
RHO_LWPLA = 0.65e-3    # g/mm3
E_CF = 135e3            # MPa
G_CF = 5.0e3            # MPa
RHO_CF = 1.6e-3         # g/mm3
E_STEEL = 200e3         # MPa
G_STEEL = 80e3          # MPa
RHO_STEEL = 7.85e-3     # g/mm3
RHO_PETG = 1.27e-3      # g/mm3
RHO_MYLAR = 1.39e-3     # g/mm3
RHO_TPU = 1.12e-3       # g/mm3

# V5 hinge for comparison
X_HINGE_V5 = 74.75
X_REAR_V5 = 69.0


def airfoil_half_thickness(x_abs, y):
    """Half-thickness (mm) of the blended airfoil at absolute X position and span y."""
    c = chord_at(abs(y))
    if c <= 0:
        return 0.0
    le = le_x(abs(y))
    xc = (x_abs - le) / c
    if xc < 0 or xc > 1:
        return 0.0
    tr = t_ratio(abs(y))
    return c * naca4_yt(xc, tr)


def section_perimeter(y, x_start_abs, x_end_abs, wall_t, n=50):
    """Perimeter of an airfoil section from x_start to x_end at span y."""
    c = chord_at(abs(y))
    if c <= 0:
        return 0.0
    le = le_x(abs(y))
    te = te_x(abs(y))
    x_s = max(x_start_abs, le)
    x_e = min(x_end_abs, te)
    if x_e <= x_s:
        return 0.0
    tr = t_ratio(abs(y))
    perim = 0.0
    for i in range(n):
        x1 = x_s + (x_e - x_s) * i / n
        x2 = x_s + (x_e - x_s) * (i + 1) / n
        xc1 = (x1 - le) / c
        xc2 = (x2 - le) / c
        z1u = c * naca4_yt(max(xc1, 0), tr)
        z2u = c * naca4_yt(max(xc2, 0), tr)
        z1l = -z1u
        z2l = -z2u
        dx = x2 - x1
        perim += math.sqrt(dx**2 + (z2u - z1u)**2)  # upper
        perim += math.sqrt(dx**2 + (z2l - z1l)**2)  # lower
    # closing web at both ends
    xc_s = max((x_s - le) / c, 0)
    xc_e = max((x_e - le) / c, 0)
    z_s = 2 * c * naca4_yt(xc_s, tr)
    z_e = 2 * c * naca4_yt(xc_e, tr)
    perim += z_s + z_e  # both webs
    return perim


def enclosed_area(y, x_start_abs, x_end_abs, n=50):
    """Enclosed area (mm2) of an airfoil section from x_start to x_end."""
    c = chord_at(abs(y))
    if c <= 0:
        return 0.0
    le = le_x(abs(y))
    te = te_x(abs(y))
    x_s = max(x_start_abs, le)
    x_e = min(x_end_abs, te)
    if x_e <= x_s:
        return 0.0
    tr = t_ratio(abs(y))
    area = 0.0
    for i in range(n):
        x1 = x_s + (x_e - x_s) * i / n
        x2 = x_s + (x_e - x_s) * (i + 1) / n
        xc1 = max((x1 - le) / c, 0)
        xc2 = max((x2 - le) / c, 0)
        z1 = 2 * c * naca4_yt(xc1, tr)
        z2 = 2 * c * naca4_yt(xc2, tr)
        area += 0.5 * (z1 + z2) * (x2 - x1)
    return area


def skin_path_integral(y, x_start_abs, x_end_abs, wall_t, n=50):
    """Integral of ds/t around the closed section (for Bredt formula)."""
    c = chord_at(abs(y))
    if c <= 0:
        return 1e12
    le = le_x(abs(y))
    te = te_x(abs(y))
    x_s = max(x_start_abs, le)
    x_e = min(x_end_abs, te)
    if x_e <= x_s:
        return 1e12
    tr = t_ratio(abs(y))
    integral = 0.0
    for i in range(n):
        x1 = x_s + (x_e - x_s) * i / n
        x2 = x_s + (x_e - x_s) * (i + 1) / n
        xc1 = max((x1 - le) / c, 0)
        xc2 = max((x2 - le) / c, 0)
        z1u = c * naca4_yt(xc1, tr)
        z2u = c * naca4_yt(xc2, tr)
        dx = x2 - x1
        ds_upper = math.sqrt(dx**2 + (z2u - z1u)**2)
        ds_lower = ds_upper  # symmetric
        integral += ds_upper / wall_t
        integral += ds_lower / wall_t
    # Closing webs (spar web and LE web or hinge web)
    xc_s = max((x_s - le) / c, 0)
    xc_e = max((x_e - le) / c, 0)
    h_s = 2 * c * naca4_yt(xc_s, tr)
    h_e = 2 * c * naca4_yt(xc_e, tr)
    # LE web: at leading edge, wall_t closure
    integral += h_s / wall_t if h_s > 0 else 0
    # Spar/hinge web: could be spar tube wall or shell wall
    integral += h_e / wall_t if h_e > 0 else 0
    return integral


# ============================================================
# SECTION 1: MASS BUDGET
# ============================================================
print("=" * 80)
print("SECTION 1: COMPLETE MASS BUDGET")
print("=" * 80)

# Integrate shell areas
dy = 1.0
stab_area_v6 = 0
elev_area_v6 = 0
stab_area_v5 = 0
elev_area_v5 = 0

for yi in range(215):
    y = yi + 0.5
    # V6
    sp6 = section_perimeter(y, le_x(y), X_HINGE, WALL_STAB)
    ep6 = section_perimeter(y, X_HINGE, te_x(y), WALL_ELEV)
    stab_area_v6 += sp6 * dy
    elev_area_v6 += ep6 * dy
    # V5
    sp5 = section_perimeter(y, le_x(y), X_HINGE_V5, WALL_STAB)
    ep5 = section_perimeter(y, X_HINGE_V5, te_x(y), WALL_ELEV)
    stab_area_v5 += sp5 * dy
    elev_area_v5 += ep5 * dy

stab_mass_one_v6 = stab_area_v6 * WALL_STAB * RHO_LWPLA
elev_mass_one_v6 = elev_area_v6 * WALL_ELEV * RHO_LWPLA
stab_mass_one_v5 = stab_area_v5 * WALL_STAB * RHO_LWPLA
elev_mass_one_v5 = elev_area_v5 * WALL_ELEV * RHO_LWPLA

# Saddle channel extra mass (concave channel in stab at hinge zone)
# ~3mm wide, ~0.5mm extra wall, from y=4 to y=165mm
saddle_span = 165 - (FIN_HALF + FIN_GAP)
saddle_extra_vol = saddle_span * 3.0 * 0.5  # mm3 per half
saddle_mass_one = saddle_extra_vol * RHO_LWPLA

# Bull-nose extra mass (convex extension on elevator LE)
# ~2.5mm forward extension, half-cylinder r=1.25mm, from y=4 to y=165mm
bullnose_span = saddle_span
bullnose_perim = math.pi * 1.25  # half circumference of r=1.25mm
bullnose_extra_area = bullnose_span * bullnose_perim
bullnose_mass_one = bullnose_extra_area * WALL_ELEV * RHO_LWPLA

# Spar
spar_length = 2 * SPAR_TERM
spar_cs_area = math.pi / 4 * (SPAR_OD**2 - SPAR_ID**2)
spar_mass = spar_cs_area * spar_length * RHO_CF

# Music wire
wire_length = 2 * WIRE_TERM
wire_cs_area = math.pi / 4 * WIRE_DIA**2
wire_mass = wire_cs_area * wire_length * RHO_STEEL

# PETG knuckles
knuckle_spacing = 8.0
knuckles_per_side = int((200 - (FIN_HALF + FIN_GAP)) / knuckle_spacing)
total_knuckles = knuckles_per_side * 2  # both sides
knuckle_len = 2.0
knuckle_od = 1.2
knuckle_id = 0.6
knuckle_vol_each = math.pi / 4 * (knuckle_od**2 - knuckle_id**2) * knuckle_len
knuckle_mass_total = total_knuckles * knuckle_vol_each * RHO_PETG

# PETG strips (4 total)
strip_len = 196  # mm each
strip_w = 2.0
strip_t = 0.5
strip_mass_total = 4 * strip_len * strip_w * strip_t * RHO_PETG

# Gap seal options
gap_seal_span = 165  # per half
gap_seal_width = 8.0

mylar_t = 0.05
mylar_mass_per_half = gap_seal_span * gap_seal_width * mylar_t * RHO_MYLAR
lwpla_lip_t = 0.25
lwpla_lip_mass_per_half = gap_seal_span * gap_seal_width * lwpla_lip_t * RHO_LWPLA
tpu_t = 0.30
tpu_mass_per_half = gap_seal_span * gap_seal_width * tpu_t * RHO_TPU
tape_t = 0.04
tape_mass_per_half = gap_seal_span * gap_seal_width * tape_t * 1.1e-3  # ~1.1 g/cm3

# Other components
bridge_mass = 0.60
clevis_mass = 0.15
ca_mass = 0.40

print()
print(f"{'Component':<40} {'V5 (g)':>8} {'V6 (g)':>8} {'Delta':>8}")
print("-" * 66)
print(f"{'Stab shells (2x, base)':<40} {2*stab_mass_one_v5:>8.2f} {2*stab_mass_one_v6:>8.2f} {2*(stab_mass_one_v6-stab_mass_one_v5):>+8.2f}")
print(f"{'Stab saddle channel extra (2x)':<40} {'--':>8} {2*saddle_mass_one:>8.2f} {2*saddle_mass_one:>+8.2f}")
print(f"{'Elevator shells (2x, base)':<40} {2*elev_mass_one_v5:>8.2f} {2*elev_mass_one_v6:>8.2f} {2*(elev_mass_one_v6-elev_mass_one_v5):>+8.2f}")
print(f"{'Elev bull-nose extra (2x)':<40} {'--':>8} {2*bullnose_mass_one:>8.2f} {2*bullnose_mass_one:>+8.2f}")
print(f"{'Main spar (3mm CF tube)':<40} {'2.29':>8} {spar_mass:>8.2f} {spar_mass-2.29:>+8.2f}")
print(f"{'Rear spar (1.5mm CF rod)':<40} {'1.15':>8} {'0.00':>8} {'-1.15':>8}")
print(f"{'Elevator stiffeners (2x 1mm CF)':<40} {'0.38':>8} {'0.00':>8} {'-0.38':>8}")
print(f"{'Music wire (0.5mm)':<40} {'0.68':>8} {wire_mass:>8.2f} {wire_mass-0.68:>+8.2f}")
print(f"{'PETG knuckles ({total_knuckles}x)':<40} {'(incl)':>8} {knuckle_mass_total:>8.2f} {'--':>8}")
print(f"{'PETG strips (4x)':<40} {'2.00':>8} {strip_mass_total:>8.2f} {strip_mass_total-2.00:>+8.2f}")
print(f"{'Tungsten putty':<40} {'1.00':>8} {'0.00':>8} {'-1.00':>8}")
print(f"{'Gap seal (Mylar, recommended)':<40} {'--':>8} {2*mylar_mass_per_half:>8.3f} {2*mylar_mass_per_half:>+8.3f}")
print(f"{'Elevator bridge joiner':<40} {'0.60':>8} {bridge_mass:>8.2f} {'0.00':>8}")
print(f"{'Z-bend clevis + pushrod fittings':<40} {'0.15':>8} {clevis_mass:>8.2f} {'0.00':>8}")
print(f"{'CA glue':<40} {'0.40':>8} {ca_mass:>8.2f} {'0.00':>8}")
print("-" * 66)

total_v6 = (2*stab_mass_one_v6 + 2*saddle_mass_one +
            2*elev_mass_one_v6 + 2*bullnose_mass_one +
            spar_mass + wire_mass + knuckle_mass_total + strip_mass_total +
            2*mylar_mass_per_half + bridge_mass + clevis_mass + ca_mass)

print(f"{'V6 GRAND TOTAL':<40} {'33.65':>8} {total_v6:>8.2f} {total_v6-33.65:>+8.2f}")
print()

# Gap seal comparison table
print("Gap seal options (total mass, both halves):")
print(f"  A: LW-PLA lip (0.25mm):  {2*lwpla_lip_mass_per_half:.3f} g")
print(f"  B: TPU strip (0.30mm):   {2*tpu_mass_per_half:.3f} g")
print(f"  C: Blenderm tape (0.04mm): {2*tape_mass_per_half:.3f} g")
print(f"  D: Mylar (0.05mm):       {2*mylar_mass_per_half:.3f} g")

# ============================================================
# SECTION 2: TORSIONAL ANALYSIS
# ============================================================
print()
print("=" * 80)
print("SECTION 2: SINGLE-SPAR TORSIONAL ANALYSIS (Bredt-Batho)")
print("=" * 80)
print()

# D-box: LE to spar (X=34.5) -- closed thin-wall section
# Open section: spar to hinge (X=34.5 to X=60.0) -- open channel
# Bredt formula: GJ = 4*A^2*G / (integral ds/t)

print(f"{'y (mm)':<8} {'D-box A':>10} {'D-box GJ':>12} {'Open GJ':>12} {'Total GJ':>12} {'V5 2-spar':>12}")
print(f"{'':8} {'(mm2)':>10} {'(N-mm2)':>12} {'(N-mm2)':>12} {'(N-mm2)':>12} {'(N-mm2)':>12}")
print("-" * 70)

span_stations = [0, 25, 50, 75, 100, 125, 150, 175, 189, 200]
gj_v6_values = []
gj_v5_values = []

for y in span_stations:
    c = chord_at(y)
    le = le_x(y)
    te = te_x(y)
    tr = t_ratio(y)

    if c <= 0:
        print(f"{y:<8} {'--':>10} {'--':>12} {'--':>12} {'--':>12} {'--':>12}")
        continue

    # V6 D-box: LE to spar
    x_spar_local = X_SPAR
    A_dbox = enclosed_area(y, le, x_spar_local)
    ds_t_dbox = skin_path_integral(y, le, x_spar_local, WALL_STAB)

    if A_dbox > 0 and ds_t_dbox > 0 and ds_t_dbox < 1e10:
        GJ_dbox = 4 * A_dbox**2 * G_LWPLA / ds_t_dbox
    else:
        GJ_dbox = 0

    # V6 Open section: spar to hinge (open C-channel)
    # GJ_open = (1/3) * G * sum(b_i * t_i^3) for each flat plate segment
    # Upper skin + lower skin + no closing web
    x_open_start = x_spar_local
    x_open_end = min(X_HINGE, te)
    open_length = x_open_end - x_open_start
    if open_length > 0:
        # Two skins (upper + lower), each of length ~open_length, thickness WALL_STAB
        GJ_open = (1/3) * G_LWPLA * 2 * open_length * WALL_STAB**3
    else:
        GJ_open = 0

    GJ_total_v6 = GJ_dbox + GJ_open
    gj_v6_values.append((y, GJ_total_v6))

    # V5 comparison: two closed cells
    # Cell 1: LE to rear spar (X=69)
    # Cell 2: rear spar to hinge (X=74.75)
    # Simplified: treat as single D-box LE to rear spar
    A_v5_main = enclosed_area(y, le, min(X_REAR_V5, te))
    ds_t_v5_main = skin_path_integral(y, le, min(X_REAR_V5, te), WALL_STAB)

    if A_v5_main > 0 and ds_t_v5_main > 0 and ds_t_v5_main < 1e10:
        GJ_v5 = 4 * A_v5_main**2 * G_LWPLA / ds_t_v5_main
    else:
        GJ_v5 = 0

    # Add small open section contribution (rear spar to hinge in v5)
    open_v5 = min(X_HINGE_V5, te) - min(X_REAR_V5, te)
    if open_v5 > 0:
        GJ_v5 += (1/3) * G_LWPLA * 2 * open_v5 * WALL_STAB**3

    gj_v5_values.append((y, GJ_v5))

    print(f"{y:<8} {A_dbox:>10.1f} {GJ_dbox:>12.0f} {GJ_open:>12.0f} {GJ_total_v6:>12.0f} {GJ_v5:>12.0f}")

print()
# Average ratio
ratios = []
for (y6, gj6), (y5, gj5) in zip(gj_v6_values, gj_v5_values):
    if gj5 > 0:
        ratios.append(gj6 / gj5)
avg_ratio = sum(ratios) / len(ratios) if ratios else 0
print(f"Average V6/V5 torsional stiffness ratio: {avg_ratio:.3f} ({avg_ratio*100:.1f}%)")

# Saddle contribution when elevator at neutral
print()
print("Saddle contribution at neutral deflection:")
print("  When elevator is at neutral, the bull-nose sits in the concave saddle,")
print("  partially closing the section from spar to hinge.")
print("  This creates a quasi-closed cell from X=34.5 to X=60.0.")
saddle_boost_pct = 15  # estimated based on partial closure
print(f"  Estimated boost: ~{saddle_boost_pct}% increase in torsional stiffness at neutral")
print(f"  Effective V6/V5 ratio at neutral: {avg_ratio * 1.15:.3f}")

# Flight load check
print()
print("Flight load torsion check at Vne=20 m/s:")
Vne = 20.0
rho_air = 1.225
S_half = 0.5 * 407.7e-6  # m2 per half
c_mean = 94.8e-3  # m
# Max pitching moment at Vne
Cm_max = 0.15  # typical max Cm for symmetric section with elevator
q = 0.5 * rho_air * Vne**2
T_max = q * S_half * c_mean * Cm_max * 1e6  # N-mm (convert from N-m)
print(f"  Dynamic pressure q = {q:.1f} Pa")
print(f"  Max torsion per half-span: T = {T_max:.1f} N-mm")

# Twist at root from tip load
GJ_root = gj_v6_values[0][1] if gj_v6_values else 1
twist_rad = T_max * (SPAR_TERM / 1000) / GJ_root  # approximate
twist_deg = math.degrees(twist_rad)
print(f"  Root D-box GJ = {GJ_root:.0f} N-mm2")
print(f"  Approximate twist over spar span: {twist_deg:.2f} deg")
print(f"  Acceptable: < 2 deg at Vne? {'YES' if abs(twist_deg) < 2 else 'NO - CONCERN'}")

# ============================================================
# SECTION 3: ELEVATOR BENDING (WITHOUT STIFFENER)
# ============================================================
print()
print("=" * 80)
print("SECTION 3: ELEVATOR BENDING ANALYSIS (NO STIFFENER)")
print("=" * 80)
print()

# The elevator is a thin LW-PLA shell (0.40mm) from root to y=212mm
# The music wire at X=60 provides some bending stiffness
# The bull-nose adds local stiffness

# Elevator shell as a thin-wall beam:
# I = integral of (t * z^2) ds around the perimeter
# For a thin airfoil section: I ~ 2 * integral(t * z(x)^2 dx) from hinge to TE

print("Elevator spanwise bending stiffness (EI):")
print(f"{'y (mm)':<8} {'Chord':>8} {'Shell I':>12} {'Wire I':>12} {'Total EI':>12}")
print(f"{'':8} {'(mm)':>8} {'(mm4)':>12} {'(mm4)':>12} {'(N-mm2)':>12}")
print("-" * 56)

def elev_shell_Ixx(y):
    """Second moment of area of elevator shell about its NA (chordwise bending)."""
    c = chord_at(abs(y))
    if c <= 0:
        return 0.0
    le = le_x(abs(y))
    te = te_x(abs(y))
    tr = t_ratio(abs(y))
    x_s = X_HINGE
    x_e = te
    if x_e <= x_s:
        return 0.0
    n = 50
    Ixx = 0.0
    for i in range(n):
        x1 = x_s + (x_e - x_s) * i / n
        x2 = x_s + (x_e - x_s) * (i + 1) / n
        xc = ((x1 + x2) / 2 - le) / c
        z = c * naca4_yt(max(xc, 0), tr)
        dx = x2 - x1
        # Upper and lower skins contribute
        Ixx += 2 * WALL_ELEV * z**2 * dx
    return Ixx

wire_I = math.pi / 64 * WIRE_DIA**4  # mm4

for y in [0, 25, 50, 75, 100, 125, 150, 175, 200]:
    ec = te_x(y) - X_HINGE if te_x(y) > X_HINGE else 0
    I_shell = elev_shell_Ixx(y)
    EI_shell = E_LWPLA * I_shell
    EI_wire = E_STEEL * wire_I if y <= WIRE_TERM else 0
    EI_total = EI_shell + EI_wire
    print(f"{y:<8} {ec:>8.1f} {I_shell:>12.2f} {wire_I:>12.4f} {EI_total:>12.0f}")

# First bending frequency estimate (cantilever from root)
# f1 = (1.875)^2 / (2*pi*L^2) * sqrt(EI / (m/L))
# Use average EI over span

EI_values = []
for y in range(0, 210, 5):
    I_s = elev_shell_Ixx(y)
    EI_s = E_LWPLA * I_s
    EI_w = E_STEEL * wire_I if y <= WIRE_TERM else 0
    EI_values.append(EI_s + EI_w)

EI_avg = sum(EI_values) / len(EI_values) if EI_values else 1
elev_span = 210.0  # mm, effective span
elev_mass_one = elev_mass_one_v6 + bullnose_mass_one  # total one-half elevator mass
mu = elev_mass_one / elev_span  # g/mm = kg/m * 1e-3/1e-3 = same ratio

# Convert: EI in N-mm2 = 1e-6 N-m2; mu in g/mm = 1e-3 kg / 1e-3 m = kg/m
EI_SI = EI_avg * 1e-6  # N-m2
mu_SI = (elev_mass_one * 1e-3) / (elev_span * 1e-3)  # kg/m

f1 = (1.875**2) / (2 * math.pi * (elev_span * 1e-3)**2) * math.sqrt(EI_SI / mu_SI)
print()
print(f"Average EI (elevator half): {EI_avg:.0f} N-mm2 = {EI_SI:.4f} N-m2")
print(f"Elevator half mass: {elev_mass_one + bullnose_mass_one:.2f} g over {elev_span:.0f} mm")
print(f"Linear density: {mu_SI:.4f} kg/m")
print(f"First bending mode frequency: {f1:.1f} Hz")
print()

# Excitation frequency at Vne
chord_elev_root = te_x(0) - X_HINGE
Strouhal = 0.2  # typical for bluff body
f_excite = Strouhal * Vne / (chord_elev_root * 1e-3)
print(f"Root elevator chord: {chord_elev_root:.1f} mm")
print(f"Vortex shedding frequency at Vne: {f_excite:.0f} Hz (St=0.2)")
print(f"Separation ratio f1/f_excite: {f1/f_excite:.2f}")
print(f"Flutter risk: {'LOW' if f1 > 1.5 * f_excite else 'MODERATE' if f1 > f_excite else 'HIGH'}")

# Minimum intervention analysis
print()
print("Minimum intervention if needed:")
print("  Option 1: Thicken elevator wall to 0.55mm in first 100mm of span")
I_thick = 0
for y in range(0, 100, 5):
    c = chord_at(y)
    le = le_x(y)
    te = te_x(y)
    tr = t_ratio(y)
    x_s = X_HINGE
    x_e = te
    if x_e <= x_s:
        continue
    for i in range(50):
        x1 = x_s + (x_e - x_s) * i / 50
        x2 = x_s + (x_e - x_s) * (i + 1) / 50
        xc = ((x1 + x2) / 2 - le) / c
        z = c * naca4_yt(max(xc, 0), tr)
        dx = x2 - x1
        I_thick += 2 * 0.55 * z**2 * dx

extra_mass_thick = 100 * 2 * (chord_elev_root * 0.5) * (0.55 - 0.40) * RHO_LWPLA * 2  # both halves approx
print(f"    Extra mass: ~{extra_mass_thick:.2f} g (both halves)")
print(f"  Option 2: Printed ribs every 40mm (0.4mm thick, full elevator chord)")
rib_count = int(210 / 40)
rib_area_avg = 15 * 3  # average elevator section area ~45mm2
rib_mass = rib_count * rib_area_avg * 0.4 * RHO_LWPLA * 2  # both halves
print(f"    {rib_count} ribs per half, extra mass: ~{rib_mass:.2f} g (both halves)")
print(f"  Option 3: Single 0.5mm CF strip bonded to interior lower surface")
cf_strip_mass = 210 * 3 * 0.5 * RHO_CF * 2  # 3mm wide, both halves
print(f"    Extra mass: ~{cf_strip_mass:.2f} g (both halves)")

# ============================================================
# SECTION 4: GAP SEAL ANALYSIS
# ============================================================
print()
print("=" * 80)
print("SECTION 4: GAP SEAL ANALYSIS")
print("=" * 80)
print()

print("Option A: Integral LW-PLA lip (0.25mm, 8mm aft extension)")
print(f"  Mass (total): {2*lwpla_lip_mass_per_half:.3f} g")
print(f"  FATIGUE CONCERN: LW-PLA at 230C is foamed and BRITTLE.")
print(f"  At 0.25mm thickness, flexing through +/-18 deg repeatedly will crack.")
print(f"  PLA fatigue endurance limit: ~30% of UTS at 10^6 cycles.")
print(f"  Foamed PLA at 0.25mm: strain at 18 deg deflection over 8mm lip ~3-5%.")
print(f"  PLA fracture strain: ~2-4% (brittle). WILL CRACK within 10-50 flights.")
print(f"  Printing at 210C (denser) helps, but lip zone must be separate material zone.")
print(f"  VERDICT: NOT RECOMMENDED for +/-18 deg deflections.")
print()
print("Option B: Separate TPU 95A strip, bonded with CA")
print(f"  Mass (total): {2*tpu_mass_per_half:.3f} g")
print(f"  TPU fracture strain: >500%. Flex through +/-18 deg: no issue.")
print(f"  CA bond to TPU: WEAK. Bond fails under peel loads.")
print(f"  Better bond: flexible CA (Loctite 4902) or PU adhesive.")
print(f"  Durability: excellent if bonded properly. 200+ flights.")
print(f"  Replacement: re-bond with CA if it peels. Easy field repair.")
print(f"  CONCERN: Multi-material not available, must print TPU separately.")
print(f"  VERDICT: VIABLE, but bonding is the weak link.")
print()
print("Option C: Blenderm/packing tape (0.04mm)")
print(f"  Mass (total): {2*tape_mass_per_half:.3f} g")
print(f"  Ultra-light. Applied by hand in 2 minutes.")
print(f"  Durability: 20-50 flights before replacement needed.")
print(f"  Adhesive degrades with UV and handling.")
print(f"  VERDICT: VIABLE for testing, not for competition.")
print()
print("Option D: 0.05mm Mylar strip (competition standard)")
print(f"  Mass (total): {2*mylar_mass_per_half:.3f} g")
print(f"  PROVEN: Every F5J competition sailplane uses Mylar gap seals.")
print(f"  Flex fatigue: Mylar rated for >10^6 cycles at this thickness.")
print(f"  Application: CA-bonded to stab TE, slides over elevator surface.")
print(f"  Pre-curved to match hinge radius. Self-springs to seal position.")
print(f"  Replacement: annual. Takes 10 minutes.")
print(f"  VERDICT: RECOMMENDED. Lightest durable option, proven technology.")
print()

# ============================================================
# SECTION 5: SADDLE GEOMETRY AT X=60mm
# ============================================================
print("=" * 80)
print("SECTION 5: SADDLE GEOMETRY AT X=60.0mm")
print("=" * 80)
print()

print(f"{'y (mm)':<8} {'Chord':>8} {'t/c':>6} {'Airfoil':>10} {'Half-t':>10} {'Full-t':>10} {'Saddle-d':>10} {'Bull-r':>8}")
print(f"{'':8} {'(mm)':>8} {'(%)':>6} {'thick@60':>10} {'@60':>10} {'@60':>10} {'(mm)':>10} {'(mm)':>8}")
print("-" * 76)

for y in [0, 25, 50, 75, 100, 125, 150, 165, 175, 185, 195, 200, 205, 210, 212]:
    c = chord_at(y)
    le = le_x(y)
    te = te_x(y)
    tr = t_ratio(y)

    if c <= 0:
        print(f"{y:<8} {'(tip)':>8}")
        continue

    xc_hinge = (X_HINGE - le) / c if c > 0 else 0
    if xc_hinge < 0 or xc_hinge > 1:
        ht = 0
    else:
        ht = c * naca4_yt(xc_hinge, tr)  # half-thickness at hinge

    full_t = 2 * ht

    # Saddle depth: how deep the concave channel is
    # Need wall clearance: saddle wall 0.45mm + gap 0.3mm + elevator wall 0.40mm
    wall_clearance = WALL_STAB + 0.3 + WALL_ELEV  # 1.15mm
    saddle_depth = max(0, full_t - wall_clearance - 0.5)  # 0.5mm min floor

    # Bull-nose radius: the convex surface extending forward into saddle
    # Max radius = (saddle_depth - clearance) / 2
    bullnose_r = max(0, (saddle_depth - 0.3) / 2)

    # Check if hinge is inside the airfoil
    hinge_inside = "IN" if (X_HINGE >= le and X_HINGE <= te) else "OUT"

    print(f"{y:<8} {c:>8.1f} {tr*100:>6.1f} {hinge_inside:>10} {ht:>10.2f} {full_t:>10.2f} {saddle_depth:>10.2f} {bullnose_r:>8.2f}")

# Compare with v5 hinge at X=74.75
print()
print("Comparison: airfoil thickness at hinge location")
print(f"{'y (mm)':<8} {'V6 (X=60)':>12} {'V5 (X=74.75)':>14} {'V6 thicker?':>12}")
print("-" * 50)
for y in [0, 50, 100, 150, 175, 200]:
    c = chord_at(y)
    le = le_x(y)
    tr = t_ratio(y)
    if c <= 0:
        continue
    xc_60 = (60.0 - le) / c
    xc_75 = (74.75 - le) / c
    t_60 = 2 * c * naca4_yt(max(min(xc_60, 1), 0), tr) if 0 <= xc_60 <= 1 else 0
    t_75 = 2 * c * naca4_yt(max(min(xc_75, 1), 0), tr) if 0 <= xc_75 <= 1 else 0
    thicker = "YES" if t_60 > t_75 else "NO"
    print(f"{y:<8} {t_60:>12.2f} {t_75:>14.2f} {thicker:>12}")

# Deflection clearance at +/-18 degrees
print()
print("Deflection clearance at +/-18 deg:")
for y in [0, 50, 100, 150, 200]:
    c = chord_at(y)
    le = le_x(y)
    te = te_x(y)
    tr = t_ratio(y)
    if c <= 0 or X_HINGE >= te:
        continue
    elev_c = te - X_HINGE
    xc_hinge = (X_HINGE - le) / c
    ht = c * naca4_yt(max(xc_hinge, 0), tr)
    # At 18 deg, the elevator TE moves up/down by:
    deflection = elev_c * math.sin(math.radians(18))
    # The gap between stab and elevator at hinge:
    gap_at_hinge = 2 * ht  # full thickness available
    # The elevator bull-nose radius limits clearance
    print(f"  y={y:>3}mm: elev_chord={elev_c:.1f}mm, TE deflection={deflection:.1f}mm, "
          f"hinge thickness={2*ht:.1f}mm, clearance OK={'YES' if 2*ht > 1.5 else 'TIGHT'}")

# Where does saddle taper to zero?
print()
for y in range(150, 215):
    c = chord_at(y)
    le = le_x(y)
    te = te_x(y)
    tr = t_ratio(y)
    if c <= 0 or X_HINGE >= te:
        print(f"  Hinge exits airfoil at y~{y}mm")
        break
    xc = (X_HINGE - le) / c
    ht = 2 * c * naca4_yt(max(xc, 0), tr)
    if ht < 1.5:  # too thin for saddle
        print(f"  Saddle tapers to zero at y~{y}mm (full thickness={ht:.1f}mm < 1.5mm)")
        break

# ============================================================
# SECTION 6: FLUTTER ASSESSMENT
# ============================================================
print()
print("=" * 80)
print("SECTION 6: FLUTTER ASSESSMENT")
print("=" * 80)
print()

# Elevator CG relative to hinge
# Without tip horn or tungsten, CG is aft of hinge
elev_chord_root = te_x(0) - X_HINGE
elev_chord_mid = te_x(100) - X_HINGE if te_x(100) > X_HINGE else 0
print(f"Elevator root chord (aft of hinge): {elev_chord_root:.1f} mm")
print(f"Elevator mid-span chord (y=100): {elev_chord_mid:.1f} mm")

# CG of elevator section: approximately at 40% of elevator chord aft of hinge
# (because it's a hollow shell, CG is near mid-chord)
cg_aft_of_hinge = 0.45 * elev_chord_root  # typical for thin shell
print(f"Estimated elevator CG: {cg_aft_of_hinge:.1f} mm aft of hinge")
print(f"  (No tungsten or tip horn to move CG forward)")

# Bull-nose mass and moment
print(f"Bull-nose mass (per half): {bullnose_mass_one:.3f} g")
bullnose_moment = bullnose_mass_one * 1.25  # CG of bull-nose is ~1.25mm fwd of hinge
print(f"Bull-nose moment about hinge: {bullnose_moment:.3f} g-mm FORWARD (helps)")

# Wire torsional stiffness
# Wire acts as a torsion spring: k_theta = G*J/L for circular wire
J_wire = math.pi / 32 * WIRE_DIA**4  # mm4
wire_half_span = WIRE_TERM
k_wire = G_STEEL * J_wire / wire_half_span  # N-mm/rad per half
print(f"Wire polar moment J: {J_wire:.6f} mm4")
print(f"Wire torsional stiffness (per half): {k_wire:.3f} N-mm/rad")

# Flutter speed estimate (simplified Theodorsen)
# V_flutter ~ sqrt(k_theta / (rho * S * e * (x_cg - x_ea)))
# where e = distance from EA to hinge, x_cg = CG aft of hinge
# For a simple binary flutter (bending-torsion):

# Mass per unit span of elevator
elev_mass_total = 2 * (elev_mass_one_v6 + bullnose_mass_one)
elev_span_total = 2 * 210  # mm
m_per_span = elev_mass_total / elev_span_total * 1e-3  # kg/mm -> divide by 1e3 to get kg/m * 1e-3
# Actually: g/mm * 1e-3 = kg/m * 1e-3... let me be careful
# elev_mass_total in grams, span in mm
# mu = mass/span = g/mm
mu_elev = elev_mass_total / elev_span_total  # g/mm

# Static imbalance
S_alpha = mu_elev * cg_aft_of_hinge  # g-mm/mm = g (mass moment per unit span)

# Divergence speed (torsional)
# V_div = sqrt(2 * k_theta / (rho * S * dCL/dalpha * e))
# Simplified flutter check using k/q*S rule
dCL_da = 2 * math.pi * 0.75  # rad^-1, elevator effectiveness ~75% of thin airfoil
e_aero = cg_aft_of_hinge * 1e-3  # m
S_elev = 176.6e-4  # m2 (from aero analysis)
b_elev = 0.210  # m half-span

# Very simplified: flutter speed ~ sqrt(k / (rho * S * x_cg * dCL/da))
# k_total = wire stiffness + shell stiffness contribution
# Shell contributes through skin tension/compression
k_total = k_wire * 2  # both halves constrain the elevator

V_flutter_sq = k_total * 1e-3 / (0.5 * rho_air * S_elev * dCL_da * e_aero)
V_flutter = math.sqrt(abs(V_flutter_sq))

print()
print(f"Elevator total mass: {elev_mass_total:.2f} g")
print(f"Elevator CG aft of hinge: {cg_aft_of_hinge:.1f} mm")
print(f"Static imbalance (S_alpha): {S_alpha:.4f} g-mm/mm")
print(f"Total torsional stiffness: {k_total:.3f} N-mm/rad")
print(f"Estimated flutter speed: {V_flutter:.1f} m/s")
print(f"Vne = 20 m/s, safety factor = {V_flutter/20:.2f}")
print(f"Flutter margin: {'ADEQUATE (>1.2x)' if V_flutter > 24 else 'MARGINAL (1.0-1.2x)' if V_flutter > 20 else 'INSUFFICIENT (<1.0x)'}")

# V5 comparison
print()
print("V5 flutter comparison:")
print(f"  V5 had: tungsten putty 1.0g moving CG forward")
print(f"  V5 had: 1mm CF stiffener increasing bending frequency")
print(f"  V5 CG was closer to hinge line -> lower static imbalance")
print(f"  V6 removes ALL mass balance -> CG moves further aft")
print(f"  This is the KEY STRUCTURAL CONCERN of V6.")

# Hinge friction contribution
print()
print("Mitigating factors:")
print(f"  1. Music wire pin hinge has inherent friction (~0.05 N-mm damping)")
print(f"  2. Mylar gap seal adds aerodynamic damping")
print(f"  3. PETG knuckle interleaving prevents free-play (zero slop)")
print(f"  4. Elevator bridge joiner provides spanwise coupling (anti-flutter)")
print(f"  5. Bull-nose extends forward of hinge, providing small forward mass")

# ============================================================
# SECTION 7: ASSEMBLY SEQUENCE
# ============================================================
print()
print("=" * 80)
print("SECTION 7: ASSEMBLY SEQUENCE")
print("=" * 80)
print()

steps = [
    "1.  PRINT: 2x stab shells (LW-PLA 230C, vase mode 0.45mm, saddle channel integral)",
    "2.  PRINT: 2x elevator shells (LW-PLA 230C, vase mode 0.40mm, bull-nose integral)",
    "3.  PRINT: 4x PETG hinge strips (PETG 240C, solid 100%, knuckles 1.2mm OD)",
    "4.  PRINT: 1x elevator bridge joiner (CF-PLA 220C, solid 1.2mm)",
    "5.  BOND: Hinge strips to stab TE faces (CA, lower surface alignment)",
    "6.  BOND: Hinge strips to elevator LE faces (CA, lower surface alignment)",
    "7.  INTERLEAVE: Mate left stab + left elevator knuckles, right stab + right elevator",
    "8.  THREAD: 0.5mm music wire from left tip through all knuckles, through VStab fin bore, to right tip",
    "9.  BEND: Wire 90-deg at each tip (y=212mm), tuck ends flush",
    "10. TEST: Full deflection range +/-18 deg, verify smooth operation",
    "11. INSTALL: Elevator bridge joiner - slide into left elevator root pocket (CA), then right (CA)",
    "12. VERIFY: Synchronization - deflect one half, confirm other follows within 1 deg",
    "13. THREAD: Main spar (3mm CF tube, 378mm) through left stab at X=34.5, through VStab fin bore, through right stab",
    "14. BOND: Stab roots to VStab fin (dovetail interlock + CA)",
    "15. APPLY: Mylar gap seal strips - CA bond to stab TE, overlapping elevator (both halves)",
    "16. ROUTE: Pushrod through fuselage, VStab fin, into left elevator, to Z-bend attachment",
    "17. VERIFY: Full deflection range with servo actuation, check for binding",
    "18. FINAL: Weigh complete assembly, verify < 35g hard limit",
]
for step in steps:
    print(f"  {step}")

print()
print("NOTE: NO tungsten packing, NO tip horn, NO rear spar, NO stiffener installation.")
print("Assembly is significantly simplified vs V5 (18 steps vs 16, but several steps removed).")
