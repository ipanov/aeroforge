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
# Each provider module registers itself at import time.
from . import cfd as _cfd_pkg  # noqa: F401
from . import fea as _fea_pkg  # noqa: F401
from . import manufacturing as _mfg_pkg  # noqa: F401
from . import slicer as _slicer_pkg  # noqa: F401
from . import airfoil as _airfoil_pkg  # noqa: F401

# Import concrete implementations
from .cfd import mock as _cfd_mock  # noqa: F401
from .cfd import su2_cuda as _cfd_su2_cuda  # noqa: F401
from .cfd import su2_cpu as _cfd_su2_cpu  # noqa: F401
from .fea import mock as _fea_mock  # noqa: F401
from .fea import freecad_calculix as _fea_fc  # noqa: F401
from .manufacturing import mock as _mfg_mock  # noqa: F401
from .manufacturing import fdm as _mfg_fdm  # noqa: F401
from .manufacturing import manual as _mfg_manual  # noqa: F401
from .slicer import mock as _slicer_mock  # noqa: F401
from .slicer import orcaslicer as _slicer_orca  # noqa: F401
from .airfoil import mock as _airfoil_mock  # noqa: F401
from .airfoil import neuralfoil as _airfoil_nf  # noqa: F401


__all__ = [
    "ProviderInfo",
    "ProviderRegistry",
    "HardwareProfile",
    "detect_hardware",
]
