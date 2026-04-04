# H-Stab Assembly Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the complete H-Stab assembly (fixed stabilizer + elevator with music wire hinge) from 2D drawings through 3D models, following the drawing-first workflow.

**Architecture:** 14 components organized into one assembly. Each component gets a folder with a 2D DXF drawing, 3D model, renders, and documentation. Off-shelf parts (CF rods, music wire) get simplified drawings. Custom printed parts (stab halves, elevator halves, hinge strips, control horn) get full technical drawings with internal structure. The assembly drawing shows the exploded view and integration with the VStab fin.

**Tech Stack:** Python 3.10+, ezdxf (2D drawings), Build123d (3D modeling), FreeCAD MCP (rendering/FEM), AeroSandbox/NeuralFoil (airfoil coordinates)

**Key References:**
- Design consensus: `cad/assemblies/empennage/HStab_Assembly/DESIGN_CONSENSUS.md`
- Existing drawing pattern: `scripts/draw_hstab_left.py` (old v2, reference for ezdxf patterns)
- Existing off-shelf pattern: `scripts/draw_offshelf_rods.py` (reference for rod drawings)
- DXF utility: `src/core/dxf_utils.py` → `save_dxf_and_png()`
- Specs code: `src/cad/tail/__init__.py` → `TailSectionSpec` (needs updating)

---

## File Map

### Scripts (new or rewritten)

| File | Responsibility |
|------|---------------|
| `scripts/draw_hstab_stab_left.py` | 2D technical drawing of left stab half (LE to 65% chord, superellipse planform, HT-13→HT-12 blend, spar tunnels, wall sections) |
| `scripts/draw_hstab_elevator_left.py` | 2D technical drawing of left elevator half (65% to 97% chord, hinge strip bonding surface, 1mm stiffener channel) |
| `scripts/draw_hstab_hinge_strip.py` | 2D technical drawing of PETG hinge strip (knuckle geometry, interleave pattern, wire bore) |
| `scripts/draw_hstab_control_horn.py` | 2D technical drawing of CF-PLA control horn (forward extension for mass balance, pushrod hole) |
| `scripts/draw_hstab_offshelf.py` | 2D drawings for all 4 off-shelf rods + wire (main spar tube, rear spar, elevator stiffener, music wire) |
| `scripts/draw_hstab_assembly.py` | 2D assembly drawing — exploded view, integration with VStab fin, hinge detail |
| `scripts/build_hstab_stab_left.py` | 3D Build123d model of left stab half |
| `scripts/build_hstab_elevator_left.py` | 3D Build123d model of left elevator half |
| `scripts/build_hstab_hinge_strip.py` | 3D Build123d model of PETG hinge strip with knuckles |
| `scripts/build_hstab_control_horn.py` | 3D Build123d model of CF-PLA control horn |
| `scripts/build_hstab_assembly.py` | 3D assembly — all components mated, collision check |

### Source code (modify)

| File | Change |
|------|--------|
| `src/cad/tail/__init__.py` | Update `TailSectionSpec` defaults to v3 consensus values |

### CAD outputs (created by scripts)

| Folder | Contents |
|--------|----------|
| `cad/components/empennage/HStab_Left/` | Drawing, model, renders, COMPONENT_INFO.md |
| `cad/components/empennage/HStab_Right/` | Mirror of left (drawing + model + renders + info) |
| `cad/components/empennage/Elevator_Left/` | Drawing, model, renders, COMPONENT_INFO.md |
| `cad/components/empennage/Elevator_Right/` | Mirror of left |
| `cad/components/empennage/HStab_Hinge_Strip_Stab/` | Drawing, model, renders, COMPONENT_INFO.md |
| `cad/components/empennage/HStab_Hinge_Strip_Elevator/` | Drawing, model, renders, COMPONENT_INFO.md |
| `cad/components/empennage/Control_Horn/` | Already exists (update with v3 design) |
| `cad/components/empennage/HStab_Main_Spar/` | Off-shelf drawing + COMPONENT_INFO.md |
| `cad/components/empennage/HStab_Rear_Spar/` | Off-shelf drawing + COMPONENT_INFO.md |
| `cad/components/empennage/Elevator_Stiffener/` | Off-shelf drawing + COMPONENT_INFO.md |
| `cad/components/empennage/Hinge_Wire/` | Off-shelf drawing + COMPONENT_INFO.md |
| `cad/components/empennage/Mass_Balance/` | Off-shelf drawing + COMPONENT_INFO.md |
| `cad/assemblies/empennage/HStab_Assembly/` | Assembly drawing, model, renders, ASSEMBLY_INFO.md |

