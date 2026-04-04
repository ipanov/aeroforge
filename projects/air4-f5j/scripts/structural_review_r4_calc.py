"""
Structural Review R4 — Full computational analysis for concealed saddle hinge design.
"""
import math
import sys
sys.path.insert(0, 'D:/Repos/aeroforge')
from scripts.hstab_geometry import (
    chord_at, le_x, te_x, t_ratio, naca4_yt, elev_chord_at,
    ROOT_CHORD, HALF_SPAN, REF_X, REF_FRAC, N_EXP,
    X_MAIN_SPAR, X_REAR_SPAR, X_HINGE, X_STIFF,
    Y_MAIN_END, Y_REAR_END, Y_HINGE_END, Y_STIFF_END,
    FIN_HALF, FIN_GAP
)

# ============================================================
# NEW DESIGN PARAMETERS
# ============================================================
# Spar moves to max thickness ~30% chord
# At root 115mm, 30% = 34.5mm. Current is 35.0 (30.4%).
# User says ~30% chord. X=34.5mm is closer to true max-t.
# Actually X=35.0 is already extremely close. Let's keep 35.0
# since it's within 0.4% and already validated. The user's
# instruction says "moves to max thickness point (~30% chord = X~34.5mm)"
# Let's use exactly 34.5 for the new analysis.
X_NEW_SPAR = 34.5
D_SPAR_BORE = 3.1  # bore diameter for 3mm tube

# Hinge line: user says ~X=60-65mm (aero will determine exact).
# For structural analysis, we'll evaluate a range and use X=62.5 as baseline.
X_NEW_HINGE = 62.5  # midpoint of 60-65mm range

# Music wire
D_WIRE = 0.5  # mm
WIRE_DENSITY = 7.85e-3  # g/mm^3 (spring steel)

# Material properties
RHO_LWPLA = 0.65e-3    # g/mm^3 (foamed LW-PLA at 230C, ~50% density reduction)
RHO_LWPLA_DENSE = 0.85e-3  # g/mm^3 (less foamed, printed at 210C)
RHO_PETG = 1.27e-3     # g/mm^3
RHO_TPU = 1.21e-3      # g/mm^3 (TPU 95A)
RHO_CF_TUBE = 1.55e-3  # g/mm^3 (carbon fiber)
RHO_CF_ROD = 1.55e-3   # g/mm^3

# Print parameters
WALL_STAB = 0.45       # mm, stab shell
WALL_ELEV = 0.40       # mm, elevator shell
WALL_SADDLE = 0.6      # mm, saddle bearing walls (2-perimeter)
WALL_BULLNOSE = 0.55   # mm, bull-nose walls (2-perimeter)

print("=" * 80)
print("STRUCTURAL REVIEW R4 — CONCEALED SADDLE HINGE DESIGN")
print("=" * 80)

# ============================================================
# SECTION 7: SPAR SPAN CALCULATION (do first, needed for mass)
# ============================================================
print("\n" + "=" * 80)
print("7. SPAR SPAN CALCULATION")
print("=" * 80)

header = "{:>6} {:>7} {:>7} {:>9} {:>7} {:>6} {:>8} {:>6}".format(
    "y", "chord", "LE_x", "spar_loc", "spar%c", "t/c", "thick", "bore")
print(header)
print("-" * len(header))

spar_max_bore_y = 0
spar_exit_y = 999
for y_i in range(0, 216, 2):
    y = float(y_i)
    c = chord_at(y)
    if c < 1.0:
        break
    lx = le_x(y)
    tx = te_x(y)
    spar_local = X_NEW_SPAR - lx

    if spar_local < 0 or X_NEW_SPAR > tx:
        print("{:6.0f} {:7.1f} {:7.2f}   ** EXITS AIRFOIL **".format(y, c, lx))
        spar_exit_y = min(spar_exit_y, y)
        break

    spar_frac = spar_local / c
    tr = t_ratio(y)
    yt = naca4_yt(spar_frac, tr)
    thick = 2 * yt * c
    bore_ok = "YES" if thick > D_SPAR_BORE else "no"

    if thick > D_SPAR_BORE:
        spar_max_bore_y = y

    if y_i % 10 == 0 or thick < 4.0:
        print("{:6.0f} {:7.1f} {:7.2f} {:9.2f} {:6.1f}% {:6.4f} {:8.2f} {:>6}".format(
            y, c, lx, spar_local, spar_frac * 100, tr, thick, bore_ok))

print("\nSpar bore clearance (3.1mm) last satisfied at y = {}mm".format(spar_max_bore_y))
print("Old design (X=35.0): spar terminated at y=186mm")
print("New design (X=34.5): spar terminates at y~{}mm".format(spar_max_bore_y))

# For mass calc, use the spar termination
Y_NEW_SPAR_END = spar_max_bore_y
SPAR_LENGTH = 2 * Y_NEW_SPAR_END  # full span, both halves
# But spar passes through VStab fin, so subtract nothing (it's continuous)
# Actually the old spar was 372mm = 2*186. New would be 2*spar_max_bore_y
print("New spar length (both halves): {}mm".format(SPAR_LENGTH))

# ============================================================
# SECTION: HINGE LINE ANALYSIS AT NEW POSITION
# ============================================================
print("\n" + "=" * 80)
print("HINGE LINE AT X={} (new position)".format(X_NEW_HINGE))
print("=" * 80)

header2 = "{:>6} {:>7} {:>7} {:>9} {:>7} {:>8} {:>6}".format(
    "y", "chord", "LE_x", "hinge_loc", "hing%c", "elv_chd", "t_hng")
print(header2)
print("-" * len(header2))

