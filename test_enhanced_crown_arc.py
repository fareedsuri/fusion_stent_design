#!/usr/bin/env python3
"""Test enhanced crown arc calculations with curvature and rule-of-thumb checks"""

import math

# Crown arc geometry functions (copied from entry.py)


def crown_arc_theta_from_sagitta(h_mm, Rc_um):
    """Solve included angle θ (deg) from sagitta h (mm) and centerline radius Rc (µm)."""
    Rc = Rc_um / 1000.0
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


def crown_arc_curvature_from_Rc(Rc_um):
    """Curvature κ = 1/R (1/mm) from centerline Rc (µm)."""
    return 1.0 / (Rc_um / 1000.0)


def crown_arc_radius_to_width_ratio(Rc_um, w_um):
    """Rule‑of‑thumb check: Rc / strut width (dimensionless)."""
    return Rc_um / w_um


def crown_arc_geometric_index_w_over_Rc(w_um, Rc_um):
    """(w/2)/Rc (dimensionless). Lower is gentler curvature."""
    return (0.5 * w_um) / Rc_um


def test_enhanced_crown_arc():
    """Test all crown arc calculations including the new curvature and rule-of-thumb parameters"""

    # Test with default stent parameters
    diameter_mm = 1.8
    crowns_per_ring = 8

    print(f"Testing Enhanced Crown Arc Calculations")
    print(f"Diameter: {diameter_mm} mm, Crowns: {crowns_per_ring}")
    print("=" * 50)

    # Calculate crown spacing parameters
    circumference_mm = math.pi * diameter_mm
    crown_spacing_mm = circumference_mm / crowns_per_ring

    # Suggested crown arc parameters
    suggested_chord_mm = crown_spacing_mm * 0.7
    suggested_sagitta_mm = suggested_chord_mm * 0.12

    # Calculate radius from chord and sagitta
    suggested_radius_mm = (
        suggested_chord_mm**2 / (8 * suggested_sagitta_mm)) + (suggested_sagitta_mm / 2)
    suggested_radius_um = suggested_radius_mm * 1000.0

    # Basic crown arc calculations
    suggested_theta_deg = crown_arc_theta_from_sagitta(
        suggested_sagitta_mm, suggested_radius_um)
    suggested_arc_length_mm = crown_arc_arc_len_from_theta(
        suggested_theta_deg, suggested_radius_um)
    verified_chord_mm = crown_arc_chord_from_theta(
        suggested_theta_deg, suggested_radius_um)

    # NEW: Enhanced calculations
    suggested_curvature = crown_arc_curvature_from_Rc(suggested_radius_um)

    # Rule-of-thumb calculations (assume typical strut width of 75 µm)
    typical_strut_width_um = 75.0
    suggested_r_over_w = crown_arc_radius_to_width_ratio(
        suggested_radius_um, typical_strut_width_um)
    suggested_geom_index = crown_arc_geometric_index_w_over_Rc(
        typical_strut_width_um, suggested_radius_um)

    print("Basic Crown Arc Parameters:")
    print(f"  Crown spacing: {crown_spacing_mm:.3f} mm")
    print(f"  Suggested Theta: {suggested_theta_deg:.1f}°")
    print(f"  Suggested Sagitta: {suggested_sagitta_mm:.3f} mm")
    print(f"  Suggested Chord: {verified_chord_mm:.3f} mm")
    print(f"  Suggested Arc Length: {suggested_arc_length_mm:.3f} mm")
    print(f"  Suggested Radius: {suggested_radius_mm:.3f} mm")

    print("\nEnhanced Parameters:")
    print(f"  Curvature: {suggested_curvature:.3f} mm⁻¹")

    print(f"\nRule-of-thumb checks (75µm strut):")
    print(f"  R/w Ratio: {suggested_r_over_w:.1f}")
    print(f"  Geometric Index: {suggested_geom_index:.4f}")

    # Interpretation guidelines
    print(f"\nDesign Guidelines:")
    if suggested_r_over_w > 5:
        print(
            f"  ✓ R/w = {suggested_r_over_w:.1f} > 5: Good radius-to-width ratio")
    else:
        print(
            f"  ⚠ R/w = {suggested_r_over_w:.1f} < 5: Consider increasing radius")

    if suggested_geom_index < 0.1:
        print(
            f"  ✓ Geometric index = {suggested_geom_index:.4f} < 0.1: Gentle curvature")
    else:
        print(
            f"  ⚠ Geometric index = {suggested_geom_index:.4f} > 0.1: Sharp curvature")


if __name__ == "__main__":
    test_enhanced_crown_arc()

    print("\n" + "=" * 60)
    print("Testing with different strut widths:")

    # Test with different strut widths to show sensitivity
    radius_um = 545  # From our calculation above
    for strut_width in [50, 75, 100, 125]:
        r_over_w = crown_arc_radius_to_width_ratio(radius_um, strut_width)
        geom_index = crown_arc_geometric_index_w_over_Rc(
            strut_width, radius_um)
        print(
            f"  {strut_width}µm strut: R/w = {r_over_w:.1f}, Index = {geom_index:.4f}")
