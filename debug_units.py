#!/usr/bin/env python3
"""
Diagnostic for unit conversion issues in Fusion 360
"""


def diagnose_unit_issue():
    print("Fusion 360 Unit Conversion Diagnostic")
    print("=" * 50)

    print("\nPOSSIBLE SCENARIOS:")
    print("1. User enters 8.0, sees 80.0 displayed")
    print("   → Factor of 10 conversion (mm to cm mistake)")
    print("   → Should see: 8.0 mm")

    print("\n2. User enters 1.8, sees 18.0 displayed")
    print("   → Factor of 10 conversion")
    print("   → Should see: 1.8 mm")

    print("\n3. User enters 8, UI shows 80")
    print("   → Possible cm→mm internal conversion (8 cm = 80 mm)")
    print("   → Wrong: Fusion treating input as cm")
    print("   → Should treat as: 8 mm")

    print("\nRECENT CHANGES MADE:")
    print("✅ Changed: defaultLengthUnits → 'mm'")
    print("✅ Changed: createByReal() → createByString('X.X mm')")
    print("✅ Maintained: All labels show '(mm)'")

    print("\nIF STILL SHOWING 80:")
    print("❓ Check: Which specific field shows 80?")
    print("❓ Check: What value was entered?")
    print("❓ Check: Fusion document units (File→Preferences→Default Units)")
    print("❓ Check: Is 80 in dialog display or in actual geometry?")

    print("\nDEBUGGING STEPS:")
    print("1. Enter 1.0 in diameter field")
    print("2. Check if it displays as 1.0 or 10.0")
    print("3. Check if generated geometry is 1mm or 10mm diameter")
    print("4. Report back what you see vs what you expect")

    print(f"\nCURRENT DEFAULT VALUES:")
    defaults = {
        'diameter': 1.8,  # mm
        'length': 8,      # mm
    }

    for key, value in defaults.items():
        print(f"  {key}: {value} mm")

    print(f"\nIF 8 is showing as 80:")
    print(f"  → 8 mm being treated as 8 cm = 80 mm")
    print(f"  → Need to verify createByString() is working")


if __name__ == "__main__":
    diagnose_unit_issue()