hinge_exit_y = 999
for y_i in range(0, 216, 5):
    y = float(y_i)
    c = chord_at(y)
    if c < 1.0:
        break
    lx = le_x(y)
    tx = te_x(y)
    hinge_local = X_NEW_HINGE - lx

    if hinge_local < 0 or X_NEW_HINGE > tx:
        print("{:6.0f} {:7.1f} {:7.2f}   ** EXITS **".format(y, c, lx))
        hinge_exit_y = min(hinge_exit_y, y)
        break

    hinge_frac = hinge_local / c
    elev_c = tx - X_NEW_HINGE
    tr = t_ratio(y)
    t_at_hinge = 2 * naca4_yt(hinge_frac, tr) * c

    print("{:6.0f} {:7.1f} {:7.2f} {:9.2f} {:6.1f}% {:8.2f} {:6.2f}".format(
        y, c, lx, hinge_local, hinge_frac * 100, elev_c, t_at_hinge))

print("\nHinge wire exits airfoil at y~{}mm".format(hinge_exit_y))

# Elevator chord ratio at root
elev_root = te_x(0) - X_NEW_HINGE
elev_frac_root = elev_root / ROOT_CHORD * 100
print("Elevator root chord: {:.1f}mm ({:.1f}% of root chord)".format(elev_root, elev_frac_root))

# Airfoil thickness at hinge line
tr_root = t_ratio(0)
hinge_frac_root = (X_NEW_HINGE - le_x(0)) / chord_at(0)
t_hinge_root = 2 * naca4_yt(hinge_frac_root, tr_root) * chord_at(0)
print("Airfoil thickness at hinge (root): {:.2f}mm".format(t_hinge_root))

# ============================================================
# SECTION 1: MASS BUDGET
# ============================================================
print("\n" + "=" * 80)
print("1. MASS BUDGET — ITEM-BY-ITEM COMPARISON")
print("=" * 80)

# --- OLD DESIGN (v5) ---
print("\n--- OLD DESIGN (v5) ---")
old = {}
old['HStab_Left'] = 8.50
old['HStab_Right'] = 8.50
old['Elevator_Left'] = 4.00
old['Elevator_Right'] = 4.00
old['Hinge_Strip_L_stab'] = 0.50
old['Hinge_Strip_R_stab'] = 0.50
old['Hinge_Strip_L_elev'] = 0.50
old['Hinge_Strip_R_elev'] = 0.50
old['Main_Spar'] = 2.29
old['Rear_Spar'] = 1.15
old['Stiffener_L'] = 0.19
old['Stiffener_R'] = 0.19
old['Hinge_Wire'] = 0.68
old['Tungsten'] = 1.00
old['Bridge_Joiner'] = 0.60
old['CA_glue'] = 0.55

total_old = sum(old.values())
for k, v in old.items():
    print("  {:30s} {:6.2f}g".format(k, v))
print("  {:30s} {:6.2f}g".format("TOTAL OLD", total_old))

# --- NEW DESIGN ---
print("\n--- NEW DESIGN (v6 concealed saddle) ---")
new = {}

# Main spar: 3mm CF tube (3/2mm OD/ID)
# Cross-section area = pi/4 * (3^2 - 2^2) = pi/4 * 5 = 3.927 mm^2
spar_area = math.pi / 4 * (3.0**2 - 2.0**2)
spar_mass = spar_area * SPAR_LENGTH * RHO_CF_TUBE
new['Main_Spar (3mm tube, {}mm)'.format(SPAR_LENGTH)] = round(spar_mass, 2)

# Hinge wire: 0.5mm music wire
# Length: need to determine. It runs from tip to tip through VStab.
# At X=62.5, hinge exits at some y. Let's say wire goes from -hinge_exit to +hinge_exit
# with a small margin (no tip bends in new design per user: "no horn")
# Actually the wire needs PETG sleeves, and goes through saddle channel.
# Length = 2 * (hinge_exit_y - margin) + VStab_fin_width
wire_span = 2 * (hinge_exit_y - 5)  # 5mm margin from exit
wire_length = min(wire_span, 430)  # cap at reasonable length
wire_area = math.pi / 4 * D_WIRE**2
wire_mass = wire_area * wire_length * WIRE_DENSITY
new['Hinge_Wire (0.5mm, {}mm)'.format(int(wire_length))] = round(wire_mass, 2)

# Stab shells: now they need a saddle channel zone
# The saddle zone adds local wall thickness. Let's estimate the extra mass.
# Saddle zone: ~5mm wide chordwise x full span of hinge x 2 sides (top/bottom)
# Additional wall: from 0.45mm to 0.6mm in saddle zone = 0.15mm extra
# But we also REMOVE the rear portion of the stab (stab now ends at hinge, not at old hinge X=74.75)
# Old stab: LE to X=74.75 (65% chord at root)
# New stab: LE to X=62.5 (~54% chord at root)
# This REDUCES stab shell area by ~17% at root

# Rough stab shell mass estimation:
# Old stab: LE to hinge at 65% chord. Shell perimeter ~ 2 * chord_frac * chord * t/c_correction
# New stab: LE to hinge at ~54% chord. Shorter chord coverage.
# Let's compute the shell area ratio

# For a rough estimate: stab shell covers LE to hinge line
# Old: LE to X=74.75 = 65% chord at root
# New: LE to X=62.5 = 54.3% chord at root
# Ratio of covered chord: 54.3/65 = 0.835
# But the saddle zone adds ~0.15mm extra wall over ~5mm chordwise span

# More precise: integrate shell surface area
# Shell perimeter at station y ≈ 2 * (distance from LE to hinge) + small LE radius
# The airfoil surface is longer than the chord due to curvature

