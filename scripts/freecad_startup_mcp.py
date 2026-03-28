"""
FreeCAD Startup Script for MCP Configuration
==============================================

This script runs automatically when FreeCAD starts to:
1. Switch to MCP workbench
2. Configure RPC port from environment variable
3. Start RPC server

Usage:
    FreeCAD.exe freecad_startup_mcp.py

Environment Variables:
    FREECAD_MCP_PORT - Port number for RPC server (default: 9875)
"""

import FreeCAD
import FreeCADGui
import os
import time
import sys

# Log to file for debugging
log_file = os.path.join(os.path.dirname(__file__), f"startup_log_{os.getpid()}.txt")
log_handle = open(log_file, 'w', buffering=1)
sys.stdout = log_handle
sys.stderr = log_handle

def log(msg):
    print(msg)
    log_handle.flush()

log(f"STARTUP SCRIPT EXECUTING - PID: {os.getpid()}")
log(f"Python: {sys.version}")
log(f"FreeCAD Version: {FreeCAD.Version()}")

def configure_and_start_mcp():
    """Configure MCP addon and start RPC server."""

    # Get port from environment variable
    port = int(os.environ.get("FREECAD_MCP_PORT", "9875"))

    log(f"=" * 70)
    log(f"FreeCAD MCP Startup Configuration")
    log(f"=" * 70)
    log(f"Target port: {port}")

    # Wait for GUI to initialize
    log("Waiting for GUI initialization...")
    time.sleep(3)

    try:
        # Step 1: Set port preference
        log("\nSetting MCP port preference...")
        param_group = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/FreeCADMCP")
        param_group.SetInt("rpc_port", port)
        param_group.SetString("rpc_host", "localhost")
        log(f"  ✓ Set port to {port}")

    except Exception as e:
        log(f"  ✗ Could not set preference: {e}")

    server_started = False

    # Add FreeCAD Mod directory to Python path
    try:
        freecad_mod_path = os.path.join(os.environ.get('APPDATA', ''), 'FreeCAD', 'Mod')
        if os.path.exists(freecad_mod_path) and freecad_mod_path not in sys.path:
            sys.path.insert(0, freecad_mod_path)
            log(f"Added to sys.path: {freecad_mod_path}")
    except Exception as e:
        log(f"  ⚠ Could not add Mod path: {e}")

    try:
        # Step 2: Import and start MCP server directly from FreeCADMCP addon
        log("\nStarting RPC server via FreeCADMCP addon...")

        # Import the addon's RPC server module
        from FreeCADMCP.rpc_server import rpc_server

        # Start server (it runs in its own thread internally)
        rpc_server.start_rpc_server(host="localhost", port=port)
        time.sleep(2)  # Give server time to start

        log(f"  ✓ Started RPC server on port {port}")
        server_started = True

    except Exception as e:
        log(f"  ✗ Could not start via direct import: {e}")
        log(f"  Traceback: {__import__('traceback').format_exc()}")

    if not server_started:
        try:
            # Step 3: Try using FreeCAD's workbench/addon system
            log("\nTrying to activate MCP workbench...")

            # Try to load InitGui which should have server start methods
            from FreeCADMCP import InitGui

            # Try to find and call start server method
            if hasattr(InitGui, 'start_rpc_server'):
                InitGui.start_rpc_server(port)
                server_started = True
                log(f"  ✓ Started via InitGui API")
            elif hasattr(InitGui, 'startServer'):
                InitGui.startServer(port)
                server_started = True
                log(f"  ✓ Started via InitGui.startServer")

        except Exception as e:
            log(f"  ✗ Could not start via workbench: {e}")
            log(f"  Traceback: {__import__('traceback').format_exc()}")

    # Verify server status
    log("\nVerifying RPC server...")
    time.sleep(1)

    for attempt in range(5):
        try:
            import xmlrpc.client
            server = xmlrpc.client.ServerProxy(f"http://localhost:{port}", allow_none=True)
            result = server.ping()
            log(f"  ✓ RPC server responding on port {port}: {result}")
            break
        except Exception as e:
            if attempt < 4:
                log(f"  Attempt {attempt+1}/5 failed, retrying...")
                time.sleep(1)
            else:
                log(f"  ✗ RPC server not responding after 5 attempts")
                log(f"  ERROR: Automatic startup failed!")
                log(f"  Final error: {e}")

    log("\n" + "=" * 70)
    log("Startup script complete")
    log("=" * 70)

# Run configuration immediately (don't use if __name__ == "__main__" as FreeCAD doesn't set it)
try:
    log("\nStarting configuration...")
    log(f"Environment FREECAD_MCP_PORT: {os.environ.get('FREECAD_MCP_PORT', 'NOT SET')}")

    try:
        # Try using QTimer for delayed execution
        log("Attempting to set up QTimer...")
        from PySide2 import QtCore
        QtCore.QTimer.singleShot(3000, configure_and_start_mcp)
        log("QTimer set for 3 second delay")
    except Exception as e:
        log(f"QTimer failed: {e}")
        log(f"Traceback: {__import__('traceback').format_exc()}")
        # Fallback: run immediately after a simple sleep
        log("Falling back to direct execution...")
        time.sleep(5)
        configure_and_start_mcp()

except Exception as e:
    log(f"\nFATAL ERROR IN STARTUP SCRIPT: {e}")
    log(f"Traceback: {__import__('traceback').format_exc()}")
finally:
    log("\nStartup script finished")
    log_handle.flush()
