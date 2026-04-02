"""CAD validation tools — collision detection, containment, spar routing."""

from .assembly_check import (
    check_collision,
    check_containment,
    check_spar_routing,
    validate_assembly,
)

__all__ = [
    "check_collision",
    "check_containment",
    "check_spar_routing",
    "validate_assembly",
]
