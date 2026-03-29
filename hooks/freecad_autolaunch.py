"""PreToolUse hook for ALL mcp__freecad__* tools.

Ensures FreeCAD is running with RPC server before any FreeCAD MCP call.
If FreeCAD is not reachable, launches it automatically with auto_start_rpc=true.
Avoids spawning duplicate instances.

Logic:
    1. Test RPC connection (xmlrpc to localhost:9875)
    2. If connected → exit 0 (proceed)
    3. If not connected → check if freecad.exe process exists
       a. If process exists but RPC not ready → wait up to 20s for RPC
       b. If no process → launch FreeCAD, wait up to 25s for RPC
    4. If RPC still not ready after waiting → exit 2 (BLOCK, let Claude retry)

Manual test:
    echo '{}' | python hooks/freecad_autolaunch.py
"""

import json
import os
import subprocess
import sys
import time
import xmlrpc.client

FREECAD_EXE = r"C:\Users\ilija\AppData\Local\Programs\FreeCAD 1.0\bin\freecad.exe"
RPC_URL = "http://localhost:9875"
RPC_TIMEOUT = 3  # seconds for each probe
LAUNCH_WAIT_MAX = 25  # seconds to wait after launching
PROCESS_WAIT_MAX = 20  # seconds to wait if process exists but RPC not ready


def rpc_is_alive() -> bool:
    """Test if FreeCAD RPC server responds."""
    try:
        server = xmlrpc.client.ServerProxy(RPC_URL, allow_none=True)
        # FreeCAD MCP doesn't support system.listMethods, use execute_code probe
        result = server.execute_code("print('ping')")
        return isinstance(result, dict) and result.get("success", False)
    except xmlrpc.client.Fault:
        # Server is alive but method errored — still means RPC is running
        return True
    except Exception:
        return False


def freecad_process_running() -> bool:
    """Check if any freecad.exe process is running (avoids duplicates)."""
    try:
        result = subprocess.run(
            ["tasklist"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        for line in result.stdout.lower().split("\n"):
            # Match freecad.exe but NOT freecad-mcp.exe
            if "freecad.exe" in line and "freecad-mcp" not in line:
                return True
    except Exception:
        pass
    return False


def wait_for_rpc(timeout: int) -> bool:
    """Poll RPC server until it responds or timeout expires."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if rpc_is_alive():
            return True
        time.sleep(2)
    return False


def ensure_autostart_setting():
    """Make sure auto_start_rpc is true in FreeCAD MCP settings."""
    settings_path = os.path.join(
        os.environ.get("APPDATA", ""),
        "FreeCAD",
        "freecad_mcp_settings.json",
    )
    try:
        if os.path.exists(settings_path):
            with open(settings_path, "r") as f:
                settings = json.load(f)
        else:
            settings = {}

        if not settings.get("auto_start_rpc", False):
            settings["auto_start_rpc"] = True
            settings.setdefault("remote_enabled", False)
            settings.setdefault("allowed_ips", "127.0.0.1")
            os.makedirs(os.path.dirname(settings_path), exist_ok=True)
            with open(settings_path, "w") as f:
                json.dump(settings, f, indent=2)
            print("[freecad-hook] Enabled auto_start_rpc in settings", file=sys.stderr)
    except Exception as exc:
        print(f"[freecad-hook] Could not update settings: {exc}", file=sys.stderr)


def main() -> int:
    """Returns 0 (proceed) or 2 (BLOCK)."""
    # Consume stdin (hook protocol requires it)
    sys.stdin.read()

    # Step 1: Already connected?
    if rpc_is_alive():
        return 0

    print("[freecad-hook] FreeCAD RPC not responding, checking process...", file=sys.stderr)

    # Step 2: Process running but RPC not ready?
    if freecad_process_running():
        print("[freecad-hook] FreeCAD process found, waiting for RPC...", file=sys.stderr)
        if wait_for_rpc(PROCESS_WAIT_MAX):
            print("[freecad-hook] RPC connected (process was starting up)", file=sys.stderr)
            return 0
        else:
            print(
                f"[freecad-hook] BLOCKED: FreeCAD running but RPC not responding after {PROCESS_WAIT_MAX}s. "
                "RPC server may not be enabled — check FreeCAD MCP addon.",
                file=sys.stderr,
            )
            return 2

    # Step 3: No process → launch FreeCAD
    print("[freecad-hook] No FreeCAD process found, launching...", file=sys.stderr)
    ensure_autostart_setting()

    try:
        subprocess.Popen(
            [FREECAD_EXE],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
        )
        print(f"[freecad-hook] Launched: {FREECAD_EXE}", file=sys.stderr)
    except FileNotFoundError:
        print(f"[freecad-hook] BLOCKED: FreeCAD not found at {FREECAD_EXE}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"[freecad-hook] BLOCKED: Failed to launch FreeCAD: {exc}", file=sys.stderr)
        return 2

    # Wait for RPC to come alive
    if wait_for_rpc(LAUNCH_WAIT_MAX):
        print("[freecad-hook] RPC connected after launch", file=sys.stderr)
        return 0

    print(
        f"[freecad-hook] BLOCKED: FreeCAD launched but RPC not ready after {LAUNCH_WAIT_MAX}s. "
        "Will retry on next tool call.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
