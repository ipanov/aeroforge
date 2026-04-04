"""AeroForge Provider System.

Swappable backends for CFD, FEA, manufacturing, slicing, and airfoil
analysis. Each provider category defines a Protocol; concrete
implementations register themselves with the ProviderRegistry.

Usage:
    from src.providers import ProviderRegistry, detect_hardware
    from src.providers.cfd.protocol import CFDProvider

    hw = detect_hardware()
    cfd = ProviderRegistry.auto_select(CFDProvider, hw)
    results = cfd.run_polar_sweep(...)
"""

from .base import ProviderInfo, ProviderRegistry
from .hardware import HardwareProfile, detect_hardware

# Import all built-in providers to trigger auto-registration.
# Imports are guarded so missing optional dependencies don't crash.
import importlib as _il
import logging as _log

_logger = _log.getLogger(__name__)

_PROVIDER_MODULES = [
    "src.providers.cfd.mock",
    "src.providers.cfd.su2_cuda",
    "src.providers.cfd.su2_cpu",
    "src.providers.fea.mock",
    "src.providers.fea.freecad_calculix",
    "src.providers.manufacturing.mock",
    "src.providers.manufacturing.fdm",
    "src.providers.manufacturing.manual",
    "src.providers.slicer.mock",
    "src.providers.slicer.orcaslicer",
    "src.providers.airfoil.mock",
    "src.providers.airfoil.neuralfoil",
]

for _mod in _PROVIDER_MODULES:
    try:
        _il.import_module(_mod)
    except ImportError:
        _logger.debug("Optional provider %s not available", _mod)


__all__ = [
    "ProviderInfo",
    "ProviderRegistry",
    "HardwareProfile",
    "detect_hardware",
]
