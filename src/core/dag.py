"""Dependency graph for parametric component updates.

Uses NetworkX directed acyclic graph (DAG) to track which components
depend on which. When a component's spec changes, all downstream
dependents are automatically marked dirty and rebuilt in topological order.

Example dependency chain:
    motor_spec_change -> motor_mount -> fuselage_pod -> top_assembly
    wing_chord_change -> wing_ribs -> wing_panel -> wing_assembly
"""

from __future__ import annotations

from typing import Any, Callable, Optional

import networkx as nx

from .component import Component


class DependencyGraph:
    """Manages component relationships and update propagation.

    The graph is a DAG where:
    - Nodes are components (keyed by component.id)
    - Edges point from dependency to dependent (A -> B means B depends on A)
    - When A changes, all descendants of A are rebuilt in topological order

    CRUD operations:
    - Create: add_component(), add_dependency()
    - Read:   get_component(), get_dependents(), get_dependencies()
    - Update: update_component() triggers cascade
    - Delete: remove_component() cleans up edges
    """

    def __init__(self) -> None:
        self._graph: nx.DiGraph = nx.DiGraph()
        self._components: dict[str, Component] = {}
        self._on_update_hooks: list[Callable[[Component, set[str]], None]] = []
        self._on_rebuild_hooks: list[Callable[[Component], None]] = []

    @property
    def component_count(self) -> int:
        return len(self._components)

    @property
    def all_components(self) -> list[Component]:
        return list(self._components.values())

    # ── CRUD: Create ──────────────────────────────────────────────

    def add_component(self, component: Component) -> None:
        """Register a component in the dependency graph."""
        if component.id in self._components:
            raise ValueError(f"Component '{component.name}' already in graph")
        self._components[component.id] = component
        self._graph.add_node(component.id)

    def add_dependency(self, dependency: Component, dependent: Component) -> None:
        """Declare that `dependent` depends on `dependency`.

        When `dependency` changes, `dependent` will be rebuilt.
        Raises ValueError if this would create a cycle.
        """
        if dependency.id not in self._components:
            raise ValueError(f"Dependency '{dependency.name}' not in graph")
        if dependent.id not in self._components:
            raise ValueError(f"Dependent '{dependent.name}' not in graph")

        # Check for cycles before adding
        self._graph.add_edge(dependency.id, dependent.id)
        if not nx.is_directed_acyclic_graph(self._graph):
            self._graph.remove_edge(dependency.id, dependent.id)
            raise ValueError(
                f"Adding dependency {dependency.name} -> {dependent.name} "
                f"would create a cycle"
            )

    # ── CRUD: Read ────────────────────────────────────────────────

    def get_component(self, component_id: str) -> Optional[Component]:
        """Get a component by ID."""
        return self._components.get(component_id)

    def find_by_name(self, name: str) -> Optional[Component]:
        """Find a component by name (first match)."""
        for comp in self._components.values():
            if comp.name == name:
                return comp
        return None

    def find_all_by_name(self, name: str) -> list[Component]:
        """Find all components matching a name."""
        return [c for c in self._components.values() if c.name == name]

    def get_dependents(self, component: Component) -> list[Component]:
        """Get direct dependents of a component (one level)."""
        if component.id not in self._graph:
            return []
        return [
            self._components[nid]
            for nid in self._graph.successors(component.id)
        ]

    def get_all_dependents(self, component: Component) -> list[Component]:
        """Get ALL downstream dependents (transitive closure)."""
        if component.id not in self._graph:
            return []
        descendants = nx.descendants(self._graph, component.id)
        return [self._components[nid] for nid in descendants]

    def get_dependencies(self, component: Component) -> list[Component]:
        """Get direct dependencies of a component (what it depends on)."""
        if component.id not in self._graph:
            return []
        return [
            self._components[nid]
            for nid in self._graph.predecessors(component.id)
        ]

    def get_build_order(self) -> list[Component]:
        """Get all components in topological build order.

        Components with no dependencies come first.
        """
        order = list(nx.topological_sort(self._graph))
        return [self._components[nid] for nid in order]

    # ── CRUD: Update ──────────────────────────────────────────────

    def update_component(self, component: Component, **kwargs: Any) -> list[Component]:
        """Update a component's spec and rebuild all dependents.

        Args:
            component: The component to update.
            **kwargs: Spec parameters to change.

        Returns:
            List of all components that were rebuilt (in build order).
        """
        changed = component.update_spec(**kwargs)
        if not changed:
            return []

        # Fire update hooks
        for hook in self._on_update_hooks:
            hook(component, changed)

        # Get all downstream dependents in topological order
        to_rebuild = self._get_rebuild_order(component)

        # Rebuild the changed component first
        component.build()
        for hook in self._on_rebuild_hooks:
            hook(component)

        # Rebuild dependents in order
        rebuilt = [component]
        for dep in to_rebuild:
            dep._dirty = True
            dep.build()
            for hook in self._on_rebuild_hooks:
                hook(dep)
            rebuilt.append(dep)

        return rebuilt

    def rebuild_all(self) -> list[Component]:
        """Rebuild all components in dependency order."""
        order = self.get_build_order()
        for comp in order:
            comp._dirty = True
            comp.build()
            for hook in self._on_rebuild_hooks:
                hook(comp)
        return order

    # ── CRUD: Delete ──────────────────────────────────────────────

    def remove_component(self, component: Component) -> None:
        """Remove a component and all its edges from the graph.

        Raises ValueError if other components still depend on it.
        """
        dependents = self.get_dependents(component)
        if dependents:
            names = [d.name for d in dependents]
            raise ValueError(
                f"Cannot remove '{component.name}': "
                f"still depended on by {names}"
            )

        self._graph.remove_node(component.id)
        del self._components[component.id]

    def force_remove_component(self, component: Component) -> list[Component]:
        """Force-remove a component, disconnecting all edges.

        Returns list of orphaned dependents (no longer connected).
        """
        orphans = self.get_dependents(component)
        self._graph.remove_node(component.id)
        del self._components[component.id]
        return orphans

    # ── Hooks ─────────────────────────────────────────────────────

    def on_update(self, hook: Callable[[Component, set[str]], None]) -> None:
        """Register a hook called when a component spec changes.

        Hook signature: hook(component, changed_params)
        """
        self._on_update_hooks.append(hook)

    def on_rebuild(self, hook: Callable[[Component], None]) -> None:
        """Register a hook called after a component is rebuilt.

        Hook signature: hook(component)
        """
        self._on_rebuild_hooks.append(hook)

    # ── Internal ──────────────────────────────────────────────────

    def _get_rebuild_order(self, component: Component) -> list[Component]:
        """Get downstream dependents in topological rebuild order."""
        if component.id not in self._graph:
            return []

        descendants = nx.descendants(self._graph, component.id)
        if not descendants:
            return []

        subgraph = self._graph.subgraph(descendants)
        order = list(nx.topological_sort(subgraph))
        return [self._components[nid] for nid in order]

    # ── Diagnostics ───────────────────────────────────────────────

    def summary(self) -> dict[str, Any]:
        """Get a summary of the dependency graph."""
        return {
            "components": self.component_count,
            "edges": self._graph.number_of_edges(),
            "roots": [
                self._components[n].name
                for n in self._graph.nodes()
                if self._graph.in_degree(n) == 0
            ],
            "leaves": [
                self._components[n].name
                for n in self._graph.nodes()
                if self._graph.out_degree(n) == 0
            ],
        }

    def print_tree(self, indent: int = 0) -> str:
        """Print the dependency tree as indented text."""
        roots = [
            self._components[n]
            for n in self._graph.nodes()
            if self._graph.in_degree(n) == 0
        ]
        lines: list[str] = []
        visited: set[str] = set()

        def _walk(comp: Component, depth: int) -> None:
            if comp.id in visited:
                lines.append("  " * depth + f"[circular ref: {comp.name}]")
                return
            visited.add(comp.id)
            prefix = "  " * depth
            lines.append(f"{prefix}{comp.name} ({comp.mass:.1f}g)")
            for child in self.get_dependents(comp):
                _walk(child, depth + 1)

        for root in roots:
            _walk(root, indent)

        return "\n".join(lines)

    def total_mass(self) -> float:
        """Total mass of all leaf components (avoid double-counting assemblies)."""
        leaves = [
            self._components[n]
            for n in self._graph.nodes()
            if self._graph.out_degree(n) == 0
        ]
        # For leaves that are assemblies, use their computed mass
        # For standalone components, sum directly
        return sum(c.mass for c in self._components.values()
                   if self._graph.in_degree(c.id) == 0 or self._graph.out_degree(c.id) == 0)
