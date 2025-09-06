# Excel Processor Command

This new command allows you to load and process detailed stent frame data from Excel or CSV files.

## Features

- **File Browser**: Click "Browse for File" to select Excel (.xlsx) or CSV files
- **Data Preview**: Shows a preview of the loaded data including row counts and sample data
- **Automatic Calculations**: Calculates stent diameter from wave width data
- **Construction Lines**: Optional drawing of ring boundaries and column divisions
- **Chord Lines**: Draws chord lines based on sagitta data from the Excel file
- **Sketch Points**: Optional creation of sketch points at key intersections

## Data Format

The Excel file should contain a sheet named "WaveInputsByColumn" with the following columns:

- `ring`: Ring number (integer)
- `col`: Column number (integer) 
- `wave_height_mm`: Wave height in millimeters
- `wave_width_mm`: Wave width in millimeters
- `strut_width_mm`: Strut width in millimeters
- `gap_above_mm`: Gap above in millimeters
- `gap_below_mm`: Gap below in millimeters
- `upper_chord_center_mm`: Upper chord center in millimeters
- `upper_sagitta_center_mm`: Upper sagitta center in millimeters
- `upper_outer_sagitta_mm`: Upper outer sagitta in millimeters
- `lower_chord_center_mm`: Lower chord center in millimeters
- `lower_sagitta_center_mm`: Lower sagitta center in millimeters
- `lower_outer_sagitta_mm`: Lower outer sagitta in millimeters
- `theta_deg`: Theta in degrees
- `Rc_mm`: Radius in millimeters

## Usage

1. Open Fusion 360 and create a new design
2. Load the Stent Frame add-in
3. Click the "Process Excel Stent Data" button in the ribbon
4. Use "Browse for File" to select your Excel or CSV file
5. Review the data preview to ensure it loaded correctly
6. Adjust processing options (construction lines, chord lines, sketch points)
7. Click OK to generate the stent frame sketch

## File Format Support

- **Excel Files (.xlsx)**: Requires openpyxl library (may need installation)
- **CSV Files (.csv)**: Supported natively, use as alternative to Excel

## Sample Data

A sample CSV file `sample_stent_data.csv` is included in the project root with example data structure.

## Generated Sketch

The command creates a new sketch with:

- Border rectangle showing overall stent dimensions
- Ring boundary lines (horizontal) marking the start/end of each ring
- Column boundary lines (vertical) dividing the circumference into wave sections
- Chord lines positioned at sagitta distances for each crown
- Optional sketch points at line intersections

The sketch name includes metadata about the number of rings and columns processed.

## Error Handling

The command includes robust error handling for:

- Missing or incorrect file paths
- Invalid Excel sheet names
- Data parsing errors
- Missing required columns
- File format issues

All errors are displayed in user-friendly message boxes with helpful guidance.
