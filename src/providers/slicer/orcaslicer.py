"""OrcaSlicer provider — CLI wrapper for Bambu-optimized slicing."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any

from ..base import ProviderInfo, ProviderRegistry
from .protocol import SlicerProvider, SliceResult


class OrcaSlicerProvider:
    """OrcaSlicer CLI wrapper for Bambu printers."""

    provider_id: str = "orcaslicer"
    display_name: str = "OrcaSlicer (Bambu)"

    def is_available(self) -> bool:
        return shutil.which("orca-slicer") is not None

    def slice(
        self, mesh_file: Path, output_dir: Path, profile: dict[str, Any],
    ) -> SliceResult:
        output_dir.mkdir(parents=True, exist_ok=True)
        out_file = output_dir / (mesh_file.stem + ".3mf")

        cmd = [
            "orca-slicer",
            "--slice", str(mesh_file),
            "--output", str(out_file),
        ]

        # Add profile overrides
        if "layer_height" in profile:
            cmd.extend(["--layer-height", str(profile["layer_height"])])

        try:
            subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        return SliceResult(output_file=out_file)

    def estimate_time(self, mesh_file: Path, profile: dict[str, Any]) -> float:
        return 0.0  # Would need full slice to estimate

    def estimate_material(self, mesh_file: Path, profile: dict[str, Any]) -> float:
        return 0.0


_instance = OrcaSlicerProvider()
ProviderRegistry.register(
    SlicerProvider,
    _instance,
    ProviderInfo(
        provider_id="orcaslicer",
        display_name="OrcaSlicer (Bambu)",
        protocol_type=SlicerProvider,
        requires_software=["orca-slicer"],
        description="OrcaSlicer CLI for Bambu printer slicing.",
    ),
)