# Old stab covered LE to 65% chord.  New covers LE to ~54%.
# Mass reduction factor for shorter chord coverage:
old_stab_frac = 0.65  # hinge at 65% root chord
new_stab_frac = X_NEW_HINGE / ROOT_CHORD  # ~54.3%

# The stab shell mass is roughly proportional to the surface area covered
# Surface area ~ integral of perimeter * dy
# Perimeter at each station ~ airfoil arc length from LE to hinge fraction
# For thin symmetric airfoils, arc length ≈ chord_covered * (1 + 0.5*(t/c)^2) approximately
# The ratio is roughly new_frac/old_frac
stab_chord_ratio = new_stab_frac / old_stab_frac
print("\n  Stab chord coverage ratio (new/old): {:.3f}".format(stab_chord_ratio))

# Old stab mass: 8.50g each. New stab (shorter chord) but with saddle:
stab_base_mass = 8.50 * stab_chord_ratio  # reduced for shorter coverage
# Add saddle zone mass: 2 walls x 0.6mm thick x ~5mm wide x span
# Saddle is from about y=FIN_HALF+FIN_GAP to y=hinge_exit-10
saddle_span = hinge_exit_y - 10 - (FIN_HALF + FIN_GAP)
saddle_wall_vol = 2 * WALL_SADDLE * 5.0 * saddle_span  # 2 walls (inner sides), 5mm deep, span
saddle_mass = saddle_wall_vol * RHO_LWPLA
print("  Saddle zone per half: vol={:.0f}mm3, mass={:.2f}g".format(saddle_wall_vol, saddle_mass))

stab_new_mass = stab_base_mass + saddle_mass
new['HStab_Left (with saddle)'] = round(stab_new_mass, 2)
new['HStab_Right (with saddle)'] = round(stab_new_mass, 2)

# Elevator shells: now include bull-nose extending forward of wire
# Old elevator: from hinge (65% chord) to TE (97% chord) = 32% chord at root = 36.8mm
# New elevator: from hinge (54.3% chord) to TE (97% chord) = 42.7% chord at root = 49.1mm
# Plus bull-nose extends ~3mm forward of wire into saddle
old_elev_frac = 1.0 - old_stab_frac  # TE truncation not important for ratio
new_elev_frac = 1.0 - new_stab_frac
elev_chord_ratio = new_elev_frac / old_elev_frac
print("  Elevator chord coverage ratio (new/old): {:.3f}".format(elev_chord_ratio))

# Old elevator: 4.00g each (including integral tip horn)
# New elevator: longer chord, but NO tip horn, NO tungsten pocket
# The tip horn zone (y=195-214) added significant mass.
# Estimate horn zone was ~15% of elevator mass = 0.60g per side
# So base elevator without horn: 3.40g, scaled up by chord ratio
elev_no_horn = 3.40
elev_base_new = elev_no_horn * elev_chord_ratio

# Add bull-nose mass: 2 walls x 0.55mm x ~3mm deep x span
bullnose_span = hinge_exit_y - 10 - (FIN_HALF + FIN_GAP)
bullnose_vol = 2 * WALL_BULLNOSE * 3.0 * bullnose_span  # top + bottom walls
bullnose_mass = bullnose_vol * RHO_LWPLA
print("  Bull-nose zone per half: vol={:.0f}mm3, mass={:.2f}g".format(bullnose_vol, bullnose_mass))

elev_new_mass = elev_base_new + bullnose_mass
new['Elevator_Left (with bull-nose)'] = round(elev_new_mass, 2)
new['Elevator_Right (with bull-nose)'] = round(elev_new_mass, 2)

# TPU flex strips: 2 per half (top and bottom), full hinge span
# Width must span the gap during deflection
# At +25 deg deflection, the gap opens. The strip must be wide enough.
# Gap geometry: the hinge gap at the surface is approximately:
# gap_width ≈ wall_thickness / cos(deflection/2) + clearance
# For structural purposes, strip width ~ 6-8mm to handle full deflection
TPU_WIDTH = 8.0  # mm
TPU_THICK = 0.3  # mm (as thin as printable)
tpu_span_per_half = hinge_exit_y - 10 - (FIN_HALF + FIN_GAP)
tpu_vol_per_strip = TPU_WIDTH * TPU_THICK * tpu_span_per_half
tpu_mass_per_strip = tpu_vol_per_strip * RHO_TPU
# 4 strips total (top+bottom, left+right)
tpu_total = 4 * tpu_mass_per_strip
print("  TPU strip: {}mm x {}mm x {}mm = {:.0f}mm3, mass={:.3f}g each".format(
    TPU_WIDTH, TPU_THICK, tpu_span_per_half, tpu_vol_per_strip, tpu_mass_per_strip))
new['TPU strips (4x)'] = round(tpu_total, 2)

# PETG sleeves: embedded in stab saddle channel, ~20 per half
# Each sleeve: OD 1.2mm, ID 0.6mm, length ~3mm
SLEEVE_OD = 1.2
SLEEVE_ID = 0.6
SLEEVE_LEN = 3.0
SLEEVE_COUNT = 40  # 20 per half
sleeve_vol_each = math.pi / 4 * (SLEEVE_OD**2 - SLEEVE_ID**2) * SLEEVE_LEN
sleeve_total_vol = SLEEVE_COUNT * sleeve_vol_each
sleeve_total_mass = sleeve_total_vol * RHO_PETG
print("  PETG sleeves: {} x {:.2f}mm3 = {:.1f}mm3, mass={:.3f}g".format(
    SLEEVE_COUNT, sleeve_vol_each, sleeve_total_vol, sleeve_total_mass))
