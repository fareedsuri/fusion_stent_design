# Fusion 360 Stent Frame Designer

A comprehensive Fusion 360 add-in for designing parametric stent frames with clinical-grade precision and advanced CAD features.

## 🎯 Overview

This add-in creates parametric 2D stent frame sketches in Fusion 360 based on clinical specifications and industry best practices. It's optimized for intracranial balloon-expandable stents but supports a wide range of configurations.

### Form Dialog Parameters
- **Stent Dimensions**: Diameter and length settings
- **Ring Configuration**: Number of rings and crowns per ring
- **Ring Height Proportions**: Base height and scaling factors
- **Gap Configuration**: Fixed gaps between rings
- **Drawing Options**: Toggle different construction line types

### Generated Construction Lines
- Border lines (top, bottom, left, right)
- Gap center lines (horizontal)
- Crown peak lines (horizontal)  
- Crown wave lines (vertical)
- **Length (mm)**: The overall length of the stent (default: 8.000 mm)

### Ring Configuration
- **Number of Rings**: Total number of rings in the stent (1-20, default: 6)
- **Crowns per Ring**: Number of crowns per ring (4-32, default: 8)

### Ring Height Proportions
- **Base Ring Height (mm)**: Base height for ring calculations (default: 0.140 mm)
- **Height Factors**: Comma-separated multipliers for each ring height (default: "1.20, 1.00, 1.00, 1.00, 1.00, 1.10")

### Gap Configuration
- **Gap Between Rings (mm)**: Spacing between rings (default: 0.200 mm)

### Drawing Options
- **Draw Border**: Show the outer boundary of the stent
- **Draw Gap Center Lines**: Show centerlines of gaps between rings
- **Draw Crown Peak Lines**: Show centerlines of each ring (crown peaks)
- **Draw Crown Wave Lines**: Show vertical divisions for crown waves

## Design Features

The stent frame designer creates:

1. **Border Lines**: Rectangular boundary showing the flattened stent dimensions
2. **Gap Center Lines**: Horizontal construction lines at the center of gaps between rings
3. **Crown Peak Lines**: Horizontal construction lines at the center of each ring
4. **Crown Wave Lines**: Vertical construction lines dividing the circumference into crown sections

### Important Design Rules

- **No gaps before first wave and after last wave**: Crown wave lines are drawn between crowns, not at the edges
- **Automatic length calculation**: If the calculated ring layout exceeds the specified length, the actual length is used
- **Circumference-based width**: Width is calculated as diameter × π to represent the flattened stent

## Usage

1. Load the add-in in Fusion 360
2. Run the "Stent Frame Designer" command
3. Configure parameters in the dialog form
4. Click OK to generate the stent frame sketch

## Calculations

### Width Calculation
```
Width = Diameter × π
```

### Ring Positioning
```
Ring Center[0] = Ring Height[0] / 2
Ring Center[i+1] = Ring Center[i] + Ring Height[i]/2 + Gap + Ring Height[i+1]/2
```

### Crown Wave Positioning
```
Crown Spacing = Width / Crowns per Ring
Crown Wave[i] = i × Crown Spacing (for i = 1 to Crowns per Ring - 1)
```

## Output

The add-in creates a sketch with:
- Construction lines for all guide elements
- Solid lines for the border
- A summary message box with all calculated dimensions

## Files Modified

- `stent_frame.py`: Main entry point, now launches the form dialog
- `commands/commandDialog/entry.py`: Complete form implementation with stent frame drawing logic
- `config.py`: Configuration settings (unchanged)

## Default Values

The form is pre-populated with sensible defaults based on typical stent designs:
- Diameter: 5.652 mm
- Length: 8.000 mm  
- Rings: 6
- Crowns per ring: 8
- Base height: 0.140 mm
- Height factors: [1.20, 1.00, 1.00, 1.00, 1.00, 1.10]
- Gap: 0.200 mm
