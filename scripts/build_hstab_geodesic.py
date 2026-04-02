"""
HStab_Left — Geodesic Lattice Structure v2 (Fixed)
====================================================
Fixes from v1:
- Normal-direction offset for inner skin (no hinge face warp)
- All rings resampled to same point count (clean mesh topology)
- Spar boss clipped to airfoil envelope
- Tip handled properly (geodesic stops at y=200)

Run: cd D:/Repos/aeroforge && PYTHONPATH=. python scripts/build_hstab_geodesic.py
"""
import sys, os, math, time, struct
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from src.cad.airfoils import blend_airfoils, scale_airfoil

# === PARAMETERS ===
HALF_SPAN = 215.0
ROOT_CHORD = 115.0
N_EXP = 2.3
REF_FRAC = 0.45
REF_X = ROOT_CHORD * REF_FRAC

X_MAIN_SPAR = 34.5
X_HINGE = 60.0
SPAR_BORE = 3.1
SPAR_BOSS_OD = 4.3        # thinner boss: 0.6mm wall (was 1.2mm / 5.5mm OD)
HINGE_BORE = 0.6
Y_MAIN_END = 189.0
Y_HINGE_END = 212.0
FIN_HALF = 3.5
# Spar boss only at root zone + end zone (not full span)
BOSS_ROOT_START = FIN_HALF  # 3.5mm
BOSS_ROOT_END = 30.0        # root load transfer zone
BOSS_TIP_START = 170.0      # end retention zone
BOSS_TIP_END = 189.0        # spar termination
WALL = 0.45
Y_CAP_START = 210.0
Y_CAP_END = 214.0

RIB_THICK = 0.45
RIB_SPACING = 12.0
RIB_ANGLE = 45.0
N_AIRFOIL = 80
N_RING = 120  # fixed point count for ALL rings (clean mesh)

SPAN_STATIONS = sorted(set([
    FIN_HALF, 10, 20, 35, 50, 65, 80, 95, 110, 125, 140, 155, 170,
    Y_MAIN_END, 195, 200, 205, Y_CAP_START, 212
]))


def _se(y):
    if abs(y) >= HALF_SPAN or y < 0:
        return 0.0
    return ROOT_CHORD * (1.0 - (y / HALF_SPAN) ** N_EXP) ** (1.0 / N_EXP)

_c0 = _se(Y_CAP_START)
_sl = (_se(Y_CAP_START) - _se(Y_CAP_START - 0.001)) / 0.001
_ca, _cb = _c0, _sl
_cd = (_ca + 2 * _cb) / 32
_cc = (-_cb - 48 * _cd) / 8

def chord_at(y):
    y = abs(y)
    if y <= Y_CAP_START: return _se(y)
    if y >= Y_CAP_END: return 0.0
    t = y - Y_CAP_START
    return max(0.0, _ca + _cb * t + _cc * t**2 + _cd * t**3)

def le_x(y):
    return REF_X - REF_FRAC * chord_at(abs(y))


def resample_to_n(pts, n):
    """Resample a polyline to exactly n points using arc-length."""
    pts = np.array(pts, dtype=np.float64)
    diffs = np.diff(pts, axis=0)
    segs = np.sqrt((diffs**2).sum(axis=1))
    cum = np.concatenate([[0], np.cumsum(segs)])
    total = cum[-1]
    if total < 1e-12:
        return np.tile(pts[0], (n, 1))
    targets = np.linspace(0, total, n)
    out = np.zeros((n, pts.shape[1]))
    for d in range(pts.shape[1]):
        out[:, d] = np.interp(targets, cum, pts[:, d])
    return out