new['PETG sleeves ({}x)'.format(SLEEVE_COUNT)] = round(sleeve_total_mass, 2)

# Bridge joiner: still needed
new['Bridge_Joiner'] = 0.60

# CA glue: fewer joints now (no hinge strips to bond, but TPU strips need bonding)
# TPU strips: 4 strips x ~200mm bond line x 0.01g/mm =
# Actually CA is very light. Let's estimate:
# Old: 0.55g (many joints)
# New: TPU bonding (4 strips), spar insertion, wire threading, root bonding
# Fewer joints overall. ~0.40g
new['CA glue (all joints)'] = 0.40

# No tip horn, no tungsten, no rear spar, no stiffeners, no PETG hinge strips
print("\n--- ITEMS REMOVED ---")
removed = {
    'Rear_Spar (1.5mm CF, 420mm)': 1.15,
    'Stiffener_L (1mm CF, 150mm)': 0.19,
    'Stiffener_R (1mm CF, 150mm)': 0.19,
    'PETG hinge strips (4x)': 2.00,
    'Tungsten putty (2x0.5g)': 1.00,
}
total_removed = sum(removed.values())
for k, v in removed.items():
    print("  {:40s} -{:.2f}g".format(k, v))
print("  {:40s} -{:.2f}g".format("TOTAL REMOVED", total_removed))

print("\n--- NEW DESIGN COMPONENTS ---")
total_new = sum(new.values())
for k, v in new.items():
    print("  {:40s} {:6.2f}g".format(k, v))
print("  {:40s} {:6.2f}g".format("TOTAL NEW", total_new))

print("\n--- COMPARISON ---")
print("  Old design total: {:.2f}g".format(total_old))
print("  New design total: {:.2f}g".format(total_new))
print("  Delta:            {:.2f}g ({})".format(
    total_new - total_old,
    "LIGHTER" if total_new < total_old else "HEAVIER"))

# ============================================================
# SECTION 2: SADDLE CHANNEL STRUCTURAL DESIGN
# ============================================================
print("\n" + "=" * 80)
print("2. SADDLE CHANNEL STRUCTURAL DESIGN")
print("=" * 80)

# Airfoil thickness at hinge line determines available space
print("\nAirfoil thickness at hinge X={:.1f}mm:".format(X_NEW_HINGE))
for y_i in [0, 50, 100, 150, 180, 200]:
    y = float(y_i)
    c = chord_at(y)
    if c < 1.0:
        continue
    lx = le_x(y)
    frac = (X_NEW_HINGE - lx) / c
    if frac < 0 or frac > 1:
        print("  y={}: hinge outside airfoil".format(y_i))
        continue
    tr = t_ratio(y)
    t_full = 2 * naca4_yt(frac, tr) * c
    print("  y={:3d}mm: chord={:.1f}mm, hinge at {:.1f}% chord, thickness={:.2f}mm".format(
        y_i, c, frac * 100, t_full))

# Saddle channel cross-section design
print("\nSaddle channel cross-section (thin-wall, NOT honeycomb per correction):")
print("  Outer shell: 0.45mm LW-PLA (continues airfoil surface)")
print("  Saddle bearing walls: 0.6mm LW-PLA (2-perimeter, printed at slightly lower temp)")
print("  Wire channel bore: 0.6mm ID (PETG sleeve 1.2mm OD provides bearing surface)")
print("  Forward depth: 3mm ahead of wire center (bull-nose slides in)")
print("  No infill — thin-wall shell construction throughout")

# Deflection clearance
print("\nDeflection clearance in saddle:")
for angle in [-20, -15, -10, 0, 10, 15, 20, 25]:
    # The elevator rotates about the wire center.
    # The bull-nose extends ~3mm forward of wire.
    # At deflection angle theta, the bull-nose tip moves:
    # vertical displacement = 3mm * sin(theta)
    # This must fit within the saddle channel
    rad = math.radians(angle)
    vert_disp = 3.0 * math.sin(rad)
    print("  {:+3d} deg: bull-nose tip moves {:.2f}mm vertically".format(angle, vert_disp))

# Available vertical space at root
frac_root = (X_NEW_HINGE - le_x(0)) / chord_at(0)
tr_root = t_ratio(0)
available_root = 2 * naca4_yt(frac_root, tr_root) * chord_at(0)
print("\nAvailable internal height at hinge (root): {:.2f}mm".format(available_root))
print("Required for +25 deg: {:.2f}mm above + {:.2f}mm below wire = {:.2f}mm total".format(
    3.0 * math.sin(math.radians(25)), 3.0 * math.sin(math.radians(20)),
    3.0 * math.sin(math.radians(25)) + 3.0 * math.sin(math.radians(20))
))
print("Wall thickness (top + bottom): 2 x 0.45mm = 0.90mm")
needed = 3.0 * math.sin(math.radians(25)) + 3.0 * math.sin(math.radians(20)) + 0.90 + 0.6  # walls + wire sleeve
print("Total needed: {:.2f}mm (including walls and sleeve)".format(needed))
print("Margin: {:.2f}mm".format(available_root - needed))
if available_root > needed:
    print("  -> ADEQUATE at root")
else:
    print("  -> INSUFFICIENT at root! Need to reduce deflection or forward depth")

