#!/usr/bin/env python3
"""Test script to verify crown_arc integration"""

import math
import sys
import os

# Add the current directory to Python path for crown_arc import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import crown_arc
    print("Successfully imported crown_arc module")
    print(f"crown_arc attributes: {dir(crown_arc)}")

    # Check if the function exists
    if hasattr(crown_arc, 'theta_from_sagitta'):
        print("theta_from_sagitta function found")
    else:
        print("theta_from_sagitta function NOT found")

except ImportError as e:
    print(f"Failed to import crown_arc: {e}")
    sys.exit(1)


def test_crown_arc_calculations():
    """Test crown arc calculations similar to what the form will do"""

    # Test parameters - typical stent values
    diameter_mm = 1.8
    crowns_per_ring = 8

    # Calculate crown spacing
    circumference_mm = math.pi * diameter_mm
    crown_spacing_mm = circumference_mm / crowns_per_ring

    print(f"Stent diameter: {diameter_mm} mm")
    print(f"Crowns per ring: {crowns_per_ring}")
    print(f"Crown spacing: {crown_spacing_mm:.3f} mm")

    # Suggested crown arc parameters
    suggested_chord_mm = crown_spacing_mm * 0.7
    suggested_sagitta_mm = suggested_chord_mm * 0.12

    print(f"\nSuggested chord: {suggested_chord_mm:.3f} mm")
    print(f"Suggested sagitta: {suggested_sagitta_mm:.3f} mm")

    # Calculate radius from chord and sagitta
    suggested_radius_mm = (
        suggested_chord_mm**2 / (8 * suggested_sagitta_mm)) + (suggested_sagitta_mm / 2)
    suggested_radius_um = suggested_radius_mm * 1000.0

    print(
        f"Calculated radius: {suggested_radius_mm:.3f} mm ({suggested_radius_um:.0f} µm)")

    # Use crown_arc functions
    suggested_theta_deg = crown_arc.theta_from_sagitta(
        suggested_sagitta_mm, suggested_radius_um)
    suggested_arc_length_mm = crown_arc.arc_len_from_theta(
        suggested_theta_deg, suggested_radius_um)
    verified_chord_mm = crown_arc.chord_from_theta(
        suggested_theta_deg, suggested_radius_um)

    print(f"\nCrown arc calculations:")
    print(f"Theta: {suggested_theta_deg:.1f}°")
    print(f"Arc length: {suggested_arc_length_mm:.3f} mm")
    print(f"Verified chord: {verified_chord_mm:.3f} mm")
    print(
        f"Chord difference: {abs(verified_chord_mm - suggested_chord_mm):.6f} mm")


if __name__ == "__main__":
    test_crown_arc_calculations()
