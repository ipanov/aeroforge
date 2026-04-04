"""
HStab Round 4 Aerodynamic Analysis
===================================
Evaluates: optimal spar position, optimal hinge position, elevator performance.
"""
import math
import sys

sys.path.insert(0, "scripts")
from hstab_geometry import (
    ROOT_CHORD, HALF_SPAN, N_EXP, REF_FRAC, REF_X,
    X_MAIN_SPAR, X_REAR_SPAR, X_HINGE, X_STIFF,
    T_ROOT, T_TIP, TE_TRUNC,
    chord_at, le_x, te_x, t_ratio, naca4_yt, elev_chord_at,
)


def flap_tau(cf_ratio):
    """Thin-airfoil theory flap effectiveness."""
    cf_ratio = max(0.001, min(cf_ratio, 0.999))
    theta_f = math.acos(1.0 - 2.0 * cf_ratio)
    return 1.0 - (theta_f - math.sin(theta_f)) / math.pi


def elevator_area(hinge_x):
    """Compute elevator and stab areas (both halves) for a given hinge X."""
    elev = 0
    stab = 0
    dy = 0.25
    y = 0
    while y <= HALF_SPAN:
        c = chord_at(y)
        if c <= 0:
            y += dy
            continue
        lx = le_x(y)
        te = lx + c * TE_TRUNC
        ec = max(0, te - hinge_x)
        sc = c * TE_TRUNC - ec
        elev += ec * dy
        stab += sc * dy
        y += dy
    return elev * 2, stab * 2  # both halves


def hinge_exit_y(hinge_x):
    """Find span station where hinge exits the TE."""
    for yi in range(0, 430):
        y = yi * 0.5
        if y > HALF_SPAN:
            return HALF_SPAN
        c = chord_at(y)
        if c <= 0:
            return y
        lx = le_x(y)
        te = lx + c * TE_TRUNC
        if hinge_x >= te:
            return y - 0.5
    return HALF_SPAN


def spar_exit_y(spar_x):
    """Find span where spar exits the planform (LE passes it)."""
    for y in range(0, 430):
        yf = y * 0.5
        c = chord_at(yf)
        if c <= 0:
            return yf
        lx = le_x(yf)
        if spar_x < lx:
            return yf - 0.5
    return HALF_SPAN


def spar_tube_max_y(spar_x, tube_od=3.1):
    """Find max span where airfoil is thick enough for tube."""
    last_ok = 0
    for yi in range(0, 430):
        y = yi * 0.5
        c = chord_at(y)
        if c <= 0:
            break
        lx = le_x(y)
        if spar_x < lx or spar_x > lx + c:
            break
        xc_local = (spar_x - lx) / c
        tr = t_ratio(y)
        yt_half = naca4_yt(xc_local, tr) * c
        thickness = 2 * yt_half
        if thickness >= tube_od:
            last_ok = y
    return last_ok


# ============================================================
print("=" * 80)
print("TASK 1: OPTIMAL MAIN SPAR POSITION")
print("=" * 80)

# Find NACA 4-digit max thickness chord fraction
best_xc = 0
best_yt = 0
for i in range(1, 10000):
    xc = i / 10000.0
    yt = naca4_yt(xc, 1.0)
    if yt > best_yt:
        best_yt = yt
        best_xc = xc

print(f"NACA 4-digit max thickness at chord fraction: {best_xc:.4f}")
print(f"Normalized half-thickness at max: {best_yt:.5f}")
print(f"  (Full thickness at t/c=6.5%: {2*best_yt*0.065*100:.2f}% of chord)")

spar_x_optimal = best_xc * ROOT_CHORD
print(f"\nOptimal spar X at root: {spar_x_optimal:.2f}mm ({best_xc*100:.2f}% of {ROOT_CHORD}mm)")
print(f"Current v5 spar X: {X_MAIN_SPAR}mm ({X_MAIN_SPAR/ROOT_CHORD*100:.1f}%)")
print(f"Difference: {spar_x_optimal - X_MAIN_SPAR:.2f}mm")

# Spar fit analysis
print("\n--- Tube fit: 3mm OD tube (3.1mm bore) ---")
for sx in [spar_x_optimal, X_MAIN_SPAR]:
    max_y = spar_tube_max_y(sx, 3.1)
    exit_y = spar_exit_y(sx)
    print(f"  Spar X={sx:.1f}mm: tube fits to y={max_y:.0f}mm, exits planform at y={exit_y:.0f}mm")

