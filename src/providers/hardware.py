"""Hardware detection for provider auto-selection.

Scans the local system for GPU, installed analysis software, and
networked 3D printers to recommend the best provider configuration.
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PrinterInfo:
    """Detected 3D printer."""

    name: str
    model: str
    connection: str  # "lan", "usb", "cloud"
    ip_address: Optional[str] = None


@dataclass
class HardwareProfile:
    """Snapshot of the local hardware environment."""

    # GPU
    gpu_type: Optional[str] = None  # "nvidia_cuda", "amd_rocm", None
    gpu_name: Optional[str] = None
    gpu_vram_mb: Optional[int] = None
    cuda_available: bool = False

    # Printers
    printers: list[PrinterInfo] = field(default_factory=list)

    # Installed analysis software {name: version_or_None}
    installed_software: dict[str, Optional[str]] = field(default_factory=dict)

    # Platform
    os_platform: str = "unknown"

    def summary(self) -> str:
        """Human-readable summary for init wizard display."""
        lines = [f"Platform: {self.os_platform}"]
        if self.gpu_name:
            lines.append(f"GPU: {self.gpu_name} ({self.gpu_type}, {self.gpu_vram_mb or '?'} MB VRAM)")
        else:
            lines.append("GPU: None detected")
        if self.installed_software:
            lines.append("Software: " + ", ".join(
                f"{k} {v or '(found)'}" for k, v in self.installed_software.items()
            ))
        if self.printers:
            lines.append("Printers: " + ", ".join(p.name for p in self.printers))
        return "\n".join(lines)


def _detect_nvidia_gpu() -> tuple[Optional[str], Optional[int]]:
    """Detect NVIDIA GPU name and VRAM via nvidia-smi."""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            parts = result.stdout.strip().split(",")
            name = parts[0].strip()
            vram = int(float(parts[1].strip())) if len(parts) > 1 else None
            return name, vram
    except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
        pass
    return None, None


def _detect_software() -> dict[str, Optional[str]]:
    """Check for installed analysis and manufacturing software."""
    software: dict[str, Optional[str]] = {}

    checks = {
        "su2": ["SU2_CFD", "--version"],
        "gmsh": ["gmsh", "--version"],
        "freecad": ["FreeCADCmd", "--version"],
        "orcaslicer": ["orca-slicer", "--version"],
        "prusaslicer": ["prusa-slicer", "--version"],
        "openfoam": ["simpleFoam", "-help"],
    }

    for name, cmd in checks.items():
        exe = cmd[0]
        if shutil.which(exe):
            version = None
            try:
                result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=5,
                )
                out = (result.stdout + result.stderr).strip()
                # Try to extract version number from first line
                for token in out.split():
                    if any(c.isdigit() for c in token) and "." in token:
                        version = token.rstrip(",;")
                        break
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
            software[name] = version

    # Special check: FreeCAD on Windows at known path
    import os
    import sys
    if sys.platform == "win32":
        fc_path = r"C:\Users\ilija\AppData\Local\Programs\FreeCAD 1.0\bin\FreeCADCmd.exe"
        if os.path.exists(fc_path) and "freecad" not in software:
            software["freecad"] = "1.0"

    return software


def detect_hardware() -> HardwareProfile:
    """Scan the local system and return a HardwareProfile.

    This is called during the init wizard to auto-suggest providers.
    """
    import sys

    profile = HardwareProfile(os_platform=sys.platform)

    # GPU detection
    gpu_name, gpu_vram = _detect_nvidia_gpu()
    if gpu_name:
        profile.gpu_type = "nvidia_cuda"
        profile.gpu_name = gpu_name
        profile.gpu_vram_mb = gpu_vram
        profile.cuda_available = True

    # Software detection
    profile.installed_software = _detect_software()

    return profile
