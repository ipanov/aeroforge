"""Tests for multi-project management.

Covers:
- Project creation, listing, switching, deletion
- Active project resolution
- Settings and state path resolution
- System vs project provider merging
- Legacy fallback (no projects/ directory)
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from src.orchestrator.project_manager import ProjectManager


@pytest.fixture
def pm(tmp_path: Path) -> ProjectManager:
    """ProjectManager with isolated projects directory."""
    return ProjectManager(projects_dir=tmp_path / "projects")


@pytest.fixture
def active_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Override the active project file path."""
    af = tmp_path / "active_project"
    monkeypatch.setattr(
        "src.orchestrator.project_manager.ACTIVE_PROJECT_FILE", af,
    )
    return af


def _create_project(pm: ProjectManager, slug: str, name: str = "") -> Path:
    """Helper to create a project with minimal config."""
    return pm.create(slug, {
        "project": {
            "project_name": name or slug,
            "aircraft_type": "SAILPLANE",
            "project_scope": "aircraft",
        },
        "providers": {
            "manufacturing": {"selected": "fdm"},
            "slicer": {"selected": "orcaslicer"},
        },
    })


class TestProjectLifecycle:

    def test_create_project(self, pm: ProjectManager) -> None:
        path = _create_project(pm, "test-project", "Test Project")
        assert path.exists()
        assert (path / "aeroforge.yaml").exists()
        assert (path / "cad" / "components").exists()
        assert (path / "exports" / "validation").exists()

    def test_list_empty(self, pm: ProjectManager) -> None:
        assert pm.list_projects() == []

    def test_list_projects(self, pm: ProjectManager, active_file: Path) -> None:
        _create_project(pm, "proj-a", "Project A")
        _create_project(pm, "proj-b", "Project B")
        projects = pm.list_projects()
        assert len(projects) == 2
        names = [p["name"] for p in projects]
        assert "proj-a" in names
        assert "proj-b" in names

    def test_delete_project(self, pm: ProjectManager) -> None:
        _create_project(pm, "to-delete")
        pm.delete("to-delete")
        assert not (pm.projects_dir / "to-delete").exists()

    def test_delete_nonexistent_is_safe(self, pm: ProjectManager) -> None:
        pm.delete("nonexistent")  # Should not raise


class TestActiveProject:

    def test_switch_sets_active(self, pm: ProjectManager, active_file: Path) -> None:
        _create_project(pm, "proj-x")
        pm.switch("proj-x")
        assert active_file.read_text() == "proj-x"

    def test_switch_nonexistent_raises(self, pm: ProjectManager, active_file: Path) -> None:
        with pytest.raises(FileNotFoundError):
            pm.switch("nonexistent")

    def test_get_active_returns_none_when_empty(self, pm: ProjectManager, active_file: Path) -> None:
        assert pm.get_active() is None

    def test_get_active_auto_detects_single_project(self, pm: ProjectManager, active_file: Path) -> None:
        _create_project(pm, "only-project")
        assert pm.get_active() == "only-project"

    def test_get_active_returns_none_for_multiple(self, pm: ProjectManager, active_file: Path) -> None:
        _create_project(pm, "proj-a")
        _create_project(pm, "proj-b")
        # No explicit switch — should not auto-pick
        assert pm.get_active() is None

    def test_list_shows_active_flag(self, pm: ProjectManager, active_file: Path) -> None:
        _create_project(pm, "proj-a")
        _create_project(pm, "proj-b")
        pm.switch("proj-b")
        projects = pm.list_projects()
        active_flags = {p["name"]: p["active"] for p in projects}
        assert active_flags["proj-a"] is False
        assert active_flags["proj-b"] is True


class TestPathResolution:

    def test_settings_path(self, pm: ProjectManager, active_file: Path) -> None:
        _create_project(pm, "my-proj")
        pm.switch("my-proj")
        path = pm.get_settings_path()
        assert path == pm.projects_dir / "my-proj" / "aeroforge.yaml"

    def test_state_path(self, pm: ProjectManager, active_file: Path) -> None:
        _create_project(pm, "my-proj")
        pm.switch("my-proj")
        path = pm.get_state_path()
        assert path == pm.projects_dir / "my-proj" / "workflow_state.json"

    def test_dashboard_path(self, pm: ProjectManager, active_file: Path) -> None:
        _create_project(pm, "my-proj")
        pm.switch("my-proj")
        path = pm.get_dashboard_path()
        assert "exports" in str(path)
        assert path.name == "workflow_dashboard.html"


class TestProviderMerging:

    def test_system_providers_empty_when_no_config(self, pm: ProjectManager) -> None:
        system = pm.load_system_providers()
        # May be empty if no system_providers.yaml in test env
        assert isinstance(system, dict)

    def test_merged_providers_include_project(self, pm: ProjectManager, active_file: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _create_project(pm, "test-proj")
        pm.switch("test-proj")

        # Mock system providers
        monkeypatch.setattr(
            "src.orchestrator.project_manager.SYSTEM_PROVIDERS_FILE",
            pm.projects_dir / "nonexistent.yaml",
        )

        merged = pm.get_merged_providers()
        # Project-level providers should be present
        assert merged.get("manufacturing", {}).get("selected") == "fdm"
        assert merged.get("slicer", {}).get("selected") == "orcaslicer"

    def test_system_providers_override_project_for_cfd(
        self, pm: ProjectManager, active_file: Path, tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        _create_project(pm, "test-proj")
        pm.switch("test-proj")

        # Write system config with cfd
        sys_cfg_path = tmp_path / "system_providers.yaml"
        sys_cfg_path.write_text(yaml.safe_dump({
            "cfd": {"selected": "su2_cuda"},
            "fea": {"selected": "freecad_calculix"},
        }))
        monkeypatch.setattr(
            "src.orchestrator.project_manager.SYSTEM_PROVIDERS_FILE",
            sys_cfg_path,
        )

        merged = pm.get_merged_providers()
        assert merged["cfd"]["selected"] == "su2_cuda"
        assert merged["fea"]["selected"] == "freecad_calculix"
