"""HTTP monitor for the workflow dashboard and state JSON.

n8n is a MANDATORY component launched alongside the monitor server.
The workflow engine will not operate without a reachable n8n instance.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from .project_settings import PROJECT_SETTINGS_FILE
from .workflow_engine import WorkflowEngine

logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _ensure_n8n_installed() -> None:
    """Install n8n via npm if not already present."""
    node_modules = _PROJECT_ROOT / "node_modules"
    if not (node_modules / "n8n").exists():
        logger.info("n8n not found locally. Running npm install...")
        subprocess.run(["npm", "install"], cwd=str(_PROJECT_ROOT), check=True)


class WorkflowMonitorServer:
    """Serve the generated dashboard and workflow state over HTTP."""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8787,
    ) -> None:
        self._host = host
        self._port = port
        self._n8n_process: Optional[subprocess.Popen[str]] = None
        self._engine = WorkflowEngine()

    def serve_forever(self) -> None:
        """Start the HTTP server and launch n8n."""

        _ensure_n8n_installed()
        self._n8n_process = launch_n8n_process()

        engine = self._engine
        n8n_proc = self._n8n_process

        class _Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802 - stdlib signature
                parsed = urlparse(self.path)
                route = parsed.path.rstrip("/") or "/"

                if route in {"/", "/dashboard"}:
                    dashboard_path = engine.generate_dashboard()
                    content = dashboard_path.read_text(encoding="utf-8")
                    self._write_response(200, content, "text/html; charset=utf-8")
                    return

                if route in {"/api/state", "/api/status"}:
                    payload = engine.get_status()
                    self._write_response(
                        200,
                        json.dumps(payload, indent=2),
                        "application/json; charset=utf-8",
                    )
                    return

                if route == "/api/settings":
                    if PROJECT_SETTINGS_FILE.exists():
                        content = PROJECT_SETTINGS_FILE.read_text(encoding="utf-8")
                        self._write_response(200, content, "application/x-yaml; charset=utf-8")
                    else:
                        self._write_response(404, "{}", "application/json; charset=utf-8")
                    return

                if route == "/api/n8n-status":
                    n8n_info = {
                        "available": engine.n8n_available,
                        "process_running": (
                            n8n_proc is not None and n8n_proc.poll() is None
                        ),
                    }
                    self._write_response(
                        200,
                        json.dumps(n8n_info, indent=2),
                        "application/json; charset=utf-8",
                    )
                    return

                self._write_response(404, "Not Found", "text/plain; charset=utf-8")

            def log_message(self, format: str, *args: object) -> None:  # noqa: A003
                return

            def _write_response(self, status: int, body: str, content_type: str) -> None:
                encoded = body.encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(encoded)))
                self.end_headers()
                self.wfile.write(encoded)

        server = ThreadingHTTPServer((self._host, self._port), _Handler)
        try:
            server.serve_forever()
        finally:
            server.server_close()
            if self._n8n_process and self._n8n_process.poll() is None:
                self._n8n_process.terminate()


def launch_n8n_process() -> subprocess.Popen[str]:
    """Launch n8n using the local or global Node toolchain.

    n8n is mandatory — this function raises if it cannot be started.
    """
    import shutil

    env = os.environ.copy()
    command = env.get("AEROFORGE_N8N_COMMAND")
    if command:
        args = command.split()
    else:
        # Try direct n8n binary first (global install), then npx
        n8n_path = shutil.which("n8n")
        if n8n_path:
            args = [n8n_path, "start", "--host", "127.0.0.1", "--port", "5678"]
        else:
            npx_path = shutil.which("npx")
            if npx_path:
                args = [npx_path, "n8n", "start", "--host", "127.0.0.1", "--port", "5678"]
            else:
                raise FileNotFoundError(
                    "Neither 'n8n' nor 'npx' found on PATH. "
                    "Install n8n with: npm install -g n8n"
                )

    return subprocess.Popen(
        args,
        cwd=str(Path(__file__).resolve().parents[2]),
        env=env,
    )
