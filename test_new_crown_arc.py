#!/usr/bin/env python3
"""Test the new crown arc calculation approach with radius input and theta_from_H_Rc"""

import math

# New theta calculation function (copied from entry.py)


def theta_from_H_Rc(H_mm, Rc_um):
    """Calculate theta from ring height H and radius Rc (new method)"""
    h = 0.5*H_mm                      # assume symmetric ring → h ≈ H/2
    R = Rc_um/1000.0                  # mm
    c = max(-1.0, min(1.0, 1.0 - h/(2.0*R)))
    return 2.0*math.degrees(math.acos(c))

# Other crown arc functions


def crown_arc_chord_from_theta(theta_deg, Rc_um):
    """Chord length (mm) for θ (deg) and Rc (µm)."""
    Rc = Rc_um / 1000.0
    return 2.0 * Rc * math.sin(math.radians(theta_deg)/2.0)


def crown_arc_arc_len_from_theta(theta_deg, Rc_um):
    """Arc length (mm) for θ (deg) and Rc (µm)."""
    Rc = Rc_um / 1000.0
    return math.radians(theta_deg) * Rc


def crown_arc_curvature_from_Rc(Rc_um):
    """Curvature κ = 1/R (1/mm) from centerline Rc (µm)."""
    return 1.0 / (Rc_um / 1000.0)


def crown_arc_radius_to_width_ratio(Rc_um, w_um):
    """Rule‑of‑thumb check: Rc / strut width (dimensionless)."""
    return Rc_um / w_um


def crown_arc_geometric_index_w_over_Rc(w_um, Rc_um):
    """(w/2)/Rc (dimensionless). Lower is gentler curvature."""
    return (0.5 * w_um) / Rc_um


def test_new_crown_arc_approach():
    """Test the new approach: user sets radius and height, we calculate the rest"""

    print("Testing New Crown Arc Calculation Approach")
    print("=========================================")

    # Test parameters (user inputs)
    radius_mm = 0.6      # User-specified radius
    height_mm = 1.2      # User-specified ring height
    radius_um = radius_mm * 1000.0

    print(f"User Inputs:")
    print(f"  Crown Arc Radius: {radius_mm} mm ({radius_um:.0f} µm)")
    print(f"  Ring Height H: {height_mm} mm")

    # Calculate sagitta (h = H/2 for symmetric rings)
    sagitta_mm = height_mm / 2.0
    print(f"  Calculated Sagitta h: {sagitta_mm} mm (H/2)")

    # Calculate theta using the new method
    theta_deg = theta_from_H_Rc(height_mm, radius_um)
    print(f"\nCalculated Parameters:")
    print(f"  Theta: {theta_deg:.1f}°")

    # Calculate other parameters from theta and radius
    chord_mm = crown_arc_chord_from_theta(theta_deg, radius_um)
    arc_length_mm = crown_arc_arc_len_from_theta(theta_deg, radius_um)
    curvature = crown_arc_curvature_from_Rc(radius_um)

    print(f"  Chord: {chord_mm:.3f} mm")
    print(f"  Arc Length: {arc_length_mm:.3f} mm")
    print(f"  Curvature: {curvature:.3f} mm⁻¹")

    # Rule-of-thumb calculations
    typical_strut_width_um = 75.0
    r_over_w = crown_arc_radius_to_width_ratio(
        radius_um, typical_strut_width_um)
    geom_index = crown_arc_geometric_index_w_over_Rc(
        typical_strut_width_um, radius_um)

    print(f"\nRule-of-thumb Checks (75µm strut):")
    print(f"  R/w Ratio: {r_over_w:.1f}")
    print(f"  Geometric Index: {geom_index:.4f}")

    # Design guidance
    print(f"\nDesign Assessment:")
    if r_over_w > 5:
        print(f"  ✓ R/w = {r_over_w:.1f} > 5: Good radius-to-width ratio")
    else:
        print(f"  ⚠ R/w = {r_over_w:.1f} < 5: Consider increasing radius")

    if geom_index < 0.1:
        print(
            f"  ✓ Geometric index = {geom_index:.4f} < 0.1: Gentle curvature")
    else:
        print(f"  ⚠ Geometric index = {geom_index:.4f} > 0.1: Sharp curvature")


def test_different_scenarios():
    """Test with different radius and height combinations"""

    print("\n" + "="*60)
    print("Testing Different Radius/Height Combinations:")
    print("="*60)

    test_cases = [
        (0.4, 1.0),   # Small radius, small height
        (0.6, 1.2),   # Medium radius, medium height
        (0.8, 1.5),   # Large radius, large height
        (0.5, 2.0),   # Medium radius, large height
        (1.0, 1.0),   # Large radius, small height
    ]

    for radius_mm, height_mm in test_cases:
        radius_um = radius_mm * 1000.0
        sagitta_mm = height_mm / 2.0
        theta_deg = theta_from_H_Rc(height_mm, radius_um)
        chord_mm = crown_arc_chord_from_theta(theta_deg, radius_um)

        print(f"\nR={radius_mm}mm, H={height_mm}mm:")
        print(
            f"  → θ={theta_deg:.1f}°, h={sagitta_mm:.2f}mm, chord={chord_mm:.3f}mm")


if __name__ == "__main__":
    test_new_crown_arc_approach()
    test_different_scenarios()
