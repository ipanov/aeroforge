"""CAD folder structure validation hook.

Validates that component and assembly folders in cad/ follow the Clear Skies
folder organization rules defined in cad/CAD_FRAMEWORK.md.

Rules enforced:
1. No .FCStd without a corresponding .dxf (drawing-first rule)
2. No .FCStd commit without renders (4 views)
3. No renders commit without COMPONENT_INFO.md or ASSEMBLY_INFO.md
4. Naming conventions: files must match folder name
5. Required render views: isometric, front, top, right

Can be run standalone or as a hook. When run as a hook, reads JSON from stdin
(PreCommit context) and checks staged files. When run standalone, validates
entire cad/ tree.

Exit codes:
    0 = PASS (all checks passed)
    1 = FAIL (structure violations found)
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CAD_ROOT = PROJECT_ROOT / "cad"
COMPONENTS_DIR = CAD_ROOT / "components"
ASSEMBLIES_DIR = CAD_ROOT / "assemblies"

REQUIRED_RENDER_VIEWS = ["isometric", "front", "top", "right"]

# Extensions that trigger validation
GEOMETRY_EXTENSIONS = {".fcstd", ".step", ".stl", ".3mf"}
DRAWING_EXTENSIONS = {".dxf"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}


class ValidationError:
    """A single validation failure."""

    def __init__(self, path: str, rule: str, message: str):
        self.path = path
        self.rule = rule
        self.message = message

    def __str__(self) -> str:
        return f"[{self.rule}] {self.path}: {self.message}"


def get_staged_files() -> list[str]:
    """Return list of staged file paths (relative to repo root)."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
    )
    return [f.strip() for f in result.stdout.strip().splitlines() if f.strip()]


def is_component_folder(folder: Path) -> bool:
    """Check if a folder is inside cad/components/."""
    try:
        folder.relative_to(COMPONENTS_DIR)
        return True
    except ValueError:
        return False


def is_assembly_folder(folder: Path) -> bool:
    """Check if a folder is inside cad/assemblies/."""
    try:
        folder.relative_to(ASSEMBLIES_DIR)
        return True
    except ValueError:
        return False


def get_item_folder(filepath: Path) -> Optional[Path]:
    """Get the component/assembly folder for a given file path.

    Walks up from the file to find the folder that sits directly inside
    a category folder (e.g., cad/components/empennage/HStab_Left).
    """
    # Normalize to absolute
    filepath = filepath.resolve() if not filepath.is_absolute() else filepath

    # Check if it's inside cad/components/ or cad/assemblies/
    for base_dir in [COMPONENTS_DIR, ASSEMBLIES_DIR]:
        try:
            rel = filepath.relative_to(base_dir)
            parts = rel.parts
            # Structure is: category/ItemName/... so we need at least 2 parts
            if len(parts) >= 2:
                return base_dir / parts[0] / parts[1]
        except ValueError:
            continue
    return None


def validate_naming(folder: Path) -> list[ValidationError]:
    """Check that files in a folder follow naming conventions."""
    errors = []
    folder_name = folder.name

    # Check drawing files
    dxf_expected = f"{folder_name}_drawing.dxf"
    png_expected = f"{folder_name}_drawing.png"

    for f in folder.iterdir():
        if f.is_file():
            name = f.name
            # Check DXF naming
            if f.suffix.lower() == ".dxf" and name != dxf_expected:
                errors.append(ValidationError(
                    str(f.relative_to(PROJECT_ROOT)),
                    "NAMING",
                    f"DXF file should be named '{dxf_expected}', got '{name}'",
                ))
            # Check drawing PNG naming
            if f.suffix.lower() == ".png" and "drawing" in name.lower() and name != png_expected:
                errors.append(ValidationError(
                    str(f.relative_to(PROJECT_ROOT)),
                    "NAMING",
                    f"Drawing PNG should be named '{png_expected}', got '{name}'",
                ))
            # Check FCStd naming
            if f.suffix.lower() == ".fcstd" and name != f"{folder_name}.FCStd":
                errors.append(ValidationError(
                    str(f.relative_to(PROJECT_ROOT)),
                    "NAMING",
                    f"Model file should be named '{folder_name}.FCStd', got '{name}'",
                ))

    # Check render naming
    renders_dir = folder / "renders"
    if renders_dir.exists():
        for f in renders_dir.iterdir():
            if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS:
                # Expected: FolderName_view.png
                valid_names = [f"{folder_name}_{v}.png" for v in REQUIRED_RENDER_VIEWS]
                if f.name not in valid_names:
                    errors.append(ValidationError(
                        str(f.relative_to(PROJECT_ROOT)),
                        "NAMING",
                        f"Render should be one of {valid_names}, got '{f.name}'",
                    ))

    return errors


def validate_drawing_first(folder: Path) -> list[ValidationError]:
    """Ensure no .FCStd exists without a corresponding .dxf."""
    errors = []
    folder_name = folder.name

    has_fcstd = (folder / f"{folder_name}.FCStd").exists()
    has_dxf = (folder / f"{folder_name}_drawing.dxf").exists()

    if has_fcstd and not has_dxf:
        errors.append(ValidationError(
            str(folder.relative_to(PROJECT_ROOT)),
            "DRAWING_FIRST",
            f"3D model '{folder_name}.FCStd' exists without a drawing "
            f"'{folder_name}_drawing.dxf'. Drawing MUST be created first.",
        ))

    return errors


