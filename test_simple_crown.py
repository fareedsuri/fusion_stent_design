#!/usr/bin/env python3
"""Simple test for crown_arc functions"""

# Test if we can define our own versions of the crown arc functions
import math


def theta_from_sagitta(h_mm, Rc_um):
    """Solve included angle θ (deg) from sagitta h (mm) and centerline radius Rc (µm)."""
    Rc = Rc_um / 1000.0
    # guard rounding
    c = max(-1.0, min(1.0, 1.0 - h_mm/(2.0*Rc)))
    return 2.0 * math.degrees(math.acos(c))


def chord_from_theta(theta_deg, Rc_um):
    """Chord length (mm) for θ (deg) and Rc (µm)."""
    Rc = Rc_um / 1000.0
    return 2.0 * Rc * math.sin(math.radians(theta_deg)/2.0)


def arc_len_from_theta(theta_deg, Rc_um):
    """Arc length (mm) for θ (deg) and Rc (µm)."""
    Rc = Rc_um / 1000.0
    return math.radians(theta_deg) * Rc


def test_calculations():
    # Test parameters
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

    # Use our crown_arc functions
    suggested_theta_deg = theta_from_sagitta(
        suggested_sagitta_mm, suggested_radius_um)
    suggested_arc_length_mm = arc_len_from_theta(
        suggested_theta_deg, suggested_radius_um)
    verified_chord_mm = chord_from_theta(
        suggested_theta_deg, suggested_radius_um)

    print(f"\nCrown arc calculations:")
    print(f"Theta: {suggested_theta_deg:.1f}°")
    print(f"Arc length: {suggested_arc_length_mm:.3f} mm")
    print(f"Verified chord: {verified_chord_mm:.3f} mm")
    print(
        f"Chord difference: {abs(verified_chord_mm - suggested_chord_mm):.6f} mm")


if __name__ == "__main__":
    test_calculations()