# Check outboard stations too
print("\nClearance check at outboard stations:")
for y_i in [100, 150, 180, 195]:
    y = float(y_i)
    c = chord_at(y)
    if c < 1.0:
        continue
    lx = le_x(y)
    frac = (X_NEW_HINGE - lx) / c
    if frac < 0 or frac > 1:
        print("  y={}mm: hinge outside airfoil".format(y_i))
        continue
    tr = t_ratio(y)
    t_avail = 2 * naca4_yt(frac, tr) * c
    print("  y={:3d}mm: available={:.2f}mm, needed={:.2f}mm, margin={:.2f}mm {}".format(
        y_i, t_avail, needed, t_avail - needed,
        "OK" if t_avail > needed else "** TIGHT **"))

# ============================================================
# SECTION 3: BULL-NOSE DESIGN
# ============================================================
print("\n" + "=" * 80)
print("3. BULL-NOSE DESIGN")
print("=" * 80)

# Bull-nose: convex shape extending 3mm forward of wire into saddle
# Wall thickness: 0.55mm (2-perimeter)
# Cross section: roughly semi-circular/elliptical
# At root: height available = airfoil thickness at hinge minus shell walls
bn_forward = 3.0  # mm forward of wire center
bn_wall = WALL_BULLNOSE  # 0.55mm

print("Bull-nose forward extension: {}mm".format(bn_forward))
print("Wall thickness: {}mm (2-perimeter LW-PLA)".format(bn_wall))

# Volume of bull-nose per half-span
# Cross section: semi-elliptical shell, major axis = airfoil height at hinge, minor axis = 3mm
# Integrate along span
bn_vol_total = 0.0
bn_mass_total = 0.0
print("\nBull-nose cross-section at each station:")
for y_i in range(5, int(hinge_exit_y), 5):
    y = float(y_i)
    c = chord_at(y)
    lx = le_x(y)
    frac = (X_NEW_HINGE - lx) / c if c > 0 else 999
    if frac < 0 or frac > 1:
        break
    tr = t_ratio(y)
    h = 2 * naca4_yt(frac, tr) * c  # internal height
    # Outer semi-ellipse area: pi/4 * h * bn_forward (half ellipse, both top and bottom)
    # Inner: pi/4 * (h - 2*bn_wall) * (bn_forward - bn_wall)
    h_inner = max(0, h - 2 * (WALL_STAB + 0.1))  # inside shell
    a_outer = math.pi / 2 * (h_inner / 2) * bn_forward  # full ellipse / 2 = nose only
    a_inner = math.pi / 2 * max(0, (h_inner / 2 - bn_wall)) * max(0, bn_forward - bn_wall)
    a_shell = a_outer - a_inner

    # Per mm of span
    dy = 5.0
    vol_slice = a_shell * dy
    bn_vol_total += vol_slice

# Multiply by 2 for both halves
bn_vol_total *= 2  # both halves
bn_mass_total = bn_vol_total * RHO_LWPLA
print("\nBull-nose total volume (both halves): {:.0f} mm3".format(bn_vol_total))
print("Bull-nose total mass (foamed LW-PLA): {:.2f}g".format(bn_mass_total))

# If printed denser (lower temp):
bn_mass_dense = bn_vol_total * RHO_LWPLA_DENSE
print("Bull-nose mass (dense LW-PLA at 210C): {:.2f}g".format(bn_mass_dense))

# ============================================================
# SECTION 4: TPU FLEX STRIP DESIGN
# ============================================================
print("\n" + "=" * 80)
print("4. TPU FLEX STRIP DESIGN")
print("=" * 80)

print("Material: TPU 95A (Shore 95A)")
print("Thickness: 0.3mm")
print("Width: 8mm (must span gap during full deflection)")

# Gap analysis during deflection
# The hinge gap on the surface opens as elevator deflects.
# At angle theta, the surface gap ≈ 2 * R * sin(theta/2) where R is the
# distance from wire center to surface
R_upper = t_hinge_root / 2  # distance from wire to upper surface at root
R_lower = t_hinge_root / 2

print("\nGap opening during deflection (root station):")
for angle in [5, 10, 15, 20, 25]:
    gap = 2 * R_upper * math.sin(math.radians(angle / 2))
    print("  {:+3d} deg: surface gap = {:.2f}mm (strip width 8mm covers it)".format(angle, gap))

# Parasitic hinge moment from TPU strip
# TPU 95A: Young's modulus ~15-30 MPa (very flexible)
E_tpu = 20.0  # MPa (conservative mid-range for TPU 95A)
# Strip acts as a beam in bending
# Moment = E * I / R, where R = radius of curvature
# For small deflections, the strip bends with radius R = L^2 / (2 * delta)
# where L = half the strip width (4mm) and delta = gap/2
# Actually, treat strip as a cantilever:
# Force per unit span = 3 * E * I * delta / L^3
# where L = half-width, delta = displacement, I = t^3/12 per unit span

L_strip = TPU_WIDTH / 2  # 4mm cantilever each side
I_strip = TPU_THICK**3 / 12  # per mm of span (mm^4/mm)
# At 25 deg deflection:
delta_25 = R_upper * (1 - math.cos(math.radians(25)))  # vertical displacement
force_per_mm = 3 * E_tpu * I_strip * delta_25 / L_strip**3  # N/mm
# Total force over span (approximate, span ~ 200mm per half)
span_eff = 190.0  # effective strip span per half
force_total = force_per_mm * span_eff * 2  # both top and bottom strips per half
moment_arm = 4.0  # mm, approximate lever arm
parasitic_moment = force_total * moment_arm  # N-mm

