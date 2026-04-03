"""REST API client for n8n workflow automation."""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "http://localhost:5678"
DEFAULT_TIMEOUT_S = 10


class N8nClient:
    """REST API client for optional n8n integration."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT_S,
    ) -> None:
        self._base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self._api_key = api_key
        self._timeout = timeout
        self._client: Optional[httpx.Client] = None
        self._available: Optional[bool] = None

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

    def create_workflow(
        self,
        project_name: str,
        aircraft_type: str,
        template_path: Optional[Path] = None,
    ) -> Optional[str]:
        if not self.available:
            return None

        template = self._load_template(template_path)
        if template is None:
            return None

        template["name"] = f"AeroForge - {project_name}"
        for node in template.get("nodes", []):
            if node.get("type") == "n8n-nodes-base.set":
                parameters = node.setdefault("parameters", {})
                values = parameters.setdefault("values", {})
                strings = values.setdefault("string", [])
                strings.append({"name": "aircraft_type", "value": aircraft_type})

        try:
            response = self._get_client().post(f"{self._base_url}/api/v1/workflows", json=template)
            response.raise_for_status()
            return str(response.json().get("id"))
        except Exception as exc:
            logger.warning("Failed to create n8n workflow: %s", exc)
            return None

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
            response = self._get_client().post(f"{self._base_url}/webhook/aeroforge/project-sync", json=body)
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
            response = self._get_client().post(f"{self._base_url}/webhook/aeroforge/step-event", json=body)
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
            response = self._get_client().post(f"{self._base_url}/webhook/aeroforge/step-event", json=body)
            return response.status_code == 200
        except Exception as exc:
            logger.debug("Failed to update n8n status: %s", exc)
            return False

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
