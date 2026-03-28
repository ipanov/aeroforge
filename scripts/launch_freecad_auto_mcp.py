#!/usr/bin/env python3
"""
Automatic FreeCAD Multi-Instance Launcher with MCP
===================================================

Launches multiple FreeCAD instances with automatic MCP configuration.

Usage:
    python scripts/launch_freecad_auto_mcp.py --count 5

This will:
1. Launch 5 FreeCAD instances as separate processes
2. Each with FREECAD_MCP_PORT environment variable set
3. Each running the auto-configuration startup script
4. Wait for all RPC servers to respond
5. Report success when ready
"""

import subprocess
import os
import sys
import time
import argparse
from pathlib import Path
import xmlrpc.client

# FreeCAD installation path (adjust if needed)
FREECAD_PATH = r"C:\Users\ilija\AppData\Local\Programs\FreeCAD 1.0\bin\FreeCAD.exe"

# Startup script path
STARTUP_SCRIPT = Path(__file__).parent / "freecad_startup_mcp.py"

# Base port
BASE_PORT = 9875


def find_freecad():
    """Find FreeCAD executable."""

    # Common installation paths
    possible_paths = [
        r"C:\Users\ilija\AppData\Local\Programs\FreeCAD 1.0\bin\FreeCAD.exe",
        r"C:\Program Files\FreeCAD 1.0\bin\FreeCAD.exe",
        r"C:\Program Files\FreeCAD 0.21\bin\FreeCAD.exe",
        r"C:\Program Files\FreeCAD 0.22\bin\FreeCAD.exe",
        r"C:\Program Files (x86)\FreeCAD 0.21\bin\FreeCAD.exe",
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    return None


def launch_freecad_instance(port: int) -> subprocess.Popen:
    """
    Launch a single FreeCAD instance with MCP auto-configuration.

    Args:
        port: RPC server port number

    Returns:
        subprocess.Popen object
    """

    freecad_exe = find_freecad()

    if not freecad_exe:
        raise FileNotFoundError("FreeCAD executable not found!")

    if not STARTUP_SCRIPT.exists():
        raise FileNotFoundError(f"Startup script not found: {STARTUP_SCRIPT}")

    # Set environment variable for port
    env = os.environ.copy()
    env["FREECAD_MCP_PORT"] = str(port)

    # Launch FreeCAD with startup script (pass script as positional argument)
    cmd = [
        freecad_exe,
        str(STARTUP_SCRIPT)
    ]

    print(f"Launching FreeCAD on port {port}...")
    print(f"  Command: {' '.join(cmd)}")
    print(f"  Env: FREECAD_MCP_PORT={port}")

    process = subprocess.Popen(
        cmd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
    )

    return process


def verify_instance(port: int, max_attempts: int = 30) -> bool:
    """
    Verify that FreeCAD instance is responding on port.

    Args:
        port: RPC server port
        max_attempts: Maximum verification attempts

    Returns:
        True if responding, False otherwise
    """

    print(f"Verifying port {port}...", end="", flush=True)

    for attempt in range(max_attempts):
        try:
            server = xmlrpc.client.ServerProxy(f"http://localhost:{port}", allow_none=True)
            result = server.ping()

            if result == "pong":
                print(f" ✓ Ready after {attempt+1} attempts")
                return True

        except Exception:
            pass

        time.sleep(2)
        print(".", end="", flush=True)

    print(f" ✗ Failed after {max_attempts} attempts")
    return False


def count_existing_instances():
    """Count how many FreeCAD instances are already running."""
    try:
        result = subprocess.run(
            ["tasklist", "/fi", "IMAGENAME eq freecad.exe"],
            capture_output=True, text=True
        )
        return result.stdout.lower().count("freecad.exe")
    except Exception:
        return 0


def launch_multiple_instances(count: int) -> list:
    """
    Launch multiple FreeCAD instances.

    Args:
        count: Number of instances to launch

    Returns:
        List of (port, process) tuples
    """

    # Pool-aware guard: enforce max 3 instances
    existing = count_existing_instances()
    if existing >= 3:
        print(f"ERROR: {existing} FreeCAD instances already running (max 3).")
        print("Use scripts/freecad_pool.py to manage instances.")
        sys.exit(1)

    to_launch = min(count, 3 - existing)
    if to_launch < count:
        print(f"WARNING: Only launching {to_launch} (already {existing} running, max 3)")

    print("=" * 70)
    print("FreeCAD Multi-Instance Launcher (Automatic MCP)")
    print("=" * 70)
    print(f"\nLaunching {to_launch} FreeCAD instances...")
    print()

    processes = []

    # Launch all instances
    for i in range(to_launch):
        port = BASE_PORT + i

        try:
            process = launch_freecad_instance(port)
            processes.append((port, process))
            time.sleep(3)  # Stagger launches

        except Exception as e:
            print(f"✗ Failed to launch instance {i+1}: {e}")

    print(f"\n✓ Launched {len(processes)} FreeCAD processes")
    print("\nWaiting for RPC servers to start...")
    print("(This takes ~10-15 seconds per instance)")
    print()

    # Verify all instances
    ready = []
    failed = []

    for port, process in processes:
        if verify_instance(port, max_attempts=30):
            ready.append(port)
        else:
            failed.append(port)

    # Report results
    print()
    print("=" * 70)
    print("Launch Results")
    print("=" * 70)
    print(f"\n✓ Ready: {len(ready)}/{count} instances")

    if ready:
        print("\nReady instances:")
        for port in ready:
            print(f"  - Port {port}")

    if failed:
        print("\n✗ Failed instances:")
        for port in failed:
            print(f"  - Port {port}")

    print()

    return processes


def main():
    """Main entry point."""

    parser = argparse.ArgumentParser(description="Launch FreeCAD instances with automatic MCP")
    parser.add_argument("--count", type=int, default=5, help="Number of instances to launch")
    args = parser.parse_args()

    try:
        processes = launch_multiple_instances(args.count)

        ready_count = sum(1 for port, _ in processes if verify_instance(port, max_attempts=1))

        if ready_count >= 3:
            print(f"✓ SUCCESS: {ready_count} instances ready!")
            print("\nYou can now run the multi-CAD coordinator:")
            print("  Task(subagent_type='general-purpose', prompt='Execute multi-agent CAD workflow for orange_blossom_nacelles_fairings', description='CAD Coordination')")
            return 0
        else:
            print(f"✗ FAILED: Only {ready_count} instances ready (need at least 3)")
            return 1

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        return 130

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