# Detailed thickness at spar position
print(f"\n--- Thickness at optimal spar X={spar_x_optimal:.1f}mm ---")
for y in [0, 50, 100, 150, 170, 180, 185, 186, 187, 188, 189, 190, 192, 195, 200]:
    c = chord_at(y)
    if c <= 0:
        continue
    lx = le_x(y)
    if spar_x_optimal < lx or spar_x_optimal > lx + c:
        print(f"  y={y:3d}: EXITS (LE={lx:.1f})")
        break
    xc_local = (spar_x_optimal - lx) / c
    tr = t_ratio(y)
    yt_half = naca4_yt(xc_local, tr) * c
    thickness = 2 * yt_half
    status = "OK" if thickness >= 3.1 else "THIN"
    print(f"  y={y:3d}: chord={c:6.1f}, xc_local={xc_local:.3f}, thickness={thickness:.2f}mm [{status}]")


# ============================================================
print("\n" + "=" * 80)
print("TASK 2: HINGE LINE COMPARISON")
print("=" * 80)

hinge_candidates = [74.75, 65.0, 63.0, 60.0, 57.5, 55.0]

print(f"\n{'Hinge_X':>8} {'Gap_mm':>7} {'Root_ec':>8} {'Root_%':>7} {'Tau':>6} "
      f"{'Elev_cm2':>9} {'Ratio%':>7} {'Exit_y':>7} "
      f"{'Cruise':>7} {'Thermal':>8} {'Flare':>7}")

for hx in hinge_candidates:
    gap = hx - spar_x_optimal
    root_ec = ROOT_CHORD * TE_TRUNC - hx
    root_pct = root_ec / ROOT_CHORD * 100
    tau = flap_tau(root_ec / (ROOT_CHORD * TE_TRUNC))
    ea, sa = elevator_area(hx)
    total = ea + sa
    ratio = ea / total * 100
    exit_y = hinge_exit_y(hx)

    cl_per_deg = 2 * math.pi * tau * math.pi / 180
    d_cruise = 0.178 / cl_per_deg if cl_per_deg > 0 else 999
    d_thermal = 0.50 / cl_per_deg if cl_per_deg > 0 else 999
    d_flare = 0.80 / cl_per_deg if cl_per_deg > 0 else 999

    tag = " <-- v5" if hx == 74.75 else ""
    print(f"{hx:8.2f} {gap:7.1f} {root_ec:8.1f} {root_pct:6.1f}% {tau:6.3f} "
          f"{ea/100:9.1f} {ratio:6.1f}% {exit_y:7.0f} "
          f"{d_cruise:6.1f}d {d_thermal:7.1f}d {d_flare:6.1f}d{tag}")


# ============================================================
print("\n" + "=" * 80)
print("TASK 3: DETAILED ANALYSIS - RECOMMENDED HINGE AT X=60mm")
print("=" * 80)

HINGE_REC = 60.0
SPAR_REC = spar_x_optimal

print(f"\nMain spar: X={SPAR_REC:.1f}mm ({SPAR_REC/ROOT_CHORD*100:.1f}% root chord)")
print(f"Hinge wire: X={HINGE_REC}mm ({HINGE_REC/ROOT_CHORD*100:.1f}% root chord)")
print(f"Gap spar-to-hinge: {HINGE_REC - SPAR_REC:.1f}mm")
print(f"No rear spar, no stiffener")

# Detailed chord table
print(f"\n{'y':>5} {'Chord':>7} {'LE_x':>7} {'Spar(rel)':>10} {'Spar%':>6} "
      f"{'Hinge(rel)':>11} {'Hinge%':>7} {'TE_x':>7} {'Elev_c':>7} {'Elev%':>6}")

stations = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120,
            130, 140, 150, 160, 170, 180, 186, 190, 195, 200, 205, 210, 214]

for y in stations:
    c = chord_at(y)
    if c <= 0:
        print(f"{y:5d}  (closed)")
        continue
    lx = le_x(y)
    te = lx + c * TE_TRUNC

    # Spar
    if SPAR_REC >= lx and SPAR_REC <= lx + c:
        sr = SPAR_REC - lx
        sp = sr / c * 100
        spar_s = f"{sr:5.1f}"
        sp_s = f"{sp:5.1f}%"
    else:
        spar_s = " exits"
        sp_s = "  --  "

    # Hinge
    if HINGE_REC >= lx and HINGE_REC <= te:
        hr = HINGE_REC - lx
        hp = hr / c * 100
        hinge_s = f"{hr:6.1f}"
        hp_s = f"{hp:5.1f}%"
    else:
        hinge_s = "  exits"
        hp_s = "  --  "

    # Elevator
    ec = max(0, te - HINGE_REC)
    ep = ec / c * 100 if c > 0 else 0

    print(f"{y:5d} {c:7.1f} {lx:7.2f} {spar_s:>10} {sp_s:>6} "
          f"{hinge_s:>11} {hp_s:>7} {te:7.2f} {ec:7.1f} {ep:5.1f}%")

