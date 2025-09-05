from typing import Dict, Optional
import adsk.core
import adsk.fusion
import os
import math
from ...lib import fusionAddInUtils as futil
from ... import config
app = adsk.core.Application.get()
ui = app.userInterface

# TODO *** Specify the command identity information. ***
CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_stentFrameDesigner'
CMD_NAME = 'Stent Frame Designer'
CMD_Description = 'Design stent frames with customizable parameters'

# Specify that the command will be promoted to the panel.
IS_PROMOTED = True

# TODO *** Define the location where the command button will be created. ***
# This is done by specifying the workspace, the tab, and the panel, and the
# command it will be inserted beside. Not providing the command to position it
# will insert it at the end.
WORKSPACE_ID = 'FusionSolidEnvironment'
PANEL_ID = 'SolidScriptsAddinsPanel'
COMMAND_BESIDE_ID = 'ScriptsManagerCommand'

# Resource location for command icons, here we assume a sub folder in this directory named "resources".
ICON_FOLDER = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'resources', '')

# Local list of event handlers used to maintain a reference so
# they are not released and garbage collected.
local_handlers = []

# Global storage for last used values (persists during Fusion session)
last_used_values = {
    'diameter': 1.8,
    'length': 8,
    'num_rings': 6,
    'crowns_per_ring': 8,

    # Rings: ends slightly taller to be “more openable”
    'height_factors': '1.20, 1.00, 1.00, 1.00, 1.00, 1.10',

    # Default chord values (mm) - will be calculated from height factors if not specified
    'chord_values': '',

    # Default sagitta values (mm) - will be calculated from crown arc radius if not specified
    'sagitta_values': '',

    # Gaps (mm, apex‑to‑apex): fold‑lock at ends (16 µm wall), body kept larger
    # Order: 1↔2, 2↔3, 3↔4, 4↔5, 5↔6
    'gap_between_rings': '0.095, 0.160, 0.160, 0.160, 0.100',

    # Drawing options
    'draw_border': True,
    'draw_gap_centerlines': True,
    'draw_crown_peaks': True,
    'draw_crown_waves': True,
    'draw_crown_midlines': False,
    'draw_crown_h_midlines': False,
    'draw_crown_chord_lines': True,
    'partial_crown_midlines': 0,
    'draw_crown_mids': False,
    'partial_crown_mids': 0,
    'create_coincident_points': False,

    # Fold‑lock (ends only)
    # let UI/table override first/last gaps from wall thickness
    'use_fold_lock_table': True,
    'balloon_wall_um': 16,            # Pebax wall used to compute end windows
    'balloon_material': 'Pebax',  # note only; current code doesn’t use it

    # Visual guides: draw short horizontals only in end “boxes” used by links
    'draw_fold_lock_limits': True,
    'fold_lock_columns': '0,2,4,6',

    # Interior‑only gap centerlines (hide g at start/end)
    'gap_centerlines_interior_only': True,

    # (Optional note for your workflow; current code ignores this field)
    'per_ring_fold_lock_config': '1-2:0,2,4,6:0.095;5-6:0,2,4,6:0.100',

    # only draw interior gap lines (2–3, 3–4, 4–5)
    'gap_centerlines_interior_only': False
}


# Default values for reset functionality
default_values = {
    'diameter': 1.8,
    'length': 8,
    'num_rings': 6,
    'crowns_per_ring': 8,

    'height_factors': '1.20, 1.00, 1.00, 1.00, 1.00, 1.10',  # Recommended pattern
    'chord_values': '',
    'sagitta_values': '',
    # g₀=0.14mm with end reductions
    'gap_between_rings': '0.095, 0.160, 0.160, 0.160, 0.100',
    'draw_border': True,
    'draw_gap_centerlines': True,  # Recommended for CAD workflow
    'draw_crown_peaks': True,
    'draw_crown_waves': True,      # Essential for crown definitions
    'draw_crown_midlines': False,
    'draw_crown_h_midlines': False,
    'draw_crown_chord_lines': True,
    'partial_crown_midlines': 0,
    'draw_crown_mids': False,
    'partial_crown_mids': 0,
    'create_coincident_points': False,
    # Fold-lock options
    'use_fold_lock_table': False,
    'balloon_wall_um': 16,              # balloon wall thickness in µm
    'balloon_material': 'Pebax',        # balloon material type
    # draw short horizontal segments in specified crown boxes
    'draw_fold_lock_limits': True,
    'fold_lock_columns': '0,2,4,6',     # crown boxes used by end links
    # per-ring configuration
    'per_ring_fold_lock_config': '1-2:0,2,4,6:0.095;5-6:0,2,4,6:0.100',
    # only draw interior gap lines (2–3, 3–4, 4–5)
    'gap_centerlines_interior_only': False
}


def calculate_fold_lock_gap(material, wall_thickness_um):
    """
    Calculate fold-lock gap based on balloon material and wall thickness.

    Args:
        material (str): Balloon material (e.g., 'Pebax', 'COC', 'Nylon', etc.)
        wall_thickness_um (int): Wall thickness in micrometers

    Returns:
        float: Fold-lock gap in millimeters
    """
    # Normalize material name for case-insensitive matching
    material = material.lower().strip()

    # Material-specific fold-lock gap calculations
    if 'pebax' in material:
        # Pebax: Flexible, good fold characteristics
        if wall_thickness_um <= 12:
            return 0.095  # mm
        elif wall_thickness_um <= 16:
            return 0.095  # mm
        elif wall_thickness_um <= 20:
            return 0.100  # mm
        else:
            return 0.110  # mm

    elif 'coc' in material or 'cyclic olefin' in material:
        # COC: Stiffer than Pebax, needs slightly more space
        if wall_thickness_um <= 12:
            return 0.105  # mm - slightly larger than Pebax
        elif wall_thickness_um <= 16:
            return 0.105  # mm
        elif wall_thickness_um <= 20:
            return 0.115  # mm
        else:
            return 0.125  # mm

    elif 'nylon' in material:
        # Nylon: Can be stiff, needs more space for folding
        if wall_thickness_um <= 12:
            return 0.110  # mm
        elif wall_thickness_um <= 16:
            return 0.115  # mm
        elif wall_thickness_um <= 20:
            return 0.125  # mm
        else:
            return 0.135  # mm

    elif 'polyurethane' in material or 'pu' in material:
        # Polyurethane: Flexible but can be thick
        if wall_thickness_um <= 12:
            return 0.100  # mm
        elif wall_thickness_um <= 16:
            return 0.105  # mm
        elif wall_thickness_um <= 20:
            return 0.115  # mm
        else:
            return 0.125  # mm

    elif 'ptfe' in material or 'teflon' in material:
        # PTFE: Very stiff, needs significant space
        if wall_thickness_um <= 12:
            return 0.120  # mm
        elif wall_thickness_um <= 16:
            return 0.125  # mm
        elif wall_thickness_um <= 20:
            return 0.135  # mm
        else:
            return 0.150  # mm

    else:
        # Unknown/Other materials: Use conservative Pebax values
        if wall_thickness_um <= 12:
            return 0.095  # mm
        elif wall_thickness_um <= 16:
            return 0.095  # mm
        elif wall_thickness_um <= 20:
            return 0.100  # mm
        else:
            return 0.110  # mm


# Crown arc geometry functions (fallback if module import fails)
def crown_arc_theta_from_sagitta(h_mm, Rc_um):
    """Solve included angle θ (deg) from sagitta h (mm) and centerline radius Rc (µm).
    Formula: h = 2R * (1 - cos(θ/2)), so θ = 2 * acos(1 - h/(2R))
    """
    Rc = Rc_um / 1000.0
    # guard rounding: ensure argument is in valid range [-1, 1]
    c = max(-1.0, min(1.0, 1.0 - h_mm/(2.0 * Rc)))  # Added factor of 2
    return 2.0 * math.degrees(math.acos(c))


def sagitta_from_theta(theta_deg, Rc_um):
    """
    Apex sagitta h (mm) from included angle theta (deg)
    and centerline radius Rc (micrometers).
    Formula: s = 2R * (1 - cos(θ/2))
    """
    R = Rc_um / 1000.0                    # µm -> mm
    half = math.radians(theta_deg / 2.0)
    return 2.0 * R * (1.0 - math.cos(half))     # Fixed: removed factor of 2


def crown_apex_from_theta(theta_deg, Rc_um):
    """
    Returns sagitta, chord, and arc length (all mm)
    from included angle theta (deg) and centerline Rc (µm).
    Returns: (h_mm, chord_mm, arc_mm)

    Formulas:
    - Arc length: L = R * θ_rad
    - Chord length: c = 2 * R * sin(θ/2)
    - Sagitta: s = 2R * (1 - cos(θ/2))
    - Curvature: κ = 1/R
    """
    try:
        R = Rc_um / 1000.0
        half = math.radians(theta_deg / 2.0)
        theta_rad = math.radians(theta_deg)
        h = 2.0 * R * (1.0 - math.cos(half))  # Sagitta (GPT convention)
        c = 2.0 * R * math.sin(half)    # Chord length
        s = R * theta_rad               # Arc length
        return h, c, s
    except Exception as e:
        futil.log(f'Error in crown_apex_from_theta: {str(e)}')
        return 0, 0, 0


def calculate_design_examples():
    """Calculate design examples for common crown arc configurations"""
    examples = []

    # Body example: theta=72°, Rc=200 µm
    h_body, chord_body, arc_body = crown_apex_from_theta(72.0, 200.0)
    examples.append({
        'name': 'Body Crown (θ=72°, Rc=200µm)',
        'theta': 72.0,
        'radius_um': 200.0,
        'sagitta_mm': h_body,
        'chord_mm': chord_body,
        'arc_mm': arc_body
    })

    # End example: theta=90°, Rc=130 µm
    h_end, chord_end, arc_end = crown_apex_from_theta(90.0, 130.0)
    examples.append({
        'name': 'End Crown (θ=90°, Rc=130µm)',
        'theta': 90.0,
        'radius_um': 130.0,
        'sagitta_mm': h_end,
        'chord_mm': chord_end,
        'arc_mm': arc_end
    })

    return examples


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


# ---------- Quarter-wave helper (from crown_arc_calc) ----------

def _solve_delta_for_R(H, W, w, R):
    """Internal: solve tangency equation for delta given H,W,w,R (radians)."""
    import math
    p = 0.5*w
    A = H - p

    def F(d):
        s = math.sin(d)
        c = math.cos(d)
        denom = W - 2.0*R*s
        if abs(denom) < 1e-14:
            denom = 1e-14 if denom >= 0 else -1e-14
        return math.tan(d) - (2.0*(A - R*(1.0 - c))) / denom
    lo, hi = math.radians(5.0), math.radians(89.9)
    step = math.radians(0.05)
    best_d, best_val = lo, abs(F(lo))
    prev_d, prev_f = lo, F(lo)
    bracket = None
    d = lo + step
    while d <= hi + 1e-12:
        fd = F(d)
        if abs(fd) < best_val:
            best_val, best_d = abs(fd), d
        if prev_f * fd < 0.0:
            bracket = (prev_d, d)
            break
        prev_d, prev_f = d, fd
        d += step
    if bracket is None:
        span = math.radians(5.0)
        lo = max(math.radians(1e-6), best_d - 0.5*span)
        hi = min(math.radians(89.9),   best_d + 0.5*span)
    else:
        lo, hi = bracket
    # bisection
    flo, fhi = F(lo), F(hi)
    for _ in range(120):
        mid = 0.5*(lo+hi)
        fm = F(mid)
        if abs(fm) < 1e-14 or (hi - lo) < 1e-12:
            return mid
        if flo * fm < 0.0:
            hi, fhi = mid, fm
        else:
            lo, flo = mid, fm
    return 0.5*(lo+hi)


def _solve_delta_for_quarter(H: float, W: float, w: float, R: float) -> float:
    """
    Solve for the contact angle δ (radians) for the quarter-rectangle construction:

        tan δ = 2 * (H - w/2 - R*(1 - cos δ)) / (W - 2*R*sin δ)

    Robust bisection on δ ∈ (5°, 89.9°), with coarse bracketing.
    """
    p = 0.5 * w
    A = H - p

    def F(d: float) -> float:
        s = math.sin(d)
        c = math.cos(d)
        denom = W - 2.0 * R * s
        if abs(denom) < 1e-14:
            denom = 1e-14 if denom >= 0 else -1e-14
        return math.tan(d) - (2.0 * (A - R * (1.0 - c))) / denom

    lo, hi = math.radians(5.0), math.radians(89.9)
    step = math.radians(0.05)

    # coarse scan to find a sign change or best point
    best_d = lo
    best_val = abs(F(lo))
    prev_d = lo
    prev_f = F(prev_d)
    bracket = None

    d = lo + step
    while d <= hi + 1e-12:
        fd = F(d)
        if abs(fd) < best_val:
            best_val, best_d = abs(fd), d
        if prev_f * fd < 0.0:
            bracket = (prev_d, d)
            break
        prev_d, prev_f = d, fd
        d += step

    if bracket is None:
        span = math.radians(5.0)
        lo = max(math.radians(1e-6), best_d - 0.5 * span)
        hi = min(math.radians(89.9), best_d + 0.5 * span)
    else:
        lo, hi = bracket

    # bisection
    flo, fhi = F(lo), F(hi)
    for _ in range(120):
        mid = 0.5 * (lo + hi)
        fm = F(mid)
        if abs(fm) < 1e-14 or (hi - lo) < 1e-12:
            return mid
        if flo * fm < 0.0:
            hi, fhi = mid, fm
        else:
            lo, flo = mid, fm

    return 0.5 * (lo + hi)


def quarter_wave_from_rect(
    rect_height_mm: float,
    rect_width_mm: float,
    strut_width_mm: float,
    R_factor: float = 2.5,
    R_override_mm: Optional[float] = None,
) -> Dict[str, float]:
    """
    Solve the crown geometry in a *quarter* rectangle (H_box, W_box).
    Circle center is at (W/2, w/2 + R), arc tangent to both straight arms.

    Returns (all mm/deg; centerline unless noted):
      {
        "delta_deg", "theta_deg",
        "X_mm", "Y_mm",           # arm offsets from the two quarter-rectangle corners to the contact
        "y_chord_mm",             # chord height above bottom
        "chord_mm", "sagitta_mm", # centerline chord & sagitta
        "Rc_mm",                  # centerline radius used
        "outer_sagitta_mm"        # outer-track sagitta (fold-lock check)
      }
    """
    H = float(rect_height_mm)
    W = float(rect_width_mm)
    w = float(strut_width_mm)
    R = float(R_override_mm) if R_override_mm is not None else float(
        R_factor) * w
    if R <= 0.0:
        raise ValueError("Centerline radius must be positive.")

    # Solve for delta
    delta = _solve_delta_for_quarter(H, W, w, R)

    s, c = math.sin(delta), math.cos(delta)
    # contact point horizontal offset from each corner
    X = 0.5 * (W - 2.0 * R * s)
    # chord height above bottom
    y_ch = (0.5 * w) + R * (1.0 - c)
    # centerline sagitta & chord
    h = R * (1.0 - c)
    chord = 2.0 * R * s
    # vertical arm
    Y = H - y_ch

    if h <= 0 or chord <= 0 or X < 0 or Y < 0:
        raise ValueError("Infeasible geometry for given (H_box, W_box, w, R).")

    return {
        "delta_deg": math.degrees(delta),
        "theta_deg": 2.0 * math.degrees(delta),
        "X_mm": X,
        "Y_mm": Y,
        "y_chord_mm": y_ch,
        "chord_mm": chord,
        "sagitta_mm": h,
        "Rc_mm": R,
        "outer_sagitta_mm": (R + 0.5 * w) * (1.0 - c),
    }


def crown_from_full_wave(
    H_full_mm: float,
    W_full_mm: float,
    strut_width_mm: float,
    R_factor: float = 2.5,
    R_override_mm: Optional[float] = None,
) -> Dict[str, float]:
    """
    Convenience wrapper: accepts *full-wave* height & width.
    Internally halves to a quarter-rectangle and calls quarter_wave_from_rect().
    """
    Hq = 0.5 * float(H_full_mm)  # quarter height
    Wq = 0.5 * float(W_full_mm)  # quarter width
    out = quarter_wave_from_rect(
        rect_height_mm=Hq,
        rect_width_mm=Wq,
        strut_width_mm=strut_width_mm,
        R_factor=R_factor,
        R_override_mm=R_override_mm,
    )
    # Add echoes of full-wave inputs for traceability
    out.update({"H_full_mm": float(H_full_mm), "W_full_mm": float(W_full_mm)})
    return out


def crown_arc_radius_to_width_ratio(Rc_um, w_um):
    """Rule‑of‑thumb check: Rc / strut width (dimensionless)."""
    return Rc_um / w_um


def crown_arc_geometric_index_w_over_Rc(w_um, Rc_um):
    """(w/2)/Rc (dimensionless). Lower is gentler curvature."""
    return (0.5 * w_um) / Rc_um


# Executed when add-in is run.
def start():
    # Create a command Definition.
    cmd_def = ui.commandDefinitions.addButtonDefinition(
        CMD_ID, CMD_NAME, CMD_Description, ICON_FOLDER)

    # Define an event handler for the command created event. It will be called when the button is clicked.
    futil.add_handler(cmd_def.commandCreated, command_created)

    # ******** Add a button into the UI so the user can run the command. ********
    # Get the target workspace the button will be created in.
    workspace = ui.workspaces.itemById(WORKSPACE_ID)

    # Get the panel the button will be created in.
    panel = workspace.toolbarPanels.itemById(PANEL_ID)

    # Create the button command control in the UI after the specified existing command.
    control = panel.controls.addCommand(cmd_def, COMMAND_BESIDE_ID, False)

    # Specify if the command is promoted to the main toolbar.
    control.isPromoted = IS_PROMOTED


# Executed when add-in is stopped.
def stop():
    # Get the various UI elements for this command
    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    panel = workspace.toolbarPanels.itemById(PANEL_ID)
    command_control = panel.controls.itemById(CMD_ID)
    command_definition = ui.commandDefinitions.itemById(CMD_ID)

    # Delete the button command control
    if command_control:
        command_control.deleteMe()

    # Delete the command definition
    if command_definition:
        command_definition.deleteMe()


