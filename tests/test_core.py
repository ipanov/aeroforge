"""Tests for the core component framework and dependency graph."""

import pytest

_has_build123d = pytest.importorskip is not None  # always True; real check below
try:
    import build123d  # noqa: F401
    _has_build123d = True
except ImportError:
    _has_build123d = False

needs_build123d = pytest.mark.skipif(not _has_build123d, reason="build123d not installed")

from src.core.component import (
    Component,
    ComponentSpec,
    CustomComponent,
    Material,
    MassProperties,
    OffShelfComponent,
    Vector3,
)
from src.core.assembly import Assembly, AssemblySpec, AssemblyConstraint, ConstraintType
from src.core.dag import DependencyGraph
from src.core.validation import (
    ValidationHook,
    ValidationSeverity,
    validate_component,
)


# ── Test helpers ──────────────────────────────────────────────────

class DummySpec(ComponentSpec):
    """Simple spec for testing."""
    length: float = 100.0
    width: float = 50.0
    height: float = 10.0


class DummyComponent(CustomComponent):
    """A component that doesn't need Build123d for testing."""

    def __init__(self, spec: DummySpec) -> None:
        super().__init__(spec)

    def _compute_geometry(self):
        """Return None - no Build123d in tests."""
        return None

    def _compute_mass_properties(self) -> MassProperties:
        """Compute mass from dimensions and density."""
        s = self.spec
        volume_mm3 = s.length * s.width * s.height
        volume_cm3 = volume_mm3 / 1000.0
        from src.core.component import MATERIAL_DENSITY
        density = MATERIAL_DENSITY.get(s.material, 1.24)
        mass = volume_cm3 * density
        return MassProperties(
            mass=mass,
            center_of_gravity=Vector3(x=s.length / 2, y=s.width / 2, z=s.height / 2),
        )

    def build(self):
        self.mass_props = self._compute_mass_properties()
        self._dirty = False
        return None


class DummyOffShelf(OffShelfComponent):
    """Off-the-shelf component for testing."""

    def _compute_geometry(self):
        return None

    def build(self):
        self.mass_props = self._compute_mass_properties()
        self._dirty = False
        return None


# ── Component tests ───────────────────────────────────────────────

class TestComponent:

    def test_create_component(self):
        spec = DummySpec(name="wing_rib_1", material=Material.PLA)
        comp = DummyComponent(spec)
        assert comp.name == "wing_rib_1"
        assert comp.id is not None

    def test_component_mass(self):
        spec = DummySpec(name="block", length=100, width=50, height=10, material=Material.PLA)
        comp = DummyComponent(spec)
        comp.build()
        # 100*50*10 = 50000 mm³ = 50 cm³, PLA density 1.24 g/cm³ = 62g
        assert abs(comp.mass - 62.0) < 0.1

    def test_component_cg(self):
        spec = DummySpec(name="block", length=100, width=50, height=10)
        comp = DummyComponent(spec)
        comp.build()
        assert comp.cg.x == 50.0
        assert comp.cg.y == 25.0
        assert comp.cg.z == 5.0

    def test_update_spec(self):
        spec = DummySpec(name="block", length=100)
        comp = DummyComponent(spec)
        changed = comp.update_spec(length=200)
        assert "length" in changed
        assert comp.spec.length == 200.0

    def test_update_spec_no_change(self):
        spec = DummySpec(name="block", length=100)
        comp = DummyComponent(spec)
        changed = comp.update_spec(length=100)  # Same value
        assert len(changed) == 0

    def test_off_shelf_fixed_mass(self):
        spec = DummySpec(name="servo_sg90")
        comp = DummyOffShelf(spec, fixed_mass=9.0)
        comp.build()
        assert comp.mass == 9.0  # Uses datasheet mass, not computed


# ── Assembly tests ────────────────────────────────────────────────