# Areas
ea_new, sa_new = elevator_area(HINGE_REC)
total_new = ea_new + sa_new
ea_v5, sa_v5 = elevator_area(X_HINGE)
total_v5 = ea_v5 + sa_v5

print(f"\n--- Area Summary ---")
print(f"                    V5 (hinge@74.75)    New (hinge@60.0)")
print(f"  Elevator area:    {ea_v5/100:7.1f} cm2         {ea_new/100:7.1f} cm2  ({(ea_new-ea_v5)/ea_v5*100:+.1f}%)")
print(f"  Stab area:        {sa_v5/100:7.1f} cm2         {sa_new/100:7.1f} cm2")
print(f"  Total area:       {total_v5/100:7.1f} cm2         {total_new/100:7.1f} cm2")
print(f"  Elev/Total:       {ea_v5/total_v5*100:5.1f}%              {ea_new/total_new*100:5.1f}%")

# Flap effectiveness
root_ec_new = ROOT_CHORD * TE_TRUNC - HINGE_REC
tau_new = flap_tau(root_ec_new / (ROOT_CHORD * TE_TRUNC))
root_ec_v5 = ROOT_CHORD * TE_TRUNC - X_HINGE
tau_v5 = flap_tau(root_ec_v5 / (ROOT_CHORD * TE_TRUNC))

print(f"\n--- Flap Effectiveness ---")
print(f"  V5:  root elev chord = {root_ec_v5:.1f}mm, tau = {tau_v5:.3f}")
print(f"  New: root elev chord = {root_ec_new:.1f}mm, tau = {tau_new:.3f}")

# Required deflections
print(f"\n--- Required Deflections ---")
cl_targets = [("Cruise CL=0.178", 0.178), ("Thermal CL=0.50", 0.50), ("Flare CL=0.80", 0.80)]

for label, cl in cl_targets:
    for name, tau_val in [("V5", tau_v5), ("New", tau_new)]:
        cl_per_deg = 2 * math.pi * tau_val * math.pi / 180
        defl = cl / cl_per_deg
        print(f"  {label}: {name} = {defl:.1f} deg")


# ============================================================
print("\n" + "=" * 80)
print("TASK 4: COMPREHENSIVE CHORD TABLE (NEW DESIGN)")
print("=" * 80)

print(f"\nSpar X={SPAR_REC:.1f}mm | Hinge X={HINGE_REC}mm | No rear spar | No stiffener")
spar_tube_y = spar_tube_max_y(SPAR_REC, 3.1)
spar_exit = spar_exit_y(SPAR_REC)
hinge_exit = hinge_exit_y(HINGE_REC)
print(f"Spar tube fits to: y={spar_tube_y:.0f}mm")
print(f"Spar exits planform: y={spar_exit:.0f}mm")
print(f"Hinge exits TE: y={hinge_exit:.0f}mm")

print(f"\n| y (mm) | Chord | LE_x | Spar X={SPAR_REC:.0f} | Hinge X={HINGE_REC:.0f} | TE_x | Elev chord |")
print(f"|--------|-------|------|----------|-----------|------|------------|")

for y in stations:
    c = chord_at(y)
    if c <= 0:
        print(f"| {y:3d}    | 0     | --   | --       | --        | --   | --         |")
        continue
    lx = le_x(y)
    te = lx + c * TE_TRUNC

    if SPAR_REC >= lx and SPAR_REC <= lx + c:
        sp = (SPAR_REC - lx) / c * 100
        spar_s = f"{SPAR_REC - lx:.1f} ({sp:.0f}%)"
    else:
        spar_s = "exits"

    if HINGE_REC >= lx and HINGE_REC <= te:
        hp = (HINGE_REC - lx) / c * 100
        hinge_s = f"{HINGE_REC - lx:.1f} ({hp:.0f}%)"
    else:
        hinge_s = "exits"

    ec = max(0, te - HINGE_REC)
    if ec > 0:
        ep = ec / c * 100
        ec_s = f"{ec:.1f} ({ep:.0f}%)"
    else:
        ec_s = "0"

    print(f"| {y:3d}    | {c:.1f} | {lx:.2f} | {spar_s:<8s} | {hinge_s:<9s} | {te:.2f} | {ec_s:<10s} |")


# ============================================================
print("\n" + "=" * 80)
print("TASK 5: TIP CLOSURE ANALYSIS")
print("=" * 80)

print("\n--- Stab shell extent (LE to hinge) at outboard stations ---")
for y in range(190, 215):
    c = chord_at(y)
    if c <= 0:
        print(f"  y={y}: closed")
        continue
    lx = le_x(y)
    te = lx + c * TE_TRUNC
    stab_chord = min(HINGE_REC, te) - lx if HINGE_REC > lx else 0
    elev_chord = max(0, te - HINGE_REC)
    stab_pct = stab_chord / c * 100 if c > 0 else 0

    print(f"  y={y:3d}: chord={c:5.1f}, stab_shell={stab_chord:5.1f}mm ({stab_pct:.0f}%), elev={elev_chord:5.1f}mm")