# Function that is called when a user clicks the corresponding button in the UI.
# This defines the contents of the command dialog and connects to the command related events.
def command_created(args: adsk.core.CommandCreatedEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Created Event')

    # https://help.autodesk.com/view/fusion360/ENU/?contextId=CommandInputs
    inputs = args.command.commandInputs

    # TODO Define the dialog for your command by adding different inputs to the command.

    # Add a description text for better user experience
    description_input = inputs.addTextBoxCommandInput('description', '',
                                                      'Design customizable stent frames with precise control over dimensions, rings, and crown patterns.',
                                                      3, True)
    # ⬅️ WIDTH CONTROL: Makes description span full dialog width
    description_input.isFullWidth = True

    # Create input groups for better organization
    diameter_group = inputs.addGroupCommandInput(
        'diameter_group', 'Stent Dimensions')
    diameter_group.isExpanded = True
    diameter_group.isEnabledCheckBoxDisplayed = False
    diameter_inputs = diameter_group.children

    # Diameter input - use createByString to ensure proper unit handling
    diameter_value = adsk.core.ValueInput.createByString(
        f'{last_used_values["diameter"]} mm')
    diameter_input = diameter_inputs.addValueInput(
        'diameter', 'Diameter (mm)', 'mm', diameter_value)
    diameter_input.tooltip = 'The outer diameter of the stent when expanded'

    # Length input - use createByString to ensure proper unit handling
    length_value = adsk.core.ValueInput.createByString(
        f'{last_used_values["length"]} mm')
    length_input = diameter_inputs.addValueInput(
        'length', 'Length (mm)', 'mm', length_value)
    length_input.tooltip = 'The total axial length of the stent'

    # Ring configuration group
    ring_group = inputs.addGroupCommandInput(
        'ring_group', 'Ring Configuration')
    ring_group.isExpanded = True
    ring_group.isEnabledCheckBoxDisplayed = False
    ring_inputs = ring_group.children

    # Number of rings with tooltip - load from saved values
    num_rings_input = ring_inputs.addIntegerSpinnerCommandInput(
        'num_rings', 'Number of Rings', 1, 20, 1, last_used_values['num_rings'])
    num_rings_input.tooltip = 'Total number of ring segments in the stent (1-20)'

    # Waves per ring (each wave = 2 crowns). Keep id for compatibility.
    crowns_input = ring_inputs.addIntegerSpinnerCommandInput(
        'crowns_per_ring', 'Waves per Ring', 2, 16, 1, max(2, last_used_values['crowns_per_ring']//2))
    crowns_input.tooltip = 'Number of waves per ring (each wave contains an up and a down crown)'

    # Crown Arc Calculations group - provides suggested values based on stent geometry
    crown_arc_group = inputs.addGroupCommandInput(
        'crown_arc_group', 'Crown Arc Suggestions')
    crown_arc_group.isExpanded = False  # Start collapsed
    crown_arc_group.isEnabledCheckBoxDisplayed = False
    crown_arc_inputs = crown_arc_group.children

    # Add a note about crown arc calculations
    crown_arc_note = crown_arc_inputs.addTextBoxCommandInput(
        'crown_arc_note', '',
        'Crown arc calculator: Enter theta (degrees) and radius (mm). Typical radius: 0.1-0.5 mm. Example: θ=72°, R=0.2mm → sagitta≈0.04mm',
        3, True)
    crown_arc_note.isFullWidth = True

    # Crown Arc Radius Input (user can edit this)
    # Default: 0.2 mm = 200 µm (typical stent crown radius)
    initial_radius_mm = 0.2
    crown_arc_radius_input = crown_arc_inputs.addValueInput(
        'crown_arc_radius', 'Crown Arc Radius (mm)', 'mm',
        adsk.core.ValueInput.createByReal(initial_radius_mm))
    crown_arc_radius_input.tooltip = 'Crown arc radius in mm (typical: 0.1-0.5 mm). Example: 0.2 mm = 200 µm'

    # Ring Height Input (needed for theta calculation)
    crown_arc_height_input = crown_arc_inputs.addValueInput(
        'crown_arc_height', 'Ring Height H (mm)', 'mm',
        adsk.core.ValueInput.createByString('1.0 mm'))
    crown_arc_height_input.tooltip = 'Ring height H in mm (auto-calculated from sagitta)'
    crown_arc_height_input.tooltip = 'Ring height H for theta calculation (h = H/2 for symmetric rings)'

    # Theta Input (primary input method)
    crown_arc_theta_input = crown_arc_inputs.addValueInput(
        'crown_arc_theta', 'Crown Arc Theta (degrees)', 'deg',
        adsk.core.ValueInput.createByString('72.0 deg'))
    crown_arc_theta_input.tooltip = 'Crown arc angle θ - primary input method. Common values: 60-90°. This value drives all crown arc calculations.'

    # Calculated crown arc parameters (read-only, updated from theta and radius)
    calculated_sagitta_input = crown_arc_inputs.addStringValueInput(
        'calculated_sagitta', 'Calculated Sagitta h (mm)', '')
    calculated_sagitta_input.isReadOnly = True
    calculated_sagitta_input.tooltip = 'Crown arc sagitta h = H/2 for symmetric rings'

    calculated_chord_input = crown_arc_inputs.addStringValueInput(
        'calculated_chord', 'Calculated Chord (mm)', '')
    calculated_chord_input.isReadOnly = True
    calculated_chord_input.tooltip = 'Crown arc chord length calculated from theta and radius'

    calculated_arc_length_input = crown_arc_inputs.addStringValueInput(
        'calculated_arc_length', 'Calculated Arc Length (mm)', '')
    calculated_arc_length_input.isReadOnly = True
    calculated_arc_length_input.tooltip = 'Crown arc length calculated from theta and radius'

    calculated_curvature_input = crown_arc_inputs.addStringValueInput(
        'calculated_curvature', 'Calculated Curvature (1/mm)', '')
    calculated_curvature_input.isReadOnly = True
    calculated_curvature_input.tooltip = 'Crown arc curvature κ = 1/R'

    # Add separator for rule-of-thumb checks
    crown_arc_rule_note = crown_arc_inputs.addTextBoxCommandInput(
        'crown_arc_rule_note', '',
        'Rule-of-thumb design checks (assumes 75µm strut width):',
        1, True)
    crown_arc_rule_note.isFullWidth = True

    calculated_r_over_w_input = crown_arc_inputs.addStringValueInput(
        'calculated_r_over_w', 'R/w Ratio', '')
    calculated_r_over_w_input.isReadOnly = True
    calculated_r_over_w_input.tooltip = 'Radius to strut width ratio - higher is gentler (assumes 75µm strut width)'

    calculated_geom_index_input = crown_arc_inputs.addStringValueInput(
        'calculated_geom_index', 'Geometric Index (w/2)/R', '')
    calculated_geom_index_input.isReadOnly = True
    # Add separator for rule-of-thumb checks
    calculated_geom_index_input.tooltip = 'Geometric strain index (w/2)/R - lower is gentler (assumes 75µm strut width)'
    crown_arc_note2 = crown_arc_inputs.addTextBoxCommandInput(
        'crown_arc_rule_note', '',
        'Rule-of-thumb design checks (assumes typical strut width ~50-100 µm):',
        1, True)
    crown_arc_note2.isFullWidth = True

    suggested_r_over_w_input = crown_arc_inputs.addStringValueInput(
        'suggested_r_over_w', 'R/w Ratio (typical strut)', '')
    suggested_r_over_w_input.isReadOnly = True
    suggested_r_over_w_input.tooltip = 'Radius to strut width ratio - higher is gentler (assumes 75µm strut width)'

    suggested_geom_index_input = crown_arc_inputs.addStringValueInput(
        'suggested_geom_index', 'Geometric Index (w/2)/R', '')
    suggested_geom_index_input.isReadOnly = True
    suggested_geom_index_input.tooltip = 'Geometric strain index (w/2)/R - lower is gentler (assumes 75µm strut width)'

    # Ring height proportions group - start collapsed (advanced feature)
    height_group = inputs.addGroupCommandInput(
        'height_group', 'Ring Height Proportions')
    height_group.isExpanded = False
    height_group.isEnabledCheckBoxDisplayed = False
    height_inputs = height_group.children

    # Default height factor control with update button - use createByString for consistency
    default_height_input = height_inputs.addValueInput(
        'default_height_factor', 'Default Height Factor', '',
        adsk.core.ValueInput.createByString('1.0'))
    default_height_input.tooltip = 'Default value to apply to all rings when Update All button is clicked'

    update_height_button = height_inputs.addBoolValueInput(
        'update_all_heights', 'Update All Heights', False, '', False)
    update_height_button.tooltip = 'Click to set all ring heights to the default value'

    # Height factors table - replaces text input for better usability
    height_factors_table = height_inputs.addTableCommandInput(
        'height_factors_table', 'Ring Height Proportions', 4, '80:120:120:120')
    height_factors_table.tooltip = 'Set relative proportions for each ring height and edit calculated chord and sagitta values'
    height_factors_table.maximumVisibleRows = 10
    height_factors_table.hasGrid = True

    # Keep original text input hidden for data storage and backwards compatibility
    height_factors_input = height_inputs.addStringValueInput(
        'height_factors', 'Height Proportions (hidden)', last_used_values['height_factors'])
    height_factors_input.isVisible = False

    # Hidden inputs for chord and sagitta values storage
    chord_values_input = height_inputs.addStringValueInput(
        'chord_values', 'Chord Values (hidden)', last_used_values['chord_values'])
    chord_values_input.isVisible = False

    sagitta_values_input = height_inputs.addStringValueInput(
        'sagitta_values', 'Sagitta Values (hidden)', last_used_values['sagitta_values'])
    sagitta_values_input.isVisible = False

    # Paste table data functionality
    paste_table_input = height_inputs.addTextBoxCommandInput(
        'paste_table_data', 'Paste Table Data',
        'Paste tab-separated table data here (with headers: Ring, Rc_mm, theta_deg, w_mm, h_mm, chord_mm, arc_mm, etc.)',
        5, False)
    paste_table_input.tooltip = 'Paste tabular data with chord_mm and h_mm columns to update the table automatically'

    paste_button = height_inputs.addBoolValueInput(
        'paste_table_button', 'Parse and Apply Pasted Data', False, '', False)
    paste_button.tooltip = 'Click to parse the pasted table data and update chord and sagitta values'

    # Gap configuration group - start collapsed (advanced feature)
    gap_group = inputs.addGroupCommandInput('gap_group', 'Gap Configuration')
    gap_group.isExpanded = False
    gap_group.isEnabledCheckBoxDisplayed = False
    gap_inputs = gap_group.children

    # Default gap value control with update button - use createByString for proper units
    default_gap_input = gap_inputs.addValueInput(
        'default_gap_value', 'Default Gap Value (mm)', 'mm',
        adsk.core.ValueInput.createByString('0.14 mm'))
    default_gap_input.tooltip = 'Default gap value in mm to apply to all gaps when Update All button is clicked'

    update_gap_button = gap_inputs.addBoolValueInput(
        'update_all_gaps', 'Update All Gaps', False, '', False)
    update_gap_button.tooltip = 'Click to set all gap values to the default value'

    # Gap configuration table - replaces text input for better usability
    gap_config_table = gap_inputs.addTableCommandInput(
        'gap_config_table', 'Gap Between Rings', 2, '100:200')
    gap_config_table.tooltip = 'Set gap values between rings in millimeters'
    gap_config_table.maximumVisibleRows = 10
    gap_config_table.hasGrid = True

    # Keep original text input hidden for data storage and backwards compatibility
    gap_input = gap_inputs.addStringValueInput(
        'gap_between_rings', 'Gap Between Rings (hidden)', last_used_values['gap_between_rings'])
    gap_input.isVisible = False

    # Drawing options group - start collapsed (secondary options)
    draw_group = inputs.addGroupCommandInput('draw_group', 'Drawing Options')
    draw_group.isExpanded = False
    draw_group.isEnabledCheckBoxDisplayed = False
    draw_inputs = draw_group.children

    # Drawing toggles with tooltips - load from saved values
    border_input = draw_inputs.addBoolValueInput(
        'draw_border', 'Draw Border', True, '', last_used_values['draw_border'])
    border_input.tooltip = 'Draw the rectangular boundary of the flattened stent'

    gap_lines_input = draw_inputs.addBoolValueInput(
        'draw_gap_centerlines', 'Draw Gap Center Lines', True, '', last_used_values['draw_gap_centerlines'])
    gap_lines_input.tooltip = 'Draw horizontal lines at the center of gaps between rings'

    peak_lines_input = draw_inputs.addBoolValueInput(
        'draw_crown_peaks', 'Draw Crown Peak Lines', True, '', last_used_values['draw_crown_peaks'])
    peak_lines_input.tooltip = 'Draw horizontal lines at the center of each ring (crown peaks)'

    wave_lines_input = draw_inputs.addBoolValueInput(
        'draw_crown_waves', 'Draw Crown Wave Lines', True, '', last_used_values['draw_crown_waves'])
    wave_lines_input.tooltip = 'Draw vertical lines dividing the circumference into crown sections'

    # Crown wave midlines option - load from saved values
    midlines_input = draw_inputs.addBoolValueInput(
        'draw_crown_midlines', 'Draw Crown Wave Midlines', True, '', last_used_values['draw_crown_midlines'])
    midlines_input.tooltip = 'Draw additional vertical lines at the midpoint between crown waves for finer detail'

    # Crown horizontal midlines option - load from saved values
    h_midlines_input = draw_inputs.addBoolValueInput(
        'draw_crown_h_midlines', 'Draw Crown Horizontal Midlines', True, '', last_used_values['draw_crown_h_midlines'])
    h_midlines_input.tooltip = 'Draw additional horizontal lines at the midpoint of each crown height for finer detail'

    # Sagitta guide lines removed; chord lines will be placed at sagitta offsets

    # Crown chord lines option - load from saved values
    chord_lines_input = draw_inputs.addBoolValueInput(
        'draw_crown_chord_lines', 'Draw Crown Chord Lines', True, '', last_used_values.get('draw_crown_chord_lines', False))
    chord_lines_input.tooltip = 'Draw horizontal chord segments at sagitta distance: first half up, second half down; alternates per ring for alignment'

    # Partial crown midlines control - load from saved values
    partial_midlines_input = draw_inputs.addIntegerSpinnerCommandInput(
        'partial_crown_midlines', 'Crown Midlines Count (from left)', 0, 20, 1, last_used_values['partial_crown_midlines'])
    partial_midlines_input.tooltip = 'Number of crowns from left to add midline vertical lines (0 = use full midlines option above)'

    # Crown mid lines option - load from saved values
    mid_lines_input = draw_inputs.addBoolValueInput(
        'draw_crown_mids', 'Draw Crown Mid Lines (Wave Quarter Lines)', True, '', last_used_values.get('draw_crown_mids', last_used_values.get('draw_crown_quarters', True)))
    mid_lines_input.tooltip = 'Draw vertical lines at the center of each crown section (wave quarter lines)'

    # Partial crown mid lines control - load from saved values
    partial_mids_input = draw_inputs.addIntegerSpinnerCommandInput(
        'partial_crown_mids', 'Crown Mid Lines Count (from left)', 0, 20, 1, last_used_values.get('partial_crown_mids', last_used_values.get('partial_crown_quarters', 0)))
    partial_mids_input.tooltip = 'Number of crowns from left to add mid vertical lines (0 = use full mid lines option above)'

    # Coincident points option - load from saved values
    coincident_points_input = draw_inputs.addBoolValueInput(
        'create_coincident_points', 'Create Coincident Points at Line Crossings', True, '', last_used_values['create_coincident_points'])
    coincident_points_input.tooltip = 'Create sketch points at all intersections where lines cross for precise geometric constraints'

    # Gap centerlines interior only option
    gap_lines_only_mid_input = draw_inputs.addBoolValueInput(
        'gap_centerlines_interior_only', 'Gap Center Lines — Interior Only', True, '', last_used_values['gap_centerlines_interior_only'])
    gap_lines_only_mid_input.tooltip = 'When enabled: only draw interior gap centerlines (exclude first and last gaps). When disabled: draw ALL gap centerlines including first and last gaps.'

    # Fold-lock options
    fl_group = inputs.addGroupCommandInput(
        'fl_group', 'Fold‑Lock Options (Ends Only)')
    fl_group.isExpanded = False
    fl_group.tooltip = 'Advanced options for fold‑lock end connections based on balloon wall thickness'
    fl_inputs = fl_group.children

    use_fl_input = fl_inputs.addBoolValueInput(
        'use_fold_lock_table', 'Use Fold‑Lock Table for End Gaps', True, '', last_used_values['use_fold_lock_table'])
    use_fl_input.tooltip = 'Override ONLY the first and last gaps with table‑based fold‑lock values from balloon wall thickness. Interior gaps are managed by the Gap Configuration table.'

    wall_input = fl_inputs.addIntegerSpinnerCommandInput(
        'balloon_wall_um', 'Balloon Wall Thickness (µm)', 8, 40, 1, last_used_values['balloon_wall_um'])
    wall_input.tooltip = 'Balloon wall thickness for fold‑lock gap calculation (typically 12‑20 µm)'

    # Try DropDownCommandInput with type ignore to bypass type checker
    try:
        # Use type ignore to bypass enum type checking issues
        material_dropdown = fl_inputs.addDropDownCommandInput(
            'balloon_material', 'Balloon Material', adsk.core.DropDownStyles.TextListDropDownStyle)  # type: ignore
        material_items = material_dropdown.listItems
        is_dropdown = True
    except:
        # Fallback to radio button group if dropdown fails
        material_dropdown = fl_inputs.addRadioButtonGroupCommandInput(
            'balloon_material', 'Balloon Material')
        material_items = material_dropdown.listItems
        is_dropdown = False

    material_options = ['Pebax', 'COC', 'Nylon', 'Polyurethane', 'PTFE']

    # Add material options and set selection
    selected_index = 0  # Default to Pebax
    try:
        selected_index = material_options.index(
            last_used_values['balloon_material'])
    except:
        pass

    for i, material in enumerate(material_options):
        if is_dropdown:
            # For dropdown: add(name, icon, isSelected) - try different parameter order
            item = material_items.add(material, i == selected_index, '')
        else:
            # For radio group: add(name, isSelected)
            item = material_items.add(material, i == selected_index)

    material_dropdown.tooltip = 'Select balloon material type - affects fold‑lock gap calculations'

    draw_fl_limits_input = fl_inputs.addBoolValueInput(
        'draw_fold_lock_limits', 'Draw Fold‑Lock Limit Lines in Crown Boxes', True, '', last_used_values['draw_fold_lock_limits'])
    draw_fl_limits_input.tooltip = 'Draw two horizontal lines per gap (above and below gap centerline) at fold‑lock limits for specified crown boxes'

    # Default fold-lock gap value control with update button
    # Calculate initial default based on material and wall thickness

    # Text input for manual configuration (hidden when table is used)
    fl_per_ring_config_input = fl_inputs.addStringValueInput(
        'per_ring_fold_lock_config', 'Per-Ring Config (ring:boxes:gap_mm)', last_used_values.get('per_ring_fold_lock_config', '1:0,2,4,6:0.095;2:1,3,5,7:0.095'))
    fl_per_ring_config_input.tooltip = 'Format: "ring:boxes:gap_mm;ring:boxes:gap_mm" (e.g., "1:0,2,4,6:0.095;2:1,3,5,7:0.095" for gap widths in mm)'

    # Add a table for per-ring configuration
    fl_per_ring_table = fl_inputs.addTableCommandInput(
        'per_ring_table', 'Fold-Lock Gap Configuration', 4, '140:60:140:100')
    fl_per_ring_table.tooltip = 'Configure fold-lock settings for all gaps (application depends on end-gap usage)'
    fl_per_ring_table.maximumVisibleRows = 10
    fl_per_ring_table.hasGrid = True

    # Always show per-ring configuration table
    fl_per_ring_table.isVisible = True
    # Hide text input for per-ring configuration (table is primary interface)
    fl_per_ring_config_input.isVisible = False

    # Reset button to restore default values
    reset_button = draw_inputs.addBoolValueInput(
        'reset_to_defaults', 'Reset to Default Values', False, '', False)
    reset_button.tooltip = 'Click to reset all inputs to their default values'

    # ⬅️ DIALOG BOX STARTUP WIDTH CONTROL:
    # Set the initial width and height of the dialog box - increased for better readability
    # Width: 500px, Height: 1000px (increased for larger font appearance)
    args.command.setDialogInitialSize(500, 1000)

    # ⬅️ ADDITIONAL DIALOG SIZE CONTROLS:
    # Set minimum dialog size (prevents user from making it too small)
    # Min Width: 450px, Min Height: 500px - increased minimums
    args.command.setDialogMinimumSize(450, 500)

    # Set maximum dialog size (prevents dialog from getting too large)
    # args.command.setDialogMaximumSize(800, 1200)  # Max Width: 800px, Max Height: 1200px - may not be available in all API versions

    # Alternative preset sizes you can try:
    # args.command.setDialogInitialSize(400, 500)  # Smaller dialog
    # args.command.setDialogInitialSize(600, 700)  # Larger dialog
    # args.command.setDialogInitialSize(450, 550)  # Medium dialog
    # args.command.setDialogInitialSize(520, 650)  # Wider dialog for better input visibility

    # TODO Connect to the events that are needed by this command.
    futil.add_handler(args.command.execute, command_execute,
                      local_handlers=local_handlers)
    futil.add_handler(args.command.inputChanged,
                      command_input_changed, local_handlers=local_handlers)
    futil.add_handler(args.command.executePreview,
                      command_preview, local_handlers=local_handlers)
    futil.add_handler(args.command.validateInputs,
                      command_validate_input, local_handlers=local_handlers)
    futil.add_handler(args.command.destroy, command_destroy,
                      local_handlers=local_handlers)

    # Initialize the per-ring table based on checkbox state
    try:
        inputs = args.command.commandInputs
        table_input = adsk.core.TableCommandInput.cast(
            inputs.itemById('per_ring_table'))
        config_input = adsk.core.StringValueCommandInput.cast(
            inputs.itemById('per_ring_fold_lock_config'))

        if table_input and config_input:
            # Always show table, keep config input hidden (table is primary interface)
            table_input.isVisible = True
            config_input.isVisible = False
        # Initialize height factors and gap configuration tables
        update_height_factors_table(inputs)
        update_gap_config_table(inputs)
        update_fold_lock_table(inputs)

        # Initialize crown arc suggestions and calculations
        update_crown_arc_suggestions(inputs)

    except Exception as e:
        # Don't show error during initialization, just log it
        futil.log(f"Error initializing tables: {str(e)}")


# This event handler is called when the user clicks the OK button in the command dialog or
# is immediately called after the created event not command inputs were created for the dialog.
def command_execute(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Execute Event')

    # Get a reference to your command's inputs.
    inputs = args.command.commandInputs

    # Extract input values with proper casting
    diameter_input = adsk.core.ValueCommandInput.cast(
        inputs.itemById('diameter'))
    length_input = adsk.core.ValueCommandInput.cast(inputs.itemById('length'))
    num_rings_input = adsk.core.IntegerSpinnerCommandInput.cast(
        inputs.itemById('num_rings'))
    crowns_per_ring_input = adsk.core.IntegerSpinnerCommandInput.cast(
        inputs.itemById('crowns_per_ring'))
    height_factors_input = adsk.core.StringValueCommandInput.cast(
        inputs.itemById('height_factors'))
    chord_values_input = adsk.core.StringValueCommandInput.cast(
        inputs.itemById('chord_values'))
    sagitta_values_input = adsk.core.StringValueCommandInput.cast(
        inputs.itemById('sagitta_values'))
    gap_input = adsk.core.StringValueCommandInput.cast(
        inputs.itemById('gap_between_rings'))

    # Drawing options
    draw_border_input = adsk.core.BoolValueCommandInput.cast(
        inputs.itemById('draw_border'))
    draw_gap_centerlines_input = adsk.core.BoolValueCommandInput.cast(
        inputs.itemById('draw_gap_centerlines'))
    draw_crown_peaks_input = adsk.core.BoolValueCommandInput.cast(
        inputs.itemById('draw_crown_peaks'))
    draw_crown_waves_input = adsk.core.BoolValueCommandInput.cast(
        inputs.itemById('draw_crown_waves'))
    draw_crown_midlines_input = adsk.core.BoolValueCommandInput.cast(
        inputs.itemById('draw_crown_midlines'))
    draw_crown_h_midlines_input = adsk.core.BoolValueCommandInput.cast(
        inputs.itemById('draw_crown_h_midlines'))
    # No sagitta lines input (removed)
    draw_crown_chord_lines_input = adsk.core.BoolValueCommandInput.cast(
        inputs.itemById('draw_crown_chord_lines'))
    partial_crown_midlines_input = adsk.core.IntegerSpinnerCommandInput.cast(
        inputs.itemById('partial_crown_midlines'))
    draw_crown_mids_input = adsk.core.BoolValueCommandInput.cast(
        inputs.itemById('draw_crown_mids'))
    partial_crown_mids_input = adsk.core.IntegerSpinnerCommandInput.cast(
        inputs.itemById('partial_crown_mids'))
    coincident_points_input = adsk.core.BoolValueCommandInput.cast(
        inputs.itemById('create_coincident_points'))

    # Fold-lock inputs
    gap_centerlines_interior_only_input = adsk.core.BoolValueCommandInput.cast(
        inputs.itemById('gap_centerlines_interior_only'))
    use_fold_lock_table_input = adsk.core.BoolValueCommandInput.cast(
        inputs.itemById('use_fold_lock_table'))
    balloon_wall_um_input = adsk.core.IntegerSpinnerCommandInput.cast(
        inputs.itemById('balloon_wall_um'))
    # Try to cast as dropdown first, then fallback to radio button group
    balloon_material_input = None
    material_input_raw = inputs.itemById('balloon_material')
    try:
        # Try dropdown first
        balloon_material_input = adsk.core.DropDownCommandInput.cast(
            material_input_raw)
        is_dropdown_type = True
    except:
        # Fallback to radio button group
        balloon_material_input = adsk.core.RadioButtonGroupCommandInput.cast(
            material_input_raw)
        is_dropdown_type = False
    draw_fold_lock_limits_input = adsk.core.BoolValueCommandInput.cast(
        inputs.itemById('draw_fold_lock_limits'))
    per_ring_fold_lock_config_input = adsk.core.StringValueCommandInput.cast(
        inputs.itemById('per_ring_fold_lock_config'))

    # Default value inputs for the new controls
    default_height_input = adsk.core.ValueCommandInput.cast(
        inputs.itemById('default_height_factor'))
    default_gap_input = adsk.core.ValueCommandInput.cast(
        inputs.itemById('default_gap_value'))

    reset_button_input = adsk.core.BoolValueCommandInput.cast(
        inputs.itemById('reset_to_defaults'))

    # Check if reset button was clicked
    if reset_button_input.value:
        # Reset all values to defaults - for value inputs, assign the numeric value directly
        diameter_input.value = default_values['diameter']
        length_input.value = default_values['length']
        num_rings_input.value = default_values['num_rings']
        crowns_per_ring_input.value = default_values['crowns_per_ring']
        height_factors_input.value = default_values['height_factors']
        chord_values_input.value = default_values['chord_values']
        sagitta_values_input.value = default_values['sagitta_values']
        gap_input.value = default_values['gap_between_rings']
        draw_border_input.value = default_values['draw_border']
        draw_gap_centerlines_input.value = default_values['draw_gap_centerlines']
        draw_crown_peaks_input.value = default_values['draw_crown_peaks']
        draw_crown_waves_input.value = default_values['draw_crown_waves']
        draw_crown_midlines_input.value = default_values['draw_crown_midlines']
        draw_crown_h_midlines_input.value = default_values['draw_crown_h_midlines']
        # sagitta lines default reset removed
        draw_crown_chord_lines_input.value = default_values['draw_crown_chord_lines']
        partial_crown_midlines_input.value = default_values['partial_crown_midlines']
        draw_crown_mids_input.value = default_values.get(
            'draw_crown_mids', default_values.get('draw_crown_quarters', False))
        partial_crown_mids_input.value = default_values.get(
            'partial_crown_mids', default_values.get('partial_crown_quarters', 0))
        coincident_points_input.value = default_values['create_coincident_points']

        # Reset fold-lock specific inputs
        gap_centerlines_interior_only_input.value = default_values['gap_centerlines_interior_only']
        use_fold_lock_table_input.value = default_values['use_fold_lock_table']
        balloon_wall_um_input.value = default_values['balloon_wall_um']

        # Reset material selection (dropdown or radio button group)
        material_options = ['Pebax', 'COC', 'Nylon', 'Polyurethane', 'PTFE']
        try:
            selected_index = material_options.index(
                default_values['balloon_material'])
        except:
            selected_index = 0  # Default to Pebax

        if is_dropdown_type:
            # For dropdown: set selectedItem by index
            if balloon_material_input.listItems.count > selected_index:
                balloon_material_input.listItems.item(
                    selected_index).isSelected = True
        else:
            # For radio button group: set isSelected on items
            for i, item in enumerate(balloon_material_input.listItems):
                item.isSelected = (i == selected_index)

        draw_fold_lock_limits_input.value = default_values['draw_fold_lock_limits']
        per_ring_fold_lock_config_input.value = default_values['per_ring_fold_lock_config']

        # Reset default value inputs
        if default_height_input:
            default_height_input.value = 1.0  # Default height factor
        if default_gap_input:
            default_gap_input.value = 0.14  # Default gap value in mm

        # Reset the button itself
        reset_button_input.value = False

        # Update last_used_values with defaults
        last_used_values.update(default_values.copy())

        return  # Exit early to just reset, don't execute

    # Get values
    # Convert cm to mm (Fusion returns values in cm)
    diameter = diameter_input.value * 10
    # Convert cm to mm (Fusion returns values in cm)
    length = length_input.value * 10
    num_rings = num_rings_input.value
    # Interpret UI value as waves; each wave = 2 crowns
    waves_per_ring = max(1, crowns_per_ring_input.value)
    crowns_per_ring = max(2, waves_per_ring * 2)

    # Collect height factors from table
    height_factors_list = []
    for ring_num in range(1, num_rings + 1):
        try:
            factor_input = adsk.core.ValueCommandInput.cast(
                inputs.itemById(f'height_ring_{ring_num}_factor'))
            if factor_input:
                height_factors_list.append(factor_input.value)
            else:
                height_factors_list.append(1.0)  # Default
        except:
            height_factors_list.append(1.0)  # Default

    # Convert to string for storage (backwards compatibility)
    height_factors_str = ', '.join([str(f) for f in height_factors_list])

    # Collect chord values from table
    chord_values_list = []
    for ring_num in range(1, num_rings + 1):
        try:
            chord_input = adsk.core.ValueCommandInput.cast(
                inputs.itemById(f'height_ring_{ring_num}_chord'))
            if chord_input:
                chord_values_list.append(chord_input.value*10)
            else:
                chord_values_list.append(1.0)  # Default
        except:
            chord_values_list.append(1.0)  # Default

    # Convert chord values to string for storage
    chord_values_str = ', '.join([str(f) for f in chord_values_list])
    # Persist into hidden input immediately (so table refresh keeps edits)
    try:
        chord_values_input.value = chord_values_str
    except:
        pass

    # Collect sagitta values from table
    sagitta_values_list = []
    for ring_num in range(1, num_rings + 1):
        try:
            sagitta_input = adsk.core.ValueCommandInput.cast(
                inputs.itemById(f'height_ring_{ring_num}_sagitta'))
            if sagitta_input:
                sagitta_values_list.append(sagitta_input.value*10)
            else:
                sagitta_values_list.append(0.1)  # Default
        except:
            sagitta_values_list.append(0.1)  # Default

    # Convert sagitta values to string for storage
    sagitta_values_str = ', '.join([str(f) for f in sagitta_values_list])
    # Persist into hidden input immediately (so table refresh keeps edits)
    try:
        sagitta_values_input.value = sagitta_values_str
    except:
        pass

    # Collect gap values from table
    gap_values_list = []
    num_gaps = max(1, num_rings - 1)
    for gap_num in range(1, num_gaps + 1):
        try:
            gap_value_input = adsk.core.ValueCommandInput.cast(
                inputs.itemById(f'gap_{gap_num}_value'))
            if gap_value_input:
                # Convert cm to mm (Fusion returns values in cm)
                gap_values_list.append(gap_value_input.value * 10)
            else:
                gap_values_list.append(0.14)  # Default in mm
        except:
            gap_values_list.append(0.14)  # Default in mm

    # Convert to string for storage (backwards compatibility)
    gap_str = ', '.join([str(g) for g in gap_values_list])

    draw_border = draw_border_input.value
    draw_gap_centerlines = draw_gap_centerlines_input.value
    draw_crown_peaks = draw_crown_peaks_input.value
    draw_crown_waves = draw_crown_waves_input.value
    draw_crown_midlines = draw_crown_midlines_input.value
    draw_crown_h_midlines = draw_crown_h_midlines_input.value
    # sagitta lines flag removed
    draw_crown_chord_lines = draw_crown_chord_lines_input.value
    partial_crown_midlines = partial_crown_midlines_input.value
    draw_crown_mids = draw_crown_mids_input.value
    partial_crown_mids = partial_crown_mids_input.value
    create_coincident_points = coincident_points_input.value

    # Fold-lock values
    gap_centerlines_interior_only = gap_centerlines_interior_only_input.value
    use_fold_lock_table = use_fold_lock_table_input.value
    balloon_wall_um = balloon_wall_um_input.value

    # Get selected material from dropdown or radio button group
    material_options = ['Pebax', 'COC', 'Nylon', 'Polyurethane', 'PTFE']
    balloon_material = 'Pebax'  # Default
    if balloon_material_input:
        if is_dropdown_type:
            # For dropdown: use selectedItem
            if balloon_material_input.selectedItem:
                selected_index = balloon_material_input.selectedItem.index
                if 0 <= selected_index < len(material_options):
                    balloon_material = material_options[selected_index]
        else:
            # For radio button group: find selected item
            for i, item in enumerate(balloon_material_input.listItems):
                if item.isSelected:
                    balloon_material = material_options[i]
                    break
    draw_fold_lock_limits = draw_fold_lock_limits_input.value
    fold_lock_columns = '0,2,4,6'  # Default crown boxes for fold-lock
    per_ring_fold_lock_config = per_ring_fold_lock_config_input.value

    # Always collect data from fold-lock table if visible
    table_input = adsk.core.TableCommandInput.cast(
        inputs.itemById('per_ring_table'))
    if table_input and table_input.isVisible:
        # Update the configuration string with current table data
        update_fold_lock_config_from_table(inputs)
        # Get the updated configuration
        per_ring_config_input = adsk.core.StringValueCommandInput.cast(
            inputs.itemById('per_ring_fold_lock_config'))
        per_ring_fold_lock_config = per_ring_config_input.value if per_ring_config_input else ''
    else:
        per_ring_fold_lock_config = per_ring_fold_lock_config_input.value

    # Use height factors from table (already collected above)
    height_factors = height_factors_list
    # Persist height factors immediately to hidden input
    try:
        height_factors_input.value = height_factors_str
    except:
        pass

    # Use gap values from table (already collected above)
    gap_values = gap_values_list

    # Apply fold-lock table if enabled
    if use_fold_lock_table and num_rings >= 2:
        # Calculate fold-lock gap based on balloon material and wall thickness
        end_gap = calculate_fold_lock_gap(balloon_material, balloon_wall_um)

        # Override ONLY first and last gaps (leave interior gaps as set by user in gap table)
        gap_values[0] = end_gap
        if len(gap_values) > 1:
            gap_values[-1] = end_gap

        # Interior gaps are now managed entirely by the gap configuration table

    # Save current values for next session (before calling drawing function)
    last_used_values.update({
        'diameter': diameter,  # Save the converted mm value, not the raw cm value
        'length': length,      # Save the converted mm value, not the raw cm value
        'num_rings': num_rings,
        'crowns_per_ring': crowns_per_ring,
        'height_factors': height_factors_str,
        'chord_values': chord_values_str,
        'sagitta_values': sagitta_values_str,
        'gap_between_rings': gap_str,
        'draw_border': draw_border,
        'draw_gap_centerlines': draw_gap_centerlines,
        'draw_crown_peaks': draw_crown_peaks,
        'draw_crown_waves': draw_crown_waves,
        'draw_crown_midlines': draw_crown_midlines,
        'draw_crown_h_midlines': draw_crown_h_midlines,
        # sagitta lines flag removed
        'draw_crown_chord_lines': draw_crown_chord_lines,
        'partial_crown_midlines': partial_crown_midlines,
        'draw_crown_mids': draw_crown_mids,
        'partial_crown_mids': partial_crown_mids,
        'create_coincident_points': create_coincident_points,
        'gap_centerlines_interior_only': gap_centerlines_interior_only,
        'use_fold_lock_table': use_fold_lock_table,
        'balloon_wall_um': balloon_wall_um,
        'balloon_material': balloon_material,
        'draw_fold_lock_limits': draw_fold_lock_limits,
        'per_ring_fold_lock_config': per_ring_fold_lock_config
    })

    # Call the stent frame drawing function
    draw_stent_frame(diameter, length, num_rings, crowns_per_ring,
                     height_factors, gap_values, draw_border, draw_gap_centerlines, gap_centerlines_interior_only,
                     draw_crown_peaks, draw_crown_waves, draw_crown_midlines, draw_crown_h_midlines, draw_crown_chord_lines,
                     partial_crown_midlines, draw_crown_mids, partial_crown_mids, create_coincident_points,
                     draw_fold_lock_limits, fold_lock_columns, per_ring_fold_lock_config,
                     balloon_wall_um, chord_values_list, sagitta_values_list)


# This event handler is called when the command needs to compute a new preview in the graphics window.
def command_preview(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Preview Event')
    inputs = args.command.commandInputs


# This event handler is called when the user changes anything in the command dialog
# allowing you to modify values of other inputs based on that change.
def command_input_changed(args: adsk.core.InputChangedEventArgs):
    changed_input = args.input
    inputs = args.inputs

    # General logging for debug.
    futil.log(
        f'{CMD_NAME} Input Changed Event fired from a change to {changed_input.id}')

    # Special check for crown arc inputs
    if changed_input.id in ['crown_arc_radius', 'crown_arc_height']:
        futil.log(f'*** CROWN ARC INPUT DETECTED: {changed_input.id} ***')

    # Handle changes to balloon wall thickness or material to update default fold-lock gap
    if changed_input.id == 'balloon_wall_um' or changed_input.id == 'balloon_material':
        # Material/wall changes no longer need to update UI since default gap field was removed
        pass

    # Handle changes to number of rings or crowns to update table
    elif changed_input.id in ['num_rings', 'crowns_per_ring']:
        try:
            command = adsk.core.Command.cast(args.firingEvent.sender)
            all_inputs = command.commandInputs
            table_input = adsk.core.TableCommandInput.cast(
                all_inputs.itemById('per_ring_table'))

            # Always update all tables when number of rings changes
            # This ensures the table rows stay in sync with the number of rings setting
            if table_input:
                update_fold_lock_table(all_inputs)
                # Sync the fold-lock table data back to the text configuration
                update_fold_lock_config_from_table(all_inputs)

            # Update height factors and gap configuration tables
            update_height_factors_table(all_inputs)
            update_gap_config_table(all_inputs)

            # Update crown arc suggestions when crowns per ring changes
            if changed_input.id == 'crowns_per_ring':
                update_crown_arc_suggestions(all_inputs)

            # Update crown arc height when number of rings changes (affects average calculation)
            if changed_input.id == 'num_rings':
                average_ring_height = calculate_average_ring_height(all_inputs)
                height_input = adsk.core.ValueCommandInput.cast(
                    all_inputs.itemById('crown_arc_height'))
                if height_input and height_input.value <= 0.1:  # Only if still at default
                    height_input.value = average_ring_height
                    update_crown_arc_calculations(all_inputs)

        except Exception as e:
            app = adsk.core.Application.get()
            ui = app.userInterface
            ui.messageBox(
                f"Error updating tables: {str(e)}", "Debug: Exception")

    # Handle changes to diameter - update crown arc suggestions
    elif changed_input.id == 'diameter':
        try:
            command = adsk.core.Command.cast(args.firingEvent.sender)
            all_inputs = command.commandInputs
            update_crown_arc_suggestions(all_inputs)
        except Exception as e:
            app = adsk.core.Application.get()
            ui = app.userInterface
            ui.messageBox(
                f"Error updating crown arc suggestions: {str(e)}", "Debug: Exception")

    # Handle changes to crown arc radius, height, or theta - recalculate all parameters
    elif changed_input.id in ['crown_arc_radius', 'crown_arc_height', 'crown_arc_theta']:
        try:
            futil.log(f'Crown arc input changed: {changed_input.id}')
            update_crown_arc_calculations(inputs)
            # Update sagitta values since crown arc radius affects sagitta calculation
            if changed_input.id == 'crown_arc_radius':
                update_sagitta_values_in_height_table(inputs)
            futil.log('Crown arc calculations completed')
        except Exception as e:
            futil.log(f'Crown arc calculation error: {str(e)}')
            app = adsk.core.Application.get()
            ui = app.userInterface
            ui.messageBox(
                f"Error updating crown arc calculations: {str(e)}", "Debug: Exception")

    # Handle changes to height factors - update crown arc height with new average
    elif changed_input.id.startswith('height_ring_') and changed_input.id.endswith('_factor'):
        try:
            futil.log(f'Height factor input changed: {changed_input.id}')

            # Calculate new average ring height
            average_ring_height = calculate_average_ring_height(inputs)
            futil.log(
                f'Calculated average ring height: {average_ring_height:.3f}mm')

            # Update crown arc height with the new average (if user hasn't manually modified it significantly)
            height_input = adsk.core.ValueCommandInput.cast(
                inputs.itemById('crown_arc_height'))
            if height_input:
                # Update if the current value is close to a calculated average (within 50% tolerance)
                # This prevents overriding user's manual adjustments
                current_value = height_input.value
                futil.log(f'Current crown arc height: {current_value:.3f}mm')
                if abs(current_value - average_ring_height) / max(average_ring_height, 0.1) < 0.5:
                    futil.log(
                        'Updating crown arc height with calculated average')
                    height_input.value = average_ring_height
                    # Trigger crown arc recalculation
                    update_crown_arc_calculations(inputs)
                else:
                    futil.log(
                        'Not updating crown arc height - user has made manual adjustments')

        except Exception as e:
            futil.log(f'Height factor calculation error: {str(e)}')
            app = adsk.core.Application.get()
            ui = app.userInterface
            ui.messageBox(
                f"Error updating crown arc height from ring heights: {str(e)}", "Debug: Exception")

    # Handle changes to length - update crown arc height with new average
    elif changed_input.id == 'length':
        try:
            futil.log('Length input changed')

            # Calculate new average ring height based on new length
            average_ring_height = calculate_average_ring_height(inputs)

            # Update crown arc height (only if still close to calculated value)
            height_input = adsk.core.ValueCommandInput.cast(
                inputs.itemById('crown_arc_height'))
            if height_input:
                current_value = height_input.value
                if abs(current_value - average_ring_height) / max(average_ring_height, 0.1) < 0.5:
                    height_input.value = average_ring_height
                    update_crown_arc_calculations(inputs)

            # Update sagitta values in height table since length affects ring scaling
            update_sagitta_values_in_height_table(inputs)

        except Exception as e:
            app = adsk.core.Application.get()
            ui = app.userInterface
            ui.messageBox(
                f"Error updating crown arc height from length change: {str(e)}", "Debug: Exception")

    # Handle changes to fold-lock table inputs and sync with text configuration
    elif changed_input.id.startswith('table_gap_') and ('_enable' in changed_input.id or '_boxes' in changed_input.id or '_gap' in changed_input.id):
        try:
            command = adsk.core.Command.cast(args.firingEvent.sender)
            all_inputs = command.commandInputs
            update_fold_lock_config_from_table(all_inputs)

        except Exception as e:
            app = adsk.core.Application.get()
            ui = app.userInterface
            ui.messageBox(
                f"Error syncing fold-lock table data: {str(e)}", "Debug: Exception")

    # Handle changes to height factors table inputs
    elif changed_input.id.startswith('height_ring_') and '_factor' in changed_input.id:
        try:
            command = adsk.core.Command.cast(args.firingEvent.sender)
            all_inputs = command.commandInputs
            config_input = adsk.core.StringValueCommandInput.cast(
                all_inputs.itemById('height_factors'))
            num_rings_input = adsk.core.IntegerSpinnerCommandInput.cast(
                all_inputs.itemById('num_rings'))

            if config_input and num_rings_input:
                # Collect current table data and update text configuration
                height_factors = []
                num_rings = num_rings_input.value

                for ring_num in range(1, num_rings + 1):
                    try:
                        factor_input = adsk.core.ValueCommandInput.cast(
                            all_inputs.itemById(f'height_ring_{ring_num}_factor'))
                        if factor_input:
                            height_factors.append(str(factor_input.value))
                    except:
                        height_factors.append('1.0')  # Default value

                # Update the text configuration
                config_input.value = ', '.join(height_factors)

                # Recalculate and update sagitta values for all rings
                update_sagitta_values_in_height_table(all_inputs)

        except Exception as e:
            app = adsk.core.Application.get()
            ui = app.userInterface
            ui.messageBox(
                f"Error syncing height factors: {str(e)}", "Debug: Exception")

    # Handle changes to gap configuration table inputs
    elif changed_input.id.startswith('gap_') and '_value' in changed_input.id:
        try:
            command = adsk.core.Command.cast(args.firingEvent.sender)
            all_inputs = command.commandInputs
            config_input = adsk.core.StringValueCommandInput.cast(
                all_inputs.itemById('gap_between_rings'))
            num_rings_input = adsk.core.IntegerSpinnerCommandInput.cast(
                all_inputs.itemById('num_rings'))

            if config_input and num_rings_input:
                # Collect current table data and update text configuration
                gap_values = []
                num_rings = num_rings_input.value
                num_gaps = max(1, num_rings - 1)

                for gap_num in range(1, num_gaps + 1):
                    try:
                        gap_input = adsk.core.ValueCommandInput.cast(
                            all_inputs.itemById(f'gap_{gap_num}_value'))
                        if gap_input:
                            gap_values.append(str(gap_input.value))
                    except:
                        gap_values.append('0.14')  # Default value

                # Update the text configuration
                config_input.value = ', '.join(gap_values)

                # Update sagitta values since gaps affect available ring space
                update_sagitta_values_in_height_table(all_inputs)

        except Exception as e:
            app = adsk.core.Application.get()
            ui = app.userInterface
            ui.messageBox(
                f"Error syncing gap values: {str(e)}", "Debug: Exception")

    # Handle update all heights button
    elif changed_input.id == 'update_all_heights':
        try:
            update_button = adsk.core.BoolValueCommandInput.cast(changed_input)
            if update_button.value:  # Button was clicked
                command = adsk.core.Command.cast(args.firingEvent.sender)
                all_inputs = command.commandInputs

                # Get the default height value
                default_height_input = adsk.core.ValueCommandInput.cast(
                    all_inputs.itemById('default_height_factor'))
                num_rings_input = adsk.core.IntegerSpinnerCommandInput.cast(
                    all_inputs.itemById('num_rings'))

                if default_height_input and num_rings_input:
                    default_value = default_height_input.value
                    num_rings = num_rings_input.value

                    # Update all height factor inputs in the table
                    for ring_num in range(1, num_rings + 1):
                        try:
                            factor_input = adsk.core.ValueCommandInput.cast(
                                all_inputs.itemById(f'height_ring_{ring_num}_factor'))
                            if factor_input:
                                factor_input.value = default_value
                        except:
                            pass  # Skip if input doesn't exist

                    # Trigger update of the hidden text input
                    update_height_factors_from_table(all_inputs)

                    # Update sagitta values since all height factors changed
                    update_sagitta_values_in_height_table(all_inputs)

                # Reset the button
                update_button.value = False

        except Exception as e:
            app = adsk.core.Application.get()
            ui = app.userInterface
            ui.messageBox(
                f"Error updating all heights: {str(e)}", "Debug: Exception")

    # Handle update all gaps button
    elif changed_input.id == 'update_all_gaps':
        try:
            update_button = adsk.core.BoolValueCommandInput.cast(changed_input)
            if update_button.value:  # Button was clicked
                command = adsk.core.Command.cast(args.firingEvent.sender)
                all_inputs = command.commandInputs

                # Get the default gap value
                default_gap_input = adsk.core.ValueCommandInput.cast(
                    all_inputs.itemById('default_gap_value'))
                num_rings_input = adsk.core.IntegerSpinnerCommandInput.cast(
                    all_inputs.itemById('num_rings'))

                if default_gap_input and num_rings_input:
                    # Convert cm to mm (Fusion returns values in cm)
                    default_value = default_gap_input.value * 10
                    num_rings = num_rings_input.value
                    num_gaps = max(1, num_rings - 1)

                    # Update all gap value inputs in the table
                    for gap_num in range(1, num_gaps + 1):
                        try:
                            gap_input = adsk.core.ValueCommandInput.cast(
                                all_inputs.itemById(f'gap_{gap_num}_value'))
                            if gap_input:
                                # Convert back to cm for Fusion's input system
                                gap_input.value = default_value / 10
                        except:
                            pass  # Skip if input doesn't exist

                    # Trigger update of the hidden text input
                    update_gap_config_from_table(all_inputs)

                # Reset the button
                update_button.value = False

        except Exception as e:
            app = adsk.core.Application.get()
            ui = app.userInterface
            ui.messageBox(
                f"Error updating all gaps: {str(e)}", "Debug: Exception")

    # Handle paste table button
    elif changed_input.id == 'paste_table_button':
        try:
            paste_button = adsk.core.BoolValueCommandInput.cast(changed_input)
            if paste_button.value:  # Button was clicked
                command = adsk.core.Command.cast(args.firingEvent.sender)
                all_inputs = command.commandInputs

                # Get the pasted data
                paste_input = adsk.core.TextBoxCommandInput.cast(
                    all_inputs.itemById('paste_table_data'))
                num_rings_input = adsk.core.IntegerSpinnerCommandInput.cast(
                    all_inputs.itemById('num_rings'))

                if paste_input and num_rings_input and paste_input.text.strip():
                    try:
                        parse_and_apply_table_data(
                            all_inputs, paste_input.text.strip())
                        # Clear the paste input
                        paste_input.text = ''
                        # Show success message
                        app = adsk.core.Application.get()
                        ui = app.userInterface
                        ui.messageBox(
                            "Table data successfully parsed and applied!", "Success")
                    except Exception as parse_error:
                        app = adsk.core.Application.get()
                        ui = app.userInterface
                        ui.messageBox(
                            f"Error parsing table data: {str(parse_error)}", "Parse Error")

                # Reset the button
                paste_button.value = False

        except Exception as e:
            app = adsk.core.Application.get()
            ui = app.userInterface
            ui.messageBox(
                f"Error processing paste table data: {str(e)}", "Debug: Exception")

    # Handle edits to chord cells: persist to hidden string input immediately
    elif changed_input.id.startswith('height_ring_') and changed_input.id.endswith('_chord'):
        try:
            command = adsk.core.Command.cast(args.firingEvent.sender)
            all_inputs = command.commandInputs
            num_rings_input = adsk.core.IntegerSpinnerCommandInput.cast(
                all_inputs.itemById('num_rings'))
            chord_config_input = adsk.core.StringValueCommandInput.cast(
                all_inputs.itemById('chord_values'))

            if num_rings_input and chord_config_input:
                num_rings = num_rings_input.value
                chord_values = []
                for ring_num in range(1, num_rings + 1):
                    try:
                        v_in = adsk.core.ValueCommandInput.cast(
                            all_inputs.itemById(f'height_ring_{ring_num}_chord'))
                        # store as mm (convert from cm)
                        chord_values.append(
                            str(v_in.value * 10.0)) if v_in else chord_values.append('0.0')
                    except:
                        chord_values.append('0.0')
                chord_config_input.value = ', '.join(chord_values)
        except:
            pass

    # Handle edits to sagitta cells: persist to hidden string input immediately
    elif changed_input.id.startswith('height_ring_') and changed_input.id.endswith('_sagitta'):
        try:
            command = adsk.core.Command.cast(args.firingEvent.sender)
            all_inputs = command.commandInputs
            num_rings_input = adsk.core.IntegerSpinnerCommandInput.cast(
                all_inputs.itemById('num_rings'))
            sagitta_config_input = adsk.core.StringValueCommandInput.cast(
                all_inputs.itemById('sagitta_values'))

            if num_rings_input and sagitta_config_input:
                num_rings = num_rings_input.value
                sagitta_values = []
                for ring_num in range(1, num_rings + 1):
                    try:
                        v_in = adsk.core.ValueCommandInput.cast(
                            all_inputs.itemById(f'height_ring_{ring_num}_sagitta'))
                        # store as mm (convert from cm)
                        sagitta_values.append(
                            str(v_in.value * 10.0)) if v_in else sagitta_values.append('0.0')
                    except:
                        sagitta_values.append('0.0')
                sagitta_config_input.value = ', '.join(sagitta_values)
        except:
            pass


def parse_and_apply_table_data(inputs, table_text):
    """Parse pasted table data and update chord and sagitta values"""
    import re
    try:
        lines = table_text.strip().split('\n')
        if len(lines) < 2:
            raise ValueError(
                "Table must have at least a header row and one data row")

        futil.log(f"Raw table text: {repr(table_text[:200])}")
        futil.log(f"Number of lines: {len(lines)}")
        futil.log(f"First few lines: {lines[:5]}")

        # EXCEL DIRECT PASTE DETECTION: cells come one-per-line; reconstruct dynamically
        if len(lines) > 10 and all(len(line.strip().split()) <= 2 for line in lines[:10]):
            futil.log(
                "Detected Excel direct paste (one cell per line); reconstructing table")

            # Helper to detect numeric tokens (defined before use)
            def _looks_like_number(s: str) -> bool:
                try:
                    float(s)
                    return True
                except:
                    return False

            # Find the first occurrence of a likely header token (e.g., 'Ring')
            header_start = -1
            for i, line in enumerate(lines):
                tok = line.strip()
                if tok and not _looks_like_number(tok):
                    header_start = i
                    break

            if header_start >= 0:
                # Collect header tokens until the first numeric cell (start of data)
                header_tokens = []
                data_tokens = []
                in_header = True
                for tok in [ln.strip() for ln in lines[header_start:] if ln.strip()]:
                    if in_header and not _looks_like_number(tok):
                        header_tokens.append(tok)
                    else:
                        in_header = False
                        data_tokens.append(tok)

                col_count = len(header_tokens)
                futil.log(
                    f"Reconstructed header tokens ({col_count}): {header_tokens}")

                if col_count >= 2 and len(data_tokens) >= col_count:
                    reconstructed = []
                    reconstructed.append('\t'.join(header_tokens))
                    for i in range(0, len(data_tokens), col_count):
                        row = data_tokens[i:i+col_count]
                        if len(row) == col_count:
                            reconstructed.append('\t'.join(row))
                    if len(reconstructed) >= 2:
                        lines = reconstructed
                        futil.log(
                            f"Reconstructed {len(reconstructed)-1} data rows from Excel paste")
                    else:
                        futil.log(
                            "Excel reconstruction produced no data rows; continuing with original lines")
                else:
                    futil.log(
                        "Excel reconstruction failed (insufficient tokens); continuing with original lines")

        # Parse header to find column indices - try different separators
        header = []
        separator = '\t'  # default

        futil.log(f"First line after reconstruction: {repr(lines[0])}")

        # SPECIAL CASE: If we detect this looks like the expected table format,
        # skip header parsing and go straight to known format
        if ('Ring' in lines[0] and len(lines) > 1):
            # Check if data rows look right
            test_row = [col for col in re.split(
                r'\s+', lines[1].strip()) if col]
            futil.log(
                f"Detected table format, test row has {len(test_row)} values: {test_row}")

            if len(test_row) >= 6:  # We expect 10 columns but at minimum need Ring + chord_mm + h_mm + others
                futil.log("Using direct known format bypass")
                # Build header mapping from the actual header row
                header_tokens = [col for col in re.split(
                    r'\s+', lines[0].strip()) if col]
                name_to_idx = {col.lower(): i for i,
                               col in enumerate(header_tokens)}

                # Helper to find preferred column index by name substring matches
                def find_idx(*candidates):
                    for c in candidates:
                        for k, i in name_to_idx.items():
                            if k == c or c in k:
                                return i
                    return -1

                ring_col = find_idx('ring')
                # Prefer centerline columns if available
                chord_col = find_idx('chord_center_mm', 'chord_mm', 'chord')
                sagitta_col = find_idx(
                    'sagitta_center_mm', 'sagitta_mm', 'h_mm', 'sagitta')
                width_col = find_idx('w_mm_from_widthlist', 'w_mm')

                futil.log(
                    f"Direct mapping: ring={ring_col}, chord={chord_col}, sagitta={sagitta_col}, width={width_col}")

                # Jump straight to data parsing
                chord_values = []
                sagitta_values = []

                for line_num, line in enumerate(lines[1:], start=2):
                    if not line.strip():
                        continue

                    # Split on any whitespace
                    cells = [col for col in re.split(
                        r'\s+', line.strip()) if col]

                    futil.log(
                        f"Line {line_num}: {len(cells)} cells: {cells[:6]}")

                    if len(cells) < 6:  # Need at least 6 columns
                        futil.log(
                            f"Skipping line {line_num} - not enough cells ({len(cells)} < 6)")
                        continue

                    try:
                        ring_num = int(
                            cells[ring_col]) if ring_col != -1 else (len(chord_values) + 1)
                        # Use provided centerline chord and sagitta directly if available
                        chord_value = float(
                            cells[chord_col]) if chord_col != -1 else 0.0
                        sagitta_value = float(
                            cells[sagitta_col]) if sagitta_col != -1 else 0.0

                        futil.log(
                            f"Parsed line {line_num}: Ring={ring_num}, Chord={chord_value}, Sagitta={sagitta_value}")

                        # Ensure we have enough entries in our lists
                        while len(chord_values) < ring_num:
                            chord_values.append(0.0)
                        while len(sagitta_values) < ring_num:
                            sagitta_values.append(0.0)

                        # Store values (ring numbers are 1-based, list indices are 0-based)
                        chord_values[ring_num - 1] = chord_value
                        sagitta_values[ring_num - 1] = sagitta_value

                    except (ValueError, IndexError) as e:
                        futil.log(
                            f"Warning: Could not parse line {line_num}: {line} - {str(e)}")
                        continue

                if not chord_values or not sagitta_values:
                    raise ValueError("No valid data rows found in table")

                # Update the hidden storage inputs
                chord_input = adsk.core.StringValueCommandInput.cast(
                    inputs.itemById('chord_values'))
                sagitta_input = adsk.core.StringValueCommandInput.cast(
                    inputs.itemById('sagitta_values'))

                if chord_input:
                    chord_input.value = ','.join(
                        [str(v) for v in chord_values])
                if sagitta_input:
                    sagitta_input.value = ','.join(
                        [str(v) for v in sagitta_values])

                # Update the height factors table to show the new values
                update_height_factors_table(inputs)

                futil.log(
                    f"Successfully parsed {len(chord_values)} chord values and {len(sagitta_values)} sagitta values")
                return  # Success - exit early

        # ORIGINAL PARSING LOGIC (fallback if direct format doesn't work)

        # Try tab separator first
        if '\t' in lines[0]:
            header = lines[0].split('\t')
            separator = '\t'
            futil.log(f"Found tabs in header, using tab separator")
        # Try multiple spaces (common when pasting from tables)
        elif '  ' in lines[0]:  # Multiple spaces
            header = [col for col in re.split(
                r'\s{2,}', lines[0]) if col.strip()]
            separator = 'multi_space'
            futil.log(f"Found multiple spaces, using multi-space separator")
        # Try any single space
        elif ' ' in lines[0]:
            header = [col for col in lines[0].split(' ') if col.strip()]
            separator = 'single_space'
            futil.log(f"Found single spaces, using single-space separator")
        # Try comma separator
        elif ',' in lines[0]:
            header = lines[0].split(',')
            separator = ','
            futil.log(f"Found commas, using comma separator")
        # Last resort: split on any whitespace
        else:
            header = lines[0].split()
            separator = 'whitespace'
            futil.log(f"No clear separator found, using whitespace split")

        # Clean up header columns (remove extra whitespace)
        header = [col.strip() for col in header if col.strip()]

        futil.log(f"Header after parsing: {header}")
        futil.log(f"Number of columns found: {len(header)}")

        # NEW FORMAT: wave_height_mm, wave_width_mm, strut_width_mm -> compute centerline chord/sagitta
        header_lc = [h.strip().lower() for h in header]
        if ('wave_height_mm' in header_lc and 'wave_width_mm' in header_lc and 'strut_width_mm' in header_lc):
            h_idx = header_lc.index('wave_height_mm')
            w_idx = header_lc.index('wave_width_mm')
            t_idx = header_lc.index('strut_width_mm')
            # ring index (optional)
            ring_idx = header_lc.index('ring') if 'ring' in header_lc else -1

            # Use quarter_wave_from_rect to compute centerline chord/sagitta

            chord_values = []
            sagitta_values = []
            for line_num, line in enumerate(lines[1:], start=2):
                if not line.strip():
                    continue
                cells = [c for c in re.split(r'\s+|\t|,', line.strip()) if c]
                try:
                    rect_h = float(cells[h_idx])
                    rect_w = float(cells[w_idx])
                    strut_w = float(cells[t_idx])

                    res = crown_from_full_wave(
                        rect_h, rect_w, strut_w, R_factor=2.5)
                    if not res:
                        futil.log(f"No valid arc for row {line_num}; skipping")
                        continue
                    chord = float(res['chord_mm'])
                    # quarter_wave_from_rect returns centerline sagitta already
                    sag = float(res['y_chord_mm'])
                    # Determine ring number
                    if ring_idx != -1 and ring_idx < len(cells):
                        ring_num = int(cells[ring_idx])
                    else:
                        ring_num = len(chord_values) + 1
                    while len(chord_values) < ring_num:
                        chord_values.append(0.0)
                    while len(sagitta_values) < ring_num:
                        sagitta_values.append(0.0)
                    chord_values[ring_num - 1] = chord
                    sagitta_values[ring_num - 1] = sag
                except Exception as e:
                    futil.log(
                        f"Wave format parse warning at line {line_num}: {e}")
                    continue

            if chord_values and sagitta_values:
                chord_input = adsk.core.StringValueCommandInput.cast(
                    inputs.itemById('chord_values'))
                sagitta_input = adsk.core.StringValueCommandInput.cast(
                    inputs.itemById('sagitta_values'))
                if chord_input:
                    chord_input.value = ','.join(
                        [f"{v:.6f}" for v in chord_values])
                if sagitta_input:
                    sagitta_input.value = ','.join(
                        [f"{v:.6f}" for v in sagitta_values])
                update_height_factors_table(inputs)
                futil.log(f"Wave mapping success: {len(chord_values)} rings")
                return

        # If we still don't have enough columns, try the most aggressive approach
        if len(header) < 5:  # We expect at least Ring, chord_mm, h_mm plus others
            futil.log(
                "Less than 5 columns found, trying aggressive regex parsing...")
            import re
            # Split on any whitespace sequence
            header = [col for col in re.split(r'\s+', lines[0].strip()) if col]
            separator = 'regex_whitespace'
            futil.log(f"After regex split: {len(header)} columns: {header}")

            # If still not enough, maybe it's a fixed-width format
            if len(header) < 5:
                futil.log(
                    "Still not enough columns - attempting fixed-width parsing...")
                # For your specific table format, let's try to parse based on known column names
                header_line = lines[0]
                if 'Ring' in header_line and 'chord_mm' in header_line and 'h_mm' in header_line:
                    # Manual parsing for your specific format
                    known_columns = ['Ring', 'Rc_mm', 'theta_deg', 'w_mm_from_widthlist', 'h_mm',
                                     'chord_mm', 'arc_mm', 'curvature_1_per_mm', 'Rc_over_w', 'geom_index_half_w_over_Rc']
                    header = known_columns
                    separator = 'known_format'
                    futil.log(f"Using known column format: {header}")
                else:
                    # Last resort: if we detect this is likely tabular data but parsing failed,
                    # assume it's the expected format and try anyway
                    futil.log(
                        "Attempting to parse as expected format despite detection failure...")
                    if len(lines) > 1 and lines[1].strip():
                        # Check if the data rows have multiple values
                        test_row = [col for col in re.split(
                            r'\s+', lines[1].strip()) if col]
                        futil.log(
                            f"Test row has {len(test_row)} values: {test_row}")

                        if len(test_row) >= 6:  # We need at least Ring, and the chord_mm, h_mm columns
                            # Assume the standard format
                            known_columns = ['Ring', 'Rc_mm', 'theta_deg', 'w_mm_from_widthlist', 'h_mm',
                                             'chord_mm', 'arc_mm', 'curvature_1_per_mm', 'Rc_over_w', 'geom_index_half_w_over_Rc']
                            header = known_columns
                            separator = 'forced_format'
                            futil.log(
                                f"Forcing known column format based on data row analysis: {header}")
                        else:
                            futil.log(
                                f"Data row only has {len(test_row)} values, cannot proceed")

        # Find required column indices (prefer centerline-specific names)
        ring_col = -1
        chord_col = -1
        sagitta_col = -1
        width_col = -1
        rc_col = -1
        theta_col = -1

        for i, col_name in enumerate(header):
            col_name_clean = col_name.lower().strip()
            futil.log(
                f"Checking column {i}: '{col_name}' -> '{col_name_clean}'")

            if 'ring' in col_name_clean:
                ring_col = i
                futil.log(f"Found Ring column at index {i}")
            elif 'chord_center' in col_name_clean:
                chord_col = i
                futil.log(f"Found Centerline Chord column at index {i}")
            elif 'sagitta_center' in col_name_clean:
                sagitta_col = i
                futil.log(f"Found Centerline Sagitta column at index {i}")
            elif 'chord' in col_name_clean and chord_col == -1:
                chord_col = i
                futil.log(f"Found Chord column at index {i}")
            elif ('h_mm' in col_name_clean or 'sagitta' in col_name_clean) and sagitta_col == -1:
                sagitta_col = i
                futil.log(f"Found Sagitta column at index {i}")
            elif 'w_mm_from_widthlist' in col_name_clean or col_name_clean == 'w_mm':
                width_col = i
                futil.log(f"Found Width column at index {i}")
            elif col_name_clean in ('rc_mm_center', 'rc_mm', 'rc_um', 'rc'):
                rc_col = i
                futil.log(f"Found Rc column at index {i}")
            elif 'theta' in col_name_clean:
                theta_col = i
                futil.log(f"Found Theta column at index {i}")

        futil.log(
            f"Final column indices: Ring={ring_col}, Chord={chord_col}, Sagitta={sagitta_col}")

        if ring_col == -1:
            raise ValueError(
                f"Could not find 'Ring' column in header. Available columns: {header}")
        if chord_col == -1:
            raise ValueError(
                f"Could not find 'chord_mm' or 'chord' column in header. Available columns: {header}")
        if sagitta_col == -1:
            raise ValueError(
                f"Could not find 'h_mm' or 'sagitta' column in header. Available columns: {header}")
        if width_col == -1:
            futil.log(
                "Width column not found; sagitta will not be adjusted by w/2")

        # Parse data rows
        chord_values = []
        sagitta_values = []

        for line_num, line in enumerate(lines[1:], start=2):
            if not line.strip():
                continue

            # Use the same separator we detected for the header
            if separator == '\t':
                cells = line.split('\t')
            elif separator == ',':
                cells = line.split(',')
            elif separator == 'multi_space':
                import re
                cells = [col for col in re.split(
                    r'\s{2,}', line) if col.strip()]
            elif separator == 'single_space':
                cells = [col for col in line.split(' ') if col.strip()]
            elif separator == 'regex_whitespace':
                import re
                cells = [col for col in re.split(r'\s+', line) if col.strip()]
            elif separator == 'known_format' or separator == 'forced_format':
                # For known format, split on any whitespace since the columns are space-separated
                import re
                cells = [col for col in re.split(r'\s+', line.strip()) if col]
            else:  # whitespace
                cells = line.split()

            # Clean up cells (remove extra whitespace)
            cells = [cell.strip() for cell in cells if cell.strip()]

            # Show first 6 cells
            futil.log(f"Line {line_num}: {len(cells)} cells: {cells[:6]}")

            if len(cells) <= max(ring_col, chord_col, sagitta_col):
                futil.log(
                    f"Skipping line {line_num} - not enough cells ({len(cells)} < {max(ring_col, chord_col, sagitta_col) + 1})")
                continue  # Skip incomplete rows

            try:
                ring_num = int(cells[ring_col])
                # Use centerline chord/sagitta directly when available
                if chord_col != -1 and sagitta_col != -1:
                    chord_value = float(cells[chord_col])
                    sagitta_value = float(cells[sagitta_col])
                else:
                    # Fallback: recompute centerline from Rc/theta if available
                    have_rc_theta = (rc_col != -1 and theta_col != -
                                     1 and rc_col < len(cells) and theta_col < len(cells))
                    # Width (optional)
                    if width_col != -1 and width_col < len(cells):
                        try:
                            w_val = float(cells[width_col])
                        except Exception:
                            w_val = 0.0
                    else:
                        w_val = 0.0
                    if have_rc_theta:
                        try:
                            Rc_edge = float(cells[rc_col])
                            theta_deg = float(cells[theta_col])
                            Rc_center = max(1e-9, Rc_edge - 0.5 * w_val)
                            a = math.radians(theta_deg / 2.0)
                            chord_value = 2.0 * Rc_center * math.sin(a)
                            sagitta_value = 2.0 * Rc_center * \
                                (1.0 - math.cos(a))
                        except Exception:
                            chord_value = float(
                                cells[chord_col]) if chord_col != -1 else 0.0
                            sagitta_value = float(
                                cells[sagitta_col]) if sagitta_col != -1 else 0.0
                    else:
                        chord_value = float(
                            cells[chord_col]) if chord_col != -1 else 0.0
                        sagitta_value = float(
                            cells[sagitta_col]) if sagitta_col != -1 else 0.0

                futil.log(
                    f"Parsed line {line_num}: Ring={ring_num}, Chord={chord_value}, Sagitta={sagitta_value}")

                # Ensure we have enough entries in our lists
                while len(chord_values) < ring_num:
                    chord_values.append(0.0)
                while len(sagitta_values) < ring_num:
                    sagitta_values.append(0.0)

                # Store values (ring numbers are 1-based, list indices are 0-based)
                chord_values[ring_num - 1] = chord_value
                sagitta_values[ring_num - 1] = sagitta_value

            except (ValueError, IndexError) as e:
                futil.log(
                    f"Warning: Could not parse line {line_num}: {line} - {str(e)}")
                continue

        if not chord_values or not sagitta_values:
            raise ValueError("No valid data rows found in table")

        # Update the hidden storage inputs
        chord_input = adsk.core.StringValueCommandInput.cast(
            inputs.itemById('chord_values'))
        sagitta_input = adsk.core.StringValueCommandInput.cast(
            inputs.itemById('sagitta_values'))

        if chord_input:
            chord_input.value = ','.join([str(v) for v in chord_values])
        if sagitta_input:
            sagitta_input.value = ','.join([str(v) for v in sagitta_values])

        # Update the height factors table to show the new values
        update_height_factors_table(inputs)

        futil.log(
            f"Successfully parsed {len(chord_values)} chord values and {len(sagitta_values)} sagitta values")

    except Exception as e:
        futil.log(f"Error parsing table data: {str(e)}")
        raise


def update_per_ring_table(inputs):
    """Update the per-ring table with current stent parameters"""
    try:
        # Get required inputs
        num_rings_input = adsk.core.IntegerSpinnerCommandInput.cast(
            inputs.itemById('num_rings'))
        crowns_input = adsk.core.IntegerSpinnerCommandInput.cast(
            inputs.itemById('crowns_per_ring'))
        table_input = adsk.core.TableCommandInput.cast(
            inputs.itemById('per_ring_table'))
        config_input = adsk.core.StringValueCommandInput.cast(
            inputs.itemById('per_ring_fold_lock_config'))

        if not all([num_rings_input, crowns_input, table_input]):
            return

        num_rings = num_rings_input.value
        crowns_per_ring = crowns_input.value

        # Parse current configuration from text input
        ring_data = {}
        if config_input and config_input.value:
            try:
                for config_part in config_input.value.split(';'):
                    if ':' in config_part:
                        parts = config_part.strip().split(':')
                        if len(parts) == 3:
                            ring_idx = int(parts[0].strip())
                            boxes_str = parts[1].strip()
                            gap_mm = float(parts[2].strip())
                            ring_data[ring_idx] = {
                                'boxes': boxes_str, 'gap_mm': gap_mm}
            except:
                pass  # Ignore parsing errors

        # Clear existing table contents
        table_input.clear()

        # Add table headers
        header_ring = inputs.addTextBoxCommandInput(
            'table_header_ring', '', 'Ring', 1, True)
        header_enable = inputs.addTextBoxCommandInput(
            'table_header_enable', '', 'Enable', 1, True)
        header_boxes = inputs.addTextBoxCommandInput(
            'table_header_boxes', '', 'Crown Boxes', 1, True)
        header_gap = inputs.addTextBoxCommandInput(
            'table_header_gap', '', 'Gap (mm)', 1, True)

        table_input.addCommandInput(header_ring, 0, 0)
        table_input.addCommandInput(header_enable, 0, 1)
        table_input.addCommandInput(header_boxes, 0, 2)
        table_input.addCommandInput(header_gap, 0, 3)

        # Add data rows for fold-lock rings (rings 1 through 5)
        # Rings 1-5, but not more than total rings
        fold_lock_rings = list(range(1, min(6, num_rings + 1)))

        for idx, ring_num in enumerate(fold_lock_rings):
            row_index = idx + 1  # Row 0 is headers

            # Ring number (read-only)
            ring_label = inputs.addTextBoxCommandInput(
                f'table_ring_{ring_num}_label', '', str(ring_num), 1, True)
            table_input.addCommandInput(ring_label, row_index, 0)

            # Enable checkbox
            is_enabled = ring_num in ring_data
            enable_checkbox = inputs.addBoolValueInput(
                f'table_ring_{ring_num}_enable', '', True, '', is_enabled)
            enable_checkbox.tooltip = f'Enable fold-lock for ring {ring_num}'
            table_input.addCommandInput(enable_checkbox, row_index, 1)

            # Crown boxes input
            default_boxes = ring_data.get(ring_num, {}).get('boxes', '0,2,4,6')
            boxes_input = inputs.addStringValueInput(
                f'table_ring_{ring_num}_boxes', '', default_boxes)
            boxes_input.tooltip = f'Comma-separated crown box indices (0-{crowns_per_ring-1})'
            table_input.addCommandInput(boxes_input, row_index, 2)

            # Gap input - use createByString for proper unit handling
            default_gap = ring_data.get(ring_num, {}).get('gap_mm', 0.095)
            gap_input = inputs.addValueInput(f'table_ring_{ring_num}_gap', '', 'mm',
                                             adsk.core.ValueInput.createByString(f'{default_gap} mm'))
            gap_input.tooltip = 'Fold-lock gap width in millimeters'
            table_input.addCommandInput(gap_input, row_index, 3)

    except Exception as e:
        app = adsk.core.Application.get()
        ui = app.userInterface
        if ui:
            ui.messageBox(f'Error updating table: {str(e)}')


def update_height_factors_table(inputs):
    """Update the height factors table with current stent parameters"""
    try:
        # Get required inputs
        num_rings_input = adsk.core.IntegerSpinnerCommandInput.cast(
            inputs.itemById('num_rings'))
        table_input = adsk.core.TableCommandInput.cast(
            inputs.itemById('height_factors_table'))
        config_input = adsk.core.StringValueCommandInput.cast(
            inputs.itemById('height_factors'))
        chord_config_input = adsk.core.StringValueCommandInput.cast(
            inputs.itemById('chord_values'))
        sagitta_config_input = adsk.core.StringValueCommandInput.cast(
            inputs.itemById('sagitta_values'))

        # Get parameters needed for sagitta calculation
        length_input = adsk.core.ValueCommandInput.cast(
            inputs.itemById('length'))
        gap_input = adsk.core.StringValueCommandInput.cast(
            inputs.itemById('gap_between_rings'))

        if not all([num_rings_input, table_input]):
            return

        num_rings = num_rings_input.value

        # Get stent length (convert from cm to mm)
        stent_length_mm = 8.0  # Default
        if length_input:
            stent_length_mm = length_input.value * 10.0  # cm to mm

        # Parse gap values to calculate available ring space
        gap_values = []
        if gap_input and gap_input.value:
            try:
                gap_values = [float(x.strip())
                              for x in gap_input.value.split(',')]
            except:
                pass

        # Ensure we have gap values
        num_gaps = max(1, num_rings - 1)
        while len(gap_values) < num_gaps:
            gap_values.append(gap_values[-1] if gap_values else 0.16)
        gap_values = gap_values[:num_gaps]

        total_gap_space = sum(gap_values) if num_gaps > 0 else 0.0
        available_ring_space = max(0.0, stent_length_mm - total_gap_space)

        # Parse current configuration from text input
        height_factors = []
        if config_input and config_input.value:
            try:
                height_factors = [float(x.strip())
                                  for x in config_input.value.split(',')]
            except:
                pass  # Ignore parsing errors

        # Ensure we have values for all rings
        while len(height_factors) < num_rings:
            height_factors.append(1.0)
        height_factors = height_factors[:num_rings]

        # Parse saved chord values
        chord_values = []
        if chord_config_input and chord_config_input.value:
            try:
                chord_values = [float(x.strip())
                                for x in chord_config_input.value.split(',')]
            except:
                pass  # Ignore parsing errors

        # Parse saved sagitta values
        sagitta_values = []
        if sagitta_config_input and sagitta_config_input.value:
            try:
                sagitta_values = [float(x.strip())
                                  for x in sagitta_config_input.value.split(',')]
            except:
                pass  # Ignore parsing errors

        # Calculate scaled ring heights based on available space
        total_height_factors = sum(height_factors) if height_factors else 1.0
        ring_scale_factor = available_ring_space / \
            total_height_factors if total_height_factors > 0 else 1.0

        # Clear existing table contents
        table_input.clear()

        # Add table headers
        header_ring = inputs.addTextBoxCommandInput(
            'height_header_ring', '', 'Ring', 1, True)
        header_factor = inputs.addTextBoxCommandInput(
            'height_header_factor', '', 'Height Factor', 1, True)
        header_chord = inputs.addTextBoxCommandInput(
            'height_header_chord', '', 'Chord (mm)', 1, True)
        header_sagitta = inputs.addTextBoxCommandInput(
            'height_header_sagitta', '', 'Sagitta (mm)', 1, True)

        table_input.addCommandInput(header_ring, 0, 0)
        table_input.addCommandInput(header_factor, 0, 1)
        table_input.addCommandInput(header_chord, 0, 2)
        table_input.addCommandInput(header_sagitta, 0, 3)

        # Add data rows for each ring
        for ring_num in range(1, num_rings + 1):
            row_index = ring_num  # Row 0 is headers

            # Ring number (read-only)
            ring_label = inputs.addTextBoxCommandInput(
                f'height_ring_{ring_num}_label', '', str(ring_num), 1, True)
            table_input.addCommandInput(ring_label, row_index, 0)

            # Height factor input - use createByString for consistency
            default_factor = height_factors[ring_num -
                                            1] if ring_num - 1 < len(height_factors) else 1.0
            factor_input = inputs.addValueInput(f'height_ring_{ring_num}_factor', '', '',
                                                adsk.core.ValueInput.createByString(f'{default_factor}'))
            factor_input.tooltip = f'Height proportion for ring {ring_num} (relative value)'
            table_input.addCommandInput(factor_input, row_index, 1)

            # Calculate crown arc chord and sagitta (not ring axial dimensions)
            # Get crown arc parameters for proper calculation
            crown_arc_radius_input = adsk.core.ValueCommandInput.cast(
                inputs.itemById('crown_arc_radius'))
            crown_arc_angle_input = adsk.core.ValueCommandInput.cast(
                inputs.itemById('crown_arc_angle'))

            if crown_arc_radius_input and crown_arc_angle_input:
                # Get crown arc parameters
                crown_radius_mm = crown_arc_radius_input.value  # Already in mm
                crown_angle_deg = crown_arc_angle_input.value   # In degrees

                # Calculate crown arc chord and sagitta using the crown_apex_from_theta function
                # Convert radius from mm to micrometers for the function
                crown_radius_um = crown_radius_mm * 1000.0

                # Calculate crown arc geometry
                calculated_sagitta_mm, calculated_chord_mm, calculated_arc_mm = crown_apex_from_theta(
                    crown_angle_deg, crown_radius_um)

                futil.log(
                    f'Crown arc calculation for ring {ring_num}: radius={crown_radius_mm:.3f}mm, angle={crown_angle_deg:.1f}°')
                futil.log(
                    f'  -> chord={calculated_chord_mm:.6f}mm, sagitta={calculated_sagitta_mm:.6f}mm')

                tooltip_info = f'Crown arc: R={crown_radius_mm:.3f}mm, θ={crown_angle_deg:.1f}°, chord={calculated_chord_mm:.6f}mm'
            else:
                # Fallback calculation if crown arc inputs not available
                crown_radius_mm = 0.2  # Default 200 micrometers
                crown_angle_deg = 72.0  # Default angle
                crown_radius_um = crown_radius_mm * 1000.0

                calculated_sagitta_mm, calculated_chord_mm, calculated_arc_mm = crown_apex_from_theta(
                    crown_angle_deg, crown_radius_um)

                tooltip_info = f'Crown arc (default): R={crown_radius_mm:.3f}mm, θ={crown_angle_deg:.1f}°'

            # Chord input - editable, use saved value if available, otherwise use calculated crown arc chord
            saved_chord = chord_values[ring_num - 1] if ring_num - \
                1 < len(chord_values) else calculated_chord_mm
            chord_input = inputs.addValueInput(
                f'height_ring_{ring_num}_chord', '', 'mm',
                adsk.core.ValueInput.createByString(f'{saved_chord} mm'))
            chord_input.tooltip = f'Crown arc chord length for ring {ring_num} (editable, in mm) - Calculated: {calculated_chord_mm:.6f}mm'
            table_input.addCommandInput(chord_input, row_index, 2)

            # Sagitta input - editable, use saved value if available, otherwise use calculated crown arc sagitta
            saved_sagitta = sagitta_values[ring_num - 1] if ring_num - \
                1 < len(sagitta_values) else calculated_sagitta_mm
            sagitta_input = inputs.addValueInput(
                f'height_ring_{ring_num}_sagitta', '', 'mm',
                adsk.core.ValueInput.createByString(f'{saved_sagitta} mm'))
            sagitta_input.tooltip = f'Crown arc sagitta for ring {ring_num} (editable, in mm) - Calculated: {calculated_sagitta_mm:.6f}mm from {tooltip_info}'
            table_input.addCommandInput(sagitta_input, row_index, 3)

    except Exception as e:
        app = adsk.core.Application.get()
        ui = app.userInterface
        if ui:
            ui.messageBox(f'Error updating height factors table: {str(e)}')


def update_sagitta_values_in_height_table(inputs):
    """Update the chord and sagitta values in the height factors table without rebuilding the entire table"""
    try:
        # Get required inputs
        num_rings_input = adsk.core.IntegerSpinnerCommandInput.cast(
            inputs.itemById('num_rings'))
        length_input = adsk.core.ValueCommandInput.cast(
            inputs.itemById('length'))
        gap_input = adsk.core.StringValueCommandInput.cast(
            inputs.itemById('gap_between_rings'))
        config_input = adsk.core.StringValueCommandInput.cast(
            inputs.itemById('height_factors'))
        sagitta_config_input = adsk.core.StringValueCommandInput.cast(
            inputs.itemById('sagitta_values'))

        if not all([num_rings_input, length_input]):
            return

        num_rings = num_rings_input.value

        # Get stent length (convert from cm to mm)
        stent_length_mm = length_input.value * 10.0  # cm to mm

        # Parse gap values to calculate available ring space
        gap_values = []
        if gap_input and gap_input.value:
            try:
                gap_values = [float(x.strip())
                              for x in gap_input.value.split(',')]
            except:
                pass

        # Ensure we have gap values
        num_gaps = max(1, num_rings - 1)
        while len(gap_values) < num_gaps:
            gap_values.append(gap_values[-1] if gap_values else 0.16)
        gap_values = gap_values[:num_gaps]

        total_gap_space = sum(gap_values) if num_gaps > 0 else 0.0
        available_ring_space = max(0.0, stent_length_mm - total_gap_space)

        # Parse current height factors
        height_factors = []
        if config_input and config_input.value:
            try:
                height_factors = [float(x.strip())
                                  for x in config_input.value.split(',')]
            except:
                pass

        # Ensure we have values for all rings
        while len(height_factors) < num_rings:
            height_factors.append(1.0)
        height_factors = height_factors[:num_rings]

        # Calculate scaling factor
        total_height_factors = sum(height_factors) if height_factors else 1.0
        ring_scale_factor = available_ring_space / \
            total_height_factors if total_height_factors > 0 else 1.0

        # Parse any user-provided sagitta values (mm)
        user_sagittas = []
        if sagitta_config_input and sagitta_config_input.value:
            try:
                user_sagittas = [float(x.strip())
                                 for x in sagitta_config_input.value.split(',')]
            except:
                user_sagittas = []

        # Update sagitta values for each ring
        for ring_num in range(1, num_rings + 1):
            try:
                # Get current height factor from table input
                factor_input = adsk.core.ValueCommandInput.cast(
                    inputs.itemById(f'height_ring_{ring_num}_factor'))
                if factor_input:
                    current_factor = factor_input.value
                else:
                    current_factor = height_factors[ring_num -
                                                    1] if ring_num - 1 < len(height_factors) else 1.0

                # Calculate actual ring height and sagitta
                scaled_ring_height_mm = current_factor * ring_scale_factor
                # Do not overwrite chord here; chord is user/paste-defined crown arc chord

                # If user provided sagitta for this ring, keep it and skip recalculation
                sagitta_input = adsk.core.ValueCommandInput.cast(
                    inputs.itemById(f'height_ring_{ring_num}_sagitta'))
                if ring_num - 1 < len(user_sagittas) and user_sagittas[ring_num - 1] > 0:
                    if sagitta_input:
                        try:
                            sagitta_input.expression = f"{user_sagittas[ring_num - 1]} mm"
                        except:
                            # cm fallback
                            sagitta_input.value = user_sagittas[ring_num - 1] / 10.0
                    continue

                # Get crown arc radius for proper sagitta calculation
                crown_arc_radius_input = adsk.core.ValueCommandInput.cast(
                    inputs.itemById('crown_arc_radius'))
                if crown_arc_radius_input:
                    # Check what units the crown arc radius actually uses
                    crown_radius_mm = crown_arc_radius_input.value  # Try without conversion first

                    # Calculate sagitta using geometric formula: sagitta = R - sqrt(R² - (chord/2)²)
                    # For a circular arc, chord = ring height, radius = crown arc radius
                    chord_mm = scaled_ring_height_mm
                    if crown_radius_mm > 0 and chord_mm > 0 and chord_mm <= 2 * crown_radius_mm:
                        # Valid geometric case
                        half_chord = chord_mm / 2.0
                        discriminant = crown_radius_mm * crown_radius_mm - half_chord * half_chord
                        if discriminant >= 0:
                            calculated_sagitta_mm = crown_radius_mm - \
                                math.sqrt(discriminant)
                        else:
                            # Fallback for invalid geometry
                            calculated_sagitta_mm = chord_mm / 8.0  # Approximate for shallow arcs
                    else:
                        # Fallback for invalid geometry
                        calculated_sagitta_mm = chord_mm / 8.0  # Approximate for shallow arcs
                    tooltip_info = f'Calculated sagitta for ring {ring_num}: {calculated_sagitta_mm:.6f} mm (geometric: R={crown_radius_mm:.3f}mm, chord={scaled_ring_height_mm:.3f}mm)'
                else:
                    # Fallback if crown arc radius not available
                    calculated_sagitta_mm = scaled_ring_height_mm / 8.0
                    tooltip_info = f'Calculated sagitta for ring {ring_num}: {calculated_sagitta_mm:.6f} mm (fallback: height/8)'

                # Update sagitta input (use expression with units to avoid cm/mm confusion)
                if sagitta_input:
                    try:
                        sagitta_input.expression = f'{calculated_sagitta_mm} mm'
                    except:
                        sagitta_input.value = calculated_sagitta_mm / 10.0  # cm fallback
                    sagitta_input.tooltip = f'Sagitta for ring {ring_num} (editable, in mm) - Default: {calculated_sagitta_mm:.6f}'

            except Exception as e:
                futil.log(
                    f'Error updating sagitta for ring {ring_num}: {str(e)}')

    except Exception as e:
        futil.log(f'Error updating sagitta values: {str(e)}')

    # Sync current table values back to hidden inputs for persistence
    try:
        config_h = adsk.core.StringValueCommandInput.cast(
            inputs.itemById('height_factors'))
        config_c = adsk.core.StringValueCommandInput.cast(
            inputs.itemById('chord_values'))
        config_s = adsk.core.StringValueCommandInput.cast(
            inputs.itemById('sagitta_values'))
        num_rings_input = adsk.core.IntegerSpinnerCommandInput.cast(
            inputs.itemById('num_rings'))
        if num_rings_input:
            n = num_rings_input.value
            factors, chords, sagittas = [], [], []
            for ring_num in range(1, n + 1):
                try:
                    f_in = adsk.core.ValueCommandInput.cast(
                        inputs.itemById(f'height_ring_{ring_num}_factor'))
                    c_in = adsk.core.ValueCommandInput.cast(
                        inputs.itemById(f'height_ring_{ring_num}_chord'))
                    s_in = adsk.core.ValueCommandInput.cast(
                        inputs.itemById(f'height_ring_{ring_num}_sagitta'))
                    if f_in:
                        factors.append(str(f_in.value))
                    if c_in:
                        chords.append(str(c_in.value * 10.0))  # cm -> mm
                    if s_in:
                        sagittas.append(str(s_in.value * 10.0))  # cm -> mm
                except:
                    pass
            if config_h and factors:
                config_h.value = ', '.join(factors)
            if config_c and chords:
                config_c.value = ', '.join(chords)
            if config_s and sagittas:
                config_s.value = ', '.join(sagittas)
    except:
        pass


def update_gap_config_table(inputs):
    """Update the gap configuration table with current stent parameters"""
    try:
        # Get required inputs
        num_rings_input = adsk.core.IntegerSpinnerCommandInput.cast(
            inputs.itemById('num_rings'))
        table_input = adsk.core.TableCommandInput.cast(
            inputs.itemById('gap_config_table'))
        config_input = adsk.core.StringValueCommandInput.cast(
            inputs.itemById('gap_between_rings'))

        if not all([num_rings_input, table_input]):
            return

        num_rings = num_rings_input.value
        num_gaps = max(1, num_rings - 1)  # At least 1 gap needed

        # Parse current configuration from text input
        gap_values = []
        if config_input and config_input.value:
            try:
                gap_values = [float(x.strip())
                              for x in config_input.value.split(',')]
            except:
                pass  # Ignore parsing errors

        # Ensure we have values for all gaps
        while len(gap_values) < num_gaps:
            gap_values.append(gap_values[-1] if gap_values else 0.14)
        gap_values = gap_values[:num_gaps]

        # Clear existing table contents
        table_input.clear()

        # Add table headers
        header_gap = inputs.addTextBoxCommandInput(
            'gap_header_gap', '', 'Gap Position', 1, True)
        header_value = inputs.addTextBoxCommandInput(
            'gap_header_value', '', 'Gap Value (mm)', 1, True)

        table_input.addCommandInput(header_gap, 0, 0)
        table_input.addCommandInput(header_value, 0, 1)

        # Add data rows for each gap
        for gap_num in range(1, num_gaps + 1):
            row_index = gap_num  # Row 0 is headers

            # Gap position (read-only)
            gap_label = inputs.addTextBoxCommandInput(
                f'gap_{gap_num}_label', '', f'Gap {gap_num} (Ring {gap_num} → {gap_num + 1})', 1, True)
            table_input.addCommandInput(gap_label, row_index, 0)

            # Gap value input - use createByString for proper unit handling
            default_gap = gap_values[gap_num -
                                     1] if gap_num - 1 < len(gap_values) else 0.14
            gap_input = inputs.addValueInput(f'gap_{gap_num}_value', '', 'mm',
                                             adsk.core.ValueInput.createByString(f'{default_gap} mm'))
            gap_input.tooltip = f'Gap width between ring {gap_num} and ring {gap_num + 1} in millimeters'
            table_input.addCommandInput(gap_input, row_index, 1)

    except Exception as e:

        app = adsk.core.Application.get()
        ui = app.userInterface
        if ui:
            ui.messageBox(f'Error updating gap config table: {str(e)}')


def update_fold_lock_table(inputs):
    """Update the fold-lock table with current stent parameters"""
    try:
        # Get required inputs
        num_rings_input = adsk.core.IntegerSpinnerCommandInput.cast(
            inputs.itemById('num_rings'))
        crowns_input = adsk.core.IntegerSpinnerCommandInput.cast(
            inputs.itemById('crowns_per_ring'))
        table_input = adsk.core.TableCommandInput.cast(
            inputs.itemById('per_ring_table'))
        config_input = adsk.core.StringValueCommandInput.cast(
            inputs.itemById('per_ring_fold_lock_config'))

        if not all([num_rings_input, crowns_input, table_input]):
            return

        num_rings = num_rings_input.value
        crowns_per_ring = crowns_input.value
        num_gaps = max(1, num_rings - 1)  # Number of gaps between rings

        # Show gaps 1-5 in the table (but limit to actual number of gaps)
        # This allows configuration of fold-lock for the first 5 gaps
        # Show up to 5 gaps, but not more than exist
        # Show all gaps in the table (same as Gap Configuration table)
        fold_lock_gaps = list(range(1, num_gaps + 1))

        # Parse current configuration from text input
        gap_data = {}
        if config_input and config_input.value:
            try:
                for config_part in config_input.value.split(';'):
                    if ':' in config_part:
                        parts = config_part.strip().split(':')
                        if len(parts) == 3:
                            gap_idx = int(parts[0].strip())
                            boxes_str = parts[1].strip()
                            gap_mm = float(parts[2].strip())
                            gap_data[gap_idx] = {
                                'boxes': boxes_str, 'gap_mm': gap_mm}
            except:
                pass  # Ignore parsing errors

        # Clear existing table contents
        table_input.clear()

        # Add table headers
        header_gap = inputs.addTextBoxCommandInput(
            'fold_lock_header_gap', '', 'Gap', 1, True)
        header_enable = inputs.addTextBoxCommandInput(
            'fold_lock_header_enable', '', 'Enable', 1, True)
        header_boxes = inputs.addTextBoxCommandInput(
            'fold_lock_header_boxes', '', 'Crown Boxes', 1, True)
        header_gap_mm = inputs.addTextBoxCommandInput(
            'fold_lock_header_gap_mm', '', 'Gap (mm)', 1, True)

        table_input.addCommandInput(header_gap, 0, 0)
        table_input.addCommandInput(header_enable, 0, 1)
        table_input.addCommandInput(header_boxes, 0, 2)
        table_input.addCommandInput(header_gap_mm, 0, 3)

        # Add data rows for each end gap only
        for idx, gap_num in enumerate(fold_lock_gaps):
            row_index = idx + 1  # Row 0 is headers

            # Gap position (read-only)
            gap_label = inputs.addTextBoxCommandInput(
                f'table_gap_{gap_num}_label', '', f'Gap {gap_num} (Ring {gap_num} → {gap_num + 1})', 1, True)
            table_input.addCommandInput(gap_label, row_index, 0)

            # Enable checkbox
            is_enabled = gap_num in gap_data
            enable_checkbox = inputs.addBoolValueInput(
                f'table_gap_{gap_num}_enable', '', True, '', is_enabled)
            enable_checkbox.tooltip = f'Enable fold-lock for gap {gap_num}'
            table_input.addCommandInput(enable_checkbox, row_index, 1)

            # Crown boxes input
            default_boxes = gap_data.get(gap_num, {}).get('boxes', '0,2,4,6')
            boxes_input = inputs.addStringValueInput(
                f'table_gap_{gap_num}_boxes', '', default_boxes)
            boxes_input.tooltip = f'Comma-separated crown box indices (0-{crowns_per_ring-1})'
            table_input.addCommandInput(boxes_input, row_index, 2)

            # Gap input - use createByString for proper unit handling
            default_gap = gap_data.get(gap_num, {}).get('gap_mm', 0.095)
            gap_input = inputs.addValueInput(f'table_gap_{gap_num}_gap', '', 'mm',
                                             adsk.core.ValueInput.createByString(f'{default_gap} mm'))
            gap_input.tooltip = 'Fold-lock gap width in millimeters'
            table_input.addCommandInput(gap_input, row_index, 3)

    except Exception as e:
        app = adsk.core.Application.get()
        ui = app.userInterface
        if ui:
            ui.messageBox(f'Error updating fold-lock table: {str(e)}')


def update_height_factors_from_table(inputs):
    """Update the hidden height factors text input from table data"""
    try:
        config_input = adsk.core.StringValueCommandInput.cast(
            inputs.itemById('height_factors'))
        num_rings_input = adsk.core.IntegerSpinnerCommandInput.cast(
            inputs.itemById('num_rings'))

        if config_input and num_rings_input:
            # Collect current table data and update text configuration
            height_factors = []
            num_rings = num_rings_input.value

            for ring_num in range(1, num_rings + 1):
                try:
                    factor_input = adsk.core.ValueCommandInput.cast(
                        inputs.itemById(f'height_ring_{ring_num}_factor'))
                    if factor_input:
                        height_factors.append(str(factor_input.value))
                except:
                    height_factors.append('1.0')  # Default value

            # Update the text configuration
            config_input.value = ', '.join(height_factors)

            # Update sagitta values since height factors changed
            update_sagitta_values_in_height_table(inputs)

    except Exception as e:
        app = adsk.core.Application.get()
        ui = app.userInterface
        if ui:
            ui.messageBox(
                f'Error updating height factors from table: {str(e)}')


def update_gap_config_from_table(inputs):
    """Update the hidden gap configuration text input from table data"""
    try:
        config_input = adsk.core.StringValueCommandInput.cast(
            inputs.itemById('gap_between_rings'))
        num_rings_input = adsk.core.IntegerSpinnerCommandInput.cast(
            inputs.itemById('num_rings'))

        if config_input and num_rings_input:
            # Collect current table data and update text configuration
            gap_values = []
            num_rings = num_rings_input.value
            num_gaps = max(1, num_rings - 1)

            for gap_num in range(1, num_gaps + 1):
                try:
                    gap_input = adsk.core.ValueCommandInput.cast(
                        inputs.itemById(f'gap_{gap_num}_value'))
                    if gap_input:
                        # Convert cm to mm (Fusion returns values in cm)
                        gap_values.append(str(gap_input.value * 10))
                except:
                    gap_values.append('0.14')  # Default value in mm

            # Update the text configuration
            config_input.value = ', '.join(gap_values)

    except Exception as e:
        app = adsk.core.Application.get()
        ui = app.userInterface
        if ui:
            ui.messageBox(f'Error updating gap config from table: {str(e)}')


def update_fold_lock_config_from_table(inputs):
    """Update the hidden fold-lock configuration text input from table data"""
    try:
        config_input = adsk.core.StringValueCommandInput.cast(
            inputs.itemById('per_ring_fold_lock_config'))
        num_rings_input = adsk.core.IntegerSpinnerCommandInput.cast(
            inputs.itemById('num_rings'))

        if config_input and num_rings_input:
            # Collect current table data and update text configuration
            config_parts = []
            num_rings = num_rings_input.value
            num_gaps = max(1, num_rings - 1)  # Number of gaps between rings

            # Collect data from all gaps (same as Gap Configuration table)
            fold_lock_gaps = list(range(1, num_gaps + 1))

            for gap_num in fold_lock_gaps:
                try:
                    enable_input = adsk.core.BoolValueCommandInput.cast(
                        inputs.itemById(f'table_gap_{gap_num}_enable'))
                    boxes_input = adsk.core.StringValueCommandInput.cast(
                        inputs.itemById(f'table_gap_{gap_num}_boxes'))
                    gap_input = adsk.core.ValueCommandInput.cast(
                        inputs.itemById(f'table_gap_{gap_num}_gap'))

                    if enable_input and enable_input.value and boxes_input and gap_input:
                        boxes_str = boxes_input.value.strip()
                        # Convert cm to mm (Fusion returns values in cm)
                        gap_mm = gap_input.value * 10

                        if boxes_str and gap_mm > 0:
                            config_parts.append(
                                f'{gap_num}:{boxes_str}:{gap_mm:.3f}')
                except:
                    pass  # Skip invalid entries

            # Update the text configuration
            config_input.value = ';'.join(config_parts)

    except Exception as e:
        app = adsk.core.Application.get()
        ui = app.userInterface
        if ui:
            ui.messageBox(
                f'Error updating fold-lock config from table: {str(e)}')


def update_per_ring_config_from_table(inputs):
    """Update the hidden per-ring fold-lock configuration text input from table data"""
    # Delegate to the new cleaner function
    update_fold_lock_config_from_table(inputs)


def update_crown_arc_calculations(inputs):
    """Update crown arc calculations based on user-input radius, height, or theta"""
    try:
        # Add debug logging
        futil.log('Crown arc calculations updating...')

        # Get user inputs
        radius_input = adsk.core.ValueCommandInput.cast(
            inputs.itemById('crown_arc_radius'))
        height_input = adsk.core.ValueCommandInput.cast(
            inputs.itemById('crown_arc_height'))
        theta_input = adsk.core.ValueCommandInput.cast(
            inputs.itemById('crown_arc_theta'))

        if not radius_input or not height_input or not theta_input:
            futil.log('Crown arc inputs not found')
            return

        # Debug: show the raw values from inputs
        futil.log(f'DEBUG: radius_input.value = {radius_input.value}')
        futil.log(
            f'DEBUG: radius_input.expression = {radius_input.expression}')
        futil.log(f'DEBUG: height_input.value = {height_input.value}')
        futil.log(f'DEBUG: theta_input.value = {theta_input.value}')

        # Test both conversion approaches to see which is correct
        # This is in cm (Fusion's internal units)
        radius_raw = radius_input.value
        height_raw = height_input.value  # This is in cm
        # This is in radians (Fusion's internal units)
        theta_raw = theta_input.value

        # Correct unit conversions:
        # - Fusion returns radius in cm, we need mm
        # - Fusion returns theta in radians, we need degrees
        radius_mm = radius_raw * 10.0           # Convert cm to mm
        height_mm = height_raw * 10.0           # Convert cm to mm
        theta_deg = math.degrees(theta_raw)     # Convert radians to degrees
        radius_um = radius_mm * 1000.0          # Convert mm to µm

        futil.log(f'Corrected conversions:')
        futil.log(
            f'Radius: {radius_raw:.6f}cm -> {radius_mm:.6f}mm = {radius_um:.1f}µm')
        futil.log(f'Theta: {theta_raw:.6f}rad -> {theta_deg:.1f}°')

        # Always use theta-based calculation from user input
        futil.log('Using theta-based calculation from user input')

        if theta_deg <= 0 or theta_deg > 180:
            futil.log(f'Crown arc: Invalid theta value: {theta_deg}')
            return

        if radius_mm <= 0:
            futil.log(f'Crown arc: Invalid radius value: {radius_mm}')
            return

        futil.log(
            f'About to call crown_apex_from_theta({theta_deg}, {radius_um})')
        # Calculate sagitta, chord, and arc from theta and radius
        sagitta_calculated, chord_calculated, arc_calculated = crown_apex_from_theta(
            theta_deg, radius_um)
        futil.log(
            f'crown_apex_from_theta returned: sagitta={sagitta_calculated:.6f}, chord={chord_calculated:.6f}, arc={arc_calculated:.6f}')

        # The sagitta is the actual crown arc height from the chord to the apex
        # For symmetric rings, the ring height H would be 2*sagitta, but here we show the actual sagitta
        # This updates the height field for ring calculations
        calculated_height = 2.0 * sagitta_calculated

        # Use calculated values
        sagitta_mm = sagitta_calculated
        chord_mm = chord_calculated
        arc_length_mm = arc_calculated
        height_mm = calculated_height

        # Calculate remaining parameters
        curvature = crown_arc_curvature_from_Rc(radius_um)

        # Rule-of-thumb calculations (assume typical strut width of 75 µm)
        typical_strut_width_um = 75.0
        r_over_w = crown_arc_radius_to_width_ratio(
            radius_um, typical_strut_width_um)
        geom_index = crown_arc_geometric_index_w_over_Rc(
            typical_strut_width_um, radius_um)

        # Log verification
        futil.log(
            f'Final values: θ={theta_deg:.2f}°, h={sagitta_mm:.4f}mm, chord={chord_mm:.4f}mm, arc={arc_length_mm:.4f}mm')

        # Update the calculated outputs
        futil.log('Looking for output fields...')
        sagitta_output = adsk.core.StringValueCommandInput.cast(
            inputs.itemById('calculated_sagitta'))
        futil.log(f'sagitta_output found: {sagitta_output is not None}')
        chord_output = adsk.core.StringValueCommandInput.cast(
            inputs.itemById('calculated_chord'))
        futil.log(f'chord_output found: {chord_output is not None}')
        arc_length_output = adsk.core.StringValueCommandInput.cast(
            inputs.itemById('calculated_arc_length'))
        futil.log(f'arc_length_output found: {arc_length_output is not None}')
        curvature_output = adsk.core.StringValueCommandInput.cast(
            inputs.itemById('calculated_curvature'))
        futil.log(f'curvature_output found: {curvature_output is not None}')
        r_over_w_output = adsk.core.StringValueCommandInput.cast(
            inputs.itemById('calculated_r_over_w'))
        futil.log(f'r_over_w_output found: {r_over_w_output is not None}')
        geom_index_output = adsk.core.StringValueCommandInput.cast(
            inputs.itemById('calculated_geom_index'))
        futil.log(f'geom_index_output found: {geom_index_output is not None}')

        if sagitta_output:
            futil.log(f'Setting sagitta_output.value to: {sagitta_mm:.3f} mm')
            sagitta_output.value = f"{sagitta_mm:.3f} mm"
        else:
            futil.log('sagitta_output is None - cannot update!')
        if chord_output:
            futil.log(f'Setting chord_output.value to: {chord_mm:.3f} mm')
            chord_output.value = f"{chord_mm:.3f} mm"
        if arc_length_output:
            futil.log(
                f'Setting arc_length_output.value to: {arc_length_mm:.3f} mm')
            arc_length_output.value = f"{arc_length_mm:.3f} mm"
        if curvature_output:
            futil.log(
                f'Setting curvature_output.value to: {curvature:.3f} mm⁻¹')
            curvature_output.value = f"{curvature:.3f} mm⁻¹"
        if r_over_w_output:
            futil.log(
                f'Setting r_over_w_output.value to: {r_over_w:.1f} (75µm strut)')
            r_over_w_output.value = f"{r_over_w:.1f} (75µm strut)"
        if geom_index_output:
            futil.log(
                f'Setting geom_index_output.value to: {geom_index:.4f} (75µm strut)')
            geom_index_output.value = f"{geom_index:.4f} (75µm strut)"

        futil.log('Crown arc calculations completed successfully')

    except Exception as e:
        futil.log(f'Crown arc calculation exception: {str(e)}')
        app = adsk.core.Application.get()
        ui = app.userInterface
        if ui:
            ui.messageBox(
                f'Error updating crown arc calculations: {str(e)}')


def calculate_average_ring_height(inputs):
    """Calculate average ring height from form's height factors and ring count"""
    try:
        # Get number of rings to know how many height factors to consider
        num_rings_input = adsk.core.IntegerSpinnerCommandInput.cast(
            inputs.itemById('num_rings'))
        length_input = adsk.core.ValueCommandInput.cast(
            inputs.itemById('length'))

        if not num_rings_input or not length_input:
            return 0.5  # Default if can't determine

        num_rings = num_rings_input.value
        # Convert cm to mm (Fusion returns values in cm)
        total_length_mm = length_input.value * 10

        # Get height factors from the table inputs
        height_factors = []
        for ring_num in range(1, num_rings + 1):
            factor_input = adsk.core.ValueCommandInput.cast(
                inputs.itemById(f'height_ring_{ring_num}_factor'))
            if factor_input and factor_input.value > 0:
                height_factors.append(factor_input.value)
            else:
                height_factors.append(1.0)  # Default factor

        # Calculate total proportion and individual ring heights
        if height_factors:
            total_proportion = sum(height_factors)
            # Calculate average ring height considering proportions
            # Each ring gets: (its_factor / total_factors) * total_length
            individual_heights = [(factor / total_proportion) * total_length_mm
                                  for factor in height_factors]
            average_height = sum(individual_heights) / len(individual_heights)
            return average_height
        else:
            # Fallback: equal distribution
            return total_length_mm / num_rings if num_rings > 0 else 0.5

    except Exception:
        return 0.5  # Default fallback


def update_crown_arc_suggestions(inputs):
    """Initialize crown arc radius suggestion based on stent geometry"""
    try:
        # Get current diameter and crowns per ring for initial suggestion
        diameter_input = adsk.core.ValueCommandInput.cast(
            inputs.itemById('diameter'))
        crowns_input = adsk.core.IntegerSpinnerCommandInput.cast(
            inputs.itemById('crowns_per_ring'))

        if not diameter_input or not crowns_input:
            return

        # Convert cm to mm (Fusion returns values in cm)
        diameter_mm = diameter_input.value * 10
        crowns_per_ring = crowns_input.value

        # Calculate average ring height from form data
        average_ring_height = calculate_average_ring_height(inputs)

        # Get design examples for reference
        examples = calculate_design_examples()

        # Calculate suggested radius based on crown spacing
        circumference_mm = math.pi * diameter_mm
        crown_spacing_mm = circumference_mm / crowns_per_ring

        # Use design examples to inform suggestion
        # For typical stent: aim for theta between 60-90°
        target_theta = 72.0  # Body crown example
        target_radius_um = 200.0  # Body crown example

        # Scale the radius based on crown spacing
        # If crown spacing is larger, use larger radius for similar curvature
        reference_spacing = 0.7  # mm (reference crown spacing)
        radius_scale_factor = crown_spacing_mm / reference_spacing
        suggested_radius_um = target_radius_um * radius_scale_factor
        suggested_radius_mm = suggested_radius_um / 1000.0

        # Alternative calculation using sagitta approach
        # Calculate what sagitta would give us for target theta
        suggested_sagitta_mm = sagitta_from_theta(
            target_theta, suggested_radius_um)

        # Log the suggestions with examples
        futil.log(f'Crown arc suggestions:')
        futil.log(
            f'  Diameter: {diameter_mm:.2f}mm, Crowns: {crowns_per_ring}')
        futil.log(f'  Crown spacing: {crown_spacing_mm:.3f}mm')
        futil.log(
            f'  Suggested radius: {suggested_radius_mm:.3f}mm ({suggested_radius_um:.0f}µm)')
        futil.log(f'  Target theta: {target_theta:.1f}°')
        futil.log(f'  Calculated sagitta: {suggested_sagitta_mm:.4f}mm')

        for example in examples:
            futil.log(
                f'  Example: {example["name"]} -> h={example["sagitta_mm"]:.4f}mm')

        # Update the radius input with the suggestion (only if it's still at default)
        radius_input = adsk.core.ValueCommandInput.cast(
            inputs.itemById('crown_arc_radius'))
        if radius_input and radius_input.value <= 0.5:  # Only update if still at default
            radius_input.value = suggested_radius_mm

        # Update crown arc height with calculated average ring height (only if at default)
        height_input = adsk.core.ValueCommandInput.cast(
            inputs.itemById('crown_arc_height'))
        if height_input and height_input.value <= 0.1:  # Only update if still at default
            height_input.value = average_ring_height

        # Update theta input with target theta (only if at default)
        theta_input = adsk.core.ValueCommandInput.cast(
            inputs.itemById('crown_arc_theta'))
        # Only update if still at default
        if theta_input and (theta_input.value <= 1.0 or theta_input.value == 72.0):
            theta_input.value = target_theta

        # Trigger calculation update
        update_crown_arc_calculations(inputs)

    except Exception as e:
        app = adsk.core.Application.get()
        ui = app.userInterface
        if ui:
            ui.messageBox(
                f'Error updating crown arc suggestions: {str(e)}')


# This event handler is called when the user interacts with any of the inputs in the dialog
# which allows you to verify that all of the inputs are valid and enables the OK button.
def command_validate_input(args: adsk.core.ValidateInputsEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Validate Input Event')

    inputs = args.inputs

    # Verify the validity of the input values. This controls if the OK button is enabled or not.
    diameter_input = adsk.core.ValueCommandInput.cast(
        inputs.itemById('diameter'))
    length_input = adsk.core.ValueCommandInput.cast(inputs.itemById('length'))
    num_rings_input = adsk.core.IntegerSpinnerCommandInput.cast(
        inputs.itemById('num_rings'))

    # Validate balloon material if present
    material_input = adsk.core.RadioButtonGroupCommandInput.cast(
        inputs.itemById('balloon_material'))
    material_valid = True
    if material_input:
        # Radio button groups always have a valid selection, so always valid
        material_valid = True

    # Basic validation
    if (diameter_input and length_input and num_rings_input and
            diameter_input.value > 0 and length_input.value > 0 and num_rings_input.value > 0 and
            material_valid):
        args.areInputsValid = True
    else:
        args.areInputsValid = False


def draw_stent_frame(diameter_mm, length_mm, num_rings, crowns_per_ring,
                     height_factors, gap_values, draw_border, draw_gap_centerlines, gap_centerlines_interior_only,
                     draw_crown_peaks, draw_crown_waves, draw_crown_midlines, draw_crown_h_midlines, draw_crown_chord_lines,
                     partial_crown_midlines, draw_crown_mids, partial_crown_mids, create_coincident_points,
                     draw_fold_lock_limits, fold_lock_columns, per_ring_fold_lock_config,
                     balloon_wall_um, chord_values=None, sagitta_values=None):
    """Draw stent frame based on parameters using optimized calculations"""
    import math

    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox(
                "Please create a new design or open an existing one before running this command.", "No Design Active")
            return

        root = design.rootComponent
        sk = root.sketches.add(root.xYConstructionPlane)
        waves_per_ring = max(1, crowns_per_ring // 2)
        sk.name = f'Stent Frame - {num_rings} rings, {waves_per_ring} waves ({crowns_per_ring} crowns)'

        # Convert mm to cm for Fusion API
        def mm_to_cm(x):
            return x * 0.1

        # Calculate width from diameter (circumference)
        width_mm = diameter_mm * math.pi

        # Use height factors as proportional values (no base height needed)
        ring_heights = height_factors  # Direct proportions

        # Calculate with variable gap values and total length of length_mm
        num_gaps = num_rings - 1
        # Sum of actual gap values
        total_gap_space = sum(gap_values[:num_gaps])
        available_ring_space = length_mm - total_gap_space

        # Scale ring heights to fit the available space
        original_total_ring_height = sum(ring_heights)
        ring_scale_factor = available_ring_space / original_total_ring_height
        scaled_ring_heights = [h * ring_scale_factor for h in ring_heights]

        # Calculate ring positions using variable gap values
        ring_centers = []
        # Start with half of first ring height
        current_y = scaled_ring_heights[0] / 2
        ring_centers.append(current_y)

        for i in range(1, num_rings):
            # Add half of previous ring + specific gap + half of current ring
            gap_value = gap_values[i-1] if i - \
                1 < len(gap_values) else gap_values[-1]
            current_y += scaled_ring_heights[i-1] / \
                2 + gap_value + scaled_ring_heights[i]/2
            ring_centers.append(current_y)

        # Calculate ring boundaries (crown start and end positions)
        ring_start_lines = []  # Top of each ring
        ring_end_lines = []    # Bottom of each ring

        for i, center in enumerate(ring_centers):
            ring_start = center - scaled_ring_heights[i]/2
            ring_end = center + scaled_ring_heights[i]/2
            ring_start_lines.append(ring_start)
            ring_end_lines.append(ring_end)

        # Calculate gap center positions (including first and last gaps)
        gap_centers = []

        # First gap: from Y=0 to start of first ring
        first_gap_center = (0.0 + ring_start_lines[0]) / 2
        gap_centers.append(first_gap_center)

        # Middle gaps: between ring end and next ring start
        for i in range(num_rings - 1):
            gap_center_y = (ring_end_lines[i] + ring_start_lines[i+1]) / 2
            gap_centers.append(gap_center_y)

        # Last gap: from end of last ring to total length
        last_gap_center = (ring_end_lines[-1] + length_mm) / 2
        gap_centers.append(last_gap_center)

        # Use the specified length as total length
        total_length = length_mm

        lines = sk.sketchCurves.sketchLines

        # Draw border
        if draw_border:
            # Left border
            line = lines.addByTwoPoints(
                adsk.core.Point3D.create(mm_to_cm(0.0), mm_to_cm(0.0), 0),
                adsk.core.Point3D.create(
                    mm_to_cm(0.0), mm_to_cm(total_length), 0)
            )
            line.isConstruction = True

            # Right border
            line = lines.addByTwoPoints(
                adsk.core.Point3D.create(mm_to_cm(width_mm), mm_to_cm(0.0), 0),
                adsk.core.Point3D.create(
                    mm_to_cm(width_mm), mm_to_cm(total_length), 0)
            )
            line.isConstruction = True

            # Top border
            line = lines.addByTwoPoints(
                adsk.core.Point3D.create(
                    mm_to_cm(0.0), mm_to_cm(total_length), 0),
                adsk.core.Point3D.create(
                    mm_to_cm(width_mm), mm_to_cm(total_length), 0)
            )
            line.isConstruction = True

            # Bottom border
            line = lines.addByTwoPoints(
                adsk.core.Point3D.create(mm_to_cm(0.0), mm_to_cm(0.0), 0),
                adsk.core.Point3D.create(mm_to_cm(width_mm), mm_to_cm(0.0), 0)
            )
            line.isConstruction = True

        # Draw ring start lines (crown tops) - only if inside the box
        if draw_crown_peaks:
            for ring_start in ring_start_lines:
                if 0 < ring_start < total_length:  # Only draw if inside the box
                    line = lines.addByTwoPoints(
                        adsk.core.Point3D.create(
                            mm_to_cm(0.0), mm_to_cm(ring_start), 0),
                        adsk.core.Point3D.create(
                            mm_to_cm(width_mm), mm_to_cm(ring_start), 0)
                    )
                    line.isConstruction = True

        # Draw ring end lines (crown bottoms) - only if inside the box
        if draw_crown_peaks:
            for ring_end in ring_end_lines:
                if 0 < ring_end < total_length:  # Only draw if inside the box
                    line = lines.addByTwoPoints(
                        adsk.core.Point3D.create(
                            mm_to_cm(0.0), mm_to_cm(ring_end), 0),
                        adsk.core.Point3D.create(
                            mm_to_cm(width_mm), mm_to_cm(ring_end), 0)
                    )
                    line.isConstruction = True

        # Draw gap center lines
        if draw_gap_centerlines and num_rings > 1:
            if gap_centerlines_interior_only and num_rings > 2:
                # Only draw interior gap lines (skip first and last gaps)
                # Skip gap_centers[0] (before first ring) and gap_centers[-1] (after last ring)
                interior_gap_centers = gap_centers[1:-
                                                   1] if len(gap_centers) > 2 else []
                for gap_center in interior_gap_centers:
                    line = lines.addByTwoPoints(
                        adsk.core.Point3D.create(
                            mm_to_cm(0.0), mm_to_cm(gap_center), 0),
                        adsk.core.Point3D.create(
                            mm_to_cm(width_mm), mm_to_cm(gap_center), 0)
                    )
                    line.isConstruction = True
            else:
                # Draw ALL gap lines (including first and last gaps)
                for gap_center in gap_centers:
                    line = lines.addByTwoPoints(
                        adsk.core.Point3D.create(
                            mm_to_cm(0.0), mm_to_cm(gap_center), 0),
                        adsk.core.Point3D.create(
                            mm_to_cm(width_mm), mm_to_cm(gap_center), 0)
                    )
                    line.isConstruction = True

        # Draw wave lines (vertical divisions at wave boundaries)
        if draw_crown_waves:
            waves = max(1, crowns_per_ring // 2)
            wave_spacing = width_mm / waves
            # Draw lines for each wave boundary (not at edges)
            for i in range(1, waves):
                x = i * wave_spacing
                line = lines.addByTwoPoints(
                    adsk.core.Point3D.create(mm_to_cm(x), mm_to_cm(0.0), 0),
                    adsk.core.Point3D.create(
                        mm_to_cm(x), mm_to_cm(total_length), 0)
                )
                line.isConstruction = True

        # Draw wave midlines (vertical lines at midpoint within each wave)
        if draw_crown_midlines or partial_crown_midlines > 0:
            waves = max(1, crowns_per_ring // 2)
            wave_spacing = width_mm / waves
            # Determine how many crowns to draw midlines for
            if partial_crown_midlines > 0:
                # Use partial count (limited from left)
                midlines_count = min(partial_crown_midlines, waves)
            else:
                # Use full count if partial is 0 and main option is enabled
                midlines_count = waves if draw_crown_midlines else 0

            # Draw midlines for the specified number of crowns from left
            for i in range(midlines_count):
                # Midline at the center of each crown section
                x = i * wave_spacing + wave_spacing / 2

                line = lines.addByTwoPoints(
                    adsk.core.Point3D.create(mm_to_cm(x), mm_to_cm(0.0), 0),
                    adsk.core.Point3D.create(
                        mm_to_cm(x), mm_to_cm(total_length), 0)
                )
                line.isConstruction = True

        # Draw crown horizontal midlines (horizontal lines at midpoint of each ring height)
        if draw_crown_h_midlines:
            # Draw horizontal midlines at each ring center
            for center in ring_centers:
                line = lines.addByTwoPoints(
                    adsk.core.Point3D.create(
                        mm_to_cm(0.0), mm_to_cm(center), 0),
                    adsk.core.Point3D.create(
                        mm_to_cm(width_mm), mm_to_cm(center), 0)
                )
                line.isConstruction = True

        # Removed drawing sagitta guide lines. Chord lines will indicate sagitta positions instead.

        # Draw crown chord lines positioned at sagitta distance from crown tips
        if draw_crown_chord_lines:
            crown_spacing = width_mm / crowns_per_ring

            # Precompute sagitta per ring (from table or fallback geometry)
            ring_sagittas = []
            for i in range(num_rings):
                ring_height = scaled_ring_heights[i]
                if sagitta_values and i < len(sagitta_values):
                    s_val = sagitta_values[i]
                    print(
                        f"Ring {i+1}: Using user-defined sagitta={s_val:.3f}mm")
                else:
                    crown_arc_radius_mm = 0.2  # Default crown arc radius
                    if crown_arc_radius_mm > 0 and ring_height > 0 and ring_height <= 2 * crown_arc_radius_mm:
                        half_chord = ring_height / 2.0
                        discriminant = crown_arc_radius_mm * crown_arc_radius_mm - half_chord * half_chord
                        if discriminant >= 0:
                            s_val = crown_arc_radius_mm - \
                                math.sqrt(discriminant)
                        else:
                            s_val = ring_height / 16.4
                    else:
                        s_val = ring_height / 16.4
                    print(
                        f"Ring {i+1}: Using calculated sagitta={s_val:.3f}mm")
                ring_sagittas.append(s_val)

            # Draw chord lines for each ring
            for i in range(num_rings):
                ring_height = scaled_ring_heights[i]
                ring_center = ring_centers[i]

                # Use user-provided chord value if available, otherwise calculate
                if chord_values and i < len(chord_values):
                    # Use user-edited chord value from table
                    chord_mm = chord_values[i]
                    print(
                        f"Ring {i+1}: Using user-defined chord={chord_mm:.3f}mm")
                else:
                    # Fallback: calculate chord using crown arc parameters
                    crown_arc_radius_mm = 0.2  # Default crown arc radius
                    crown_angle_deg = 72.0  # Default crown angle
                    crown_radius_um = crown_arc_radius_mm * 1000.0
                    sagitta_calc, chord_calc, arc_calc = crown_apex_from_theta(
                        crown_angle_deg, crown_radius_um)
                    chord_mm = chord_calc
                    print(
                        f"Ring {i+1}: Using calculated chord={chord_mm:.3f}mm")

                # Draw chord lines for each crown in this ring
                for crown_index in range(crowns_per_ring):
                    # Calculate crown center position
                    crown_center_x = (crown_index + 0.5) * crown_spacing

                    # Calculate chord start and end positions (centered on crown)
                    chord_half_length = chord_mm / 2.0
                    chord_start_x = crown_center_x - chord_half_length
                    chord_end_x = crown_center_x + chord_half_length

                    # Place a single chord per crown:
                    # - First half of crowns are 'up' (near top tip)
                    # - Second half are 'down' (near bottom tip)
                    # - Alternate the pattern per ring index so adjacent rings are opposite
                    sagitta_mm = ring_sagittas[i]
                    chord_y_top = ring_center + ring_height/2 - sagitta_mm
                    chord_y_bottom = ring_center - ring_height/2 + sagitta_mm

                    # Orientation per wave: within each wave (2 crowns), first crown up, second down; flip per ring
                    wave_index = crown_index // 2
                    is_first_in_wave = (crown_index % 2 == 0)
                    # even rings: first in wave up; odd: first in wave down
                    up_first = (i % 2 == 0)
                    is_up = is_first_in_wave if up_first else (
                        not is_first_in_wave)
                    chord_y = chord_y_top if is_up else chord_y_bottom
                    orientation = 'up' if is_up else 'down'

                    print(
                        f"  Crown {crown_index+1} ({orientation}): chord x={chord_start_x:.3f}-{chord_end_x:.3f} at y={chord_y:.3f}mm")
                    line = lines.addByTwoPoints(
                        adsk.core.Point3D.create(
                            mm_to_cm(chord_start_x), mm_to_cm(chord_y), 0),
                        adsk.core.Point3D.create(
                            mm_to_cm(chord_end_x), mm_to_cm(chord_y), 0)
                    )
                    line.isConstruction = True

        # Draw crown mid lines (vertical lines at center of each crown - wave quarter lines)
        if draw_crown_mids or partial_crown_mids > 0:
            crown_spacing = width_mm / crowns_per_ring
            # Determine how many crowns to draw mid lines for
            if partial_crown_mids > 0:
                # Use partial count (limited from left)
                mids_count = min(partial_crown_mids, crowns_per_ring)
            else:
                # Use full count if partial is 0 and main option is enabled
                mids_count = crowns_per_ring if draw_crown_mids else 0

            # Draw mid lines for the specified number of crowns from left
            for i in range(mids_count):
                # Mid line at center position (wave quarter line)
                x_mid = i * crown_spacing + crown_spacing / 2
                line = lines.addByTwoPoints(
                    adsk.core.Point3D.create(
                        mm_to_cm(x_mid), mm_to_cm(0.0), 0),
                    adsk.core.Point3D.create(
                        mm_to_cm(x_mid), mm_to_cm(total_length), 0)
                )
                line.isConstruction = True

        # Draw fold-lock limit lines in specified crown boxes
        if draw_fold_lock_limits:
            crown_spacing = width_mm / crowns_per_ring

            # Always use per-ring configuration
            try:
                # Parse per-ring configuration: "ring:boxes:gap_mm;ring:boxes:gap_mm"
                ring_configs = {}
                for config_part in per_ring_fold_lock_config.split(';'):
                    if ':' in config_part:
                        parts = config_part.strip().split(':')
                        if len(parts) == 3:
                            # Convert to 0-based
                            ring_idx = int(parts[0].strip()) - 1
                            boxes_str = parts[1].strip()
                            # Now in mm, not fraction
                            gap_width_mm = float(parts[2].strip())
                            box_indices = [int(x.strip()) for x in boxes_str.split(
                                ',') if x.strip().isdigit()]
                            ring_configs[ring_idx] = {
                                'boxes': box_indices, 'gap_mm': gap_width_mm}

                # Draw fold-lock lines for each configured ring/gap
                for gap_idx, gap_center_y in enumerate(gap_centers):
                    if gap_idx in ring_configs:
                        config = ring_configs[gap_idx]
                        fold_lock_indices = config['boxes']
                        # Gap width in mm
                        fold_lock_gap_mm = config['gap_mm']

                        # Use half the gap width for vertical offset
                        line_offset = fold_lock_gap_mm / 2

                        # Draw lines for specified crown boxes
                        for crown_idx in fold_lock_indices:
                            if 0 <= crown_idx < crowns_per_ring:
                                # Calculate crown box boundaries
                                crown_left = crown_idx * crown_spacing
                                crown_right = (
                                    crown_idx + 1) * crown_spacing

                                # Draw horizontal fold-lock limit line ABOVE gap center
                                line = lines.addByTwoPoints(
                                    adsk.core.Point3D.create(
                                        mm_to_cm(crown_left), mm_to_cm(gap_center_y - line_offset), 0),
                                    adsk.core.Point3D.create(
                                        mm_to_cm(crown_right), mm_to_cm(gap_center_y - line_offset), 0)
                                )
                                line.isConstruction = True

                                # Draw horizontal fold-lock limit line BELOW gap center
                                line = lines.addByTwoPoints(
                                    adsk.core.Point3D.create(
                                        mm_to_cm(crown_left), mm_to_cm(gap_center_y + line_offset), 0),
                                    adsk.core.Point3D.create(
                                        mm_to_cm(crown_right), mm_to_cm(gap_center_y + line_offset), 0)
                                )
                                line.isConstruction = True

            except (ValueError, IndexError):
                # If per-ring config is invalid, don't draw fold-lock lines
                pass

        # Show summary
        if ui:
            # Count the lines that were actually drawn
            lines_inside_box = len([r for r in ring_start_lines if 0 < r < total_length]) + \
                len([r for r in ring_end_lines if 0 < r < total_length]) + \
                len(gap_centers)

            # Count wave boundary lines and midlines
            waves = max(1, crowns_per_ring // 2)
            crown_waves_count = (waves - 1) if draw_crown_waves else 0

            # Count actual midlines drawn (partial or full)
            if partial_crown_midlines > 0:
                midlines_count = min(partial_crown_midlines, waves)
            else:
                midlines_count = waves if draw_crown_midlines else 0

            h_midlines_count = num_rings if draw_crown_h_midlines else 0

            # Count actual mid lines drawn (partial or full)
            if partial_crown_mids > 0:
                # 1 line per crown
                mids_count = min(partial_crown_mids, crowns_per_ring)
            else:
                mids_count = crowns_per_ring if draw_crown_mids else 0

            # Create coincident points at line intersections if requested
            points_created = 0
            constraints_created = 0
            if create_coincident_points:
                try:
                    # Collect all horizontal line Y positions
                    horizontal_lines = []

                    # Add border lines
                    if draw_border:
                        horizontal_lines.extend([0.0, total_length])

                    # Add gap centerlines
                    if draw_gap_centerlines:
                        horizontal_lines.extend(gap_centers)

                    # Add crown peaks (ring start positions)
                    if draw_crown_peaks:
                        # Add both ring start and ring end lines (as drawn in the actual code)
                        for ring_start in ring_start_lines:
                            if 0 < ring_start < total_length:  # Only add if inside the box
                                horizontal_lines.append(ring_start)
                        for ring_end in ring_end_lines:
                            if 0 < ring_end < total_length:  # Only add if inside the box
                                horizontal_lines.append(ring_end)

                    # Add horizontal crown midlines (ring centers)
                    if draw_crown_h_midlines:
                        horizontal_lines.extend(ring_centers)

                    # Collect all vertical line X positions
                    vertical_lines = []

                    # Add border lines
                    if draw_border:
                        vertical_lines.extend([0.0, width_mm])

                    # Add wave boundary lines
                    if draw_crown_waves:
                        waves = max(1, crowns_per_ring // 2)
                        wave_width = width_mm / waves
                        # Only add lines that are actually drawn (between waves, not at borders)
                        for w in range(1, waves):
                            x = w * wave_width
                            vertical_lines.append(x)

                    # Add wave midlines (full or partial)
                    if draw_crown_midlines or partial_crown_midlines > 0:
                        waves = max(1, crowns_per_ring // 2)
                        wave_width = width_mm / waves
                        midlines_to_draw = partial_crown_midlines if partial_crown_midlines > 0 else waves
                        for w in range(min(midlines_to_draw, waves)):
                            midline_x = (w + 0.5) * wave_width
                            vertical_lines.append(midline_x)

                    # Add crown mid lines (full or partial)
                    if draw_crown_mids or partial_crown_mids > 0:
                        crown_width = width_mm / crowns_per_ring
                        mids_to_draw = partial_crown_mids if partial_crown_mids > 0 else crowns_per_ring
                        for crown in range(min(mids_to_draw, crowns_per_ring)):
                            mid_x = (crown + 0.5) * crown_width
                            vertical_lines.append(mid_x)

                    # Create points at all intersections and add coincident constraints
                    created_points = []

                    # Debug: log which horizontal lines we're collecting
                    debug_info = []
                    debug_info.append(f"Horizontal lines collected:")
                    if draw_border:
                        debug_info.append(f"  Border: 0.0, {total_length}")
                    if draw_gap_centerlines:
                        debug_info.append(
                            f"  Gap centers: {[f'{g:.3f}' for g in gap_centers]}")
                    if draw_crown_peaks:
                        ring_starts_inside = [
                            rs for rs in ring_start_lines if 0 < rs < total_length]
                        ring_ends_inside = [
                            re for re in ring_end_lines if 0 < re < total_length]
                        debug_info.append(
                            f"  Ring starts: {[f'{rs:.3f}' for rs in ring_starts_inside]}")
                        debug_info.append(
                            f"  Ring ends: {[f'{re:.3f}' for re in ring_ends_inside]}")
                    if draw_crown_h_midlines:
                        debug_info.append(
                            f"  Ring centers: {[f'{rc:.3f}' for rc in ring_centers]}")

                    debug_info.append(f"Vertical lines collected:")
                    if draw_border:
                        debug_info.append(f"  Border: 0.0, {width_mm}")
                    if draw_crown_waves:
                        crown_width = width_mm / crowns_per_ring
                        wave_lines = [
                            crown * crown_width for crown in range(1, crowns_per_ring)]
                        debug_info.append(
                            f"  Crown waves: {[f'{w:.3f}' for w in wave_lines]}")

                    futil.log('\n'.join(debug_info))

                    for h_y in horizontal_lines:
                        for v_x in vertical_lines:
                            # Convert to cm for Fusion (Fusion uses cm internally)
                            point_x_cm = v_x / 10.0
                            point_y_cm = h_y / 10.0
                            point = adsk.core.Point3D.create(
                                point_x_cm, point_y_cm, 0)
                            sketch_point = sk.sketchPoints.add(point)
                            created_points.append((sketch_point, v_x, h_y))
                            points_created += 1

                    # Create coincident constraints between points and lines
                    constraints_created = 0
                    try:
                        constraints = sk.geometricConstraints

                        # Sort lines into horizontal and vertical for easier matching
                        horizontal_sketch_lines = []
                        vertical_sketch_lines = []

                        for line in sk.sketchCurves.sketchLines:
                            start_pt = line.startSketchPoint.geometry
                            end_pt = line.endSketchPoint.geometry

                            # Check if horizontal (Y values are the same)
                            if abs(start_pt.y - end_pt.y) < 0.001:
                                y_mm = start_pt.y * 10.0  # Convert to mm
                                horizontal_sketch_lines.append((line, y_mm))

                            # Check if vertical (X values are the same)
                            elif abs(start_pt.x - end_pt.x) < 0.001:
                                x_mm = start_pt.x * 10.0  # Convert to mm
                                vertical_sketch_lines.append((line, x_mm))

                        for sketch_point, x_mm, y_mm in created_points:
                            # Find horizontal line at this Y position
                            for line, line_y_mm in horizontal_sketch_lines:
                                if abs(line_y_mm - y_mm) < 0.01:  # Tighter tolerance
                                    try:
                                        constraint = constraints.addCoincident(
                                            sketch_point, line)
                                        constraints_created += 1
                                    except:
                                        pass  # Skip if constraint fails

                            # Find vertical line at this X position
                            for line, line_x_mm in vertical_sketch_lines:
                                if abs(line_x_mm - x_mm) < 0.01:  # Tighter tolerance
                                    try:
                                        constraint = constraints.addCoincident(
                                            sketch_point, line)
                                        constraints_created += 1
                                    except:
                                        pass  # Skip if constraint fails

                    except Exception as constraint_error:
                        futil.log(
                            f'Error creating constraints: {str(constraint_error)}')
                        constraints_created = 0

                except Exception as e:
                    futil.log(f'Error creating coincident points: {str(e)}')

            waves = max(1, crowns_per_ring // 2)
            ui.messageBox(
                f'Stent frame created successfully!\n'
                f'• Diameter: {diameter_mm:.3f} mm\n'
                f'• Length: {length_mm:.3f} mm\n'
                f'• Width (circumference): {width_mm:.3f} mm\n'
                f'• Rings: {num_rings}\n'
                f'• Waves per ring: {waves} (crowns: {crowns_per_ring})\n'
                f'• Scaled ring heights: {[f"{h:.3f}" for h in scaled_ring_heights]}\n'
                f'• Gap values: {[f"{g:.3f}" for g in gap_values[:num_gaps]]} mm\n'
                f'• Ring scale factor: {ring_scale_factor:.3f}\n'
                f'• Horizontal lines inside box: {lines_inside_box}\n'
                f'• Vertical wave boundaries: {crown_waves_count}\n'
                f'• Vertical wave midlines: {midlines_count}\n'
                f'• Vertical crown mid lines: {mids_count}\n'
                f'• Horizontal crown midlines: {h_midlines_count}\n'
                f'• Coincident points created: {points_created}\n'
                f'• Coincident constraints created: {constraints_created}'
            )

    except Exception as e:
        try:
            app = adsk.core.Application.get()
            ui = app.userInterface
            ui.messageBox(f'Error creating stent frame: {str(e)}')
        except:
            pass
        import traceback
        futil.log(f'Error in draw_stent_frame: {traceback.format_exc()}')


# This event handler is called when the command terminates.
def command_destroy(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Destroy Event')

    global local_handlers
    local_handlers = []