---

## Task 1: Update TailSectionSpec to v3 Consensus

**Files:**
- Modify: `src/cad/tail/__init__.py:17-57`

- [ ] **Step 1: Update TailSectionSpec defaults**

```python
@dataclass
class TailSectionSpec:
    """Specification for tail section.

    All dimensions in mm.
    """
    # Configuration
    tail_type: Literal["conventional", "v_tail", "t_tail"] = "conventional"

    # Horizontal stabilizer (Design Consensus v3, 2026-03-30)
    h_stab_type: str = "fixed_elevator"  # fixed stabilizer + 35% chord elevator
    h_stab_planform: str = "superellipse"  # n=2.3
    h_stab_planform_n: float = 2.3
    h_stab_span: float = 430.0  # mm
    h_stab_root_chord: float = 115.0  # Re 61,300 at 8 m/s
    h_stab_root_airfoil: str = "HT-13"  # 6.5% thickness
    h_stab_tip_airfoil: str = "HT-12"  # 5.1% thickness, linear blend
    h_stab_area: float = 4077.0  # mm² (~4.08 dm²)
    h_stab_ar: float = 4.53
    h_stab_oswald_e: float = 0.990
    h_stab_elevator_chord_ratio: float = 0.35  # 35% of local chord
    h_stab_hinge_frac: float = 0.65  # Hinge line at 65% chord
    h_stab_main_spar_frac: float = 0.25  # 3mm CF tube at 25% chord
    h_stab_rear_spar_frac: float = 0.60  # 1.5mm CF rod at 60% chord
    h_stab_elev_stiffener_frac: float = 0.80  # 1mm CF rod at 80% chord
    h_stab_main_spar_od: float = 3.0  # mm, tube OD
    h_stab_main_spar_id: float = 2.0  # mm, tube ID
    h_stab_main_spar_length: float = 390.0  # mm (terminates at 195mm/half)
    h_stab_rear_spar_dia: float = 1.5  # mm, solid rod
    h_stab_elev_stiffener_dia: float = 1.0  # mm, solid rod
    h_stab_hinge_wire_dia: float = 0.5  # mm, music wire
    h_stab_deflection_up: float = 25.0  # Degrees (nose up, elevator)
    h_stab_deflection_down: float = 20.0  # Degrees (nose down, elevator)
    h_stab_mass_target: float = 33.7  # grams (35g hard limit)
    h_stab_te_truncation: float = 0.97  # TE at 97% chord
    h_stab_wall_stab: float = 0.45  # mm, vase mode wall (stab)
    h_stab_wall_elevator: float = 0.40  # mm, vase mode wall (elevator)

    # Vertical stabilizer (integrated into fuselage)
    v_stab_height: float = 165.0
    v_stab_root_chord: float = 180.0
    v_stab_tip_chord: float = 95.0
    v_stab_root_airfoil: str = "HT-14"  # 7.5%
    v_stab_tip_airfoil: str = "HT-12"  # 5.1%
    rudder_ratio: float = 0.35  # Rudder as fraction of chord

    # Tail moment arm
    tail_moment: float = 651.0  # mm, from fuselage consensus

    # Control throws
    rudder_throw_left: float = 25.0
    rudder_throw_right: float = 25.0

    def chord_at(self, eta: float) -> float:
        """Superellipse chord at span fraction eta (0=root, 1=tip)."""
        n = self.h_stab_planform_n
        return self.h_stab_root_chord * (1.0 - abs(eta) ** n) ** (1.0 / n)

    def thickness_ratio_at(self, eta: float) -> float:
        """Blend HT-13 (6.5%) at root to HT-12 (5.1%) at tip."""
        t_root = 0.065  # HT-13
        t_tip = 0.051   # HT-12
        return t_root + (t_tip - t_root) * eta
```