class TestAssembly:

    def test_empty_assembly(self):
        spec = AssemblySpec(name="wing_assembly")
        asm = Assembly(spec)
        assert asm.child_count == 0
        assert asm.mass == 0.0

    def test_add_children(self):
        asm = Assembly(AssemblySpec(name="wing"))
        rib1 = DummyComponent(DummySpec(name="rib_1"))
        rib2 = DummyComponent(DummySpec(name="rib_2"))

        asm.add_child(rib1, position=Vector3(x=0))
        asm.add_child(rib2, position=Vector3(x=50))

        assert asm.child_count == 2

    @needs_build123d
    def test_assembly_mass(self):
        asm = Assembly(AssemblySpec(name="wing"))

        rib = DummyComponent(DummySpec(name="rib", length=100, width=50, height=10))
        rib.build()

        servo = DummyOffShelf(DummySpec(name="servo"), fixed_mass=9.0)
        servo.build()

        asm.add_child(rib)
        asm.add_child(servo)
        asm.build()

        expected = rib.mass + servo.mass
        assert abs(asm.mass - expected) < 0.1

    @needs_build123d
    def test_assembly_cg(self):
        asm = Assembly(AssemblySpec(name="test"))

        # Two equal-mass blocks at different positions
        spec = DummySpec(name="a", length=10, width=10, height=10)
        a = DummyComponent(spec)
        a.build()

        b = DummyComponent(DummySpec(name="b", length=10, width=10, height=10))
        b.build()

        asm.add_child(a, position=Vector3(x=0))
        asm.add_child(b, position=Vector3(x=100))
        asm.build()

        # CG should be midway between the two
        assert abs(asm.cg.x - 55.0) < 1.0  # (0+5 + 100+5) / 2 = 55

    def test_remove_child(self):
        asm = Assembly(AssemblySpec(name="wing"))
        rib = DummyComponent(DummySpec(name="rib"))
        asm.add_child(rib)
        assert asm.child_count == 1
        asm.remove_child(rib)
        assert asm.child_count == 0

    def test_duplicate_child_raises(self):
        asm = Assembly(AssemblySpec(name="wing"))
        rib = DummyComponent(DummySpec(name="rib"))
        asm.add_child(rib)
        with pytest.raises(ValueError, match="already in assembly"):
            asm.add_child(rib)

    @needs_build123d
    def test_bill_of_materials(self):
        asm = Assembly(AssemblySpec(name="wing"))
        rib = DummyComponent(DummySpec(name="rib"))
        servo = DummyOffShelf(DummySpec(name="servo"), fixed_mass=9.0)
        asm.add_child(rib)
        asm.add_child(servo)
        rib.build()
        servo.build()
        asm.build()

        bom = asm.bill_of_materials()
        assert len(bom) == 3  # Assembly + 2 children
        names = [b["name"] for b in bom]
        assert "wing" in names
        assert "rib" in names
        assert "servo" in names


# ── DAG tests ─────────────────────────────────────────────────────