def validate_renders(folder: Path) -> list[ValidationError]:
    """Check that renders/ has all 4 required views if model exists."""
    errors = []
    folder_name = folder.name

    has_fcstd = (folder / f"{folder_name}.FCStd").exists()
    if not has_fcstd:
        return errors  # No model, no renders needed yet

    renders_dir = folder / "renders"
    if not renders_dir.exists():
        errors.append(ValidationError(
            str(folder.relative_to(PROJECT_ROOT)),
            "RENDERS",
            f"Model exists but renders/ folder is missing. "
            f"Take 4 standard view screenshots.",
        ))
        return errors

    for view in REQUIRED_RENDER_VIEWS:
        expected = renders_dir / f"{folder_name}_{view}.png"
        if not expected.exists():
            errors.append(ValidationError(
                str(expected.relative_to(PROJECT_ROOT)),
                "RENDERS",
                f"Missing render: {folder_name}_{view}.png",
            ))

    return errors


def validate_info_doc(folder: Path) -> list[ValidationError]:
    """Check that COMPONENT_INFO.md or ASSEMBLY_INFO.md exists if model exists."""
    errors = []
    folder_name = folder.name

    has_fcstd = (folder / f"{folder_name}.FCStd").exists()
    if not has_fcstd:
        return errors  # No model, no docs needed yet

    has_component_info = (folder / "COMPONENT_INFO.md").exists()
    has_assembly_info = (folder / "ASSEMBLY_INFO.md").exists()

    if is_component_folder(folder) and not has_component_info:
        errors.append(ValidationError(
            str(folder.relative_to(PROJECT_ROOT)),
            "INFO_DOC",
            "Model exists but COMPONENT_INFO.md is missing.",
        ))
    elif is_assembly_folder(folder) and not has_assembly_info:
        errors.append(ValidationError(
            str(folder.relative_to(PROJECT_ROOT)),
            "INFO_DOC",
            "Model exists but ASSEMBLY_INFO.md is missing.",
        ))

    return errors


def validate_folder(folder: Path) -> list[ValidationError]:
    """Run all validation checks on a single component/assembly folder."""
    errors = []
    errors.extend(validate_naming(folder))
    errors.extend(validate_drawing_first(folder))
    errors.extend(validate_renders(folder))
    errors.extend(validate_info_doc(folder))
    return errors


def validate_all() -> list[ValidationError]:
    """Validate entire cad/ tree."""
    errors = []

    for base_dir in [COMPONENTS_DIR, ASSEMBLIES_DIR]:
        if not base_dir.exists():
            continue
        # Walk category folders
        for category in base_dir.iterdir():
            if not category.is_dir():
                continue
            # Walk item folders
            for item_folder in category.iterdir():
                if not item_folder.is_dir():
                    continue
                errors.extend(validate_folder(item_folder))

    return errors


def validate_staged_files() -> list[ValidationError]:
    """Validate only folders that have staged files."""
    staged = get_staged_files()
    if not staged:
        return []

    # Find unique component/assembly folders affected by staged files
    affected_folders: set[Path] = set()
    has_cad_files = False

    for filepath_str in staged:
        filepath = PROJECT_ROOT / filepath_str

        # Only check files inside cad/
        if not filepath_str.startswith("cad/"):
            continue

        has_cad_files = True
        item_folder = get_item_folder(filepath)
        if item_folder and item_folder.exists():
            affected_folders.add(item_folder)

    if not has_cad_files:
        return []  # No cad files staged, skip validation

    # Validate each affected folder
    errors = []
    for folder in sorted(affected_folders):
        folder_errors = validate_folder(folder)
        # Only report errors relevant to what's being committed
        # If only a drawing is staged, don't require renders yet
        staged_in_folder = [
            s for s in staged
            if s.startswith(str(folder.relative_to(PROJECT_ROOT)).replace("\\", "/"))
        ]

        staged_has_fcstd = any(
            s.lower().endswith(".fcstd") for s in staged_in_folder
        )
        staged_has_renders = any(
            "/renders/" in s for s in staged_in_folder
        )

        for err in folder_errors:
            # Always enforce DRAWING_FIRST and NAMING
            if err.rule in ("DRAWING_FIRST", "NAMING"):
                errors.append(err)
            # Only enforce RENDERS if .FCStd is being committed
            elif err.rule == "RENDERS" and staged_has_fcstd:
                errors.append(err)
            # Only enforce INFO_DOC if renders are being committed
            elif err.rule == "INFO_DOC" and staged_has_renders:
                errors.append(err)

    return errors


def main() -> int:
    """Main entry point.

    When called with --all flag, validates entire cad/ tree.
    When called without args (hook mode), validates staged files only.

    Returns:
        0 if all checks pass, 1 if violations found.
    """
    if "--all" in sys.argv:
        print("[CAD STRUCTURE] Validating entire cad/ tree...", file=sys.stderr)
        errors = validate_all()
    else:
        # Hook mode: check staged files
        errors = validate_staged_files()

    if not errors:
        if "--all" in sys.argv:
            print("[CAD STRUCTURE] All checks passed.", file=sys.stderr)
        return 0

    print(f"[CAD STRUCTURE] BLOCKED: {len(errors)} violation(s) found:", file=sys.stderr)
    for err in errors:
        print(f"  FAIL {err}", file=sys.stderr)
    print(
        "\nSee cad/CAD_FRAMEWORK.md for required folder structure and workflow.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