- [ ] **Step 2: Run any existing tail tests**

Run: `cd D:/Repos/aeroforge && PYTHONPATH=. python -m pytest tests/ -k tail -v 2>/dev/null || echo "No tail tests yet"`

- [ ] **Step 3: Commit**

```bash
git add src/cad/tail/__init__.py
git commit -m "refactor: update TailSectionSpec to v3 consensus (fixed+elevator, superellipse)"
```

---

## Task 2: Draw Off-Shelf Components (5 rods/wire)

**Files:**
- Create: `scripts/draw_hstab_offshelf.py`
- Create: `cad/components/empennage/HStab_Main_Spar/` (drawing + info)
- Create: `cad/components/empennage/HStab_Rear_Spar/` (drawing + info)
- Create: `cad/components/empennage/Elevator_Stiffener/` (drawing + info)
- Create: `cad/components/empennage/Hinge_Wire/` (drawing + info)
- Create: `cad/components/empennage/Mass_Balance/` (drawing + info)
- Reference: `scripts/draw_offshelf_rods.py` (existing pattern for rod drawings)

This task creates all 5 off-shelf component folders with drawings and COMPONENT_INFO.md files. These are simple rod/wire drawings following the existing pattern in `draw_offshelf_rods.py`.

- [ ] **Step 1: Write `scripts/draw_hstab_offshelf.py`**

The script generates 5 drawings using the rod-drawing pattern from `draw_offshelf_rods.py`. Each rod gets a side view (rectangle), end view (circle or annulus for tube), centerline, length and diameter dimensions, and a title block with material/purpose info.

Components:
1. `HStab_Main_Spar` — 3mm CF tube (3/2mm OD/ID), 390mm
2. `HStab_Rear_Spar` — 1.5mm CF solid rod, 440mm
3. `Elevator_Stiffener` — 1mm CF solid rod, 440mm
4. `Hinge_Wire` — 0.5mm music wire (spring steel), 440mm
5. `Mass_Balance` — 1.0g tungsten putty blob, ~5mm dia sphere (schematic drawing)

Read `scripts/draw_offshelf_rods.py` for the exact ezdxf pattern (layer setup, dimstyle, draw_rod function), then extend it for the tube (annular end view) and wire. Use `save_dxf_and_png()` from `src/core/dxf_utils.py`.

Each drawing saves to `cad/components/empennage/{ComponentName}/{ComponentName}_drawing.dxf` (and `.png`).

- [ ] **Step 2: Run the script**

Run: `cd D:/Repos/aeroforge && PYTHONPATH=. python scripts/draw_hstab_offshelf.py`

Verify 5 DXF + 5 PNG files created in the correct folders.

- [ ] **Step 3: Write COMPONENT_INFO.md for each off-shelf component**

Create 5 COMPONENT_INFO.md files following the template in `cad/CAD_FRAMEWORK.md`. Key info per component:

- **HStab_Main_Spar**: 3mm CF tube 3/2mm, 390mm, 2.40g, pultruded carbon fiber, slides through stab halves and VStab fin
- **HStab_Rear_Spar**: 1.5mm CF solid rod, 440mm, 1.20g, at 60% chord in fixed stab
- **Elevator_Stiffener**: 1mm CF solid rod, 440mm, 0.55g, at 80% chord in elevator (flutter prevention)
- **Hinge_Wire**: 0.5mm music wire (ASTM A228 spring steel), 440mm, 0.68g, threads through PETG knuckle strips
- **Mass_Balance**: ~1.0g tungsten putty, applied to control horn forward extension (flutter prevention)

- [ ] **Step 4: Review drawings visually**

