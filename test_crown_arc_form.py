#!/usr/bin/env python3
"""Test crown arc calculation functions"""

import math

# Copy the fallback crown arc functions from our main file


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


def simulate_crown_arc_suggestions():
    """Simulate the crown arc suggestions function"""

    # Test with default stent parameters
    diameter_mm = 1.8
    crowns_per_ring = 8

    print(f"Testing crown arc suggestions for:")
    print(f"  Diameter: {diameter_mm} mm")
    print(f"  Crowns per ring: {crowns_per_ring}")

    # Calculate crown spacing parameters
    circumference_mm = math.pi * diameter_mm
    crown_spacing_mm = circumference_mm / crowns_per_ring

    print(f"  Crown spacing: {crown_spacing_mm:.3f} mm")

    # Calculate suggested crown arc parameters
    suggested_chord_mm = crown_spacing_mm * 0.7
    suggested_sagitta_mm = suggested_chord_mm * 0.12

    print(f"\nSuggested parameters:")
    print(f"  Chord: {suggested_chord_mm:.3f} mm")
    print(f"  Sagitta: {suggested_sagitta_mm:.3f} mm")

    # Calculate radius from chord and sagitta
    suggested_radius_mm = (
        suggested_chord_mm**2 / (8 * suggested_sagitta_mm)) + (suggested_sagitta_mm / 2)
    suggested_radius_um = suggested_radius_mm * 1000.0

    print(
        f"  Radius: {suggested_radius_mm:.3f} mm ({suggested_radius_um:.0f} µm)")

    # Use fallback functions (as would happen in our form)
    suggested_theta_deg = crown_arc_theta_from_sagitta(
        suggested_sagitta_mm, suggested_radius_um)
    suggested_arc_length_mm = crown_arc_arc_len_from_theta(
        suggested_theta_deg, suggested_radius_um)
    verified_chord_mm = crown_arc_chord_from_theta(
        suggested_theta_deg, suggested_radius_um)

    print(f"\nCalculated crown arc results:")
    print(f"  Theta: {suggested_theta_deg:.1f}°")
    print(f"  Arc length: {suggested_arc_length_mm:.3f} mm")
    print(f"  Verified chord: {verified_chord_mm:.3f} mm")
    print(
        f"  Chord error: {abs(verified_chord_mm - suggested_chord_mm):.6f} mm")

    # Simulate form output strings (as would appear in the form)
    print(f"\nForm display values:")
    print(f"  Suggested Theta: {suggested_theta_deg:.1f}°")
    print(f"  Suggested Sagitta: {suggested_sagitta_mm:.3f} mm")
    print(f"  Suggested Chord: {verified_chord_mm:.3f} mm")
    print(f"  Suggested Arc Length: {suggested_arc_length_mm:.3f} mm")
    print(f"  Suggested Radius: {suggested_radius_mm:.3f} mm")


if __name__ == "__main__":
    simulate_crown_arc_suggestions()

    # Test with different stent sizes
    print("\n" + "="*60)
    print("Testing with different stent sizes:\n")

    test_cases = [
        (1.5, 6),   # Small stent, fewer crowns
        (2.0, 10),  # Larger stent, more crowns
        (3.0, 12),  # Large stent, many crowns
    ]

    for diameter, crowns in test_cases:
        print(f"Diameter: {diameter} mm, Crowns: {crowns}")
        circumference = math.pi * diameter
        spacing = circumference / crowns
        chord = spacing * 0.7
        sagitta = chord * 0.12
        radius_mm = (chord**2 / (8 * sagitta)) + (sagitta / 2)
        theta = crown_arc_theta_from_sagitta(sagitta, radius_mm * 1000)
        print(
            f"  Spacing: {spacing:.3f} mm, Chord: {chord:.3f} mm, Theta: {theta:.1f}°")
        print()