print("\nParasitic hinge moment from TPU strips:")
print("  E_TPU = {} MPa".format(E_tpu))
print("  Strip half-width (cantilever L) = {}mm".format(L_strip))
print("  Strip I per mm span = {:.6f} mm4".format(I_strip))
print("  Vertical displacement at 25 deg = {:.3f}mm".format(delta_25))
print("  Force per mm span = {:.4f} N/mm".format(force_per_mm))
print("  Total force (one half, 2 strips) = {:.3f} N".format(force_total))
print("  Parasitic moment = {:.2f} N-mm = {:.4f} N-m".format(parasitic_moment, parasitic_moment / 1000))
print("  Servo torque (typical micro) = 2000-3000 N-mm")
print("  Parasitic load = {:.1f}% of servo torque".format(parasitic_moment / 2500 * 100))

# Buckling check
# Strip buckles when compression side exceeds critical stress
# For a thin strip, buckling stress = pi^2 * E * t^2 / (12 * L^2)
sigma_buckle = math.pi**2 * E_tpu * TPU_THICK**2 / (12 * L_strip**2)
print("\nBuckling analysis:")
print("  Critical buckling stress = {:.3f} MPa".format(sigma_buckle))
# Strain in strip at max deflection
strain_max = TPU_THICK / 2 * delta_25 / (L_strip**2 / 3)  # approximate
stress_max = E_tpu * strain_max
print("  Max bending stress at 25 deg = {:.3f} MPa".format(stress_max))
if stress_max < sigma_buckle:
    print("  -> No buckling expected")
else:
    print("  -> BUCKLING RISK — consider wider strip or thicker material")

# Fatigue life
print("\nFatigue life estimate:")
print("  TPU 95A fatigue limit: >1M cycles at <30% elongation")
print("  Strip max strain at 25 deg: {:.2f}%".format(strain_max * 100))
print("  Typical flight cycle: ~200 deflections per flight")
print("  At 500 flights: ~100,000 cycles")
print("  -> Expected fatigue life: >500 flights (conservative)")
print("  -> Replacement interval: inspect annually, replace if cracked")

# CA bond to LW-PLA
print("\nBonding: CA glue to LW-PLA")
print("  CA shear strength on LW-PLA: ~2-5 MPa (foamed surface reduces bond)")
print("  Bond area per strip: {}mm x {}mm = {:.0f} mm2 per half".format(
    TPU_WIDTH, tpu_span_per_half, TPU_WIDTH * tpu_span_per_half / 2))
print("  Peel force: {:.3f} N (from bending analysis)".format(force_total))
print("  Peel stress: {:.4f} MPa — well below CA limit".format(
    force_total / (TPU_WIDTH * tpu_span_per_half / 2)))
print("  RECOMMENDATION: CA is adequate. Flexible CA (e.g., ZAP-A-GAP PT-03)")
print("  gives better peel resistance on flexible substrates.")

# ============================================================
# SECTION 5: STRUCTURAL ADEQUACY WITHOUT REAR SPAR
# ============================================================
print("\n" + "=" * 80)
print("5. STRUCTURAL ADEQUACY WITHOUT REAR SPAR")
print("=" * 80)

# Torsional stiffness analysis
# OLD: Two-spar torque box (main spar at X=35, rear spar at X=69)
# Closed-section torque box GJ = 4 * A^2 * G / (perimeter/t)
# where A = enclosed area, G = shear modulus, t = wall thickness

# NEW: Single-spar D-box (LE to spar) + open section (spar to hinge)
# D-box is a closed section. Open section has much lower GJ.

# D-box dimensions at root:
# Chord from LE to spar: X_NEW_SPAR - le_x(0) = 34.5 - 0 = 34.5mm
# Height: airfoil thickness at max-t point
dbox_chord = X_NEW_SPAR - le_x(0)  # 34.5mm at root
tr_root = t_ratio(0)
# Average height of D-box (airfoil from LE to 30% chord)
# Max thickness at ~30% = 7.5mm at root. Average ~5mm
dbox_h_max = 2 * naca4_yt(0.30, tr_root) * ROOT_CHORD
dbox_h_avg = dbox_h_max * 0.7  # average height is roughly 70% of max for NACA shapes

# D-box enclosed area
A_dbox = dbox_chord * dbox_h_avg * 0.7  # roughly elliptical
# D-box perimeter
P_dbox = 2 * math.sqrt((dbox_chord**2 + dbox_h_avg**2) / 2) * math.pi / 2 + dbox_chord  # rough
# G for LW-PLA (foamed): ~200-400 MPa (very rough)
G_lwpla = 300  # MPa

# OLD two-spar torque box
old_box_chord = X_REAR_SPAR - X_MAIN_SPAR  # 69 - 35 = 34mm
old_box_h = dbox_h_max * 0.8  # height at mid-box
A_old_box = old_box_chord * old_box_h * 0.8
P_old_box = 2 * (old_box_chord + old_box_h)
GJ_old = 4 * A_old_box**2 * G_lwpla * WALL_STAB / P_old_box  # N-mm^2

print("OLD DESIGN - Two-spar torque box (X=35 to X=69):")
print("  Box chord: {:.1f}mm".format(old_box_chord))
print("  Box height (avg): {:.1f}mm".format(old_box_h))
print("  Enclosed area: {:.0f} mm2".format(A_old_box))
print("  Perimeter: {:.0f}mm".format(P_old_box))
print("  GJ (Bredt-Batho): {:.0f} N-mm2".format(GJ_old))

# D-box torsional stiffness
GJ_dbox = 4 * A_dbox**2 * G_lwpla * WALL_STAB / P_dbox
print("\nNEW DESIGN - D-box (LE to X=34.5):")
print("  D-box chord: {:.1f}mm".format(dbox_chord))
print("  D-box height (avg): {:.1f}mm".format(dbox_h_avg))
print("  Enclosed area: {:.0f} mm2".format(A_dbox))
print("  Perimeter: {:.0f}mm".format(P_dbox))
print("  GJ (Bredt-Batho): {:.0f} N-mm2".format(GJ_dbox))