# With hinge at 60mm, the stab covers LE to X=60 and elevator covers X=60 to TE
# At the tip, as chord shrinks, when does the hinge exit?
print(f"\nHinge exits TE at y~{hinge_exit:.0f}mm")
print(f"At y={int(hinge_exit)}: chord={chord_at(hinge_exit):.1f}mm")
print(f"Beyond y={int(hinge_exit)}mm, the entire remaining chord is 'stab' (no elevator)")
print(f"Tip cap (y=210-214) has chord 32->0mm, ALL stab shell")


# ============================================================
print("\n" + "=" * 80)
print("FLUTTER ANALYSIS")
print("=" * 80)

# Elevator mass CG aft of hinge
# With hinge at 60mm, root elevator chord = 51.6mm (center at ~25.8mm aft of hinge)
# With hinge at 74.75mm, root elevator chord = 36.8mm (center at ~18.4mm aft)
# More elevator chord = CG further aft = worse for flutter
# BUT: concealed saddle hinge acts as structural element

root_ec_60 = ROOT_CHORD * TE_TRUNC - 60.0
root_ec_75 = ROOT_CHORD * TE_TRUNC - 74.75
print(f"Root elevator chord at hinge=60mm:    {root_ec_60:.1f}mm (CG ~{root_ec_60/2:.0f}mm aft of hinge)")
print(f"Root elevator chord at hinge=74.75mm: {root_ec_75:.1f}mm (CG ~{root_ec_75/2:.0f}mm aft of hinge)")
print(f"Flutter mass arm increase: {root_ec_60/2 - root_ec_75/2:.1f}mm (+{(root_ec_60/root_ec_75 - 1)*100:.0f}%)")
print()
print("Mitigation factors:")
print("  1. Concealed saddle hinge provides torsional rigidity at hinge line")
print("  2. Bull-nose forward of wire adds forward mass")
print("  3. Elevator tabs forward of wire axis provide counter-flutter damping")
print("  4. Vne < 20 m/s: flutter speed scales with sqrt(torsional_stiffness)")
print("  5. No horn mass at tip (was 1g tungsten in v5) -- REMOVED per directive")


# ============================================================
print("\n" + "=" * 80)
print("HINGE MOMENT ANALYSIS")
print("=" * 80)

# Hinge moment coefficient: Ch = dCh/d_alpha * alpha + dCh/d_delta * delta
# For plain flaps: dCh/d_delta ~ -0.6 to -0.8 per radian (depends on cf/c)
# Larger flap ratio -> lighter hinge moments (counterintuitive but true for cf/c > 0.30)

for hx, label in [(74.75, "v5"), (60.0, "new")]:
    cf = ROOT_CHORD * TE_TRUNC - hx
    cf_ratio = cf / (ROOT_CHORD * TE_TRUNC)
    # Approximate dCh/d_delta (thin airfoil theory)
    theta_f = math.acos(1 - 2 * cf_ratio)
    # dCh/d_delta = -(1/pi)(theta_f - sin(theta_f)*cos(theta_f) - pi + ...)
    # Simplified: larger cf_ratio -> magnitude decreases slightly then increases
    print(f"  {label}: cf/c = {cf_ratio:.3f} ({cf:.1f}mm)")


print("\n" + "=" * 80)
print("MASS IMPACT")
print("=" * 80)

print("Components REMOVED:")
print("  - Rear spar (1.5mm CF rod, 420mm): -1.15g")
print("  - Elevator stiffener L+R (1mm CF rod, 2x150mm): -0.38g")
print("  - Tungsten mass balance (2x0.5g): -1.00g")
print("  - Tip horn material (extra wall thickness): ~-0.30g")
print(f"  TOTAL REMOVED: ~-2.83g")
print()
print("Components CHANGED:")
print(f"  - Main spar X moves from {X_MAIN_SPAR:.0f}mm to {SPAR_REC:.1f}mm (position only)")
print(f"  - Hinge wire X moves from {X_HINGE:.2f}mm to {HINGE_REC:.1f}mm (position only)")
print()
print("Concealed saddle hinge ADDS:")
print("  - 2x TPU flex strips (top+bottom): ~1.0g")
print("  - Saddle structure (integrated into stab/elev shells): ~0.3g")
print(f"  TOTAL ADDED: ~1.3g")
print()
v5_mass = 33.65
delta = -2.83 + 1.3
print(f"V5 mass: {v5_mass:.2f}g")
print(f"Net delta: {delta:+.2f}g")
print(f"New estimated mass: {v5_mass + delta:.2f}g")
