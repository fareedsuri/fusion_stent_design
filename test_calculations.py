#!/usr/bin/env python3
"""
Test script for stent frame designer - validates calculations
"""


def test_stent_calculations():
    """Test the stent frame calculations without Fusion 360"""
    import math

    # Test parameters
    diameter_mm = 1.8
    length_mm = 8.0
    num_rings = 6
    crowns_per_ring = 8
    base_height_mm = 0.140
    height_factors = [1.20, 1.00, 1.00, 1.00, 1.00, 1.10]
    gap_mm = 0.200

    # Calculate width from diameter (circumference)
    width_mm = diameter_mm * math.pi
    print(f"Width (circumference): {width_mm:.3f} mm")

    # Calculate ring heights
    ring_heights = [base_height_mm * factor for factor in height_factors]
    print(f"Original ring heights: {[f'{h:.3f}' for h in ring_heights]} mm")

    # Calculate with fixed gap_mm and total length of 8mm
    num_gaps = num_rings - 1
    total_gap_space = num_gaps * gap_mm
    available_ring_space = length_mm - total_gap_space

    # Scale ring heights to fit the available space
    original_total_ring_height = sum(ring_heights)
    ring_scale_factor = available_ring_space / original_total_ring_height
    scaled_ring_heights = [h * ring_scale_factor for h in ring_heights]

    print(f"Fixed gap size: {gap_mm:.3f} mm")
    print(f"Number of gaps: {num_gaps}")
    print(f"Total gap space: {total_gap_space:.3f} mm")
    print(f"Available ring space: {available_ring_space:.3f} mm")
    print(f"Ring scale factor: {ring_scale_factor:.3f}")
    print(
        f"Scaled ring heights: {[f'{h:.3f}' for h in scaled_ring_heights]} mm")

    # Calculate ring positions using gap_mm
    ring_centers = []
    # Start with half of first ring height
    current_y = scaled_ring_heights[0] / 2
    ring_centers.append(current_y)

    for i in range(1, num_rings):
        # Add half of previous ring + gap_mm + half of current ring
        current_y += scaled_ring_heights[i-1] / \
            2 + gap_mm + scaled_ring_heights[i]/2
        ring_centers.append(current_y)

    print(
        f"Ring centers ({gap_mm}mm gaps, 8mm total): {[f'{c:.3f}' for c in ring_centers]} mm")

    # Verify total length
    actual_length = ring_centers[-1] + scaled_ring_heights[-1]/2
    total_length = length_mm

    print(f"Specified length: {length_mm:.3f} mm")
    print(f"Actual calculated length: {actual_length:.3f} mm")

    # Use scaled ring heights for subsequent calculations
    ring_heights = scaled_ring_heights
    print(f"Final length used: {total_length:.3f} mm")

    # Calculate crown wave positions
    crown_spacing = width_mm / crowns_per_ring

    # All crown positions (including edges)
    all_crown_positions = [
        i * crown_spacing for i in range(crowns_per_ring + 1)]
    print(
        f"All crown positions (edges + waves): {[f'{x:.3f}' for x in all_crown_positions]} mm")

    # Crown wave lines (between crowns, excluding edges)
    crown_waves = [i * crown_spacing for i in range(1, crowns_per_ring)]
    print(
        f"Crown wave lines only (no edges): {[f'{x:.3f}' for x in crown_waves]} mm")

    # Edge positions
    print(f"Left edge: 0.000 mm")
    print(f"Right edge: {width_mm:.3f} mm")

    # Calculate ring boundaries (crown start and end positions)
    ring_start_lines = []  # Top of each ring
    ring_end_lines = []    # Bottom of each ring

    for i, center in enumerate(ring_centers):
        ring_start = center - ring_heights[i]/2
        ring_end = center + ring_heights[i]/2
        ring_start_lines.append(ring_start)
        ring_end_lines.append(ring_end)

    print(
        f"Ring start lines (crown tops): {[f'{s:.3f}' for s in ring_start_lines]} mm")
    print(
        f"Ring end lines (crown bottoms): {[f'{e:.3f}' for e in ring_end_lines]} mm")

    # Calculate gap center positions (between ring end and next ring start)
    gap_centers = []
    for i in range(num_rings - 1):
        gap_center_y = (ring_end_lines[i] + ring_start_lines[i+1]) / 2
        gap_centers.append(gap_center_y)

    print(f"Gap center lines: {[f'{g:.3f}' for g in gap_centers]} mm")

    # Draw ASCII representation of stent frame
    draw_stent_frame_ascii(width_mm, total_length, ring_start_lines,
                           ring_end_lines, gap_centers, crown_waves)

    print("\n=== SUMMARY ===")
    print(
        f"Stent frame: {diameter_mm:.3f}mm dia x {total_length:.3f}mm length")
    print(f"Flattened: {width_mm:.3f}mm wide x {total_length:.3f}mm tall")
    print(f"Rings: {num_rings} rings with {crowns_per_ring} crowns each")
    print(f"Crown waves: {len(crown_waves)} vertical lines (no gaps at edges)")
    print(f"Gap centerlines: {len(gap_centers)} horizontal lines")
    print(f"Crown peaks: {len(ring_centers)} horizontal lines")


