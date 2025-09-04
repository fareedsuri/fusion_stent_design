#!/usr/bin/env python3
"""Quick test of the crown arc fallback functions to verify they work properly"""

import math

# Crown arc geometry functions (copied from entry.py)


def crown_arc_theta_from_sagitta(h_mm, Rc_um):
    """Solve included angle θ (deg) from sagitta h (mm) and centerline radius Rc (µm)."""
    Rc = Rc_um / 1000.0
    # guard rounding
    c = max(-1.0, min(1.0, 1.0 - h_mm/(2.0*Rc)))
    return 2.0 * math.degrees(math.acos(c))


def crown_arc_chord_from_theta(theta_deg, Rc_um):
    """Chord length (mm) for θ (deg) and Rc (µm)."""
    Rc = Rc_um / 1000.0
    return 2.0 * Rc * math.sin(math.radians(theta_deg)/2.0)


def crown_arc_arc_len_from_theta(theta_deg, Rc_um):
    """Arc length (mm) for θ (deg) and Rc (µm)."""
    Rc = Rc_um / 1000.0
    return math.radians(theta_deg) * Rc


def test_crown_arc_calculations():
    """Test the crown arc functions with the same logic as in update_crown_arc_suggestions"""

    # Default stent parameters from entry.py
    diameter_mm = 1.8
    crowns_per_ring = 8

    print(
        f"Testing with diameter: {diameter_mm} mm, crowns: {crowns_per_ring}")

    # Calculate crown spacing parameters (same as in the function)
    circumference_mm = math.pi * diameter_mm
    crown_spacing_mm = circumference_mm / crowns_per_ring

    # Suggested crown arc parameters (same logic)
    suggested_chord_mm = crown_spacing_mm * 0.7
    suggested_sagitta_mm = suggested_chord_mm * 0.12

    # Calculate radius from chord and sagitta (same formula)
    suggested_radius_mm = (
        suggested_chord_mm**2 / (8 * suggested_sagitta_mm)) + (suggested_sagitta_mm / 2)
    suggested_radius_um = suggested_radius_mm * 1000.0

    # Use fallback functions (exactly as in the updated code)
    suggested_theta_deg = crown_arc_theta_from_sagitta(
        suggested_sagitta_mm, suggested_radius_um)
    suggested_arc_length_mm = crown_arc_arc_len_from_theta(
        suggested_theta_deg, suggested_radius_um)
    verified_chord_mm = crown_arc_chord_from_theta(
        suggested_theta_deg, suggested_radius_um)

    # Print results in the same format as would appear in the form
    print(f"Crown spacing: {crown_spacing_mm:.3f} mm")
    print(f"Suggested Theta: {suggested_theta_deg:.1f}°")
    print(f"Suggested Sagitta: {suggested_sagitta_mm:.3f} mm")
    print(f"Suggested Chord: {verified_chord_mm:.3f} mm")
    print(f"Suggested Arc Length: {suggested_arc_length_mm:.3f} mm")
    print(f"Suggested Radius: {suggested_radius_mm:.3f} mm")

    # Verify consistency
    chord_error = abs(verified_chord_mm - suggested_chord_mm)
    print(f"Chord calculation error: {chord_error:.6f} mm (should be small)")

    return chord_error < 0.001  # Should be very small


if __name__ == "__main__":
    success = test_crown_arc_calculations()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