class TestDependencyGraph:

    def test_add_component(self):
        dag = DependencyGraph()
        comp = DummyComponent(DummySpec(name="rib"))
        dag.add_component(comp)
        assert dag.component_count == 1

    def test_add_dependency(self):
        dag = DependencyGraph()
        motor = DummyComponent(DummySpec(name="motor"))
        mount = DummyComponent(DummySpec(name="motor_mount"))

        dag.add_component(motor)
        dag.add_component(mount)
        dag.add_dependency(dependency=motor, dependent=mount)

        deps = dag.get_dependents(motor)
        assert len(deps) == 1
        assert deps[0].name == "motor_mount"

    def test_cycle_detection(self):
        dag = DependencyGraph()
        a = DummyComponent(DummySpec(name="a"))
        b = DummyComponent(DummySpec(name="b"))

        dag.add_component(a)
        dag.add_component(b)
        dag.add_dependency(a, b)

        with pytest.raises(ValueError, match="cycle"):
            dag.add_dependency(b, a)

    def test_build_order(self):
        dag = DependencyGraph()
        motor = DummyComponent(DummySpec(name="motor"))
        mount = DummyComponent(DummySpec(name="mount"))
        pod = DummyComponent(DummySpec(name="pod"))

        dag.add_component(motor)
        dag.add_component(mount)
        dag.add_component(pod)
        dag.add_dependency(motor, mount)
        dag.add_dependency(mount, pod)

        order = dag.get_build_order()
        names = [c.name for c in order]
        assert names.index("motor") < names.index("mount")
        assert names.index("mount") < names.index("pod")

    def test_update_propagation(self):
        dag = DependencyGraph()
        motor = DummyComponent(DummySpec(name="motor", length=30))
        mount = DummyComponent(DummySpec(name="mount", length=40))

        dag.add_component(motor)
        dag.add_component(mount)
        dag.add_dependency(motor, mount)

        rebuilt = dag.update_component(motor, length=50)
        assert len(rebuilt) == 2
        assert motor.spec.length == 50

    def test_find_by_name(self):
        dag = DependencyGraph()
        comp = DummyComponent(DummySpec(name="wing_rib"))
        dag.add_component(comp)
        found = dag.find_by_name("wing_rib")
        assert found is not None
        assert found.id == comp.id

    def test_remove_component(self):
        dag = DependencyGraph()
        comp = DummyComponent(DummySpec(name="rib"))
        dag.add_component(comp)
        dag.remove_component(comp)
        assert dag.component_count == 0

    def test_remove_with_dependents_raises(self):
        dag = DependencyGraph()
        a = DummyComponent(DummySpec(name="a"))
        b = DummyComponent(DummySpec(name="b"))
        dag.add_component(a)
        dag.add_component(b)
        dag.add_dependency(a, b)

        with pytest.raises(ValueError, match="still depended on"):
            dag.remove_component(a)

    def test_get_all_dependents(self):
        dag = DependencyGraph()
        a = DummyComponent(DummySpec(name="a"))
        b = DummyComponent(DummySpec(name="b"))
        c = DummyComponent(DummySpec(name="c"))

        dag.add_component(a)
        dag.add_component(b)
        dag.add_component(c)
        dag.add_dependency(a, b)
        dag.add_dependency(b, c)

        all_deps = dag.get_all_dependents(a)
        names = {d.name for d in all_deps}
        assert names == {"b", "c"}

    def test_on_update_hook(self):
        dag = DependencyGraph()
        comp = DummyComponent(DummySpec(name="rib"))
        dag.add_component(comp)

        hook_calls = []
        dag.on_update(lambda c, changed: hook_calls.append((c.name, changed)))

        dag.update_component(comp, length=200)
        assert len(hook_calls) == 1
        assert hook_calls[0][0] == "rib"
        assert "length" in hook_calls[0][1]

    def test_summary(self):
        dag = DependencyGraph()
        a = DummyComponent(DummySpec(name="root"))
        b = DummyComponent(DummySpec(name="leaf"))
        dag.add_component(a)
        dag.add_component(b)
        dag.add_dependency(a, b)

        summary = dag.summary()
        assert summary["components"] == 2
        assert summary["edges"] == 1
        assert "root" in summary["roots"]
        assert "leaf" in summary["leaves"]


# ── Validation tests ──────────────────────────────────────────────

class TestValidation:

    def test_passing_validation(self):
        comp = DummyComponent(DummySpec(name="small_part", length=10, width=10, height=10))
        comp.build()
        results = validate_component(comp)
        # Should have no errors (only warnings at most)
        errors = [r for r in results if r.severity == ValidationSeverity.ERROR]
        assert len(errors) == 0

    def test_custom_hook(self):
        comp = DummyComponent(DummySpec(name="thin_wall", length=100, width=100, height=0.2))
        comp.build()

        thin_wall_hook = ValidationHook(
            name="min_wall_thickness",
            check=lambda c: c.spec.height >= 0.4,
            severity=ValidationSeverity.WARNING,
            message="Wall too thin for FDM printing (min 0.4mm)",
        )

        results = validate_component(comp, hooks=[thin_wall_hook])
        warnings = [r for r in results if r.severity == ValidationSeverity.WARNING]
        assert any(r.rule == "min_wall_thickness" for r in warnings)

    def test_error_severity_raises(self):
        comp = DummyComponent(DummySpec(name="bad_part"))
        comp.build()

        always_fail = ValidationHook(
            name="always_fail",
            check=lambda c: False,
            severity=ValidationSeverity.ERROR,
            message="This always fails",
        )

        with pytest.raises(ValueError, match="Validation failed"):
            validate_component(comp, hooks=[always_fail])
