"""Tests for the FreeCAD RPC helper module.

These tests require a running FreeCAD instance with the freecad-mcp addon
serving XML-RPC on localhost:9875. Tests are skipped if the server is
unreachable.
"""

import os
import tempfile

import pytest

from hooks.freecad_rpc_helper import FreecadRPC


@pytest.fixture
def rpc():
    """Create an RPC client, skip if FreeCAD is not available."""
    client = FreecadRPC()
    if not client.ping():
        pytest.skip("FreeCAD RPC server not available on localhost:9875")
    return client


def test_rpc_connection(rpc: FreecadRPC):
    """Verify that the RPC server responds to ping."""
    assert rpc.ping() is True


def test_rpc_screenshot(rpc: FreecadRPC):
    """Take a screenshot and verify the file is created on disk."""
    # Ensure there is an active document with geometry to screenshot
    rpc.execute("""
import FreeCAD
import Part
if not FreeCAD.ActiveDocument:
    doc = FreeCAD.newDocument("ScreenshotTest")
    box = doc.addObject("Part::Box", "Box")
    doc.recompute()
""")
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "test_screenshot.png").replace("\\", "/")
        result = rpc.take_screenshot(filepath)
        assert result is True
        assert os.path.exists(filepath), f"Screenshot not found at {filepath}"


def test_rpc_bounding_box(rpc: FreecadRPC):
    """Create a test box 10x20x30 in FreeCAD, query its bounding box."""
    # Create a fresh document with a test box
    rpc.execute("""
import FreeCAD
import Part
if FreeCAD.ActiveDocument:
    FreeCAD.closeDocument(FreeCAD.ActiveDocument.Name)
doc = FreeCAD.newDocument("TestBB")
box = doc.addObject("Part::Box", "TestBox")
box.Length = 10
box.Width = 20
box.Height = 30
doc.recompute()
""")

    bb = rpc.get_bounding_box("TestBox")
    assert abs(bb["X"] - 10.0) < 0.01
    assert abs(bb["Y"] - 20.0) < 0.01
    assert abs(bb["Z"] - 30.0) < 0.01
    assert abs(bb["VOL"] - 6000.0) < 1.0

    # Cleanup
    rpc.execute("""
import FreeCAD
FreeCAD.closeDocument("TestBB")
""")
