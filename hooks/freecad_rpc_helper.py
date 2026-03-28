"""FreeCAD XML-RPC helper for communicating with FreeCAD GUI.

Uses the neka-nat/freecad-mcp addon which exposes an XML-RPC server
with an execute_code(code) method that returns {"success": bool, "message": str}.
"""

import os
import re
import xmlrpc.client

class FreecadRPC:
    """Helper class for communicating with FreeCAD via XML-RPC."""

    def __init__(self, host: str = "localhost", port: int = 9875):
        self.host = host
        self.port = port
        self.server = xmlrpc.client.ServerProxy(f"http://{host}:{port}")

    def ping(self) -> bool:
        """Returns True if FreeCAD RPC server responds, False otherwise."""
        try:
            self.server.execute_code("print('pong')")
            return True
        except Exception:
            return False

    def execute(self, code: str) -> str:
        """Execute Python code in FreeCAD and return output string.

        Args:
            code: Python code to execute in FreeCAD.

        Returns:
            Output message string from FreeCAD.

        Raises:
            RuntimeError: If execution fails (success=False in response).
            ConnectionError: If FreeCAD RPC server is unreachable.
        """
        try:
            result = self.server.execute_code(code)
        except Exception as exc:
            raise ConnectionError(f"Cannot reach FreeCAD RPC at {self.host}:{self.port}") from exc

        if not result.get("success", False):
            raise RuntimeError(f"FreeCAD execution failed: {result.get('message', 'unknown error')}")

        return result.get("message", "")

    def take_screenshot(
        self,
        filepath: str,
        view: str = "isometric",
        width: int = 1920,
        height: int = 1080,
    ) -> bool:
        """Take a screenshot of the current FreeCAD view.

        Args:
            filepath: Absolute path for the output image file.
            view: One of 'isometric', 'front', 'top', 'right', 'left'.
            width: Image width in pixels.
            height: Image height in pixels.

        Returns:
            True if screenshot was saved successfully.
        """
        view_commands = {
            "isometric": "v.viewIsometric()",
            "front": "v.viewFront()",
            "top": "v.viewTop()",
            "right": "v.viewRight()",
            "left": "v.viewLeft()",
        }
        view_call = view_commands.get(view, "v.viewIsometric()")
        # Normalize path separators for FreeCAD (Python on Windows)
        safe_path = filepath.replace("\\", "/")

        code = f"""
import FreeCADGui
v = FreeCADGui.activeDocument().activeView()
{view_call}
v.fitAll()
v.saveImage(r"{safe_path}", {width}, {height}, "Current")
print("SCREENSHOT_OK")
"""
        output = self.execute(code)
        return "SCREENSHOT_OK" in output

    def get_bounding_box(self, object_name: str) -> dict[str, float]:
        """Query the bounding box of a named object in FreeCAD.

        Args:
            object_name: Name of the FreeCAD document object.

        Returns:
            Dict with keys 'X', 'Y', 'Z' (dimensions) and 'VOL' (volume).
        """
        code = (
            'import FreeCAD\n'
            'obj = FreeCAD.ActiveDocument.getObject("' + object_name + '")\n'
            'if obj is None:\n'
            '    print("BB_ERROR: not found")\n'
            'else:\n'
            '    bb = obj.Shape.BoundBox\n'
            '    print("BB_X:" + str(bb.XLength))\n'
            '    print("BB_Y:" + str(bb.YLength))\n'
            '    print("BB_Z:" + str(bb.ZLength))\n'
            '    print("BB_VOL:" + str(obj.Shape.Volume))\n'
        )
        output = self.execute(code)
        result: dict[str, float] = {}
        for match in re.finditer(r"BB_(X|Y|Z|VOL):([\d.]+)", output):
            result[match.group(1)] = float(match.group(2))
        return result

    def get_all_objects(self) -> str:
        """List all objects in the active FreeCAD document with bounding boxes.

        Returns:
            Raw output string with object names and bounding box info.
        """
        code = """
import FreeCAD
doc = FreeCAD.ActiveDocument
if doc is None:
    print("NO_ACTIVE_DOCUMENT")
else:
    for obj in doc.Objects:
        try:
            bb = obj.Shape.BoundBox
            print(f"OBJ:{obj.Name} X:{bb.XLength:.3f} Y:{bb.YLength:.3f} Z:{bb.ZLength:.3f}")
        except Exception:
            print(f"OBJ:{obj.Name} (no shape)")
"""
        return self.execute(code)

    def take_validation_screenshots(
        self,
        component_name: str,
        output_dir: str = "exports/validation",
    ) -> list[str]:
        """Take screenshots from 4 standard views for validation.

        Args:
            component_name: Name used for output filenames.
            output_dir: Directory to save screenshots into.

        Returns:
            List of absolute file paths for the saved screenshots.
        """
        os.makedirs(output_dir, exist_ok=True)

        views = ["isometric", "front", "top", "right"]
        paths: list[str] = []

        for view in views:
            filename = f"{component_name}_{view}.png"
            filepath = os.path.join(output_dir, filename).replace("\\", "/")
            self.take_screenshot(filepath, view=view)
            paths.append(filepath)

        return paths
