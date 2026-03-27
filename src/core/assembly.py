"""Assembly system for combining components with constraints.

An Assembly is itself a Component - it has mass, CG, bounding box.
Assemblies contain other components and/or sub-assemblies, positioned
relative to each other via constraints.

Assembly hierarchy example:
    Sailplane (top assembly)
    ├── Wing Assembly
    │   ├── Center Panel Assembly
    │   │   ├── Rib x 5 (CustomComponent)
    │   │   ├── Main Spar (OffShelfComponent - carbon tube)
    │   │   ├── Rear Spar (OffShelfComponent - carbon rod)
    │   │   ├── Servo Mount x 2 (CustomComponent)
    │   │   └── Servo x 2 (OffShelfComponent)
    │   ├── Left Tip Panel Assembly
    │   └── Right Tip Panel Assembly
    ├── Fuselage Assembly
    │   ├── Pod (CustomComponent)
    │   ├── Boom (OffShelfComponent - carbon tube)
    │   ├── Motor Mount (CustomComponent)
    │   └── Motor (OffShelfComponent)
    └── Empennage Assembly
        ├── H-Stab (CustomComponent)
        ├── V-Stab (CustomComponent)
        └── Servo (OffShelfComponent)
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional

import numpy as np
from pydantic import BaseModel, Field

from .component import (
    BoundingBox,
    Component,
    ComponentSpec,
    LocalFrame,
    MassProperties,
    Vector3,
)


class ConstraintType(str, Enum):
    """Types of assembly constraints."""
    FIXED = "fixed"             # Component is fixed at a position
    COINCIDENT = "coincident"   # Two faces/points touch
    COAXIAL = "coaxial"         # Two axes align
    OFFSET = "offset"           # Fixed distance between references
    FLUSH = "flush"             # Two faces are coplanar
    ANGLE = "angle"             # Fixed angle between references


class AssemblyConstraint(BaseModel):
    """A constraint between two components in an assembly."""
    type: ConstraintType
    component_a_id: str
    component_b_id: str
    # Reference geometry on each component (face name, edge name, point)
    ref_a: str = ""
    ref_b: str = ""
    # Constraint value (offset distance, angle, etc.)
    value: float = 0.0
    description: str = ""


class AssemblySpec(ComponentSpec):
    """Specification for an assembly."""
    pass


class Assembly(Component):
    """A collection of components and sub-assemblies with constraints.

    An Assembly:
    - Contains child components and sub-assemblies
    - Positions children relative to each other via constraints
    - Computes aggregate mass properties (total mass, combined CG)
    - Is itself a Component (can be nested in larger assemblies)
    """

    def __init__(self, spec: AssemblySpec) -> None:
        self._children: dict[str, Component] = {}
        self._child_frames: dict[str, LocalFrame] = {}
        self._constraints: list[AssemblyConstraint] = []
        super().__init__(spec)

    @property
    def children(self) -> list[Component]:
        return list(self._children.values())

    @property
    def child_count(self) -> int:
        return len(self._children)

    def add_child(
        self,
        component: Component,
        position: Optional[Vector3] = None,
        rotation: Optional[Vector3] = None,
    ) -> None:
        """Add a component to this assembly.

        Args:
            component: Component or sub-Assembly to add.
            position: Position in assembly's local frame (mm).
            rotation: Rotation in assembly's local frame (degrees).
        """
        if component.id in self._children:
            raise ValueError(f"Component '{component.name}' already in assembly")

        self._children[component.id] = component
        self._child_frames[component.id] = LocalFrame(
            origin=position or Vector3(),
            rotation=rotation or Vector3(),
        )
        self._dirty = True

    def remove_child(self, component: Component) -> None:
        """Remove a component from this assembly."""
        if component.id not in self._children:
            raise ValueError(f"Component '{component.name}' not in assembly")

        del self._children[component.id]
        del self._child_frames[component.id]

        # Remove related constraints
        self._constraints = [
            c for c in self._constraints
            if c.component_a_id != component.id and c.component_b_id != component.id
        ]
        self._dirty = True

    def add_constraint(self, constraint: AssemblyConstraint) -> None:
        """Add a constraint between two children."""
        if constraint.component_a_id not in self._children:
            raise ValueError("Component A not in assembly")
        if constraint.component_b_id not in self._children:
            raise ValueError("Component B not in assembly")
        self._constraints.append(constraint)

    def get_child_position(self, component: Component) -> LocalFrame:
        """Get a child's position within this assembly."""
        if component.id not in self._child_frames:
            raise ValueError(f"Component '{component.name}' not in assembly")
        return self._child_frames[component.id]

    def set_child_position(
        self,
        component: Component,
        position: Optional[Vector3] = None,
        rotation: Optional[Vector3] = None,
    ) -> None:
        """Update a child's position within the assembly."""
        if component.id not in self._child_frames:
            raise ValueError(f"Component '{component.name}' not in assembly")

        frame = self._child_frames[component.id]
        if position is not None:
            frame.origin = position
        if rotation is not None:
            frame.rotation = rotation
        self._dirty = True

    def _compute_geometry(self) -> Any:
        """Build assembly geometry by combining children.

        Each child is built (if dirty) and positioned according to its frame.
        """
        from build123d import Compound, Location, Rotation

        parts = []
        for child_id, child in self._children.items():
            child_geom = child.build()
            if child_geom is None:
                continue

            frame = self._child_frames[child_id]
            loc = Location(
                (frame.origin.x, frame.origin.y, frame.origin.z),
                (frame.rotation.x, frame.rotation.y, frame.rotation.z),
            )
            parts.append(child_geom.moved(loc))

        if not parts:
            return None

        return Compound(parts)

    def _compute_mass_properties(self) -> MassProperties:
        """Compute aggregate mass properties from children."""
        total_mass = 0.0
        weighted_cg = np.zeros(3)

        for child_id, child in self._children.items():
            if child.mass <= 0:
                continue

            frame = self._child_frames[child_id]
            # Child CG in assembly frame = child local CG + child position
            child_cg = child.cg.as_array() + frame.origin.as_array()
            total_mass += child.mass
            weighted_cg += child.mass * child_cg

        if total_mass > 0:
            cg = weighted_cg / total_mass
        else:
            cg = np.zeros(3)

        return MassProperties(
            mass=total_mass,
            center_of_gravity=Vector3(x=float(cg[0]), y=float(cg[1]), z=float(cg[2])),
        )

    def _compute_bounding_box(self) -> BoundingBox:
        """Compute bounding box encompassing all children."""
        if not self._children:
            return BoundingBox()

        all_min = np.array([np.inf, np.inf, np.inf])
        all_max = np.array([-np.inf, -np.inf, -np.inf])

        for child_id, child in self._children.items():
            frame = self._child_frames[child_id]
            offset = frame.origin.as_array()
            bb = child.bounding_box

            child_min = bb.min_point.as_array() + offset
            child_max = bb.max_point.as_array() + offset

            all_min = np.minimum(all_min, child_min)
            all_max = np.maximum(all_max, child_max)

        return BoundingBox(
            min_point=Vector3(x=float(all_min[0]), y=float(all_min[1]), z=float(all_min[2])),
            max_point=Vector3(x=float(all_max[0]), y=float(all_max[1]), z=float(all_max[2])),
        )

    def bill_of_materials(self) -> list[dict[str, Any]]:
        """Generate a flat bill of materials."""
        bom: list[dict[str, Any]] = []

        def _collect(comp: Component, parent: str = "") -> None:
            entry = {
                "name": comp.name,
                "type": comp.__class__.__name__,
                "material": comp.spec.material.value if hasattr(comp.spec, 'material') else "",
                "mass_g": comp.mass,
                "parent": parent,
            }
            bom.append(entry)

            if isinstance(comp, Assembly):
                for child in comp.children:
                    _collect(child, parent=comp.name)

        _collect(self)
        return bom

    def __repr__(self) -> str:
        return (
            f"Assembly(name={self.name!r}, children={self.child_count}, "
            f"mass={self.mass:.1f}g)"
        )