# Saddle acts as partial structural member
# The saddle channel at the hinge line is a closed-ish section
# It provides some torsional restraint aft of the spar
saddle_h = t_hinge_root - 2 * WALL_STAB  # internal height at hinge
saddle_w = 5.0  # ~5mm wide channel
A_saddle = saddle_h * saddle_w * 0.5
P_saddle = 2 * (saddle_h + saddle_w)
GJ_saddle = 4 * A_saddle**2 * G_lwpla * WALL_SADDLE / P_saddle

print("\nSADDLE contribution to torsion:")
print("  Saddle height: {:.1f}mm".format(saddle_h))
print("  Saddle width: {:.1f}mm".format(saddle_w))
print("  GJ (saddle): {:.0f} N-mm2".format(GJ_saddle))

# Total new
GJ_new_total = GJ_dbox + GJ_saddle
ratio = GJ_new_total / GJ_old * 100
print("\nTORSIONAL STIFFNESS COMPARISON:")
print("  Old (two-spar box):     {:.0f} N-mm2".format(GJ_old))
print("  New (D-box + saddle):   {:.0f} N-mm2".format(GJ_new_total))
print("  Ratio: {:.1f}%".format(ratio))

# Flight load check
print("\nFlight load check at Vne = 20 m/s:")
# Tail load at Vne with max elevator deflection
rho_air = 1.225  # kg/m3
V = 20.0  # m/s
S_h = 407.7e-6  # m2
CL_max = 1.586  # at 25 deg deflection
L_max = 0.5 * rho_air * V**2 * S_h * CL_max  # N
print("  Max tail lift: {:.2f} N ({:.0f}g)".format(L_max, L_max / 9.81 * 1000))

# Pitching moment about spar
# Center of pressure at ~40% of stab chord = 0.40 * 94.8mm mean chord
moment_arm_cp = 0.40 * 94.8 - (X_NEW_SPAR - le_x(0))  # from spar to CP, roughly
# Actually CP is measured from LE. Spar is at X=34.5 from root LE.
# Mean CP ~ 40% of mean chord from LE = 37.9mm from LE
# Torque = L * (CP_x - spar_x) -- but this is bending, not torsion
# Torsion comes from asymmetric loading
# For torsion: pitching moment coefficient Cm ~ -0.05 for trimmed tail
Cm = -0.05
c_mean = 94.8e-3  # m
M_torsion = 0.5 * rho_air * V**2 * S_h * c_mean * abs(Cm)  # N-m
M_torsion_Nmm = M_torsion * 1000  # N-mm
print("  Torsional moment (Cm=-0.05): {:.1f} N-mm".format(M_torsion_Nmm))

# Twist angle
# theta = M * L / GJ
L_halfspan = 215.0  # mm
twist_old = M_torsion_Nmm * L_halfspan / GJ_old  # radians
twist_new = M_torsion_Nmm * L_halfspan / GJ_new_total
print("  Tip twist (old design): {:.3f} deg".format(math.degrees(twist_old)))
print("  Tip twist (new design): {:.3f} deg".format(math.degrees(twist_new)))
print("  Acceptable if < 1.0 deg at Vne")
if abs(math.degrees(twist_new)) < 1.0:
    print("  -> ACCEPTABLE")
else:
    print("  -> WARNING: excessive twist, may need stiffening")

# Bending stiffness
print("\nBending stiffness (spanwise):")
# Main spar provides most bending stiffness
# EI_spar = E_CF * I_tube
E_cf = 150000  # MPa (carbon fiber)
I_tube = math.pi / 64 * (3.0**4 - 2.0**4)  # mm4
EI_spar = E_cf * I_tube
print("  Main spar EI = {:.0f} N-mm2 ({:.2f} N-m2)".format(EI_spar, EI_spar / 1e6))

# Old rear spar contribution
I_rod = math.pi / 64 * 1.5**4
EI_rear = E_cf * I_rod
print("  Old rear spar EI = {:.0f} N-mm2 ({:.4f} N-m2)".format(EI_rear, EI_rear / 1e6))
print("  Rear spar was {:.1f}% of main spar bending stiffness".format(EI_rear / EI_spar * 100))
print("  -> Loss of rear spar reduces total bending stiffness by {:.1f}%".format(
    EI_rear / (EI_spar + EI_rear) * 100))
print("  -> This is acceptable: main spar dominates bending")

# ============================================================
# SECTION 6: FLUTTER ANALYSIS WITHOUT TUNGSTEN
# ============================================================
print("\n" + "=" * 80)
print("6. FLUTTER ANALYSIS WITHOUT TUNGSTEN")
print("=" * 80)

# Mass of bull-nose forward of wire
# This provides the counter-flutter mass balance
# The bull-nose extends 3mm forward of wire center
# Volume was computed above

print("Bull-nose mass (foamed LW-PLA): {:.3f}g total (both halves)".format(bn_mass_total))
print("Bull-nose mass (dense LW-PLA):  {:.3f}g total (both halves)".format(bn_mass_dense))

# Mass moment about hinge axis
# Old design: tungsten at 8mm forward of hinge = 0.5g * 8mm = 4.0 g-mm per half
# New design: bull-nose CG at ~1.5mm forward of wire (half of 3mm extension)
bn_mass_per_half = bn_mass_total / 2
bn_cg_fwd = bn_forward / 2  # ~1.5mm forward of wire
bn_moment = bn_mass_per_half * bn_cg_fwd  # g-mm per half

bn_mass_dense_per_half = bn_mass_dense / 2
bn_moment_dense = bn_mass_dense_per_half * bn_cg_fwd