def get_airfoil_ring(y_sta):
    """Get airfoil clipped at X_HINGE as a closed ring of 3D points.

    Returns ring with hinge face as straight line (not curved).
    Resampled to N_RING points.
    """
    c = chord_at(abs(y_sta))
    if c < 2.0:
        return None
    lx = le_x(abs(y_sta))
    blend = min(abs(y_sta) / HALF_SPAN, 1.0)

    af = blend_airfoils("ht13", "ht12", blend, N_AIRFOIL)
    sc = scale_airfoil(af, c)

    # Split into upper and lower at LE
    le_idx = np.argmin(sc[:, 0])
    upper = sc[:le_idx + 1][::-1]  # LE -> TE (increasing x)
    lower = sc[le_idx:]             # LE -> TE (increasing x)

    # Clip both at hinge x (in local coords)
    hinge_local = X_HINGE - lx

    def clip_surface(pts, x_max):
        """Clip surface at x_max, interpolating the crossing point."""
        clipped = []
        for i, p in enumerate(pts):
            if p[0] <= x_max:
                clipped.append(p)
            else:
                # Interpolate crossing
                if i > 0 and pts[i-1][0] < x_max:
                    prev = pts[i-1]
                    dx = p[0] - prev[0]
                    if dx > 1e-9:
                        t = (x_max - prev[0]) / dx
                        z_cross = prev[1] + t * (p[1] - prev[1])
                        clipped.append([x_max, z_cross])
                break
        return np.array(clipped) if clipped else None

    upper_c = clip_surface(upper, hinge_local)
    lower_c = clip_surface(lower, hinge_local)

    if upper_c is None or lower_c is None or len(upper_c) < 3 or len(lower_c) < 3:
        return None

    # Build closed ring: upper (LE->hinge) + hinge face + lower (hinge->LE)
    # Upper: LE to hinge upper point
    # Hinge face: straight line from upper hinge to lower hinge
    # Lower: hinge lower point back to LE

    n_upper = N_RING // 3
    n_hinge = max(4, N_RING // 15)  # few points for straight hinge face
    n_lower = N_RING - n_upper - n_hinge

    upper_r = resample_to_n(upper_c, n_upper)
    lower_r = resample_to_n(lower_c[::-1], n_lower)  # reversed: hinge->LE

    # Hinge face: straight line from upper end to lower start
    hinge_z_top = float(upper_r[-1, 1])
    hinge_z_bot = float(lower_r[0, 1])
    hinge_pts = np.zeros((n_hinge, 2))
    hinge_pts[:, 0] = hinge_local
    hinge_pts[:, 1] = np.linspace(hinge_z_top, hinge_z_bot, n_hinge)

    # Concatenate: upper + hinge + lower (closed ring)
    ring_2d = np.vstack([upper_r, hinge_pts[1:], lower_r[1:]])  # skip duplicates

    # Resample to exact N_RING
    ring_2d = resample_to_n(ring_2d, N_RING)

    # Convert to 3D absolute coordinates
    ring_3d = np.zeros((N_RING, 3))
    ring_3d[:, 0] = lx + ring_2d[:, 0]  # absolute X
    ring_3d[:, 1] = y_sta
    ring_3d[:, 2] = ring_2d[:, 1]        # Z

    return ring_3d


def offset_ring_normal(ring, offset):
    """Offset a closed ring inward by computing proper 2D normals in XZ plane.

    Uses tangent-perpendicular normals, which correctly handles:
    - Curved LE (normals follow curvature)
    - Straight hinge face (normals point uniformly inward in -X)
    """
    n = len(ring)
    y_val = ring[0, 1]
    xz = ring[:, [0, 2]].copy()

    result_xz = np.zeros_like(xz)

    for i in range(n):
        # Central difference tangent
        p_prev = xz[(i - 1) % n]
        p_next = xz[(i + 1) % n]
        tx = p_next[0] - p_prev[0]
        tz = p_next[1] - p_prev[1]
        tlen = math.hypot(tx, tz)
        if tlen < 1e-12:
            result_xz[i] = xz[i]
            continue

        # For CW-wound ring viewed from +Y:
        # Inward normal = LEFT perpendicular = (-tz, tx) / len
        nx = -tz / tlen
        nz = tx / tlen
        result_xz[i, 0] = xz[i, 0] + nx * offset
        result_xz[i, 1] = xz[i, 1] + nz * offset

    # Check for self-intersection at LE (where curvature > 1/offset)
    # If inner ring crosses itself, clamp
    # Simple check: inner ring X shouldn't go below outer ring min X
    x_min_outer = xz[:, 0].min()
    result_xz[:, 0] = np.maximum(result_xz[:, 0], x_min_outer + 0.1)

    result = np.zeros_like(ring)
    result[:, 0] = result_xz[:, 0]
    result[:, 1] = y_val
    result[:, 2] = result_xz[:, 1]
    return result


def make_skin_strip(ring_a, ring_b, reverse=False):
    """Triangulate a strip between two rings of equal point count.
    Returns (verts, faces) with local indexing starting at 0."""
    n = len(ring_a)
    assert len(ring_b) == n

    verts = np.vstack([ring_a, ring_b])  # 2N verts
    faces = []
    for j in range(n):
        j_next = (j + 1) % n
        v0, v1 = j, j_next
        v2, v3 = n + j, n + j_next
        if reverse:
            faces.append([v0, v1, v2])
            faces.append([v1, v3, v2])
        else:
            faces.append([v0, v2, v1])
            faces.append([v1, v2, v3])

    return verts, np.array(faces)


def make_end_cap(ring, center=None, reverse=False):
    """Create a fan triangulation to cap a ring."""
    n = len(ring)
    if center is None:
        center = ring.mean(axis=0)

    verts = np.vstack([ring, [center]])
    center_idx = n
    faces = []
    for j in range(n):
        j_next = (j + 1) % n
        if reverse:
            faces.append([j, j_next, center_idx])
        else:
            faces.append([j, center_idx, j_next])
    return verts, np.array(faces)


def airfoil_z_at(ring, x_target, surface='upper'):
    """Find Z coordinate on ring at given X, for upper or lower surface."""
    xz = ring[:, [0, 2]]
    n = len(ring)

    # Upper surface = first half of ring (higher Z)
    # Lower surface = second half (lower Z)
    half = n // 2

    if surface == 'upper':
        search = xz[:half]
    else:
        search = xz[half:]

    # Find closest X
    diffs = np.abs(search[:, 0] - x_target)
    idx = np.argmin(diffs)
    return float(search[idx, 1])


def is_inside_airfoil(ring, x, z):
    """Check if point (x, z) is inside the airfoil ring cross-section."""
    z_upper = airfoil_z_at(ring, x, 'upper')
    z_lower = airfoil_z_at(ring, x, 'lower')
    return z_lower <= z <= z_upper


def merge_meshes(mesh_list):
    """Merge list of (verts, faces) into single mesh."""
    all_verts = []
    all_faces = []
    offset = 0
    for verts, faces in mesh_list:
        all_verts.append(verts)
        all_faces.append(faces + offset)
        offset += len(verts)
    return np.vstack(all_verts), np.vstack(all_faces)


def make_geodesic_ribs(outer_rings, inner_rings, ys):
    """Create geodesic diagonal ribs between span stations.
    Each rib is a thin quad connecting outer to inner skin."""
    meshes = []

    for i in range(len(ys) - 1):
        y_a, y_b = ys[i], ys[i + 1]
        if y_a >= 205:  # stop geodesic before tip
            break

        dy = y_b - y_a
        outer_a, outer_b = outer_rings[i], outer_rings[i + 1]
        inner_a, inner_b = inner_rings[i], inner_rings[i + 1]

        if inner_a is None or inner_b is None:
            continue

        x_min = max(outer_a[:, 0].min(), outer_b[:, 0].min()) + 3
        x_max = min(outer_a[:, 0].max(), outer_b[:, 0].max()) - 1
        if x_max <= x_min:
            continue

        x_shift = dy * math.tan(math.radians(RIB_ANGLE))

        # Two sets of diagonal ribs
        for sign in [+1, -1]:
            x = x_min
            while x < x_max:
                x_a = x
                x_b = x + sign * x_shift

                if x_min <= x_a <= x_max and x_min <= x_b <= x_max:
                    # Get Z bounds at each station
                    zu_a = airfoil_z_at(outer_a, x_a, 'upper')
                    zl_a = airfoil_z_at(outer_a, x_a, 'lower')
                    zu_b = airfoil_z_at(outer_b, x_b, 'upper')
                    zl_b = airfoil_z_at(outer_b, x_b, 'lower')
                    ziu_a = airfoil_z_at(inner_a, x_a, 'upper')
                    zil_a = airfoil_z_at(inner_a, x_a, 'lower')
                    ziu_b = airfoil_z_at(inner_b, x_b, 'upper')
                    zil_b = airfoil_z_at(inner_b, x_b, 'lower')

                    # Create rib as two quads (outer wall + inner wall)
                    verts = np.array([
                        [x_a, y_a, zu_a],   # 0
                        [x_a, y_a, zl_a],   # 1
                        [x_b, y_b, zu_b],   # 2
                        [x_b, y_b, zl_b],   # 3
                        [x_a, y_a, ziu_a],  # 4
                        [x_a, y_a, zil_a],  # 5
                        [x_b, y_b, ziu_b],  # 6
                        [x_b, y_b, zil_b],  # 7
                    ], dtype=np.float32)

                    faces = np.array([
                        [0, 2, 3], [0, 3, 1],  # outer wall
                        [4, 7, 6], [4, 5, 7],  # inner wall
                        [0, 6, 2], [0, 4, 6],  # top cap
                        [1, 3, 7], [1, 7, 5],  # bottom cap
                    ], dtype=np.int32)

                    meshes.append((verts, faces))

                x += RIB_SPACING

    if not meshes:
        return np.zeros((0, 3), dtype=np.float32), np.zeros((0, 3), dtype=np.int32)
    return merge_meshes(meshes)


def make_spar_boss(outer_rings, ys, x_center, od, bore,
                   boss_zones, n_seg=24):
    """Spar boss tube CLIPPED to airfoil envelope.
    boss_zones: list of (y_start, y_end) tuples for boss segments."""
    verts = []
    faces = []

    # Only at stations inside boss zones
    boss_ys = []
    for y in ys:
        for zs, ze in boss_zones:
            if zs <= y <= ze:
                boss_ys.append(y)
                break
    if len(boss_ys) < 2:
        return np.zeros((0, 3)), np.zeros((0, 3), dtype=np.int32)

    rings_per_station = []
    for iy, y in enumerate(boss_ys):
        # Find the corresponding outer ring
        ring_idx = ys.index(y) if y in ys else None
        if ring_idx is None:
            continue

        outer = outer_rings[ring_idx]
        zu = airfoil_z_at(outer, x_center, 'upper')
        zl = airfoil_z_at(outer, x_center, 'lower')
        z_max_radius = (zu - zl) / 2 - 0.2  # max radius that fits

        r_outer = min(od / 2, z_max_radius)
        r_inner = bore / 2

        if r_outer <= r_inner:
            continue

        inner_ring = []
        outer_ring = []
        for ia in range(n_seg):
            theta = 2 * math.pi * ia / n_seg
            cos_t, sin_t = math.cos(theta), math.sin(theta)

            # Outer ring of boss
            xo = x_center + r_outer * cos_t
            zo = r_outer * sin_t
            # Clip Z to airfoil envelope
            zu_at = airfoil_z_at(outer, xo, 'upper')
            zl_at = airfoil_z_at(outer, xo, 'lower')
            zo = max(zl_at + 0.1, min(zu_at - 0.1, zo))
            outer_ring.append([xo, y, zo])

            # Inner ring (bore)
            xi = x_center + r_inner * cos_t
            zi = r_inner * sin_t
            inner_ring.append([xi, y, zi])

        rings_per_station.append((y, np.array(outer_ring), np.array(inner_ring)))

    if len(rings_per_station) < 2:
        return np.zeros((0, 3)), np.zeros((0, 3), dtype=np.int32)

    meshes = []
    for i in range(len(rings_per_station) - 1):
        _, outer_a, inner_a = rings_per_station[i]
        _, outer_b, inner_b = rings_per_station[i + 1]

        # Outer surface
        v, f = make_skin_strip(outer_a, outer_b, reverse=False)
        meshes.append((v, f))
        # Inner surface (bore)
        v, f = make_skin_strip(inner_a, inner_b, reverse=True)
        meshes.append((v, f))

    return merge_meshes(meshes)


def write_binary_stl(filename, vertices, faces):
    vertices = np.array(vertices, dtype=np.float32)
    faces = np.array(faces, dtype=np.int32)
    with open(filename, 'wb') as f:
        f.write(b'\0' * 80)
        f.write(struct.pack('<I', len(faces)))
        for face in faces:
            v0, v1, v2 = vertices[face[0]], vertices[face[1]], vertices[face[2]]
            e1, e2 = v1 - v0, v2 - v0
            n = np.cross(e1, e2)
            nl = np.linalg.norm(n)
            if nl > 0: n /= nl
            f.write(struct.pack('<fff', *n))
            f.write(struct.pack('<fff', *v0))
            f.write(struct.pack('<fff', *v1))
            f.write(struct.pack('<fff', *v2))
            f.write(struct.pack('<H', 0))


def write_3mf(filename, vertices, faces):
    import lib3mf
    wrapper = lib3mf.get_wrapper()
    model = wrapper.CreateModel()
    model.SetUnit(lib3mf.ModelUnit.MilliMeter)
    mesh = model.AddMeshObject()
    mesh.SetName("HStab_Left_Geodesic")

    positions = []
    for v in vertices:
        p = lib3mf.Position()
        p.Coordinates[0] = float(v[0])
        p.Coordinates[1] = float(v[1])
        p.Coordinates[2] = float(v[2])
        positions.append(p)

    triangles = []
    for f in faces:
        t = lib3mf.Triangle()
        t.Indices[0] = int(f[0])
        t.Indices[1] = int(f[1])
        t.Indices[2] = int(f[2])
        triangles.append(t)

    mesh.SetGeometry(positions, triangles)
    model.AddBuildItem(mesh, wrapper.GetIdentityTransform())

    md = model.GetMetaDataGroup()
    md.AddMetaData("", "Title", "HStab_Left Geodesic - AeroForge", "string", True)

    writer = model.QueryWriter("3mf")
    writer.WriteToFile(filename)


def main():
    t0 = time.time()
    print("=" * 60)
    print("HStab_Left — GEODESIC v2 (fixed)")
    print("  Normal offset, clipped spar boss, clean topology")
    print("=" * 60)

    # === Generate rings ===
    print(f"\nGenerating {len(SPAN_STATIONS)} sections (N_RING={N_RING})...")
    outer_rings = []
    inner_rings = []
    valid_ys = []

    for y in SPAN_STATIONS:
        ring = get_airfoil_ring(y)
        if ring is None:
            continue
        outer_rings.append(ring)

        # Inner ring with proper normal offset
        if y < Y_CAP_START - 1 and chord_at(y) > 8:
            inner = offset_ring_normal(ring, WALL)
            inner_rings.append(inner)
        else:
            inner_rings.append(None)

        valid_ys.append(y)
        print(f"  y={y:6.1f}: chord={chord_at(y):5.1f}mm")

    print(f"  {len(valid_ys)} stations, {N_RING} pts each")

    # === Skin mesh ===
    print("\nBuilding outer + inner skin...")
    skin_meshes = []
    for i in range(len(valid_ys) - 1):
        # Outer skin strip
        v, f = make_skin_strip(outer_rings[i], outer_rings[i+1])
        skin_meshes.append((v, f))

        # Inner skin strip (where inner rings exist)
        if inner_rings[i] is not None and inner_rings[i+1] is not None:
            v, f = make_skin_strip(inner_rings[i], inner_rings[i+1], reverse=True)
            skin_meshes.append((v, f))

    # Root cap (close the open root)
    if inner_rings[0] is not None:
        v, f = make_skin_strip(outer_rings[0], inner_rings[0])
        skin_meshes.append((v, f))

    # Tip cap
    v, f = make_end_cap(outer_rings[-1])
    skin_meshes.append((v, f))

    # Close inner end where inner stops
    last_inner_idx = None
    for i in range(len(inner_rings) - 1, -1, -1):
        if inner_rings[i] is not None:
            last_inner_idx = i
            break
    if last_inner_idx is not None:
        v, f = make_end_cap(inner_rings[last_inner_idx], reverse=True)
        skin_meshes.append((v, f))

    skin_v, skin_f = merge_meshes(skin_meshes)
    print(f"  Skin: {len(skin_v)} verts, {len(skin_f)} tris")

    # === Geodesic ribs ===
    print(f"\nBuilding geodesic ribs (±{RIB_ANGLE}°, {RIB_SPACING}mm)...")
    rib_v, rib_f = make_geodesic_ribs(outer_rings, inner_rings, valid_ys)
    print(f"  Ribs: {len(rib_v)} verts, {len(rib_f)} tris")

    # === Spar boss (clipped to airfoil, root + tip zones only) ===
    boss_zones = [
        (BOSS_ROOT_START, BOSS_ROOT_END),  # root load transfer: 3.5-30mm
        (BOSS_TIP_START, BOSS_TIP_END),    # end retention: 170-189mm
    ]
    print(f"\nBuilding spar boss (OD={SPAR_BOSS_OD}mm, bore={SPAR_BORE}mm, zones only)...")
    print(f"  Root zone: y={BOSS_ROOT_START}-{BOSS_ROOT_END}mm")
    print(f"  Tip zone:  y={BOSS_TIP_START}-{BOSS_TIP_END}mm")
    boss_v, boss_f = make_spar_boss(
        outer_rings, valid_ys, X_MAIN_SPAR, SPAR_BOSS_OD, SPAR_BORE,
        boss_zones
    )
    print(f"  Boss: {len(boss_v)} verts, {len(boss_f)} tris")

    # === Merge all ===
    print("\nMerging...")
    all_meshes = [(skin_v, skin_f)]
    if len(rib_v) > 0:
        all_meshes.append((rib_v, rib_f))
    if len(boss_v) > 0:
        all_meshes.append((boss_v, boss_f))

    all_v, all_f = merge_meshes(all_meshes)
    print(f"  Total: {len(all_v)} verts, {len(all_f)} tris")

    # === Stats ===
    dt = time.time() - t0
    ext = all_v.max(axis=0) - all_v.min(axis=0)
    print(f"\n{'='*60}")
    print(f"HStab_Left GEODESIC v2")
    print(f"  Mesh: {len(all_v)} verts, {len(all_f)} tris")
    print(f"  Extent: {ext[0]:.1f} x {ext[1]:.1f} x {ext[2]:.1f} mm")
    print(f"  Build: {dt:.1f}s")
    print(f"{'='*60}")

    # === Export ===
    out = "cad/components/empennage/HStab_Left"
    os.makedirs(out, exist_ok=True)

    stl_path = f"{out}/HStab_Left.stl"
    threemf_path = f"{out}/HStab_Left.3mf"

    print(f"\nExporting STL: {stl_path}")
    write_binary_stl(stl_path, all_v, all_f)
    print(f"  {os.path.getsize(stl_path)/1024:.0f} KB")

    print(f"Exporting 3MF: {threemf_path}")
    write_3mf(threemf_path, all_v, all_f)
    print(f"  {os.path.getsize(threemf_path)/1024:.0f} KB")

    # === Open in OCP Viewer ===
    print("\nOpening in OCP Viewer...")
    try:
        from build123d import import_stl
        from ocp_vscode import show
        part = import_stl(stl_path)
        show(part)
        print("Displayed in OCP Viewer")
    except Exception as e:
        print(f"OCP: {e}")

    # === Open in OrcaSlicer ===
    print("Opening in OrcaSlicer...")
    abs_path = os.path.abspath(threemf_path).replace("\\", "/")
    os.startfile(abs_path)
    print("OrcaSlicer launched")


if __name__ == "__main__":
    main()
