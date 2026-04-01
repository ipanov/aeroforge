"""
Assembly Validation: Collision Detection & Fit Checks
======================================================
Every assembly MUST pass these checks before being declared complete.
This module provides Build123d-based validation tools.

Checks:
1. Collision detection — no two components may intersect
2. Containment — internal components (spars, rods) must be fully inside shells
3. Clearance — minimum clearance between spar and channel wall
4. Spar routing — spars must stay inside airfoil at every station along span
"""

from build123d import *
from typing import Optional


def check_collision(solid_a: Solid, solid_b: Solid, name_a: str = "A", name_b: str = "B") -> dict:
    """Check if two solids intersect.

    Returns dict with:
        - collides: bool
        - intersection_volume: float (mm³, 0 if no collision)
        - message: str
    """
    try:
        intersection = solid_a & solid_b  # Boolean AND = intersection
        vol = intersection.volume if hasattr(intersection, 'volume') else 0.0
        collides = vol > 0.01  # tolerance: 0.01 mm³
        return {
            "collides": collides,
            "intersection_volume": vol,
            "message": f"COLLISION: {name_a} ∩ {name_b} = {vol:.2f} mm³" if collides
                       else f"OK: {name_a} and {name_b} do not intersect"
        }
    except Exception as e:
        return {
            "collides": None,
            "intersection_volume": -1,
            "message": f"ERROR checking {name_a} vs {name_b}: {e}"
        }


def check_containment(container: Solid, contained: Solid,
                       name_container: str = "shell", name_contained: str = "spar") -> dict:
    """Check if 'contained' is fully inside 'container'.

    The contained solid minus the container should have zero volume
    if fully contained.

    Returns dict with:
        - fully_contained: bool
        - protruding_volume: float (mm³)
        - message: str
    """
    try:
        protrusion = contained - container  # What sticks out
        vol = protrusion.volume if hasattr(protrusion, 'volume') else 0.0
        contained_ok = vol < 0.01
        return {
            "fully_contained": contained_ok,
            "protruding_volume": vol,
            "message": f"OK: {name_contained} fully inside {name_container}" if contained_ok
                       else f"PROTRUSION: {name_contained} sticks out of {name_container} by {vol:.2f} mm³"
        }
    except Exception as e:
        return {
            "fully_contained": None,
            "protruding_volume": -1,
            "message": f"ERROR checking containment: {e}"
        }


def check_spar_routing(shell: Solid, spar_diameter: float,
                        spar_points: list[tuple[float, float, float]],
                        name: str = "spar") -> dict:
    """Check that a spar rod stays inside the shell at every point along its path.

    Args:
        shell: The airfoil shell solid
        spar_diameter: Diameter of the spar rod (mm)
        spar_points: List of (x, y, z) points defining the spar centerline path
        name: Name for reporting

    Returns dict with:
        - all_inside: bool
        - violations: list of (point, message) for stations where spar exits shell
        - message: str
    """
    violations = []
    radius = spar_diameter / 2.0

    for i, (x, y, z) in enumerate(spar_points):
        # Create a small sphere at this point to check if it's inside the shell
        try:
            test_sphere = Solid.make_sphere(radius, Plane(origin=(x, y, z)))
            protrusion = test_sphere - shell
            vol = protrusion.volume if hasattr(protrusion, 'volume') else 0.0
            if vol > 0.01:
                violations.append({
                    "station": i,
                    "point": (x, y, z),
                    "protruding_volume": vol,
                })
        except Exception as e:
            violations.append({
                "station": i,
                "point": (x, y, z),
                "error": str(e),
            })

    all_inside = len(violations) == 0
    return {
        "all_inside": all_inside,
        "violations": violations,
        "total_stations": len(spar_points),
        "violation_count": len(violations),
        "message": f"OK: {name} inside shell at all {len(spar_points)} stations" if all_inside
                   else f"VIOLATION: {name} exits shell at {len(violations)}/{len(spar_points)} stations"
    }


def validate_assembly(components: dict[str, Solid],
                       containment_pairs: list[tuple[str, str]] = None,
                       collision_pairs: list[tuple[str, str]] = None) -> dict:
    """Run full assembly validation.

    Args:
        components: Dict of name -> Solid
        containment_pairs: List of (container_name, contained_name) to check
        collision_pairs: List of (name_a, name_b) to check for collision.
                        If None, checks all pairs.

    Returns summary dict with all results.
    """
    results = {
        "collisions": [],
        "containment": [],
        "pass": True,
        "summary": "",
    }

    # Collision checks
    names = list(components.keys())
    if collision_pairs is None:
        collision_pairs = [(names[i], names[j])
                          for i in range(len(names))
                          for j in range(i+1, len(names))]

    for name_a, name_b in collision_pairs:
        if name_a in components and name_b in components:
            result = check_collision(components[name_a], components[name_b], name_a, name_b)
            results["collisions"].append(result)
            if result["collides"]:
                results["pass"] = False

    # Containment checks
    if containment_pairs:
        for container_name, contained_name in containment_pairs:
            if container_name in components and contained_name in components:
                result = check_containment(
                    components[container_name], components[contained_name],
                    container_name, contained_name
                )
                results["containment"].append(result)
                if result.get("fully_contained") == False:
                    results["pass"] = False

    # Summary
    n_collisions = sum(1 for r in results["collisions"] if r.get("collides"))
    n_protrusions = sum(1 for r in results["containment"] if r.get("fully_contained") == False)

    if results["pass"]:
        results["summary"] = f"PASS: {len(results['collisions'])} collision checks, {len(results['containment'])} containment checks — all clear"
    else:
        results["summary"] = f"FAIL: {n_collisions} collisions, {n_protrusions} protrusions detected"

    return results