Open each PNG in the IDE and verify dimensions, labels, and proportions look correct.

- [ ] **Step 5: Commit**

```bash
git add scripts/draw_hstab_offshelf.py cad/components/empennage/HStab_Main_Spar/ cad/components/empennage/HStab_Rear_Spar/ cad/components/empennage/Elevator_Stiffener/ cad/components/empennage/Hinge_Wire/ cad/components/empennage/Mass_Balance/
git commit -m "feat: add off-shelf component drawings for H-Stab v3 (5 rods/wire/putty)"
```

---

## Task 3: Draw Left Stab Half (Custom, Printed)

**Files:**
- Create: `scripts/draw_hstab_stab_left.py`
- Create: `cad/components/empennage/HStab_Left/HStab_Left_drawing.dxf`
- Create: `cad/components/empennage/HStab_Left/HStab_Left_drawing.png`

This is the most complex drawing. It shows the left stab half from LE to 65% chord, with the superellipse planform, HT-13→HT-12 airfoil blend, spar tunnels, wall sections, and hinge strip bonding surface.

- [ ] **Step 1: Write `scripts/draw_hstab_stab_left.py`**

The drawing must include 3 views:

**Top view (planform):**
- Superellipse leading edge curve: `c(y) = 115 * (1 - |y/215|^2.3)^(1/2.3)`
- Straight trailing edge at 65% of local chord (the hinge line)
- Main spar line at 25% chord (dashed, from root to 195mm)
- Rear spar line at 60% chord (dashed, full span)
- Span dimensions, root/tip chord dimensions
- Spar termination callout at y=195mm

**Front view (root cross-section):**
- HT-13 airfoil profile (LE to 65% chord) at root chord 115mm
- Wall thickness 0.45mm shown
- 3mm spar tunnel at 25% chord (3.1mm ID bore)
- 1.5mm rear spar tunnel at 60% chord
- Hinge strip bonding surface (2mm wide flat face at TE)

**Section view (at 50% span):**
- Blended HT-13/HT-12 profile at chord ~106mm
- Same internal features scaled to local chord

