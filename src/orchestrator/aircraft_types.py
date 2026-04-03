"""Aircraft type registry for generic, type-driven workflow generation.

The orchestrator does not hardcode any particular aircraft layout.
Instead, the user specifies an aircraft type and mission requirements,
and this registry provides the template from which the workflow is built.

Each aircraft type defines:
- Sub-assemblies that exist for this type
- Which sub-assemblies require aero analysis (vs structural-only)
- Dependency ordering between sub-assemblies
- Type-specific validation criteria (convergence targets)
- Default analysis tools and mesh resolution
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class AircraftType(str, Enum):
    """Supported aircraft categories."""

    SAILPLANE = "SAILPLANE"
    DRONE = "DRONE"
    AEROBATIC = "AEROBATIC"
    PYLON_RACER = "PYLON_RACER"
    INTERCEPTOR = "INTERCEPTOR"
    UAV = "UAV"


class AnalysisLevel(str, Enum):
    """Required analysis rigor for a sub-assembly."""

    NONE = "none"             # Off-the-shelf, no analysis needed
    STRUCTURAL_ONLY = "structural_only"  # No aero surface (e.g., landing gear)
    AERO_STRUCTURAL = "aero_structural"  # Full aero + structural loop
    AERO_CRITICAL = "aero_critical"      # Highest fidelity (main wing, empennage)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SubAssemblyTemplate:
    """Template for a sub-assembly within an aircraft type.

    Attributes:
        name: Canonical name (e.g., "wing", "fuselage", "motor_arm").
        level: Design hierarchy level (1=top, 2=component-group, 3=detail).
        parent: Parent assembly name (None for top-level).
        analysis_level: What kind of analysis this sub-assembly needs.
        depends_on: Other sub-assemblies that must complete first.
        notes: Human-readable description.
    """

    name: str
    level: int = 1
    parent: Optional[str] = None
    analysis_level: AnalysisLevel = AnalysisLevel.AERO_STRUCTURAL
    depends_on: list[str] = field(default_factory=list)
    notes: str = ""


@dataclass(frozen=True)
class ValidationCriteria:
    """Convergence criteria for the final aircraft validation loop.

    Each criterion maps to a pass/fail boolean in the state manager's
    convergence tracking.
    """

    # Aerodynamic
    ld_ratio_target: Optional[float] = None          # Lift-to-drag ratio
    interference_drag_pct: Optional[float] = None     # Max % of total CD
    static_margin_range: Optional[tuple[float, float]] = None  # (% MAC)
    control_authority: Optional[bool] = None          # Surfaces achieve required moments

    # Structural
    structural_sf: Optional[float] = None             # Safety factor (min)
    flutter_margin: Optional[float] = None            # V_flutter / VNE (min)
    buckling_factor: Optional[float] = None           # Lambda (min)

    # Mass & geometry
    auw_target_g: Optional[float] = None              # All-up weight in grams
    auw_tolerance_pct: Optional[float] = None         # Allowed deviation
    no_collisions: bool = True                        # Zero assembly intersections

    # Mission-specific
    endurance_min: Optional[float] = None             # Flight time (minutes)
    max_speed_ms: Optional[float] = None              # VNE in m/s
    climb_rate_ms: Optional[float] = None             # m/s


@dataclass(frozen=True)
class MeshDefaults:
    """Default mesh/solver settings for this aircraft type."""

    cfd_euler_cells: int = 2_000_000
    cfd_rans_coarse_cells: int = 5_000_000
    cfd_rans_fine_cells: int = 10_000_000
    farfield_multiplier: float = 20.0       # x chord
    boundary_layer_yplus: float = 1.0
    fea_max_load_factor_g: float = 10.0
    fea_safety_factor: float = 1.5


@dataclass(frozen=True)
class AircraftTypeDefinition:
    """Complete definition of an aircraft type's workflow template.

    This is the recipe from which the workflow engine builds the process.
    """

    type_id: AircraftType
    display_name: str
    description: str
    sub_assemblies: list[SubAssemblyTemplate]
    validation_criteria: ValidationCriteria
    mesh_defaults: MeshDefaults
    typical_speed_range_ms: tuple[float, float]  # (cruise, VNE)
    typical_reynolds_range: tuple[float, float]   # (min, max) chord-based


# ---------------------------------------------------------------------------
# Type Registry
# ---------------------------------------------------------------------------

_SAILPLANE = AircraftTypeDefinition(
    type_id=AircraftType.SAILPLANE,
    display_name="Thermal Sailplane (F5J / F3J / RES)",
    description=(
        "High-aspect-ratio sailplane optimized for thermal soaring. "
        "Subsonic, low-Reynolds flight. Wing is the dominant aerodynamic "
        "surface. Empennage provides stability. Fuselage is a slender pod-and-boom."
    ),
    sub_assemblies=[
        SubAssemblyTemplate(
            name="wing",
            level=1,
            analysis_level=AnalysisLevel.AERO_CRITICAL,
            notes="Main lifting surface. Multi-panel, blended airfoils.",
        ),
        SubAssemblyTemplate(
            name="fuselage",
            level=1,
            analysis_level=AnalysisLevel.AERO_STRUCTURAL,
            notes="Pod-and-boom. Houses battery, RX, servos, tow hook.",
        ),
        SubAssemblyTemplate(
            name="empennage",
            level=1,
            analysis_level=AnalysisLevel.AERO_CRITICAL,
            depends_on=["wing"],  # Tail sizing depends on wing area
            notes="H-stab + V-stab. Sized by tail volume coefficients.",
        ),
        SubAssemblyTemplate(
            name="control_surfaces",
            level=2,
            parent="wing",
            analysis_level=AnalysisLevel.AERO_STRUCTURAL,
            depends_on=["wing"],
            notes="Ailerons, flaps, elevator, rudder. Hinges, horns, linkages.",
        ),
        SubAssemblyTemplate(
            name="propulsion",
            level=1,
            analysis_level=AnalysisLevel.STRUCTURAL_ONLY,
            notes="Motor, ESC, propeller, spinner. Fixed off-shelf components.",
        ),
        SubAssemblyTemplate(
            name="landing_gear",
            level=1,
            analysis_level=AnalysisLevel.STRUCTURAL_ONLY,
            notes="Tow hook or belly skid. Minimal.",
        ),
    ],
    validation_criteria=ValidationCriteria(
        ld_ratio_target=15.0,
        interference_drag_pct=5.0,
        static_margin_range=(5.0, 15.0),
        control_authority=True,
        structural_sf=1.5,
        flutter_margin=1.2,
        buckling_factor=1.0,
        auw_target_g=800.0,
        auw_tolerance_pct=5.0,
        no_collisions=True,
    ),
    mesh_defaults=MeshDefaults(
        cfd_euler_cells=2_000_000,
        cfd_rans_coarse_cells=5_000_000,
        cfd_rans_fine_cells=10_000_000,
        farfield_multiplier=20.0,
        boundary_layer_yplus=1.0,
        fea_max_load_factor_g=10.0,
        fea_safety_factor=1.5,
    ),
    typical_speed_range_ms=(5.0, 30.0),  # 5 m/s cruise, 30 m/s VNE
    typical_reynolds_range=(80000, 300000),
)

_DRONE = AircraftTypeDefinition(
    type_id=AircraftType.DRONE,
    display_name="Multirotor Drone / UAV",
    description=(
        "Multirotor aircraft. No conventional wing. Lift comes from propellers. "
        "Fuselage is a central body with motor arms. Focus on endurance, "
        "payload, and stability."
    ),
    sub_assemblies=[
        SubAssemblyTemplate(
            name="body",
            level=1,
            analysis_level=AnalysisLevel.STRUCTURAL_ONLY,
            notes="Central frame. Houses FC, battery, payload.",
        ),
        SubAssemblyTemplate(
            name="motor_arms",
            level=1,
            analysis_level=AnalysisLevel.AERO_STRUCTURAL,
            notes="Arms connecting motors to body. Drag and vibration analysis.",
        ),
        SubAssemblyTemplate(
            name="propulsion",
            level=1,
            analysis_level=AnalysisLevel.AERO_CRITICAL,
            notes="Motors, ESCs, propellers. Thrust and efficiency are critical.",
        ),
        SubAssemblyTemplate(
            name="landing_gear",
            level=1,
            analysis_level=AnalysisLevel.STRUCTURAL_ONLY,
            notes="Skids or retractable gear.",
        ),
        SubAssemblyTemplate(
            name="payload_bay",
            level=2,
            parent="body",
            analysis_level=AnalysisLevel.STRUCTURAL_ONLY,
            notes="Camera gimbal, sensors, or drop mechanism.",
        ),
    ],
    validation_criteria=ValidationCriteria(
        ld_ratio_target=None,  # Not applicable
        interference_drag_pct=10.0,
        structural_sf=2.0,  # Higher SF for safety over people
        flutter_margin=1.5,
        auw_target_g=1500.0,
        auw_tolerance_pct=5.0,
        no_collisions=True,
        endurance_min=20.0,
    ),
    mesh_defaults=MeshDefaults(
        cfd_euler_cells=3_000_000,
        cfd_rans_coarse_cells=8_000_000,
        cfd_rans_fine_cells=15_000_000,
        farfield_multiplier=15.0,
        boundary_layer_yplus=1.0,
        fea_max_load_factor_g=5.0,
        fea_safety_factor=2.0,
    ),
    typical_speed_range_ms=(0.0, 20.0),
    typical_reynolds_range=(50000, 200000),
)

_AEROBATIC = AircraftTypeDefinition(
    type_id=AircraftType.AEROBATIC,
    display_name="Aerobatic Aircraft (F3A / Pattern)",
    description=(
        "Precision aerobatic aircraft. Symmetrical airfoils, thick wing, "
        "large control surfaces with high deflection. Short, stout fuselage. "
        "Focus on control authority, precision, and structural strength."
    ),
    sub_assemblies=[
        SubAssemblyTemplate(
            name="wing",
            level=1,
            analysis_level=AnalysisLevel.AERO_CRITICAL,
            notes="Thick symmetrical airfoil. Large ailerons. May be single-piece.",
        ),
        SubAssemblyTemplate(
            name="fuselage",
            level=1,
            analysis_level=AnalysisLevel.AERO_STRUCTURAL,
            notes="Short, stout. Motor upfront. Tail surfaces on long moment arm.",
        ),
        SubAssemblyTemplate(
            name="empennage",
            level=1,
            analysis_level=AnalysisLevel.AERO_CRITICAL,
            depends_on=["wing"],
            notes="Large symmetrical stab surfaces. Full-flying elevator possible.",
        ),
        SubAssemblyTemplate(
            name="control_surfaces",
            level=2,
            parent="wing",
            analysis_level=AnalysisLevel.AERO_STRUCTURAL,
            depends_on=["wing"],
            notes="Large deflection ailerons, elevator, rudder. High rate servos.",
        ),
        SubAssemblyTemplate(
            name="propulsion",
            level=1,
            analysis_level=AnalysisLevel.STRUCTURAL_ONLY,
            notes="High-power motor, large prop. Thrust-to-weight > 1:1.",
        ),
        SubAssemblyTemplate(
            name="landing_gear",
            level=1,
            analysis_level=AnalysisLevel.STRUCTURAL_ONLY,
            notes="Tricycle or tail-dragger retractable gear.",
        ),
    ],
    validation_criteria=ValidationCriteria(
        ld_ratio_target=8.0,
        interference_drag_pct=8.0,
        static_margin_range=(-5.0, 10.0),  # Can be neutral or slightly unstable
        control_authority=True,
        structural_sf=2.5,  # High G maneuvers
        flutter_margin=1.5,
        auw_target_g=2500.0,
        auw_tolerance_pct=5.0,
        no_collisions=True,
        max_speed_ms=50.0,
        climb_rate_ms=15.0,
    ),
    mesh_defaults=MeshDefaults(
        cfd_euler_cells=3_000_000,
        cfd_rans_coarse_cells=8_000_000,
        cfd_rans_fine_cells=15_000_000,
        farfield_multiplier=15.0,
        boundary_layer_yplus=1.0,
        fea_max_load_factor_g=15.0,  # High G aerobatics
        fea_safety_factor=2.5,
    ),
    typical_speed_range_ms=(10.0, 50.0),
    typical_reynolds_range=(150000, 500000),
)

_PYLON_RACER = AircraftTypeDefinition(
    type_id=AircraftType.PYLON_RACER,
    display_name="Pylon Racer (F5D / Q500)",
    description=(
        "High-speed pylon racing aircraft. Thin airfoils, minimum drag, "
        "slender fuselage. Minimal tail surfaces. Focus on raw speed and "
        "turn performance at high G."
    ),
    sub_assemblies=[
        SubAssemblyTemplate(
            name="wing",
            level=1,
            analysis_level=AnalysisLevel.AERO_CRITICAL,
            notes="Thin, low-drag airfoil. May have very low aspect ratio for turn performance.",
        ),
        SubAssemblyTemplate(
            name="fuselage",
            level=1,
            analysis_level=AnalysisLevel.AERO_STRUCTURAL,
            notes="Slender, minimal cross-section. Engine and fuel upfront.",
        ),
        SubAssemblyTemplate(
            name="empennage",
            level=1,
            analysis_level=AnalysisLevel.AERO_CRITICAL,
            depends_on=["wing"],
            notes="Minimal tail surfaces for stability at speed.",
        ),
        SubAssemblyTemplate(
            name="control_surfaces",
            level=2,
            parent="wing",
            analysis_level=AnalysisLevel.AERO_STRUCTURAL,
            depends_on=["wing"],
            notes="Small, high-rate ailerons and elevator.",
        ),
        SubAssemblyTemplate(
            name="propulsion",
            level=1,
            analysis_level=AnalysisLevel.AERO_CRITICAL,
            notes="High-RPM motor, racing prop. Thrust is critical.",
        ),
        SubAssemblyTemplate(
            name="landing_gear",
            level=1,
            analysis_level=AnalysisLevel.STRUCTURAL_ONLY,
            notes="Fixed or retractable. Hand-launch possible.",
        ),
    ],
    validation_criteria=ValidationCriteria(
        ld_ratio_target=6.0,
        interference_drag_pct=3.0,
        static_margin_range=(5.0, 12.0),
        control_authority=True,
        structural_sf=2.0,
        flutter_margin=1.5,
        auw_target_g=800.0,
        auw_tolerance_pct=3.0,
        no_collisions=True,
        max_speed_ms=80.0,
    ),
    mesh_defaults=MeshDefaults(
        cfd_euler_cells=4_000_000,
        cfd_rans_coarse_cells=10_000_000,
        cfd_rans_fine_cells=20_000_000,
        farfield_multiplier=25.0,
        boundary_layer_yplus=0.5,  # Tight BL for high-speed accuracy
        fea_max_load_factor_g=12.0,
        fea_safety_factor=2.0,
    ),
    typical_speed_range_ms=(25.0, 80.0),
    typical_reynolds_range=(200000, 800000),
)

_INTERCEPTOR = AircraftTypeDefinition(
    type_id=AircraftType.INTERCEPTOR,
    display_name="Interceptor (High-Speed Combat)",
    description=(
        "High-speed interceptor aircraft. Delta or swept wing, "
        "thrust-to-weight >= 1.0, extremely fast. Focus on speed, "
        "maneuverability, and structural margins at high dynamic pressure."
    ),
    sub_assemblies=[
        SubAssemblyTemplate(
            name="wing",
            level=1,
            analysis_level=AnalysisLevel.AERO_CRITICAL,
            notes="Delta or swept. May be thin with sharp LE.",
        ),
        SubAssemblyTemplate(
            name="fuselage",
            level=1,
            analysis_level=AnalysisLevel.AERO_STRUCTURAL,
            notes="Sleek, area-ruled. Houses all internals.",
        ),
        SubAssemblyTemplate(
            name="empennage",
            level=1,
            analysis_level=AnalysisLevel.AERO_CRITICAL,
            depends_on=["wing"],
            notes="May use delta canard or V-tail.",
        ),
        SubAssemblyTemplate(
            name="control_surfaces",
            level=2,
            parent="wing",
            analysis_level=AnalysisLevel.AERO_STRUCTURAL,
            depends_on=["wing"],
            notes="Elevons, canards, or conventional.",
        ),
        SubAssemblyTemplate(
            name="propulsion",
            level=1,
            analysis_level=AnalysisLevel.AERO_CRITICAL,
            notes="EDF or high-power prop. Duct design matters.",
        ),
        SubAssemblyTemplate(
            name="landing_gear",
            level=1,
            analysis_level=AnalysisLevel.STRUCTURAL_ONLY,
            notes="Retractable gear or hand-launch.",
        ),
    ],
    validation_criteria=ValidationCriteria(
        ld_ratio_target=5.0,
        interference_drag_pct=3.0,
        static_margin_range=(3.0, 10.0),
        control_authority=True,
        structural_sf=2.0,
        flutter_margin=1.5,
        auw_target_g=2000.0,
        auw_tolerance_pct=5.0,
        no_collisions=True,
        max_speed_ms=100.0,
        climb_rate_ms=30.0,
    ),
    mesh_defaults=MeshDefaults(
        cfd_euler_cells=5_000_000,
        cfd_rans_coarse_cells=12_000_000,
        cfd_rans_fine_cells=25_000_000,
        farfield_multiplier=30.0,
        boundary_layer_yplus=0.5,
        fea_max_load_factor_g=15.0,
        fea_safety_factor=2.0,
    ),
    typical_speed_range_ms=(30.0, 100.0),
    typical_reynolds_range=(300000, 1000000),
)

_UAV = AircraftTypeDefinition(
    type_id=AircraftType.UAV,
    display_name="Fixed-Wing UAV / Survey Platform",
    description=(
        "Fixed-wing unmanned aerial vehicle for survey, mapping, or cargo. "
        "High endurance, stable platform, payload bay. May have conventional "
        "or flying-wing layout."
    ),
    sub_assemblies=[
        SubAssemblyTemplate(
            name="wing",
            level=1,
            analysis_level=AnalysisLevel.AERO_CRITICAL,
            notes="High-aspect-ratio for endurance. May be modular.",
        ),
        SubAssemblyTemplate(
            name="fuselage",
            level=1,
            analysis_level=AnalysisLevel.AERO_STRUCTURAL,
            notes="Payload bay, avionics, battery bay.",
        ),
        SubAssemblyTemplate(
            name="empennage",
            level=1,
            analysis_level=AnalysisLevel.AERO_CRITICAL,
            depends_on=["wing"],
            notes="Conventional tail or V-tail.",
        ),
        SubAssemblyTemplate(
            name="control_surfaces",
            level=2,
            parent="wing",
            analysis_level=AnalysisLevel.AERO_STRUCTURAL,
            depends_on=["wing"],
            notes="Standard control surfaces. Autopilot-driven.",
        ),
        SubAssemblyTemplate(
            name="propulsion",
            level=1,
            analysis_level=AnalysisLevel.STRUCTURAL_ONLY,
            notes="Electric motor, folding prop for soaring.",
        ),
        SubAssemblyTemplate(
            name="landing_gear",
            level=1,
            analysis_level=AnalysisLevel.STRUCTURAL_ONLY,
            notes="Belly land or fixed gear.",
        ),
        SubAssemblyTemplate(
            name="payload_bay",
            level=2,
            parent="fuselage",
            analysis_level=AnalysisLevel.STRUCTURAL_ONLY,
            notes="Camera, sensors, or cargo.",
        ),
    ],
    validation_criteria=ValidationCriteria(
        ld_ratio_target=12.0,
        interference_drag_pct=5.0,
        static_margin_range=(10.0, 20.0),  # Very stable
        control_authority=True,
        structural_sf=2.0,
        flutter_margin=1.5,
        auw_target_g=3000.0,
        auw_tolerance_pct=5.0,
        no_collisions=True,
        endurance_min=45.0,
    ),
    mesh_defaults=MeshDefaults(
        cfd_euler_cells=3_000_000,
        cfd_rans_coarse_cells=8_000_000,
        cfd_rans_fine_cells=15_000_000,
        farfield_multiplier=20.0,
        boundary_layer_yplus=1.0,
        fea_max_load_factor_g=5.0,
        fea_safety_factor=2.0,
    ),
    typical_speed_range_ms=(8.0, 25.0),
    typical_reynolds_range=(100000, 400000),
)


# ---------------------------------------------------------------------------
# Public Registry
# ---------------------------------------------------------------------------

AIRCRAFT_TYPE_REGISTRY: dict[AircraftType, AircraftTypeDefinition] = {
    AircraftType.SAILPLANE: _SAILPLANE,
    AircraftType.DRONE: _DRONE,
    AircraftType.AEROBATIC: _AEROBATIC,
    AircraftType.PYLON_RACER: _PYLON_RACER,
    AircraftType.INTERCEPTOR: _INTERCEPTOR,
    AircraftType.UAV: _UAV,
}


def get_type_definition(aircraft_type: AircraftType) -> AircraftTypeDefinition:
    """Look up an aircraft type definition.

    Raises:
        KeyError: If the type is not in the registry.
    """
    return AIRCRAFT_TYPE_REGISTRY[aircraft_type]


def list_types() -> list[dict[str, str]]:
    """Return a summary of all registered aircraft types."""
    return [
        {
            "id": t.value,
            "name": d.display_name,
            "description": d.description[:80] + "...",
            "sub_assemblies": [sa.name for sa in d.sub_assemblies],
        }
        for t, d in AIRCRAFT_TYPE_REGISTRY.items()
    ]
