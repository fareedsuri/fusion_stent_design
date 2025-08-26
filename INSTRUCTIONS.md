# Stent Frame Designer - Input Instructions

## Overview
The Stent Frame Designer is a Fusion 360 add-in that creates parametric stent frame sketches based on your specifications. This guide explains all input parameters and their effects.

## Quick Start
1. Open Fusion 360
2. Run the "Stent Frame Designer" command
3. Configure your parameters (see sections below)
4. Click OK to generate your stent frame

---

## 📐 **Dimension Inputs**

### Diameter (cm)
- **Range:** 0.01 - 5.0 cm
- **Default:** 0.18 cm (1.8mm) - *Optimized for intracranial applications*
- **Description:** The diameter of the stent when deployed
- **Effect:** Determines the circumference (width) of the unrolled stent frame
- **Formula:** Width = Diameter × π
- **Recommendation:** 0.18cm provides 5.652mm circumference per clinical guidelines

### Length (cm)
- **Range:** 0.1 - 20.0 cm
- **Default:** 0.8 cm (8mm) - *Clinical standard for intracranial stents*
- **Description:** The total length of the stent frame
- **Effect:** Total vertical dimension of the sketch

---

## 🔢 **Ring Configuration**

### Number of Rings
- **Range:** 1 - 20 rings
- **Default:** 6 rings - *Optimal for intracranial applications per clinical data*
- **Description:** How many horizontal ring sections the stent has
- **Effect:** Divides the stent into segments, each with crowns

### Crowns per Ring
- **Range:** 3 - 20 crowns
- **Default:** 8 crowns - *45° spacing provides optimal mechanical properties*
- **Description:** Number of crown (wave) sections in each ring
- **Effect:** Determines the circumferential pattern detail

---

## 📏 **Height Proportions**

### Height Factors
- **Format:** Comma-separated numbers (e.g., "1.20, 1.00, 1.00, 1.00, 1.00, 1.10")
- **Default:** "1.20, 1.00, 1.00, 1.00, 1.00, 1.10" - *Clinically optimized pattern*
- **Description:** Relative height of each ring
- **Clinical Rationale:** End rings (1.20, 1.10) provide higher retention and easier opening without forcing end-first expansion
- **Rules:**
  - Must provide one factor per ring
  - Values > 1.0 make rings taller
  - Values < 1.0 make rings shorter
  - System auto-scales to fit total length

**Example:**
- 6 rings with factors "1.5, 1.0, 1.0, 1.0, 1.0, 1.5"
- First and last rings are 50% taller than middle rings

---

## 📊 **Gap Configuration**

### Gap Between Rings
- **Format:** Comma-separated values in mm (e.g., "0.19, 0.2, 0.2, 0.2, 0.195")
- **Default:** "0.19, 0.2, 0.2, 0.2, 0.195" - *Optimized with slight end reductions for better retention*
- **Description:** Space between adjacent rings
- **Clinical Rationale:** Slightly reduced end gaps (0.19, 0.195) improve balloon retention while maintaining low opening pressure
- **Rules:**
  - For N rings, you need N-1 gap values
  - If fewer values provided, last value is repeated
  - If more values provided, extras are ignored

**Examples:**
- **Uniform gaps:** "0.2" → All gaps are 0.2mm
- **Variable gaps:** "0.1, 0.3, 0.2, 0.1, 0.2" → Different gap sizes

---

## 🎨 **Drawing Options**

### Border Lines
- **Default:** Enabled
- **Description:** Draws the outer rectangle boundary
- **Lines Created:** Top, bottom, left, right borders

### Gap Center Lines
- **Default:** Enabled
- **Description:** Horizontal lines at the center of each gap
- **Use Case:** Reference for gap positioning

### Crown Peak Lines
- **Default:** Enabled
- **Description:** Horizontal lines at top and bottom of each ring
- **Lines Created:** Ring start and ring end boundaries
- **Use Case:** Crown height references

### Crown Wave Lines
- **Default:** Enabled
- **Description:** Vertical lines separating each crown
- **Lines Created:** N-1 lines for N crowns (excludes borders)
- **Use Case:** Crown wave definitions

---

## 🔍 **Detail Options**

### Crown Wave Midlines
- **Default:** Disabled
- **Description:** Vertical lines at the center of each crown section
- **Use Case:** Additional detail for crown geometry

### Horizontal Crown Midlines
- **Default:** Disabled
- **Description:** Horizontal lines at the center of each ring
- **Use Case:** Ring center references

