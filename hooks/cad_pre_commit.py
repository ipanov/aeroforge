"""PreCommit hook: blocks commits with backup files or unvalidated geometry.

Checks:
1. Blocks .FCBak files from being committed
2. Blocks temp_* files from being committed
3. Blocks geometry files (.step/.stl/.FCStd/.3mf) without recent validation screenshots
4. Warns if .step or .stl is committed for printed components without a .3mf file
"""

import subprocess
import sys
import os
import time
from pathlib import Path

GEOMETRY_EXTENSIONS = {".step", ".stl", ".fcstd", ".3mf"}
VALIDATION_DIR = Path("exports/validation")
MAX_SCREENSHOT_AGE_SECONDS = 600  # 10 minutes


def get_staged_files() -> list[str]:
    """Return list of staged file paths."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True, text=True
    )
    return [f.strip() for f in result.stdout.strip().splitlines() if f.strip()]


def has_recent_validation_screenshot() -> bool:
    """Check if any .png in exports/validation/ was modified in the last 10 minutes."""
    if not VALIDATION_DIR.exists():
        return False

    now = time.time()
    for png_file in VALIDATION_DIR.glob("*.png"):
        age = now - png_file.stat().st_mtime
        if age <= MAX_SCREENSHOT_AGE_SECONDS:
            return True
    return False


def main() -> int:
    staged = get_staged_files()
    if not staged:
        return 0

    # Check for .FCBak files
    fcbak_files = [f for f in staged if f.endswith(".FCBak")]
    if fcbak_files:
        print(f"BLOCKED: .FCBak backup files staged for commit: {fcbak_files}")
        print("Remove them with: git reset HEAD <file>")
        return 1

    # Check for temp_* files
    temp_files = [f for f in staged if os.path.basename(f).startswith("temp_")]
    if temp_files:
        print(f"BLOCKED: Temporary files staged for commit: {temp_files}")
        print("Remove them with: git reset HEAD <file>")
        return 1

    # Check for geometry files without recent validation
    geometry_files = [
        f for f in staged
        if Path(f).suffix.lower() in GEOMETRY_EXTENSIONS
    ]
    if geometry_files and not has_recent_validation_screenshot():
        print(f"BLOCKED: Geometry files staged without recent validation: {geometry_files}")
        print("Run validation first to generate a screenshot in exports/validation/")
        print(f"Screenshot must be less than {MAX_SCREENSHOT_AGE_SECONDS // 60} minutes old.")
        return 1

    # Warn if .step or .stl is committed without a corresponding .3mf
    # (printed components need 3MF for Bambu P1S/A1)
    printable_files = [
        f for f in staged
        if Path(f).suffix.lower() in {".step", ".stl"}
        and f.startswith("cad/components/")
    ]
    if printable_files:
        missing_3mf = []
        for pf in printable_files:
            p = Path(pf)
            threemf_path = p.with_suffix(".3mf")
            # Check if the .3mf is staged or already exists on disk
            threemf_str = str(threemf_path).replace("\\", "/")
            project_root = Path(__file__).resolve().parent.parent
            if threemf_str not in staged and not (project_root / threemf_path).exists():
                missing_3mf.append(pf)
        if missing_3mf:
            print(f"WARNING: Printed component geometry without .3mf: {missing_3mf}")
            print("Bambu P1S/A1 requires .3mf files for slicing. Generate with OrcaSlicer.")
            # Warning only, do not block

    # MANDATORY: Run drawing orientation and component integrity tests
    # if ANY DXF or drawing-related files are staged
    drawing_files = [f for f in staged if f.endswith(".dxf") or f.endswith(".png")
                     or "hstab_geometry" in f or "orientation.py" in f
                     or "draw_" in f]
    if drawing_files:
        print("Running drawing orientation & component integrity tests...")
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/test_drawing_orientation.py", "-v",
             "--tb=short"],
            capture_output=True, text=True,
            env={**os.environ, "PYTHONPATH": "."},
        )
        if result.returncode != 0:
            print("BLOCKED: Drawing tests FAILED. Fix before committing.")
            print(result.stdout)
            print(result.stderr)
            return 1
        print(f"Drawing tests passed.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
