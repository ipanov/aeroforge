"""HTTP monitor for the workflow dashboard and state JSON."""

from __future__ import annotations

import json
import os
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from .project_settings import PROJECT_SETTINGS_FILE
from .workflow_engine import WorkflowEngine


class WorkflowMonitorServer:
    """Serve the generated dashboard and workflow state over HTTP."""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8787,
        launch_n8n: bool = False,
    ) -> None:
        self._host = host
        self._port = port
        self._launch_n8n = launch_n8n
        self._n8n_process: Optional[subprocess.Popen[str]] = None
        self._engine = WorkflowEngine()

    def serve_forever(self) -> None:
        """Start the HTTP server and optionally launch n8n."""

        if self._launch_n8n:
            self._n8n_process = launch_n8n_process()

        engine = self._engine

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
    """Launch n8n using the local or global Node toolchain."""

    env = os.environ.copy()
    command = env.get("AEROFORGE_N8N_COMMAND")
    if command:
        args = command.split()
    else:
        args = ["npx", "n8n", "start", "--host", "127.0.0.1", "--port", "5678"]

    return subprocess.Popen(
        args,
        cwd=str(Path(__file__).resolve().parents[2]),
        env=env,
    )
