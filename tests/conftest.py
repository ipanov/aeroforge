"""Pytest configuration for AeroForge tests."""

import sys
from pathlib import Path

import pytest

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Add src to path for imports
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture
def freecad_rpc():
    """Fixture providing FreeCAD RPC connection. Skips if unavailable."""
    from hooks.freecad_rpc_helper import FreecadRPC
    rpc = FreecadRPC(port=9875)
    if not rpc.ping():
        pytest.skip("FreeCAD RPC not available on port 9875")
    return rpc