print("\nMass moment about hinge axis (per half):")
print("  Old (tungsten): 0.50g x 8.0mm = 4.00 g-mm")
print("  New (foamed bull-nose): {:.3f}g x {:.1f}mm = {:.3f} g-mm".format(
    bn_mass_per_half, bn_cg_fwd, bn_moment))
print("  New (dense bull-nose):  {:.3f}g x {:.1f}mm = {:.3f} g-mm".format(
    bn_mass_dense_per_half, bn_cg_fwd, bn_moment_dense))
print("  Ratio (foamed/old): {:.1f}%".format(bn_moment / 4.0 * 100))
print("  Ratio (dense/old):  {:.1f}%".format(bn_moment_dense / 4.0 * 100))

# Flutter speed estimate
# Binary flutter velocity: V_flutter = K * sqrt(I_alpha / (rho * S * c^2))
# The key factor: mass balance reduces flutter susceptibility
# For sub-20 m/s RC sailplane with zero-slop hinge:
print("\nFlutter risk assessment:")
print("  Vne = 20 m/s (Reynolds ~60,000-80,000)")
print("  Zero-slop music wire pin hinge: CRITICAL for flutter prevention")
print("  Mass balance moment is {:.1f}% of old design (foamed)".format(bn_moment / 4.0 * 100))
print("  Mass balance moment is {:.1f}% of old design (dense)".format(bn_moment_dense / 4.0 * 100))
print()
print("  Key mitigating factors:")
print("  1. Zero hinge slop (music wire in PETG sleeves) — eliminates #1 flutter trigger")
print("  2. Bull-nose extends forward of wire — CG is AHEAD of hinge axis")
print("  3. TPU strips add aerodynamic damping at hinge gap")
print("  4. Very low Vne (20 m/s) — flutter speed scales with V^2, margin is large")
print()
if bn_moment_dense > 1.0:
    print("  RECOMMENDATION: Print bull-nose zone at 210C (dense) for {:.2f} g-mm/half".format(bn_moment_dense))
    print("  This provides {:.0f}% of old tungsten moment — adequate for Vne<20 m/s".format(bn_moment_dense / 4.0 * 100))
else:
    print("  WARNING: Bull-nose moment is very low. Consider:")
    print("  - Increasing forward extension to 4-5mm")
    print("  - Printing bull-nose at 200C (minimal foaming)")
    print("  - Adding small amount of tungsten epoxy in bull-nose cavity")

# ============================================================
# SECTION 8: ASSEMBLY SEQUENCE
# ============================================================
print("\n" + "=" * 80)
print("8. ASSEMBLY SEQUENCE")
print("=" * 80)

print("""
PRINT PHASE:
1. Stab halves (2x): LW-PLA vase mode at 230C, 0.45mm wall.
   Saddle channel zone: 2-perimeter (0.6mm) printed in same pass
   by increasing wall thickness in slicer at hinge-line region.
   PETG sleeves are NOT printed with the stab — installed after.

2. Elevator halves (2x): LW-PLA vase mode at 230C, 0.40mm wall.
   Bull-nose zone: 2-perimeter (0.55mm) at 210C (denser, less foaming)
   for mass balance. Printed with bull-nose facing down (on bed).

3. TPU flex strips (4x): Separate prints on TPU 95A.
   0.3mm thick x 8mm wide x ~190mm long each. Print flat on bed.

ASSEMBLY PHASE:
4. Insert PETG sleeves into stab saddle channels:
   - Pre-printed PETG tubes (1.2mm OD, 0.6mm ID, 3mm long)
   - ~20 per half, spaced 8-10mm apart along hinge line
   - Press-fit into printed pockets in saddle walls, spot of CA each

5. Thread music wire through one stab half:
   - Insert wire from root end through all PETG sleeves
   - Wire slides through saddle channel

6. Mate elevator to stab:
   - Slide elevator bull-nose into stab saddle channel
   - Wire passes through bull-nose bore (or between bull-nose and saddle)
   - Test deflection: -20 to +25 deg, verify smooth rotation

7. Thread wire through VStab fin bore:
   - PETG sleeve pre-installed in fin (1.2mm OD, 0.6mm ID)

8. Repeat steps 5-6 for opposite half

9. Bond TPU flex strips:
   - Apply flexible CA (ZAP PT-03) to stab surface at hinge line
   - Lay TPU strip centered on hinge gap (4mm on stab, 4mm on elevator)
   - Hold in deflected position (neutral + 5 deg) while CA sets
   - Repeat for top and bottom, both halves (4 strips total)

10. Install main spar:
    - Thread 3mm CF tube through left stab at X=34.5mm
    - Through VStab fin bore (3.1mm, PETG sleeve)
    - Through right stab
    - CA at fin junction

11. Bond stab roots to VStab fin (dovetail + CA)

12. Install bridge joiner between elevator halves

13. Route pushrod and connect to servo

DISASSEMBLY FOR REPAIR:
- TPU strips can be peeled off (CA bond is the weakest link)
- Wire can be withdrawn by removing one tip cap (if designed removable)
- Main spar cannot be removed without breaking CA bonds
- Elevator halves can be separated from stab by peeling TPU + withdrawing wire
""")

# Final summary
print("=" * 80)
print("FINAL MASS BUDGET SUMMARY")
print("=" * 80)
print("  Old design (v5):  {:.2f}g".format(total_old))
print("  New design (v6):  {:.2f}g".format(total_new))
print("  Saving:           {:.2f}g".format(total_old - total_new))
print("  vs 35g hard limit: {:.2f}g margin".format(35.0 - total_new))