Use NeuralFoil/AeroSandbox to get actual HT-13 and HT-12 airfoil coordinate arrays for accurate profiles. The airfoil profile from LE to 65% chord is an open section (no TE closure in the drawing — that's the hinge face).

Reference `scripts/draw_hstab_left.py` for the ezdxf pattern (layer setup, airfoil generation function `ht_yt`, dimension styles), but replace the old trapezoidal planform with the superellipse and update all dimensions to v3.

- [ ] **Step 2: Run the script**

Run: `cd D:/Repos/aeroforge && PYTHONPATH=. python scripts/draw_hstab_stab_left.py`

Verify DXF + PNG created at the correct path.

- [ ] **Step 3: Review drawing visually**

Open the PNG. Check:
- Superellipse LE curve is visibly curved (not straight taper)
- Spar terminates before tip
- Root airfoil profile looks correct (HT-13, 6.5% t/c)
- Dimensions are labeled and readable
- Hinge face (flat TE at 65% chord) is clearly shown

- [ ] **Step 4: Commit**

```bash
git add scripts/draw_hstab_stab_left.py cad/components/empennage/HStab_Left/
git commit -m "feat: add HStab_Left 2D technical drawing (superellipse, HT-13/12 blend)"
```

**STOP: Drawing must be reviewed and approved before proceeding to 3D model (Task 8).**

---

## Task 4: Draw Left Elevator Half (Custom, Printed)

**Files:**
- Create: `scripts/draw_hstab_elevator_left.py`
- Create: `cad/components/empennage/Elevator_Left/Elevator_Left_drawing.dxf`
- Create: `cad/components/empennage/Elevator_Left/Elevator_Left_drawing.png`

- [ ] **Step 1: Write `scripts/draw_hstab_elevator_left.py`**

The elevator runs from 65% to 97% chord. Three views:

**Top view (planform):**
- LE follows 65% chord line of the superellipse (curved)
- TE follows 97% chord line (also curved, slightly)
- 1mm stiffener line at 80% chord (dashed)
- Hinge strip bonding surface at LE face
- Span dimensions, root/tip elevator chord dimensions

**Front view (root cross-section):**
- Airfoil profile from 65% to 97% chord at root (40.2mm elevator chord)
- 0.40mm wall thickness shown
- 1mm stiffener tunnel at 80% chord
- Hinge strip bonding surface (2mm wide flat face at LE)
- TE truncation detail at 97% chord (~0.7mm flat)

**Section at 50% span:**
- Same features at local chord

Use the same airfoil coordinate functions but extract only the 65%-97% chord portion.

- [ ] **Step 2: Run the script**

Run: `cd D:/Repos/aeroforge && PYTHONPATH=. python scripts/draw_hstab_elevator_left.py`

- [ ] **Step 3: Review drawing visually**

Check elevator profile shape, stiffener position, hinge face, TE truncation.

- [ ] **Step 4: Commit**

```bash
git add scripts/draw_hstab_elevator_left.py cad/components/empennage/Elevator_Left/
git commit -m "feat: add Elevator_Left 2D technical drawing (35% chord, TPU hinge face)"
```

---

## Task 5: Draw PETG Hinge Strips (Custom, Printed)

**Files:**
- Create: `scripts/draw_hstab_hinge_strip.py`
- Create: `cad/components/empennage/HStab_Hinge_Strip_Stab/` (drawing + info)
- Create: `cad/components/empennage/HStab_Hinge_Strip_Elevator/` (drawing + info)

- [ ] **Step 1: Write `scripts/draw_hstab_hinge_strip.py`**

Two hinge strips (stab-side and elevator-side) with identical geometry except the knuckle offset (they interleave). Each strip is 215mm long x 2mm wide x 1.2mm tall with knuckles.

**Side view:** Strip profile with knuckle bumps at 8mm spacing. Each knuckle is a 1.2mm OD / 0.6mm ID semicircle. Alternating: knuckle-gap-knuckle-gap... (27 knuckles per half-span, 3mm long each).

**End view (cross-section at knuckle):** Shows the 2mm wide base strip, the 1.2mm OD knuckle with 0.6mm bore hole for the 0.5mm wire.

**Top view:** Shows the 215mm strip with knuckle positions marked.

The stab-side strip and elevator-side strip are OFFSET by 4mm (half the 8mm spacing) so they interleave.

- [ ] **Step 2: Run the script**

Run: `cd D:/Repos/aeroforge && PYTHONPATH=. python scripts/draw_hstab_hinge_strip.py`

- [ ] **Step 3: Write COMPONENT_INFO.md for both strips**

- [ ] **Step 4: Review drawings visually**

Verify knuckle geometry, interleave pattern, bore diameter, strip dimensions.

- [ ] **Step 5: Commit**

```bash
git add scripts/draw_hstab_hinge_strip.py cad/components/empennage/HStab_Hinge_Strip_Stab/ cad/components/empennage/HStab_Hinge_Strip_Elevator/
git commit -m "feat: add PETG hinge strip drawings (music wire knuckle design)"
```

---

## Task 6: Draw Control Horn (Custom, Printed)

**Files:**
- Modify: `cad/components/empennage/Control_Horn/` (update existing)
- Create: `scripts/draw_hstab_control_horn.py`

- [ ] **Step 1: Write `scripts/draw_hstab_control_horn.py`**

The control horn is a CF-PLA printed part with:
- Main horn extending below the elevator surface (~10-12mm)
- Forward extension (3-5mm forward of hinge line, inside stab cavity) for mass balance
- Pushrod hole (0.8mm) for music wire Z-bend or clevis
- Mounting holes for bolting through the elevator skin
- Pocket/depression in forward extension for 1.0g tungsten putty

Three views: front (horn profile), side (showing forward extension and pushrod hole), top (mounting footprint).

- [ ] **Step 2: Run the script**

Run: `cd D:/Repos/aeroforge && PYTHONPATH=. python scripts/draw_hstab_control_horn.py`

- [ ] **Step 3: Update COMPONENT_INFO.md**

Update the existing Control_Horn folder with v3 design info.

- [ ] **Step 4: Review drawing visually**

- [ ] **Step 5: Commit**

```bash
git add scripts/draw_hstab_control_horn.py cad/components/empennage/Control_Horn/
git commit -m "feat: add Control_Horn drawing (v3, forward mass balance extension)"
```

---

## Task 7: Draw H-Stab Assembly (Exploded + Integration)

**Files:**
- Create: `scripts/draw_hstab_assembly.py` (rewrite the old one)
- Create: `cad/assemblies/empennage/HStab_Assembly/HStab_Assembly_drawing.dxf`
- Create: `cad/assemblies/empennage/HStab_Assembly/HStab_Assembly_drawing.png`

- [ ] **Step 1: Write `scripts/draw_hstab_assembly.py`**

The assembly drawing shows:

**Top view (assembled):** Full 430mm span planform showing both stab halves and both elevators. VStab fin outline at center. Fillet blending shown. Spar routing shown as dashed lines.

**Front view (assembled):** Cross-section showing stab, elevator, hinge, VStab fin junction fillet. Dovetail interlock detail.

**Exploded view:** All 14 components separated with leader lines:
- Left/right stab halves
- Left/right elevator halves
- 4 hinge strips (showing interleave pattern)
- Main spar tube (through both halves + VStab)
- Rear spar rod
- Elevator stiffener rod
- Music wire (through knuckles)
- Control horn with mass balance
- VStab fin outline (reference, not part of this assembly)

**Hinge detail (zoomed):** Shows the knuckle interleave, wire path, 0.3mm gap, and cross-section of assembled hinge.

- [ ] **Step 2: Run the script**

Run: `cd D:/Repos/aeroforge && PYTHONPATH=. python scripts/draw_hstab_assembly.py`

- [ ] **Step 3: Review drawing visually**

Check all components are shown, integration with VStab makes sense, hinge detail is clear.

- [ ] **Step 4: Commit**

```bash
git add scripts/draw_hstab_assembly.py cad/assemblies/empennage/HStab_Assembly/HStab_Assembly_drawing.*
git commit -m "feat: add HStab_Assembly 2D drawing (exploded, hinge detail, VStab integration)"
```

**STOP: All drawings must be reviewed and approved before proceeding to 3D modeling.**

---

## Task 8: Build 3D Left Stab Half (Build123d)

**Files:**
- Create: `scripts/build_hstab_stab_left.py`
- Create: `cad/components/empennage/HStab_Left/HStab_Left.step`
- Create: `cad/components/empennage/HStab_Left/HStab_Left.stl`

**Prerequisite:** Task 3 drawing approved.

- [ ] **Step 1: Write `scripts/build_hstab_stab_left.py`**

The 3D model must match the 2D drawing exactly. Build123d approach:

1. Generate airfoil coordinate arrays (HT-13 at root, HT-12 at tip, blended at intermediate stations) — use AeroSandbox `Airfoil` objects or manual coordinate generation
2. Trim each airfoil from LE to 65% chord (open section at hinge line)
3. Create cross-section Wire objects at ~10mm span intervals (per the chord distribution table in DESIGN_CONSENSUS.md)
4. Loft through all sections to create the outer shell surface
5. Shell/offset to 0.45mm wall thickness
6. Cut spar tunnel (3.1mm ID bore at 25% chord, root to 195mm) — the tunnel drifts from 25% to 30% chord at termination
7. Cut rear spar tunnel (1.6mm ID bore at 60% chord, full span)
8. Cut hinge strip bonding flat (2mm wide flat on TE lower surface)
9. Create dovetail tongue feature at root for VStab joint
10. Close tip with parabolic fairing cap (last 5mm, thicker walls 0.55mm)
11. Export STEP and STL

Dimensions MUST match the drawing. Use `TailSectionSpec.chord_at(eta)` for the superellipse chord at each station.

- [ ] **Step 2: Run the script**

Run: `cd D:/Repos/aeroforge && PYTHONPATH=. python scripts/build_hstab_stab_left.py`

Verify STEP + STL created.

- [ ] **Step 3: Load into FreeCAD and take 4 render views**

Use FreeCAD MCP to open the STEP, capture isometric/front/top/right views, save to `cad/components/empennage/HStab_Left/renders/`.

- [ ] **Step 4: Visual comparison — renders vs drawing**

Compare the 4 renders against the 2D drawing PNG. Check:
- Superellipse planform matches
- Spar tunnels visible in cross-section view
- Tip fairing cap present
- Wall thickness consistent
- Root dovetail tongue visible

- [ ] **Step 5: Write COMPONENT_INFO.md**

- [ ] **Step 6: Commit**

```bash
git add scripts/build_hstab_stab_left.py cad/components/empennage/HStab_Left/
git commit -m "feat: build HStab_Left 3D model (superellipse, HT-13/12, spar tunnels)"
```

---

## Task 9: Build 3D Right Stab Half (Mirror)

**Files:**
- Create: `scripts/build_hstab_stab_right.py` (or mirror in the left script)
- Create: `cad/components/empennage/HStab_Right/`

- [ ] **Step 1: Mirror the left stab model**

The right half is an exact mirror of the left about the YZ plane (X-axis flip). In Build123d, use `mirror()` on the left half's shape, then export.

Alternatively, modify the left script to accept a `--mirror` flag.

- [ ] **Step 2: Export STEP + STL, take 4 renders**

- [ ] **Step 3: Write COMPONENT_INFO.md**

- [ ] **Step 4: Commit**

```bash
git add cad/components/empennage/HStab_Right/
git commit -m "feat: build HStab_Right 3D model (mirror of left)"
```

---

## Task 10: Build 3D Left Elevator Half

**Files:**
- Create: `scripts/build_hstab_elevator_left.py`
- Create: `cad/components/empennage/Elevator_Left/`

**Prerequisite:** Task 4 drawing approved.

- [ ] **Step 1: Write `scripts/build_hstab_elevator_left.py`**

Same airfoil generation as the stab, but extract only the 65%-97% chord portion:
1. Generate blended airfoil at each span station
2. Trim to 65%-97% chord — the LE face is the flat hinge bonding surface
3. Loft through sections
4. Shell to 0.40mm wall
5. Cut 1.1mm ID bore at 80% chord (elevator stiffener tunnel)
6. Cut hinge strip bonding flat (2mm wide on LE lower surface)
7. TE truncation at 97% chord (flat face, ~0.7mm)
8. Tip closure matching stab tip
9. Export STEP + STL

- [ ] **Step 2: Run, render, verify against drawing**

- [ ] **Step 3: Write COMPONENT_INFO.md, commit**

```bash
git add scripts/build_hstab_elevator_left.py cad/components/empennage/Elevator_Left/
git commit -m "feat: build Elevator_Left 3D model (35% chord, stiffener tunnel)"
```

---

## Task 11: Build 3D Right Elevator Half (Mirror) + Hinge Strips + Control Horn

**Files:**
- Create: `cad/components/empennage/Elevator_Right/`
- Create: `scripts/build_hstab_hinge_strip.py`
- Create: `cad/components/empennage/HStab_Hinge_Strip_Stab/`
- Create: `cad/components/empennage/HStab_Hinge_Strip_Elevator/`
- Create: `scripts/build_hstab_control_horn.py`
- Modify: `cad/components/empennage/Control_Horn/`

- [ ] **Step 1: Mirror the left elevator**

Same approach as Task 9. Export to `Elevator_Right/`.

- [ ] **Step 2: Build PETG hinge strips**

Build123d model: 215mm x 2mm x 1.2mm base strip with 27 semicylindrical knuckles (1.2mm OD, 0.6mm ID bore). The stab strip and elevator strip are identical except the knuckle positions are offset by 4mm.

- [ ] **Step 3: Build control horn**

Build123d model: CF-PLA horn with forward extension and mass balance pocket.

- [ ] **Step 4: Render all, write COMPONENT_INFO.md for each, commit**

```bash
git add cad/components/empennage/Elevator_Right/ cad/components/empennage/HStab_Hinge_Strip_Stab/ cad/components/empennage/HStab_Hinge_Strip_Elevator/ cad/components/empennage/Control_Horn/ scripts/build_hstab_hinge_strip.py scripts/build_hstab_control_horn.py
git commit -m "feat: build elevator right, hinge strips, and control horn 3D models"
```

---

## Task 12: Build H-Stab Assembly + Validation

**Files:**
- Create: `scripts/build_hstab_assembly.py`
- Create: `cad/assemblies/empennage/HStab_Assembly/HStab_Assembly.FCStd`
- Create: `cad/assemblies/empennage/HStab_Assembly/renders/`
- Create: `cad/assemblies/empennage/HStab_Assembly/ASSEMBLY_INFO.md`

**Prerequisite:** All component 3D models complete.

- [ ] **Step 1: Write `scripts/build_hstab_assembly.py`**

Load all component STEP files, position them:
1. Left stab half at Y=0 to Y=-215 (root at center)
2. Right stab half at Y=0 to Y=+215 (mirrored)
3. Main spar tube through both halves (centered, 390mm)
4. Rear spar rod through both stab halves (440mm)
5. Hinge strips bonded to stab TE and elevator LE faces
6. Elevator halves attached via hinge knuckle interleave
7. Music wire through all knuckles
8. Elevator stiffener through both elevator halves (440mm)
9. Control horn on left elevator at 50% span
10. Mass balance in horn pocket

Export the assembly as FreeCAD document.

- [ ] **Step 2: Run collision detection**

Use `src/cad/validation/assembly_check.py` to verify:
- No component intersections (boolean AND volume = 0)
- Spar contained within stab shells
- Rear spar contained within stab shells
- Elevator stiffener contained within elevator shells
- Hinge wire passes through all knuckle bores

- [ ] **Step 3: Run containment check**

Verify all internal components (spars, rods, wire) are FULLY inside their shells at every 10mm span station.

- [ ] **Step 4: Take 4 assembly renders**

Save to `cad/assemblies/empennage/HStab_Assembly/renders/`.

- [ ] **Step 5: Visual inspection of renders**

ACTUALLY LOOK at the renders for:
- No protruding spars (Incident 004 lesson)
- Hinge knuckles interleave correctly
- Fillet at VStab junction visible and smooth
- Elevator sits flush with stab at neutral deflection
- Control horn visible on lower surface

- [ ] **Step 6: Write ASSEMBLY_INFO.md**

Full BOM, assembly sequence, mass summary, validation results.

- [ ] **Step 7: Commit**

```bash
git add scripts/build_hstab_assembly.py cad/assemblies/empennage/HStab_Assembly/
git commit -m "feat: complete HStab_Assembly 3D model — collision/containment validated"
```

---

## Task 13: Aero-Structural Assembly Review

**Prerequisite:** Task 12 complete with passing validation.

- [ ] **Step 1: Spawn aerodynamicist to review the ASSEMBLY**

Per CLAUDE.md rules, the agent team must review the assembly integration (not just individual components). The aerodynamicist checks:
- Fillet integration with VStab
- Hinge gap geometry
- Elevator deflection clearance at -20° and +25°
- No interference drag sources visible

- [ ] **Step 2: Spawn structural engineer to review the ASSEMBLY**

The structural engineer checks:
- Spar routing through VStab fin
- Dovetail joint adequacy
- Assembly sequence feasibility
- Mass budget vs actual model volume calculations

- [ ] **Step 3: Address any findings, re-render if needed**

- [ ] **Step 4: Final commit**

```bash
git add -A cad/assemblies/empennage/HStab_Assembly/
git commit -m "feat: HStab_Assembly aero-structural review complete — all checks pass"
```
