"""REST API client for the n8n workflow visibility layer.

n8n is a MANDATORY component. The workflow engine will NOT operate without
a reachable n8n instance. If n8n is not running, the engine auto-launches it.
If it remains unreachable after launch, the engine raises N8nUnavailableError.
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any, Optional

import httpx
import yaml

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "http://localhost:5678"
DEFAULT_TIMEOUT_S = 10
_SYSTEM_CONFIG = Path(__file__).resolve().parent.parent.parent / "config" / "system_providers.yaml"


def _load_api_key() -> Optional[str]:
    """Read the n8n API key from system_providers.yaml."""
    if not _SYSTEM_CONFIG.exists():
        return None
    with open(_SYSTEM_CONFIG) as f:
        cfg = yaml.safe_load(f) or {}
    return cfg.get("n8n", {}).get("api_key")


def _save_api_key(api_key: str) -> None:
    """Persist the n8n API key into system_providers.yaml."""
    cfg: dict[str, Any] = {}
    if _SYSTEM_CONFIG.exists():
        with open(_SYSTEM_CONFIG) as f:
            cfg = yaml.safe_load(f) or {}
    cfg.setdefault("n8n", {})["api_key"] = api_key
    with open(_SYSTEM_CONFIG, "w") as f:
        yaml.safe_dump(cfg, f, sort_keys=False)


class N8nUnavailableError(RuntimeError):
    """Raised when n8n is not reachable and cannot be auto-launched."""


class N8nClient:
    """REST API client for the n8n workflow visibility layer."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT_S,
    ) -> None:
        self._base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self._api_key = api_key or _load_api_key()
        self._timeout = timeout
        self._client: Optional[httpx.Client] = None
        self._available: Optional[bool] = None
        self._workflow_id: Optional[str] = None

    def _get_client(self) -> httpx.Client:
        if self._client is None:
            headers = {"Content-Type": "application/json"}
            if self._api_key:
                headers["X-N8N-API-KEY"] = self._api_key
            self._client = httpx.Client(headers=headers, timeout=self._timeout)
        return self._client

    def health_check(self) -> bool:
        try:
            response = self._get_client().get(f"{self._base_url}/healthz")
            self._available = response.status_code == 200
        except Exception as exc:
            logger.debug("n8n health check failed: %s", exc)
            self._available = False
        return bool(self._available)

    @property
    def available(self) -> bool:
        if self._available is None:
            return self.health_check()
        return bool(self._available)

    def set_api_key(self, api_key: str) -> None:
        """Set and persist the n8n API key."""
        self._api_key = api_key
        _save_api_key(api_key)
        # Reset the client so next call uses new key
        if self._client:
            self._client.close()
            self._client = None

    # ------------------------------------------------------------------
    # Workflow lifecycle — single "AeroForge" workflow, regenerated per project
    # ------------------------------------------------------------------

    def ensure_workflow(
        self,
        project_name: str,
        aircraft_type: str,
        template_path: Optional[Path] = None,
    ) -> Optional[str]:
        """Create or update the AeroForge workflow in n8n.

        Uses a single workflow named 'AeroForge - {project_name}'.
        Deletes any previous AeroForge workflow first, then recreates.
        Returns the workflow ID or None on failure.
        """
        if not self.available or not self._api_key:
            logger.warning("n8n not available or no API key — skipping workflow sync")
            return None

        # Delete existing AeroForge workflows
        self._delete_aeroforge_workflows()

        # Load template
        template = self._load_template(template_path)
        if template is None:
            logger.warning("No workflow template found")
            return None

        # Build clean payload (only fields the API accepts)
        payload = {
            "name": f"AeroForge - {project_name}",
            "nodes": template.get("nodes", []),
            "connections": template.get("connections", {}),
            "settings": template.get("settings", {}),
        }

        # Ensure nodes have required fields
        for i, node in enumerate(payload["nodes"]):
            node.setdefault("typeVersion", 1)
            node.setdefault("id", f"node-{i}")

        # Inject aircraft_type into Set nodes
        for node in payload["nodes"]:
            if node.get("type") == "n8n-nodes-base.set":
                parameters = node.setdefault("parameters", {})
                values = parameters.setdefault("values", {})
                strings = values.setdefault("string", [])
                strings.append({"name": "aircraft_type", "value": aircraft_type})

        try:
            resp = self._get_client().post(
                f"{self._base_url}/api/v1/workflows", json=payload,
            )
            if resp.status_code != 200:
                logger.warning("Failed to create workflow: %s %s", resp.status_code, resp.text[:200])
                return None

            wf_id = resp.json().get("id")
            self._workflow_id = wf_id

            # Activate
            self._get_client().post(f"{self._base_url}/api/v1/workflows/{wf_id}/activate")
            logger.info("n8n workflow created and activated: %s (id=%s)", project_name, wf_id)
            return wf_id

        except Exception as exc:
            logger.warning("Failed to create n8n workflow: %s", exc)
            return None

    def _delete_aeroforge_workflows(self) -> None:
        """Remove all AeroForge event workflows (NOT dashboard workflows)."""
        try:
            resp = self._get_client().get(f"{self._base_url}/api/v1/workflows")
            if resp.status_code != 200:
                return
            for wf in resp.json().get("data", []):
                name = wf.get("name", "")
                # Only delete event workflows, preserve dashboard workflows
                if name.startswith("AeroForge") and not name.startswith("AeroForge Dashboard"):
                    wf_id = wf["id"]
                    self._get_client().delete(f"{self._base_url}/api/v1/workflows/{wf_id}")
                    logger.info("Deleted old n8n workflow: %s (id=%s)", name, wf_id)
        except Exception as exc:
            logger.debug("Failed to clean up old workflows: %s", exc)

    # ------------------------------------------------------------------
    # Backward-compatible create_workflow (calls ensure_workflow)
    # ------------------------------------------------------------------

    def create_workflow(
        self,
        project_name: str,
        aircraft_type: str,
        template_path: Optional[Path] = None,
    ) -> Optional[str]:
        return self.ensure_workflow(project_name, aircraft_type, template_path)

    # ------------------------------------------------------------------
    # Event pushers
    # ------------------------------------------------------------------

    def sync_project(
        self,
        project_name: str,
        aircraft_type: str,
        project_scope: str,
        round_label: str,
        workflow_profile: Optional[dict[str, Any]] = None,
    ) -> bool:
        """Push the current project profile into n8n."""
        if not self.available:
            return False
        body = {
            "project": project_name,
            "aircraft_type": aircraft_type,
            "project_scope": project_scope,
            "round_label": round_label,
            "workflow_profile": workflow_profile or {},
        }
        try:
            response = self._get_client().post(
                f"{self._base_url}/webhook/aeroforge/project-sync", json=body,
            )
            return response.status_code == 200
        except Exception as exc:
            logger.debug("Failed to sync project to n8n: %s", exc)
            return False

    def execute_step(
        self,
        sub_assembly: str,
        step: str,
        payload: Optional[dict[str, Any]] = None,
    ) -> Optional[str]:
        if not self.available:
            return None

        body = {
            "sub_assembly": sub_assembly,
            "step": step,
            "status": "running",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            **(payload or {}),
        }
        try:
            response = self._get_client().post(
                f"{self._base_url}/webhook/aeroforge/step-event", json=body,
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("executionId") if isinstance(data, dict) else None
        except Exception:
            return None
        return None

    def update_status(
        self,
        sub_assembly: str,
        step: str,
        status: str,
        notes: str = "",
    ) -> bool:
        if not self.available:
            return False

        body = {
            "sub_assembly": sub_assembly,
            "step": step,
            "status": status,
            "notes": notes,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        try:
            response = self._get_client().post(
                f"{self._base_url}/webhook/aeroforge/step-event", json=body,
            )
            return response.status_code == 200
        except Exception as exc:
            logger.debug("Failed to update n8n status: %s", exc)
            return False

    # ------------------------------------------------------------------
    # Visual dashboard workflow — rebuilt on every state change
    # ------------------------------------------------------------------

    def sync_visual_workflow(self, workflow_json: dict[str, Any]) -> Optional[str]:
        """Create or update the visual dashboard workflow in n8n.

        Deletes any previous dashboard workflow, then creates a new one
        from the provided JSON. Returns the workflow ID or None on failure.

        The dashboard workflow is separate from the event webhook workflow.
        It uses sticky notes arranged on the n8n canvas to visualize
        the current AeroForge workflow state.
        """
        if not self.available or not self._api_key:
            logger.warning("n8n not available or no API key — skipping visual sync")
            return None

        # Delete existing dashboard workflows (but NOT event workflows)
        self._delete_workflows_by_prefix("AeroForge Dashboard")

        # Build clean payload
        payload = {
            "name": workflow_json.get("name", "AeroForge Dashboard"),
            "nodes": workflow_json.get("nodes", []),
            "connections": workflow_json.get("connections", {}),
            "settings": workflow_json.get("settings", {}),
        }

        # Ensure nodes have required fields
        for i, node in enumerate(payload["nodes"]):
            node.setdefault("typeVersion", 1)
            node.setdefault("id", f"node-{i}")

        try:
            resp = self._get_client().post(
                f"{self._base_url}/api/v1/workflows", json=payload,
            )
            if resp.status_code != 200:
                logger.warning(
                    "Failed to create dashboard workflow: %s %s",
                    resp.status_code, resp.text[:200],
                )
                return None

            wf_id = resp.json().get("id")
            logger.info("n8n dashboard workflow synced (id=%s)", wf_id)
            return wf_id

        except Exception as exc:
            logger.warning("Failed to sync n8n dashboard workflow: %s", exc)
            return None

    def _delete_workflows_by_prefix(self, prefix: str) -> None:
        """Remove all workflows whose name starts with the given prefix."""
        try:
            resp = self._get_client().get(f"{self._base_url}/api/v1/workflows")
            if resp.status_code != 200:
                return
            for wf in resp.json().get("data", []):
                if wf.get("name", "").startswith(prefix):
                    wf_id = wf["id"]
                    self._get_client().delete(
                        f"{self._base_url}/api/v1/workflows/{wf_id}",
                    )
                    logger.info("Deleted n8n workflow: %s (id=%s)", wf["name"], wf_id)
        except Exception as exc:
            logger.debug("Failed to clean up workflows with prefix '%s': %s", prefix, exc)

    def status_summary(self) -> dict[str, Any]:
        """Return a summary for dashboard display."""
        return {
            "available": self.available,
            "base_url": self._base_url,
            "workflow_id": self._workflow_id,
            "has_api_key": bool(self._api_key),
        }

    def _load_template(self, path: Optional[Path] = None) -> Optional[dict[str, Any]]:
        target = path or (Path(__file__).parent / "workflow_template.json")
        if not target.exists():
            return None
        try:
            with open(target, "r", encoding="utf-8") as handle:
                return json.load(handle)
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Failed to load n8n template: %s", exc)
            return None