def draw_stent_frame_ascii(width_mm, length_mm, ring_start_lines, ring_end_lines, gap_centers, crown_waves):
    """Draw ASCII representation of the stent frame rectangle with guide lines"""
    print("\n=== STENT FRAME LAYOUT ===")

    # Define the drawing area (scale down for ASCII display)
    ascii_width = 60
    ascii_height = 20

    # Scale factors
    width_scale = ascii_width / width_mm
    height_scale = ascii_height / length_mm

    # Create drawing grid
    grid = [[' ' for _ in range(ascii_width + 2)]
            for _ in range(ascii_height + 2)]

    # Draw rectangle border
    for i in range(ascii_width + 2):
        grid[0][i] = '-'  # Top border
        grid[ascii_height + 1][i] = '-'  # Bottom border
    for i in range(ascii_height + 2):
        grid[i][0] = '|'  # Left border
        grid[i][ascii_width + 1] = '|'  # Right border

    # Draw corners
    grid[0][0] = '+'
    grid[0][ascii_width + 1] = '+'
    grid[ascii_height + 1][0] = '+'
    grid[ascii_height + 1][ascii_width + 1] = '+'

    # Draw crown wave lines (vertical)
    for wave_pos in crown_waves:
        x = int(wave_pos * width_scale) + 1
        if 1 <= x <= ascii_width:
            for y in range(1, ascii_height + 1):
                if grid[y][x] == ' ':
                    grid[y][x] = '|'

    # Draw ring start lines (horizontal) - crown tops
    for ring_start in ring_start_lines:
        y = ascii_height - int(ring_start * height_scale)
        if 1 <= y <= ascii_height:
            for x in range(1, ascii_width + 1):
                if grid[y][x] == ' ':
                    grid[y][x] = '-'
                elif grid[y][x] == '|':
                    grid[y][x] = '+'

    # Draw ring end lines (horizontal) - crown bottoms
    for ring_end in ring_end_lines:
        y = ascii_height - int(ring_end * height_scale)
        if 1 <= y <= ascii_height:
            for x in range(1, ascii_width + 1):
                if grid[y][x] == ' ':
                    grid[y][x] = '-'
                elif grid[y][x] == '|':
                    grid[y][x] = '+'

    # Draw gap center lines (horizontal)
    for gap_center in gap_centers:
        y = ascii_height - int(gap_center * height_scale)
        if 1 <= y <= ascii_height:
            for x in range(1, ascii_width + 1):
                if grid[y][x] == ' ':
                    grid[y][x] = ':'
                elif grid[y][x] == '|':
                    grid[y][x] = '+'

    # Print the grid
    for row in grid:
        print(''.join(row))

    print("\nLegend:")
    print("+ - - - + Rectangle border")
    print("|       | Crown wave lines (vertical)")
    print("- - - - - Ring boundary lines (crown start/end)")
    print(": : : : : Gap center lines (horizontal)")
    print("+       + Intersections")

    print(f"\nScale: {width_mm:.1f}mm wide × {length_mm:.1f}mm tall")
    print(f"Crown waves at: {[f'{x:.2f}' for x in crown_waves]} mm")
    print(f"Ring start lines at: {[f'{y:.2f}' for y in ring_start_lines]} mm")
    print(f"Ring end lines at: {[f'{y:.2f}' for y in ring_end_lines]} mm")
    print(f"Gap centers at: {[f'{y:.2f}' for y in gap_centers]} mm")


if __name__ == "__main__":
    test_stent_calculations()
