"""FreeCAD + CalculiX FEA provider.

Wraps the existing ``src.analysis.structural_fem`` module.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from ..base import ProviderInfo, ProviderRegistry
from .protocol import (
    BucklingResult,
    FEAProvider,
    LoadCase,
    ModalResult,
    StaticResult,
)

def _find_freecad_cmd() -> str:
    """Find FreeCADCmd executable via PATH or known install locations."""
    import shutil
    import sys

    found = shutil.which("FreeCADCmd")
    if found:
        return found

    # Check known Windows install paths
    if sys.platform == "win32":
        candidates = [
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\FreeCAD 1.0\bin\FreeCADCmd.exe"),
            os.path.expandvars(r"%PROGRAMFILES%\FreeCAD 1.0\bin\FreeCADCmd.exe"),
        ]
        for c in candidates:
            if os.path.exists(c):
                return c

    return "FreeCADCmd"  # Fallback — will fail gracefully if not found


class FreeCADCalculixProvider:
    """FreeCAD headless + CalculiX solver for structural FEA."""

    provider_id: str = "freecad_calculix"
    display_name: str = "FreeCAD + CalculiX"

    def is_available(self) -> bool:
        cmd = _find_freecad_cmd()
        return os.path.exists(cmd) if os.path.isabs(cmd) else shutil.which(cmd) is not None

    def run_static(
        self,
        step_file: Path,
        load_cases: list[LoadCase],
        output_dir: Path,
    ) -> list[StaticResult]:
        from src.analysis.structural_fem import run_spar_analysis

        output_dir.mkdir(parents=True, exist_ok=True)
        results = []
        for lc in load_cases:
            raw = run_spar_analysis(
                load_factor=lc.load_factor_g,
                output_dir=str(output_dir / lc.name.replace(" ", "_")),
            )
            if "error" in raw:
                results.append(StaticResult(
                    load_case=lc.name,
                    max_displacement_mm=0,
                    max_von_mises_mpa=0,
                    safety_factor=0,
                    passed=False,
                    details={"error": raw["error"]},
                ))
            else:
                results.append(StaticResult(
                    load_case=lc.name,
                    max_displacement_mm=raw.get("max_displacement_mm", 0),
                    max_von_mises_mpa=raw.get("max_von_mises_MPa", 0),
                    safety_factor=raw.get("safety_factor", 0),
                    mesh_nodes=raw.get("mesh_nodes", 0),
                    mesh_elements=raw.get("mesh_elements", 0),
                    passed=raw.get("pass", False),
                    details=raw,
                ))
        return results

    def run_modal(
        self,
        step_file: Path,
        n_modes: int,
        output_dir: Path,
    ) -> ModalResult:
        # Modal analysis not yet implemented in structural_fem.py
        return ModalResult(
            frequencies_hz=[],
            mode_shapes=[],
            flutter_speed_ms=None,
            flutter_margin=None,
        )

    def run_buckling(
        self,
        step_file: Path,
        load_case: LoadCase,
        output_dir: Path,
    ) -> BucklingResult:
        # Buckling analysis not yet implemented in structural_fem.py
        return BucklingResult(
            load_case=load_case.name,
            buckling_factor=0,
            critical_load_n=0,
            passed=False,
        )


_instance = FreeCADCalculixProvider()
ProviderRegistry.register(
    FEAProvider,
    _instance,
    ProviderInfo(
        provider_id="freecad_calculix",
        display_name="FreeCAD + CalculiX",
        protocol_type=FEAProvider,
        requires_software=["FreeCADCmd"],
        description="FreeCAD 1.0 headless with CalculiX solver for structural FEA.",
    ),
)
