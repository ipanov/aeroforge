"""Base component classes for the parametric design system.

Every physical part in the sailplane is a Component - from wing spars
down to individual M2 screws. Components carry:
- Parametric specifications (dimensions, material)
- Mass properties (weight, center of gravity, inertia tensor)
- Local coordinate system (origin, orientation)
- Dependency relationships (what depends on this component)

All dimensions in mm, weights in grams.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Optional

import numpy as np
from pydantic import BaseModel, Field, model_validator


class Material(str, Enum):
    """Printable and structural materials."""
    PLA = "pla"
    LW_PLA = "lw_pla"          # Lightweight foamed PLA
    PETG = "petg"
    TPU = "tpu"                 # Flexible (hinges, fairings)
    CARBON_ROD = "carbon_rod"   # Pultruded carbon fiber rod
    CARBON_TUBE = "carbon_tube" # Carbon fiber tube
    STEEL = "steel"             # Screws, pins
    ALUMINUM = "aluminum"       # Horns, clevises
    BALSA = "balsa"             # Optional lightweight filler
    DEPRON = "depron"           # Foam sheet


# Material densities in g/cm³
MATERIAL_DENSITY: dict[str, float] = {
    Material.PLA: 1.24,
    Material.LW_PLA: 0.62,     # ~50% foamed
    Material.PETG: 1.27,
    Material.TPU: 1.21,
    Material.CARBON_ROD: 1.60,
    Material.CARBON_TUBE: 1.55,
    Material.STEEL: 7.85,
    Material.ALUMINUM: 2.70,
    Material.BALSA: 0.16,
    Material.DEPRON: 0.04,
}


class Vector3(BaseModel):
    """3D vector for positions and directions."""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def as_array(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z])

    def __add__(self, other: Vector3) -> Vector3:
        return Vector3(x=self.x + other.x, y=self.y + other.y, z=self.z + other.z)

    def __sub__(self, other: Vector3) -> Vector3:
        return Vector3(x=self.x - other.x, y=self.y - other.y, z=self.z - other.z)


class BoundingBox(BaseModel):
    """Axis-aligned bounding box."""
    min_point: Vector3 = Field(default_factory=Vector3)
    max_point: Vector3 = Field(default_factory=Vector3)

    @property
    def size(self) -> Vector3:
        return self.max_point - self.min_point

    @property
    def center(self) -> Vector3:
        return Vector3(
            x=(self.min_point.x + self.max_point.x) / 2,
            y=(self.min_point.y + self.max_point.y) / 2,
            z=(self.min_point.z + self.max_point.z) / 2,
        )


class LocalFrame(BaseModel):
    """Local coordinate system for a component."""
    origin: Vector3 = Field(default_factory=Vector3)
    # Rotation as euler angles (degrees) - roll, pitch, yaw
    rotation: Vector3 = Field(default_factory=Vector3)


class MassProperties(BaseModel):
    """Mass and inertia properties."""
    mass: float = 0.0                                      # grams
    center_of_gravity: Vector3 = Field(default_factory=Vector3)  # mm, in local frame
    # Inertia tensor (3x3) stored as flat list for Pydantic serialization
    inertia_tensor: list[float] = Field(default_factory=lambda: [0.0] * 9)

    @property
    def inertia_matrix(self) -> np.ndarray:
        return np.array(self.inertia_tensor).reshape(3, 3)


class ComponentSpec(BaseModel):
    """Base specification for any component.

    Subclass this for specific component types (ServoSpec, WingRibSpec, etc.).
    All parametric dimensions go here so they are validated and tracked.
    """
    name: str
    description: str = ""
    material: Material = Material.PLA
    # Parametric dimensions - override in subclasses
    # This dict holds any dimension that should trigger dependency updates
    parameters: dict[str, float] = Field(default_factory=dict)

    model_config = {"frozen": False}


class Component(ABC):
    """Base class for all physical parts in the design.

    Every component has:
    - A unique ID for dependency graph tracking
    - A specification (parametric dimensions)
    - Mass properties (computed from geometry)
    - A local coordinate frame
    - A bounding box

    Subclasses must implement:
    - _compute_geometry(): generate Build123d geometry from spec
    - _compute_mass_properties(): calculate mass/CG/inertia
    """

    def __init__(self, spec: ComponentSpec) -> None:
        self.id: str = str(uuid.uuid4())
        self.spec: ComponentSpec = spec
        self.local_frame: LocalFrame = LocalFrame()
        self.mass_props: MassProperties = MassProperties()
        self.bounding_box: BoundingBox = BoundingBox()
        self._geometry: Any = None  # Build123d Part/Compound
        self._dirty: bool = True    # Needs recomputation
        self._validate_spec()

    @property
    def name(self) -> str:
        return self.spec.name

    @property
    def mass(self) -> float:
        """Component mass in grams."""
        return self.mass_props.mass

    @property
    def cg(self) -> Vector3:
        """Center of gravity in local frame (mm)."""
        return self.mass_props.center_of_gravity

    def update_spec(self, **kwargs: Any) -> set[str]:
        """Update specification parameters.

        Returns:
            Set of parameter names that actually changed.
        """
        changed: set[str] = set()
        for key, value in kwargs.items():
            if hasattr(self.spec, key):
                old_value = getattr(self.spec, key)
                if old_value != value:
                    setattr(self.spec, key, value)
                    changed.add(key)
            elif key in self.spec.parameters:
                if self.spec.parameters[key] != value:
                    self.spec.parameters[key] = value
                    changed.add(key)

        if changed:
            self._dirty = True
            self._validate_spec()

        return changed

    def build(self) -> Any:
        """Build or rebuild geometry if dirty.

        Returns:
            Build123d geometry object.
        """
        if self._dirty:
            self._geometry = self._compute_geometry()
            self.mass_props = self._compute_mass_properties()
            self.bounding_box = self._compute_bounding_box()
            self._dirty = False
        return self._geometry

    def _validate_spec(self) -> None:
        """Validate the component spec. Override for custom validation."""
        pass

    @abstractmethod
    def _compute_geometry(self) -> Any:
        """Generate Build123d geometry from spec. Must be implemented by subclasses."""
        ...

    def _compute_mass_properties(self) -> MassProperties:
        """Compute mass properties from geometry and material.

        Default implementation uses Build123d volume * material density.
        Override for off-the-shelf components with known mass.
        """
        if self._geometry is None:
            return MassProperties()

        try:
            volume_mm3 = self._geometry.volume  # Build123d volumes are in mm³
            volume_cm3 = volume_mm3 / 1000.0
            density = MATERIAL_DENSITY.get(self.spec.material, 1.24)
            mass = volume_cm3 * density

            # Build123d center of mass
            com = self._geometry.center()
            cg = Vector3(x=com.X, y=com.Y, z=com.Z)

            return MassProperties(mass=mass, center_of_gravity=cg)
        except (AttributeError, Exception):
            return MassProperties()

    def _compute_bounding_box(self) -> BoundingBox:
        """Compute bounding box from geometry."""
        if self._geometry is None:
            return BoundingBox()

        try:
            bb = self._geometry.bounding_box()
            return BoundingBox(
                min_point=Vector3(x=bb.min.X, y=bb.min.Y, z=bb.min.Z),
                max_point=Vector3(x=bb.max.X, y=bb.max.Y, z=bb.max.Z),
            )
        except (AttributeError, Exception):
            return BoundingBox()

    def export_step(self, path: str) -> None:
        """Export component as STEP file."""
        from build123d import export_step
        if self._geometry is None:
            self.build()
        export_step(self._geometry, path)

    def export_stl(self, path: str) -> None:
        """Export component as STL file."""
        from build123d import export_stl
        if self._geometry is None:
            self.build()
        export_stl(self._geometry, path)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, mass={self.mass:.1f}g)"


class OffShelfComponent(Component):
    """Off-the-shelf component with fixed dimensions from datasheets.

    Servos, motors, screws, bearings, etc. These have fixed mass and
    dimensions - they don't change parametrically. Their geometry is
    a simplified bounding-box or detailed model from datasheet dims.
    """

    def __init__(self, spec: ComponentSpec, fixed_mass: float) -> None:
        self._fixed_mass = fixed_mass
        super().__init__(spec)

    def _compute_mass_properties(self) -> MassProperties:
        """Use datasheet mass instead of computing from volume."""
        if self._geometry is not None:
            try:
                com = self._geometry.center()
                cg = Vector3(x=com.X, y=com.Y, z=com.Z)
            except (AttributeError, Exception):
                cg = Vector3()
        else:
            cg = Vector3()

        return MassProperties(mass=self._fixed_mass, center_of_gravity=cg)


class CustomComponent(Component):
    """Custom designed component - fully parametric.

    Wing ribs, spar mounts, fuselage sections, etc.
    Geometry is generated from parametric spec via Build123d.
    Mass is computed from volume and material density.
    """

    def _compute_geometry(self) -> Any:
        """Default implementation - subclasses should override with actual Build123d code."""
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement _compute_geometry()"
        )
