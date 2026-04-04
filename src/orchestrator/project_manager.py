"""Multi-project management for AeroForge.

Projects live under ``projects/`` in the repo root. Each project gets its
own ``aeroforge.yaml``, ``workflow_state.json``, ``cad/``, ``exports/``, and
``docs/`` directories. The active project is tracked in ``.claude/active_project``.

Provider hierarchy:
    * **System-level providers** (analysis engines) — CFD, FEA, airfoil.
      These depend on local hardware (GPU, FreeCAD install) and are shared
      across all projects. Configured once in ``config/system_providers.yaml``.
    * **Project-level providers** — manufacturing/tooling (FDM, manual, CNC)
      and slicer (OrcaSlicer, PrusaSlicer). These vary per project.
      Configured in each project's ``aeroforge.yaml`` under ``providers:``.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Optional

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROJECTS_DIR = PROJECT_ROOT / "projects"
ACTIVE_PROJECT_FILE = PROJECT_ROOT / ".claude" / "active_project"
SYSTEM_PROVIDERS_FILE = PROJECT_ROOT / "config" / "system_providers.yaml"


class ProjectManager:
    """Manages multiple projects within the AeroForge workspace."""

    def __init__(self, projects_dir: Optional[Path] = None) -> None:
        self.projects_dir = projects_dir or PROJECTS_DIR
        self.projects_dir.mkdir(parents=True, exist_ok=True)

    # -- Project CRUD -------------------------------------------------------

    def list_projects(self) -> list[dict[str, Any]]:
        """List all projects with basic metadata."""
        projects = []
        if not self.projects_dir.exists():
            return projects
        for d in sorted(self.projects_dir.iterdir()):
            if d.is_dir() and (d / "aeroforge.yaml").exists():
                cfg = self._load_yaml(d / "aeroforge.yaml")
                proj = cfg.get("project", {})
                projects.append({
                    "name": d.name,
                    "project_name": proj.get("project_name", d.name),
                    "aircraft_type": proj.get("aircraft_type", "unknown"),
                    "scope": proj.get("project_scope", "unknown"),
                    "path": str(d),
                    "active": d.name == self.get_active(),
                })
        return projects

    def create(
        self,
        slug: str,
        settings_dict: dict[str, Any],
    ) -> Path:
        """Create a new project directory with initial config.

        Args:
            slug: Directory name (e.g., "air4-f5j", "paper-plane").
            settings_dict: Full YAML content for aeroforge.yaml.

        Returns:
            Path to the new project directory.
        """
        project_dir = self.projects_dir / slug
        project_dir.mkdir(parents=True, exist_ok=True)

        # Create standard subdirectories
        for sub in ["cad/components", "cad/assemblies", "exports/validation", "docs"]:
            (project_dir / sub).mkdir(parents=True, exist_ok=True)

        # Write config
        cfg_path = project_dir / "aeroforge.yaml"
        with open(cfg_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(settings_dict, f, sort_keys=False, allow_unicode=True)

        return project_dir

    def delete(self, slug: str) -> None:
        """Delete a project (removes directory)."""
        project_dir = self.projects_dir / slug
        if project_dir.exists():
            shutil.rmtree(project_dir)
        if self.get_active() == slug:
            ACTIVE_PROJECT_FILE.unlink(missing_ok=True)

    # -- Active project -----------------------------------------------------

    def get_active(self) -> Optional[str]:
        """Return the slug of the currently active project, or None."""
        if ACTIVE_PROJECT_FILE.exists():
            return ACTIVE_PROJECT_FILE.read_text(encoding="utf-8").strip()
        # Fallback: if only one project exists, use it
        projects = [
            d.name for d in self.projects_dir.iterdir()
            if d.is_dir() and (d / "aeroforge.yaml").exists()
        ] if self.projects_dir.exists() else []
        if len(projects) == 1:
            return projects[0]
        return None

    def switch(self, slug: str) -> Path:
        """Switch the active project.

        Returns:
            Path to the project directory.

        Raises:
            FileNotFoundError: If the project doesn't exist.
        """
        project_dir = self.projects_dir / slug
        if not project_dir.exists():
            raise FileNotFoundError(f"Project not found: {slug}")
        ACTIVE_PROJECT_FILE.parent.mkdir(parents=True, exist_ok=True)
        ACTIVE_PROJECT_FILE.write_text(slug, encoding="utf-8")
        return project_dir

    def get_project_dir(self, slug: Optional[str] = None) -> Path:
        """Return the directory for a project (active if slug is None).

        Falls back to PROJECT_ROOT if no projects exist (legacy mode).
        """
        name = slug or self.get_active()
        if name:
            d = self.projects_dir / name
            if d.exists():
                return d
        # Legacy fallback: use repo root
        return PROJECT_ROOT

    # -- Settings paths -----------------------------------------------------

    def get_settings_path(self, slug: Optional[str] = None) -> Path:
        """Return the aeroforge.yaml path for a project."""
        d = self.get_project_dir(slug)
        return d / "aeroforge.yaml"

    def get_state_path(self, slug: Optional[str] = None) -> Path:
        """Return the workflow_state.json path for a project."""
        d = self.get_project_dir(slug)
        return d / "workflow_state.json"

    def get_dashboard_path(self, slug: Optional[str] = None) -> Path:
        """Return the dashboard HTML path for a project."""
        d = self.get_project_dir(slug)
        exports = d / "exports"
        exports.mkdir(parents=True, exist_ok=True)
        return exports / "workflow_dashboard.html"

    # -- System providers ---------------------------------------------------

    @staticmethod
    def load_system_providers() -> dict[str, Any]:
        """Load system-level provider configuration.

        System providers (CFD, FEA, airfoil) are shared across all projects
        and depend on local hardware, not project decisions.
        """
        if SYSTEM_PROVIDERS_FILE.exists():
            with open(SYSTEM_PROVIDERS_FILE, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {}

    @staticmethod
    def save_system_providers(config: dict[str, Any]) -> Path:
        """Save system-level provider configuration."""
        SYSTEM_PROVIDERS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(SYSTEM_PROVIDERS_FILE, "w", encoding="utf-8") as f:
            yaml.safe_dump(config, f, sort_keys=False)
        return SYSTEM_PROVIDERS_FILE

    def get_merged_providers(self, slug: Optional[str] = None) -> dict[str, Any]:
        """Merge system providers with project providers.

        System providers (cfd, fea, airfoil) come from system config.
        Project providers (manufacturing, slicer) come from project config.
        """
        system = self.load_system_providers()
        project_cfg = self._load_yaml(self.get_settings_path(slug))
        project_providers = project_cfg.get("providers", {})

        merged = {}
        # System-level categories
        for cat in ("cfd", "fea", "airfoil"):
            merged[cat] = system.get(cat, project_providers.get(cat, {}))
        # Project-level categories
        for cat in ("manufacturing", "slicer"):
            merged[cat] = project_providers.get(cat, {})

        return merged

    # -- Helpers ------------------------------------------------------------

    @staticmethod
    def _load_yaml(path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
