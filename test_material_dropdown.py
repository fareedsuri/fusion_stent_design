#!/usr/bin/env python3
"""
Simple test to verify the radio button material selection logic
"""

# Simulate the material options and selection logic
material_options = ['Pebax', 'COC', 'Nylon', 'Polyurethane', 'PTFE']

# Simulate list items with isSelected property


class MockListItem:
    def __init__(self, name, is_selected=False):
        self.name = name
        self.isSelected = is_selected

# Test the selection logic


def test_material_selection():
    print("Testing material selection logic...")

    # Test case 1: Pebax selected (index 0)
    mock_items = [
        MockListItem('Pebax', True),
        MockListItem('COC', False),
        MockListItem('Nylon', False),
        MockListItem('Polyurethane', False),
        MockListItem('PTFE', False)
    ]

    balloon_material = 'Pebax'  # Default
    for i, item in enumerate(mock_items):
        if item.isSelected:
            balloon_material = material_options[i]
            break

    print(f"Test 1 - Expected: Pebax, Got: {balloon_material}")
    assert balloon_material == 'Pebax'

    # Test case 2: COC selected (index 1)
    mock_items = [
        MockListItem('Pebax', False),
        MockListItem('COC', True),
        MockListItem('Nylon', False),
        MockListItem('Polyurethane', False),
        MockListItem('PTFE', False)
    ]

    balloon_material = 'Pebax'  # Default
    for i, item in enumerate(mock_items):
        if item.isSelected:
            balloon_material = material_options[i]
            break

    print(f"Test 2 - Expected: COC, Got: {balloon_material}")
    assert balloon_material == 'COC'

    # Test case 3: PTFE selected (index 4)
    mock_items = [
        MockListItem('Pebax', False),
        MockListItem('COC', False),
        MockListItem('Nylon', False),
        MockListItem('Polyurethane', False),
        MockListItem('PTFE', True)
    ]

    balloon_material = 'Pebax'  # Default
    for i, item in enumerate(mock_items):
        if item.isSelected:
            balloon_material = material_options[i]
            break

    print(f"Test 3 - Expected: PTFE, Got: {balloon_material}")
    assert balloon_material == 'PTFE'

    print("All material selection tests passed!")


if __name__ == "__main__":
    test_material_selection()
