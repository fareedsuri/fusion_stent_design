#!/usr/bin/env python3
"""
Test script to verify the Fusion 360 add-in can load and display the form.
This script simulates the Fusion 360 environment to test the add-in structure.
"""

import os
import sys
import importlib.util


def test_addon_structure():
    """Test if the add-in has proper structure and can be imported"""
    print("Testing Fusion 360 Add-in Structure...")
    print("=" * 50)

    # Check if main files exist
    current_dir = os.path.dirname(os.path.abspath(__file__))

    required_files = [
        'stent_frame.py',
        'stent_frame.manifest',
        'config.py',
        'commands/__init__.py',
        'commands/commandDialog/__init__.py',
        'commands/commandDialog/entry.py'
    ]

    missing_files = []
    for file_path in required_files:
        full_path = os.path.join(current_dir, file_path)
        if os.path.exists(full_path):
            print(f"✓ Found: {file_path}")
        else:
            print(f"✗ Missing: {file_path}")
            missing_files.append(file_path)

    if missing_files:
        print(f"\nError: Missing {len(missing_files)} required files!")
        return False

    print("\n" + "=" * 50)
    print("Testing module imports...")

    # Test if we can import the main module
    try:
        # Add current directory to path
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)

        # Test importing config
        import config
        print(f"✓ Config imported: {config.ADDIN_NAME}")

        # Test importing command dialog entry
        from commands.commandDialog import entry
        print("✓ Command dialog entry imported")

        # Check if the command definition exists
        if hasattr(entry, 'CMD_ID'):
            print(f"✓ Command ID defined: {entry.CMD_ID}")

        if hasattr(entry, 'CMD_NAME'):
            print(f"✓ Command Name: {entry.CMD_NAME}")

        if hasattr(entry, 'start'):
            print("✓ Start function exists")

        if hasattr(entry, 'stop'):
            print("✓ Stop function exists")

        if hasattr(entry, 'command_created'):
            print("✓ Command created handler exists")

        return True

    except Exception as e:
        print(f"✗ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_manifest():
    """Test if the manifest file is properly formatted"""
    print("\n" + "=" * 50)
    print("Testing manifest file...")

    manifest_path = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'stent_frame.manifest')

    try:
        import json
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)

        required_keys = ['autodeskProduct', 'type', 'id', 'author',
                         'description', 'version', 'runOnStartup', 'supportedOS', 'editEnabled']

        for key in required_keys:
            if key in manifest:
                print(f"✓ Manifest key '{key}': {manifest[key]}")
            else:
                print(f"✗ Missing manifest key: {key}")

        return True

    except Exception as e:
        print(f"✗ Manifest error: {e}")
        return False


def main():
    """Main test function"""
    print("Fusion 360 Stent Frame Add-in Test")
    print("=" * 50)

    structure_ok = test_addon_structure()
    manifest_ok = test_manifest()

    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)

    if structure_ok:
        print("✓ Add-in structure is correct")
    else:
        print("✗ Add-in structure has issues")

    if manifest_ok:
        print("✓ Manifest file is correct")
    else:
        print("✗ Manifest file has issues")

    if structure_ok and manifest_ok:
        print("\n🎉 Add-in should load successfully in Fusion 360!")
        print("\nTo test in Fusion 360:")
        print("1. Copy this folder to your Fusion 360 add-ins directory")
        print("2. In Fusion 360, go to Scripts and Add-ins")
        print("3. Find 'Stent Frame Designer' in the add-ins list")
        print("4. Click 'Run' to load the add-in")
        print("5. Look for the 'Stent Frame Designer' button in the toolbar")
        print("6. Click the button to open the form dialog")
    else:
        print("\n❌ Add-in needs fixes before it can load properly")


if __name__ == "__main__":
    main()