---

## ⚙️ **Partial Control Options**

### Crown Midlines Count (from left)
- **Range:** 0 - 20
- **Default:** 0 (disabled)
- **Description:** Add midlines to only the first N crowns
- **Use Case:** Gradual detail increase, asymmetric designs
- **Rule:** When > 0, overrides the full midlines option

### Crown Quarter Lines
- **Default:** Disabled
- **Description:** Vertical lines at 1/4 and 3/4 positions in each crown
- **Lines Created:** 2 lines per crown

### Crown Quarter Lines Count (from left)
- **Range:** 0 - 20
- **Default:** 0 (disabled)
- **Description:** Add quarter lines to only the first N crowns
- **Rule:** When > 0, overrides the full quarter lines option

---

## 🎯 **Advanced Options**

### Create Coincident Points at Line Crossings
- **Default:** Disabled
- **Description:** Creates sketch points at every line intersection
- **Features:**
  - Automatic coincident constraints to crossing lines
  - Parametric intersection points
  - Perfect for adding dimensions or additional geometry
- **Performance:** May slow down generation with many intersections

---

## 💾 **Session Management**

### Automatic Value Storage
- **Feature:** All inputs are automatically saved during your Fusion session
- **Behavior:** When you reopen the dialog, your last values are restored
- **Scope:** Values persist until Fusion 360 is closed

### Reset to Default Values
- **Button:** "Reset to Default Values"
- **Action:** Instantly restores all inputs to original defaults
- **Use Case:** Quick reset when experimenting

---

## 📊 **Output Information**

After generation, you'll see a summary showing:
- Physical dimensions (diameter, length, width)
- Ring and crown counts
- Actual gap values used
- Line counts for each element type
- Points and constraints created (if enabled)

---

## 💡 **Tips & Best Practices**

### For Simple Designs:
- Use uniform height factors (all 1.0)
- Use single gap value (e.g., "0.2")
- Enable basic options: border, gaps, peaks, waves

### For Complex Designs:
- Vary height factors for tapered stents
- Use variable gaps for optimized spacing
- Add midlines and quarter lines for detailed geometry
- Enable coincident points for further CAD work

### For Performance:
- Disable coincident points for large designs (>10 rings, >15 crowns)
- Use partial controls instead of full detail options
- Start simple and add detail incrementally

### For CAD Integration:
- Enable coincident points for parametric models
- Use consistent gap values for manufacturability
- Consider symmetrical height factors for balanced designs

---

## 🔧 **Troubleshooting**

### Common Issues:
- **Values reset:** Check if you clicked the reset button
- **Unexpected proportions:** Verify height factors match ring count
- **Missing details:** Check if partial counts override full options
- **Performance slow:** Reduce rings/crowns or disable coincident points

### Value Validation:
- Height factors: Must be positive numbers
- Gap values: Must be positive, in millimeters
- Counts: Must be within specified ranges

---

## 📐 **Example Configurations**

### Clinical Intracranial Stent (Recommended):
```
Diameter: 0.18 cm (1.8mm)
Length: 0.8 cm (8mm)  
Rings: 6
Crowns per Ring: 8
Height Factors: 1.20, 1.00, 1.00, 1.00, 1.00, 1.10
Gaps: 0.19, 0.2, 0.2, 0.2, 0.195
Drawing Options: Border, Gap Centerlines, Crown Peaks, Crown Waves
```

### Basic Cardiac Stent:
```
Diameter: 0.30 cm
Length: 1.2 cm
Rings: 4
Crowns per Ring: 6
Height Factors: 1.0, 1.0, 1.0, 1.0
Gaps: 0.3
```

### Detailed Research Stent:
```
Diameter: 0.18 cm
Length: 0.8 cm
Rings: 6
Crowns per Ring: 8
Height Factors: 1.2, 1.0, 1.0, 1.0, 1.0, 1.2
Gaps: 0.15, 0.2, 0.2, 0.2, 0.15
Crown Midlines: Enabled
Coincident Points: Enabled
```

### Asymmetric Design:
```
Diameter: 0.25 cm
Length: 1.0 cm
Rings: 5
Crowns per Ring: 10
Height Factors: 1.5, 1.2, 1.0, 1.2, 1.5
Gaps: 0.1, 0.3, 0.3, 0.1
Partial Midlines: 3 (first 3 crowns only)
```

---

*Generated by Stent Frame Designer v1.0*
