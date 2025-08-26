#!/usr/bin/env python3
"""
Test script to verify imports work correctly
"""


def test_imports():
    """Test that all modules can be imported"""

    print("Testing imports...")

    # Test standard library imports
    try:
        import math
        import traceback
        print("✓ Standard library imports successful")
    except Exception as e:
        print(f"✗ Standard library import failed: {e}")

    # Test relative import (as it would work in Fusion 360)
    try:
        # This simulates how it would work when loaded as an add-in
        import sys
        import os

        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.append(current_dir)

        from commands.commandDialog import entry as cmdDialog
        print("✓ Command dialog import successful")
        print(f"  Command ID: {cmdDialog.CMD_ID}")
        print(f"  Command Name: {cmdDialog.CMD_NAME}")

    except Exception as e:
        print(f"✗ Command dialog import failed: {e}")
        import traceback
        print(traceback.format_exc())

    # Test that the functions exist
    try:
        if 'cmdDialog' in locals():
            functions = ['start', 'stop', 'command_created',
                         'command_execute', 'draw_stent_frame']
            for func in functions:
                if hasattr(cmdDialog, func):
                    print(f"  ✓ Function {func} exists")
                else:
                    print(f"  ✗ Function {func} missing")
    except Exception as e:
        print(f"✗ Function check failed: {e}")


if __name__ == "__main__":
    test_imports()
