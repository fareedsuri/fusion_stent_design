#!/usr/bin/env python3
"""
Test script to explore available Fusion 360 command input types
"""


def list_fusion_command_inputs():
    """
    List all available command input types in Fusion 360 based on the pattern we see in entry.py
    """

    print("Fusion 360 Command Input Types Found in Code:")
    print("=" * 50)

    input_types = [
        "addTextBoxCommandInput",           # Text box for descriptions
        "addGroupCommandInput",             # Groups to organize inputs
        "addValueCommandInput",             # Numeric value inputs with units
        "addIntegerSpinnerCommandInput",    # Integer spinner controls
        "addStringValueInput",              # String text inputs
        "addBoolValueInput",                # Checkboxes/toggles
        "addTableCommandInput",             # Tables with rows/columns
        # Radio button groups (what we're using)
        "addRadioButtonGroupCommandInput",
        "addSelectionInput",                # For selecting geometry
        "addDropDownCommandInput",          # The problematic dropdown we tried
    ]

    for input_type in input_types:
        print(f"• {input_type}")

    print("\n" + "=" * 50)
    print("Analysis for Material Selection:")
    print("=" * 50)

    print("\n1. addDropDownCommandInput:")
    print("   ❌ Had compilation errors with DropDownStyles")
    print("   ❌ API seems to have issues or requires specific imports")

    print("\n2. addRadioButtonGroupCommandInput:")
    print("   ✅ Currently working solution")
    print("   ✅ Provides clear visual selection")
    print("   ✅ No typing errors possible")
    print("   ⚠️  Takes more vertical space")

    print("\n3. addStringValueInput:")
    print("   ✅ Compact")
    print("   ❌ Requires typing (error-prone)")
    print("   ❌ Needs validation")

    print("\n4. Potential Combo Box Alternatives:")
    print("   • Table with single column (overkill)")
    print("   • Custom button that shows popup (complex)")
    print("   • Multiple grouped buttons (similar to radio)")

    print("\nConclusion:")
    print("Fusion 360 doesn't seem to have a traditional 'combo box' control.")
    print("The radio button group is the best dropdown-like solution available.")


if __name__ == "__main__":
    list_fusion_command_inputs()
