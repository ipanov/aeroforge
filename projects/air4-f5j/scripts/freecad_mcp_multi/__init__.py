"""
Custom FreeCAD MCP Wrapper with Multi-Instance Support
=======================================================

This wrapper extends freecad-mcp to support multiple FreeCAD instances
by allowing port configuration via command line arguments.

Usage:
    python -m scripts.freecad_mcp_multi --port 9875
    python -m scripts.freecad_mcp_multi --port 9876 --only-text-feedback

Author: Clear Skies Project
Date: 2026-01-12
"""

import argparse
import os
import sys


def main():
    """Main entry point for custom FreeCAD MCP server."""

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="FreeCAD MCP Server with configurable port"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=9875,
        help="Port for FreeCAD XML-RPC server (default: 9875)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Host for FreeCAD XML-RPC server (default: localhost)"
    )
    parser.add_argument(
        "--only-text-feedback",
        action="store_true",
        help="Only return text feedback (saves tokens)"
    )

    # Parse our custom args first, before freecad-mcp sees them
    args, unknown = parser.parse_known_args()

    # Set environment variables that patched server will read
    os.environ["FREECAD_RPC_PORT"] = str(args.port)
    os.environ["FREECAD_RPC_HOST"] = args.host

    if args.only_text_feedback:
        os.environ["FREECAD_ONLY_TEXT"] = "1"

    print(f"[FreeCAD MCP Multi] Connecting to FreeCAD at {args.host}:{args.port}", file=sys.stderr)

    # Monkey-patch the original freecad-mcp to use our port
    print(f"[FreeCAD MCP Multi] Monkey-patching freecad-mcp for port {args.port}", file=sys.stderr)

    try:
        import freecad_mcp.server as original_server

        # Monkey-patch the FreeCADConnection class BEFORE importing main
        original_init = original_server.FreeCADConnection.__init__

        def patched_init(self, host: str = "localhost", port: int = 9875):
            """Patched __init__ that reads port from environment."""
            import xmlrpc.client

            # Override with environment variables if set
            host = os.environ.get("FREECAD_RPC_HOST", host)
            port = int(os.environ.get("FREECAD_RPC_PORT", str(port)))

            print(f"[FreeCAD MCP Multi] Actually connecting to {host}:{port}", file=sys.stderr)

            self.server = xmlrpc.client.ServerProxy(
                f"http://{host}:{port}",
                allow_none=True
            )

        # Apply monkey patch
        original_server.FreeCADConnection.__init__ = patched_init

        # Modify sys.argv to only include args that freecad-mcp understands
        original_argv = sys.argv.copy()
        sys.argv = [sys.argv[0]]  # Keep program name
        if args.only_text_feedback:
            sys.argv.append("--only-text-feedback")

        # Run original main
        from freecad_mcp.server import main as original_main
        original_main()

        # Restore original argv
        sys.argv = original_argv

    except ImportError as e:
        print(f"[FreeCAD MCP Multi] ERROR: Could not import freecad-mcp: {e}", file=sys.stderr)
        print(f"[FreeCAD MCP Multi] Make sure freecad-mcp is installed: pip install freecad-mcp", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
