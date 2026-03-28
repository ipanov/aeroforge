#!/usr/bin/env python3
"""
Verify FreeCAD Instances
=========================

Checks that all FreeCAD instances in the pool are running and responsive.

Usage:
    python scripts/verify_freecad_instances.py

Author: Clear Skies Project
Date: 2026-01-12
"""

import xmlrpc.client
import sys


def verify_instance(port):
    """
    Verify FreeCAD instance on given port.

    Args:
        port: Port number to check

    Returns:
        bool: True if instance is responsive, False otherwise
    """
    try:
        server = xmlrpc.client.ServerProxy(
            f"http://localhost:{port}",
            allow_none=True
        )

        # Try to ping
        result = server.ping()
        print(f"  ✓ Port {port}: {result}")
        return True

    except ConnectionRefusedError:
        print(f"  ✗ Port {port}: Connection refused (RPC server not started)")
        return False

    except Exception as e:
        print(f"  ✗ Port {port}: ERROR - {str(e)[:50]}")
        return False


def main():
    """Main verification routine."""

    print("=" * 60)
    print("FreeCAD Instance Verification")
    print("=" * 60)
    print()

    # Default ports for 5 instances
    ports = [9875, 9876, 9877, 9878, 9879]

    results = {}

    for port in ports:
        results[port] = verify_instance(port)

    # Summary
    print()
    print("=" * 60)

    ready = sum(results.values())
    total = len(ports)

    print(f"Ready: {ready}/{total} instances")

    if ready >= 4:
        print("✓ Sufficient instances for multi-agent workflow (need >= 4)")
        exit_code = 0
    elif ready > 0:
        print(f"⚠ Only {ready} instances ready. Need at least 4 for optimal performance.")
        exit_code = 1
    else:
        print("✗ No instances responding! Please start FreeCAD instances.")
        exit_code = 2

    print("=" * 60)

    # Detailed instructions if some failed
    if ready < total:
        print()
        print("Failed Instances - Troubleshooting:")
        for port, success in results.items():
            if not success:
                instance_num = port - 9874
                print(f"\nInstance {instance_num} (Port {port}):")
                print("  1. Launch FreeCAD")
                print(f"  2. Edit → Preferences → FreeCAD MCP → Port: {port}")
                print("  3. Toolbar → FreeCAD MCP → Start RPC Server")

    return exit_code


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
