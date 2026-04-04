"""Aircraft type reference templates for workflow generation.

IMPORTANT: These templates are REFERENCE EXAMPLES, not a limiting registry.
The aircraft type is a free-form string determined by the LLM during the
initialization wizard. The only constraint is: heavier-than-air, exposed
to airflow.

The LLM can use these templates as starting points and modify them, or
create entirely new configurations from scratch. The workflow engine
accepts any aircraft type string.

Templates provide sensible defaults for:
- Sub-assemblies and their analysis levels
- Validation criteria (convergence targets)
- Mesh/solver defaults
- Typical operating conditions
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class AircraftType(str, Enum):
    """Reference aircraft templates. NOT a limiting registry.

    The LLM can use any free-form string as aircraft type. These enum
    values are shortcuts to pre-built templates for common categories.
    """

    SAILPLANE = "SAILPLANE"
    DRONE = "DRONE"
    AEROBATIC = "AEROBATIC"
    PYLON_RACER = "PYLON_RACER"
    INTERCEPTOR = "INTERCEPTOR"
    UAV = "UAV"
    PAPER_PLANE = "PAPER_PLANE"


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
    """Convergence criteria for the final aircraft validation loop."""

    # Aerodynamic
    ld_ratio_target: Optional[float] = None
    interference_drag_pct: Optional[float] = None
    static_margin_range: Optional[tuple[float, float]] = None
    control_authority: Optional[bool] = None

    # Structural
    structural_sf: Optional[float] = None
    flutter_margin: Optional[float] = None
    buckling_factor: Optional[float] = None

    # Mass & geometry
    auw_target_g: Optional[float] = None
    auw_tolerance_pct: Optional[float] = None
    no_collisions: bool = True

    # Mission-specific
    endurance_min: Optional[float] = None
    max_speed_ms: Optional[float] = None
    climb_rate_ms: Optional[float] = None


@dataclass(frozen=True)
class MeshDefaults:
    """Default mesh/solver settings for this aircraft type."""

    cfd_euler_cells: int = 2_000_000
    cfd_rans_coarse_cells: int = 5_000_000
    cfd_rans_fine_cells: int = 10_000_000
    farfield_multiplier: float = 20.0
    boundary_layer_yplus: float = 1.0
    fea_max_load_factor_g: float = 10.0
    fea_safety_factor: float = 1.5


@dataclass(frozen=True)
class AircraftTypeDefinition:
    """Complete definition of an aircraft type's workflow template.

    This is a REFERENCE template, not a constraint. The LLM can modify
    any field or create entirely custom configurations.
    """

    type_id: str  # Free-form string, not limited to AircraftType enum
    display_name: str
    description: str
    sub_assemblies: list[SubAssemblyTemplate]
    validation_criteria: ValidationCriteria
    mesh_defaults: MeshDefaults
    typical_speed_range_ms: tuple[float, float]
    typical_reynolds_range: tuple[float, float]


# ---------------------------------------------------------------------------
# Reference Template Library
# ---------------------------------------------------------------------------

_SAILPLANE = AircraftTypeDefinition(
    type_id=AircraftType.SAILPLANE.value,
    display_name="Thermal Sailplane (F5J / F3J / RES)",
    description=(
        "High-aspect-ratio sailplane optimized for thermal soaring. "
        "Subsonic, low-Reynolds flight. Wing is the dominant aerodynamic "
        "surface. Empennage provides stability. Fuselage is a slender pod-and-boom."
    ),
    sub_assemblies=[
        SubAssemblyTemplate(
            name="wing", level=1,
            analysis_level=AnalysisLevel.AERO_CRITICAL,
            notes="Main lifting surface. Multi-panel, blended airfoils.",
        ),
        SubAssemblyTemplate(
            name="fuselage", level=1,
            analysis_level=AnalysisLevel.AERO_STRUCTURAL,
            notes="Pod-and-boom. Houses battery, RX, servos, tow hook.",
        ),
        SubAssemblyTemplate(
            name="empennage", level=1,
            analysis_level=AnalysisLevel.AERO_CRITICAL,
            depends_on=["wing"],
            notes="H-stab + V-stab. Sized by tail volume coefficients.",
        ),
        SubAssemblyTemplate(
            name="control_surfaces", level=2, parent="wing",
            analysis_level=AnalysisLevel.AERO_STRUCTURAL,
            depends_on=["wing"],
            notes="Ailerons, flaps, elevator, rudder. Hinges, horns, linkages.",
        ),
        SubAssemblyTemplate(
            name="propulsion", level=1,
            analysis_level=AnalysisLevel.STRUCTURAL_ONLY,
            notes="Motor, ESC, propeller, spinner. Fixed off-shelf components.",
        ),
        SubAssemblyTemplate(
            name="landing_gear", level=1,
            analysis_level=AnalysisLevel.STRUCTURAL_ONLY,
            notes="Tow hook or belly skid. Minimal.",
        ),
    ],
    validation_criteria=ValidationCriteria(
        ld_ratio_target=15.0, interference_drag_pct=5.0,
        static_margin_range=(5.0, 15.0), control_authority=True,
        structural_sf=1.5, flutter_margin=1.2, buckling_factor=1.0,
        auw_target_g=800.0, auw_tolerance_pct=5.0, no_collisions=True,
    ),
    mesh_defaults=MeshDefaults(),
    typical_speed_range_ms=(5.0, 30.0),
    typical_reynolds_range=(80000, 300000),
)

_DRONE = AircraftTypeDefinition(
    type_id=AircraftType.DRONE.value,
    display_name="Multirotor Drone / UAV",
    description="Multirotor aircraft. Lift from propellers, not conventional wing.",
    sub_assemblies=[
        SubAssemblyTemplate(name="body", level=1, analysis_level=AnalysisLevel.STRUCTURAL_ONLY),
        SubAssemblyTemplate(name="motor_arms", level=1, analysis_level=AnalysisLevel.AERO_STRUCTURAL),
        SubAssemblyTemplate(name="propulsion", level=1, analysis_level=AnalysisLevel.AERO_CRITICAL),
        SubAssemblyTemplate(name="landing_gear", level=1, analysis_level=AnalysisLevel.STRUCTURAL_ONLY),
    ],
    validation_criteria=ValidationCriteria(
        structural_sf=2.0, flutter_margin=1.5, auw_target_g=1500.0,
        no_collisions=True, endurance_min=20.0,
    ),
    mesh_defaults=MeshDefaults(fea_safety_factor=2.0),
    typical_speed_range_ms=(0.0, 20.0),
    typical_reynolds_range=(50000, 200000),
)

_AEROBATIC = AircraftTypeDefinition(
    type_id=AircraftType.AEROBATIC.value,
    display_name="Aerobatic Aircraft (F3A / Pattern)",
    description="Precision aerobatic aircraft. Symmetrical airfoils, high control authority.",
    sub_assemblies=[
        SubAssemblyTemplate(name="wing", level=1, analysis_level=AnalysisLevel.AERO_CRITICAL),
        SubAssemblyTemplate(name="fuselage", level=1, analysis_level=AnalysisLevel.AERO_STRUCTURAL),
        SubAssemblyTemplate(name="empennage", level=1, analysis_level=AnalysisLevel.AERO_CRITICAL, depends_on=["wing"]),
        SubAssemblyTemplate(name="control_surfaces", level=2, parent="wing", analysis_level=AnalysisLevel.AERO_STRUCTURAL, depends_on=["wing"]),
        SubAssemblyTemplate(name="propulsion", level=1, analysis_level=AnalysisLevel.STRUCTURAL_ONLY),
        SubAssemblyTemplate(name="landing_gear", level=1, analysis_level=AnalysisLevel.STRUCTURAL_ONLY),
    ],
    validation_criteria=ValidationCriteria(
        ld_ratio_target=8.0, structural_sf=2.5, flutter_margin=1.5,
        auw_target_g=2500.0, no_collisions=True, max_speed_ms=50.0,
    ),
    mesh_defaults=MeshDefaults(fea_max_load_factor_g=15.0, fea_safety_factor=2.5),
    typical_speed_range_ms=(10.0, 50.0),
    typical_reynolds_range=(150000, 500000),
)

_PYLON_RACER = AircraftTypeDefinition(
    type_id=AircraftType.PYLON_RACER.value,
    display_name="Pylon Racer (F5D / Q500)",
    description="High-speed pylon racing. Thin airfoils, minimum drag.",
    sub_assemblies=[
        SubAssemblyTemplate(name="wing", level=1, analysis_level=AnalysisLevel.AERO_CRITICAL),
        SubAssemblyTemplate(name="fuselage", level=1, analysis_level=AnalysisLevel.AERO_STRUCTURAL),
        SubAssemblyTemplate(name="empennage", level=1, analysis_level=AnalysisLevel.AERO_CRITICAL, depends_on=["wing"]),
        SubAssemblyTemplate(name="propulsion", level=1, analysis_level=AnalysisLevel.AERO_CRITICAL),
    ],
    validation_criteria=ValidationCriteria(
        ld_ratio_target=6.0, structural_sf=2.0, flutter_margin=1.5,
        auw_target_g=800.0, no_collisions=True, max_speed_ms=80.0,
    ),
    mesh_defaults=MeshDefaults(boundary_layer_yplus=0.5, fea_safety_factor=2.0),
    typical_speed_range_ms=(25.0, 80.0),
    typical_reynolds_range=(200000, 800000),
)

_INTERCEPTOR = AircraftTypeDefinition(
    type_id=AircraftType.INTERCEPTOR.value,
    display_name="Interceptor (High-Speed Combat)",
    description="High-speed interceptor. Delta or swept wing, T/W >= 1.0.",
    sub_assemblies=[
        SubAssemblyTemplate(name="wing", level=1, analysis_level=AnalysisLevel.AERO_CRITICAL),
        SubAssemblyTemplate(name="fuselage", level=1, analysis_level=AnalysisLevel.AERO_STRUCTURAL),
        SubAssemblyTemplate(name="empennage", level=1, analysis_level=AnalysisLevel.AERO_CRITICAL, depends_on=["wing"]),
        SubAssemblyTemplate(name="propulsion", level=1, analysis_level=AnalysisLevel.AERO_CRITICAL),
    ],
    validation_criteria=ValidationCriteria(
        structural_sf=2.0, flutter_margin=1.5, auw_target_g=2000.0,
        no_collisions=True, max_speed_ms=100.0,
    ),
    mesh_defaults=MeshDefaults(boundary_layer_yplus=0.5, fea_safety_factor=2.0),
    typical_speed_range_ms=(30.0, 100.0),
    typical_reynolds_range=(300000, 1000000),
)

_UAV = AircraftTypeDefinition(
    type_id=AircraftType.UAV.value,
    display_name="Fixed-Wing UAV / Survey Platform",
    description="Fixed-wing UAV for survey, mapping, or cargo. High endurance.",
    sub_assemblies=[
        SubAssemblyTemplate(name="wing", level=1, analysis_level=AnalysisLevel.AERO_CRITICAL),
        SubAssemblyTemplate(name="fuselage", level=1, analysis_level=AnalysisLevel.AERO_STRUCTURAL),
        SubAssemblyTemplate(name="empennage", level=1, analysis_level=AnalysisLevel.AERO_CRITICAL, depends_on=["wing"]),
        SubAssemblyTemplate(name="propulsion", level=1, analysis_level=AnalysisLevel.STRUCTURAL_ONLY),
        SubAssemblyTemplate(name="payload_bay", level=2, parent="fuselage", analysis_level=AnalysisLevel.STRUCTURAL_ONLY),
    ],
    validation_criteria=ValidationCriteria(
        ld_ratio_target=12.0, structural_sf=2.0, flutter_margin=1.5,
        auw_target_g=3000.0, no_collisions=True, endurance_min=45.0,
    ),
    mesh_defaults=MeshDefaults(fea_safety_factor=2.0),
    typical_speed_range_ms=(8.0, 25.0),
    typical_reynolds_range=(100000, 400000),
)

_PAPER_PLANE = AircraftTypeDefinition(
    type_id=AircraftType.PAPER_PLANE.value,
    display_name="Paper Airplane (Folded Sheet)",
    description="Paper airplane from a single folded sheet. Manual manufacturing.",
    sub_assemblies=[
        SubAssemblyTemplate(
            name="paper_plane", level=1,
            analysis_level=AnalysisLevel.AERO_STRUCTURAL,
            notes="Single folded component. Aero agent optimizes shape within fold constraints.",
        ),
    ],
    validation_criteria=ValidationCriteria(auw_target_g=5.0, no_collisions=True),
    mesh_defaults=MeshDefaults(cfd_euler_cells=0, cfd_rans_coarse_cells=0, cfd_rans_fine_cells=0),
    typical_speed_range_ms=(2.0, 8.0),
    typical_reynolds_range=(20000, 80000),
)


# ---------------------------------------------------------------------------
# Template Library (reference only — LLM can use any free-form type)
# ---------------------------------------------------------------------------

REFERENCE_TEMPLATES: dict[str, AircraftTypeDefinition] = {
    AircraftType.SAILPLANE.value: _SAILPLANE,
    AircraftType.DRONE.value: _DRONE,
    AircraftType.AEROBATIC.value: _AEROBATIC,
    AircraftType.PYLON_RACER.value: _PYLON_RACER,
    AircraftType.INTERCEPTOR.value: _INTERCEPTOR,
    AircraftType.UAV.value: _UAV,
    AircraftType.PAPER_PLANE.value: _PAPER_PLANE,
}

# Legacy alias — prefer REFERENCE_TEMPLATES
AIRCRAFT_TYPE_REGISTRY = REFERENCE_TEMPLATES


def get_type_definition(aircraft_type: AircraftType | str) -> AircraftTypeDefinition:
    """Look up a reference template by type ID.

    This is for REFERENCE only. The LLM can create entirely custom
    configurations. If the type is not in the template library, a
    KeyError is raised — the caller should handle this by asking the
    LLM to define the configuration from scratch.

    Raises:
        KeyError: If the type is not in the reference library.
    """
    key = aircraft_type.value if isinstance(aircraft_type, AircraftType) else aircraft_type
    return REFERENCE_TEMPLATES[key]


def list_types() -> list[dict[str, str]]:
    """Return a summary of reference templates (for display, not limitation)."""
    return [
        {
            "id": type_id,
            "name": defn.display_name,
            "description": defn.description[:80] + "..." if len(defn.description) > 80 else defn.description,
            "sub_assemblies": [sa.name for sa in defn.sub_assemblies],
        }
        for type_id, defn in REFERENCE_TEMPLATES.items()
    ]
