#!/usr/bin/env python3
"""
Fusion 360 Stent Frame Add-in - Installation and Usage Guide
"""

import os


def print_installation_guide():
    """Print detailed instructions for installing and testing the add-in in Fusion 360"""

    print("🔧 FUSION 360 STENT FRAME ADD-IN INSTALLATION GUIDE")
    print("=" * 60)

    print("\n📁 STEP 1: Install the Add-in")
    print("-" * 30)
    print("1. Open Fusion 360")
    print("2. Go to 'Scripts and Add-ins' (Tools menu or Utilities panel)")
    print("3. Click the 'Add-ins' tab")
    print("4. Click the green '+' button to add a new add-in")
    print("5. Navigate to this folder:")
    print(f"   {os.path.dirname(os.path.abspath(__file__))}")
    print("6. Select the folder and click 'Open'")
    print("7. The 'Stent Frame Designer' should appear in the add-ins list")

    print("\n▶️ STEP 2: Run the Add-in")
    print("-" * 30)
    print("1. In the Add-ins list, find 'Stent Frame Designer'")
    print("2. Click 'Run' to load the add-in")
    print("3. A button should appear in the Scripts and Add-ins panel")
    print("   (Look for 'Stent Frame Designer' button)")

    print("\n🎛️ STEP 3: Test the Form Dialog")
    print("-" * 30)
    print("1. Click the 'Stent Frame Designer' button")
    print("2. A dialog should open with the following sections:")
    print("   • Stent Dimensions")
    print("     - Diameter (mm): Default 1.8mm")
    print("     - Length (mm): Default 8.0mm")
    print("   • Ring Configuration")
    print("     - Number of Rings: Default 6")
    print("     - Crowns per Ring: Default 8")
    print("   • Ring Height Proportions")
    print("     - Base Ring Height (mm): Default 0.140mm")
    print("     - Height Factors: Default '1.20, 1.00, 1.00, 1.00, 1.00, 1.10'")
    print("   • Gap Configuration")
    print("     - Gap Between Rings (mm): Default 0.200mm")
    print("   • Drawing Options")
    print("     - Draw Border: ✓")
    print("     - Draw Gap Center Lines: ✓")
    print("     - Draw Crown Peak Lines: ✓")
    print("     - Draw Crown Wave Lines: ✓")

    print("\n✏️ STEP 4: Create Stent Frame")
    print("-" * 30)
    print("1. Adjust parameters as needed")
    print("2. Click 'OK' to create the stent frame")
    print("3. The sketch should be created with construction lines:")
    print("   • Border lines (top, bottom, left, right)")
    print("   • Gap center lines (horizontal)")
    print("   • Crown peak lines (horizontal)")
    print("   • Crown wave lines (vertical)")

    print("\n🔍 STEP 5: Verify Results")
    print("-" * 30)
    print("Expected output for default parameters:")
    print("• Total of 26 construction lines")
    print("• 15 horizontal lines (gaps + crown peaks)")
    print("• 7 vertical lines (crown waves)")
    print("• 4 border lines")
    print("• Ring scale factor: ~7.937")
    print("• Total width: ~5.655mm")

    print("\n❗ TROUBLESHOOTING")
    print("-" * 30)
    print("If the add-in doesn't load:")
    print("1. Check that all files are in the correct folder structure")
    print("2. Verify the manifest file is valid JSON")
    print("3. Try restarting Fusion 360")
    print("4. Check the Text Commands window for error messages")

    print("If the form doesn't appear:")
    print("1. Look for the button in the Scripts panel")
    print("2. Check if any error messages appear")
    print("3. Try running from the Scripts and Add-ins dialog")

    print("If drawing fails:")
    print("1. Ensure you're in a sketch environment")
    print("2. Check that the active component exists")
    print("3. Verify parameter values are valid")


def check_files():
    """Check if all required files exist"""

    print("\n📋 FILE STRUCTURE CHECK")
    print("-" * 30)

    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))

    required_files = [
        'stent_frame.py',
        'stent_frame.manifest',
        'config.py',
        'AddInIcon.svg',
        'commands/__init__.py',
        'commands/commandDialog/__init__.py',
        'commands/commandDialog/entry.py',
        'lib/fusionAddInUtils/__init__.py',
        'lib/fusionAddInUtils/event_utils.py',
        'lib/fusionAddInUtils/general_utils.py'
    ]

    all_exist = True
    for file_path in required_files:
        full_path = os.path.join(current_dir, file_path)
        if os.path.exists(full_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path}")
            all_exist = False

    if all_exist:
        print("\n✅ All required files are present!")
    else:
        print("\n❌ Some files are missing!")

    return all_exist


def main():
    """Main function"""
    import os

    files_ok = check_files()
    print_installation_guide()

    if files_ok:
        print("\n🎉 READY TO TEST IN FUSION 360!")
        print("Follow the installation guide above to test the form dialog.")
    else:
        print("\n⚠️ Fix missing files before testing in Fusion 360.")


if __name__ == "__main__":
    main()
