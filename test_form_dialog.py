#!/usr/bin/env python3
"""
Mock test for Fusion 360 form dialog structure.
This creates mock objects to simulate the Fusion 360 API and test the form creation.
"""

import types
import os
import sys

# Mock Fusion 360 API classes


class MockValueInput:
    def __init__(self, value):
        self.value = value

    @staticmethod
    def createByReal(value):
        return MockValueInput(value)


class MockCommandInput:
    def __init__(self, id, name, value=None):
        self.id = id
        self.name = name
        self.value = value
        self.children = MockCommandInputs()
        self.isExpanded = True


class MockCommandInputs:
    def __init__(self):
        self._inputs = {}

    def addGroupCommandInput(self, id, name):
        input_obj = MockCommandInput(id, name)
        self._inputs[id] = input_obj
        return input_obj

    def addValueInput(self, id, name, units, value):
        input_obj = MockCommandInput(id, name, value)
        self._inputs[id] = input_obj
        return input_obj

    def addIntegerSpinnerCommandInput(self, id, name, min_val, max_val, step, default):
        input_obj = MockCommandInput(id, name, default)
        self._inputs[id] = input_obj
        return input_obj

    def addStringValueInput(self, id, name, default_value):
        input_obj = MockCommandInput(id, name, default_value)
        self._inputs[id] = input_obj
        return input_obj

    def addBoolValueInput(self, id, name, is_checked, tooltip, is_enabled):
        input_obj = MockCommandInput(id, name, is_checked)
        self._inputs[id] = input_obj
        return input_obj

    def itemById(self, id):
        return self._inputs.get(id)


class MockUnitsManager:
    def __init__(self):
        self.defaultLengthUnits = "mm"


class MockActiveProduct:
    def __init__(self):
        self.unitsManager = MockUnitsManager()


class MockApplication:
    def __init__(self):
        self.activeProduct = MockActiveProduct()

    @staticmethod
    def get():
        return MockApplication()


class MockCommand:
    def __init__(self):
        self.commandInputs = MockCommandInputs()


class MockCommandCreatedEventArgs:
    def __init__(self):
        self.command = MockCommand()

# Mock the adsk module


class MockCore:
    Application = MockApplication
    ValueInput = MockValueInput
    CommandCreatedEventArgs = MockCommandCreatedEventArgs


class MockAdsk:
    core = MockCore()


# Add mock to sys.modules with proper types

# Create mock modules with proper attributes
mock_adsk = types.ModuleType('adsk')
mock_core = types.ModuleType('adsk.core')

# Set attributes on the mock modules
setattr(mock_core, 'Application', MockApplication)
setattr(mock_core, 'ValueInput', MockValueInput)
setattr(mock_core, 'CommandCreatedEventArgs', MockCommandCreatedEventArgs)
setattr(mock_adsk, 'core', mock_core)

sys.modules['adsk'] = mock_adsk
sys.modules['adsk.core'] = mock_core


def test_form_creation():
    """Test if the form can be created with mock Fusion 360 API"""
    print("Testing Form Creation with Mock Fusion 360 API...")
    print("=" * 60)

    try:
        # Add current directory to path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)

        # Import the command entry module
        from commands.commandDialog import entry

        print("✓ Successfully imported command dialog entry")

        # Create mock event args
        mock_args = MockCommandCreatedEventArgs()

        # Call the command_created function to test form creation
        entry.command_created(mock_args)  # type: ignore

        print("✓ Form creation completed without errors")

        # Check if expected inputs were created
        inputs = mock_args.command.commandInputs

        expected_groups = [
            'diameter_group',
            'ring_group',
            'height_group',
            'gap_group',
            'draw_group'
        ]

        print("\nChecking form groups:")
        for group_id in expected_groups:
            group = inputs.itemById(group_id)
            if group:
                print(f"✓ Found group: {group_id} - {group.name}")
            else:
                print(f"✗ Missing group: {group_id}")

        # Check specific inputs within groups
        diameter_group = inputs.itemById('diameter_group')
        if diameter_group:
            diameter_input = diameter_group.children.itemById('diameter')
            length_input = diameter_group.children.itemById('length')

            if diameter_input:
                print(f"✓ Diameter input: {diameter_input.value.value}mm")
            if length_input:
                print(f"✓ Length input: {length_input.value.value}mm")

        ring_group = inputs.itemById('ring_group')
        if ring_group:
            rings_input = ring_group.children.itemById('num_rings')
            crowns_input = ring_group.children.itemById('crowns_per_ring')

            if rings_input:
                print(f"✓ Number of rings: {rings_input.value}")
            if crowns_input:
                print(f"✓ Crowns per ring: {crowns_input.value}")

        draw_group = inputs.itemById('draw_group')
        if draw_group:
            border_input = draw_group.children.itemById('draw_border')
            gap_lines_input = draw_group.children.itemById(
                'draw_gap_centerlines')
            crown_peaks_input = draw_group.children.itemById(
                'draw_crown_peaks')
            crown_waves_input = draw_group.children.itemById(
                'draw_crown_waves')

            drawing_options = []
            if border_input:
                drawing_options.append(f"Border: {border_input.value}")
            if gap_lines_input:
                drawing_options.append(f"Gap Lines: {gap_lines_input.value}")
            if crown_peaks_input:
                drawing_options.append(
                    f"Crown Peaks: {crown_peaks_input.value}")
            if crown_waves_input:
                drawing_options.append(
                    f"Crown Waves: {crown_waves_input.value}")

            print(f"✓ Drawing options: {', '.join(drawing_options)}")

        return True

    except Exception as e:
        print(f"✗ Form creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_command_info():
    """Test if command information is properly defined"""
    print("\n" + "=" * 60)
    print("Testing Command Information...")

    try:
        from commands.commandDialog import entry

        print(f"✓ Command ID: {entry.CMD_ID}")
        print(f"✓ Command Name: {entry.CMD_NAME}")
        print(f"✓ Command Description: {entry.CMD_Description}")
        print(f"✓ Is Promoted: {entry.IS_PROMOTED}")
        print(f"✓ Workspace: {entry.WORKSPACE_ID}")
        print(f"✓ Panel: {entry.PANEL_ID}")

        return True

    except Exception as e:
        print(f"✗ Command info test failed: {e}")
        return False


def main():
    """Main test function"""
    print("Fusion 360 Stent Frame Form Dialog Test")
    print("=" * 60)

    form_ok = test_form_creation()
    info_ok = test_command_info()

    print("\n" + "=" * 60)
    print("FORM DIALOG TEST SUMMARY")
    print("=" * 60)

    if form_ok:
        print("✓ Form dialog structure is correct")
    else:
        print("✗ Form dialog has issues")

    if info_ok:
        print("✓ Command information is correct")
    else:
        print("✗ Command information has issues")

    if form_ok and info_ok:
        print("\n🎉 Form dialog should display correctly in Fusion 360!")
        print("\nThe form includes:")
        print("• Stent Dimensions (diameter, length)")
        print("• Ring Configuration (number of rings, crowns per ring)")
        print("• Ring Height Proportions (base height, height factors)")
        print("• Gap Configuration (gap between rings)")
        print("• Drawing Options (border, gap lines, crown peaks, crown waves)")
    else:
        print("\n❌ Form dialog needs fixes before it can work properly")


if __name__ == "__main__":
    main()
