
import adsk.core
import adsk.fusion
import os
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
    'diameter': 0.18,          # 0.18 cm = 1.80 mm
    'length': 0.8,             # 0.80 cm = 8.00 mm
    'num_rings': 6,
    'crowns_per_ring': 8,
    'height_factors': '1.20, 1.00, 1.00, 1.00, 1.00, 1.10',
    # Default gaps: fold‑lock at ends (for 16 µm wall), body 0.160
    'gap_between_rings': '0.095, 0.160, 0.160, 0.160, 0.100',
    # Drawing options
    'draw_border': True,
    'draw_gap_centerlines': True,
    'gap_centerlines_interior_only': True,  # only 2–3, 3–4, 4–5
    'draw_crown_peaks': True,
    'draw_crown_waves': True,
    'draw_crown_midlines': False,
    'draw_crown_h_midlines': False,
    'partial_crown_midlines': 0,
    'draw_crown_quarters': False,
    'partial_crown_quarters': 0,
    'create_coincident_points': False,
    # Fold‑lock options
    'use_fold_lock_table': True,
    'balloon_wall_um': 16,              # Pebax wall thickness in µm
    'body_gap_mm': 0.160,               # interior/body gap if table is used
    'draw_fold_lock_limits': True,      # draw short horizontal segments in specified crown boxes
    'fold_lock_columns': '0,2,4,6'      # crown boxes used by end links
}

# Default values for reset functionality
default_values = last_used_values.copy()


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

    inputs = args.command.commandInputs

    # Description
    description_input = inputs.addTextBoxCommandInput('description', '',
                                                      'Design customizable stent frames with precise control over dimensions, rings, crown pattern, and fold‑lock end windows.',
                                                      3, True)
    description_input.isFullWidth = True

    # Dimensions
    diameter_group = inputs.addGroupCommandInput('diameter_group', 'Stent Dimensions')
    diameter_group.isExpanded = True
    diameter_inputs = diameter_group.children

    defaultLengthUnits = app.activeProduct.unitsManager.defaultLengthUnits
    diameter_value = adsk.core.ValueInput.createByReal(last_used_values['diameter'])
    diameter_input = diameter_inputs.addValueInput('diameter', 'Diameter (mm)', defaultLengthUnits, diameter_value)
    diameter_input.tooltip = 'Expanded stent outer diameter'

    length_value = adsk.core.ValueInput.createByReal(last_used_values['length'])
    length_input = diameter_inputs.addValueInput('length', 'Length (mm)', defaultLengthUnits, length_value)
    length_input.tooltip = 'Total axial length of the stent (unrolled height)'

    # Ring configuration
    ring_group = inputs.addGroupCommandInput('ring_group', 'Ring Configuration')
    ring_group.isExpanded = True
    ring_inputs = ring_group.children

    num_rings_input = ring_inputs.addIntegerSpinnerCommandInput('num_rings', 'Number of Rings', 1, 50, 1, last_used_values['num_rings'])
    crowns_input = ring_inputs.addIntegerSpinnerCommandInput('crowns_per_ring', 'Crowns per Ring', 4, 64, 1, last_used_values['crowns_per_ring'])

    # Height proportions
    height_group = inputs.addGroupCommandInput('height_group', 'Ring Height Proportions')
    height_group.isExpanded = True
    height_inputs = height_group.children

    height_factors_input = height_inputs.addStringValueInput('height_factors', 'Height Proportions (comma-separated)', last_used_values['height_factors'])
    height_factors_input.tooltip = 'Relative proportions for each ring height (e.g., 1.20, 1.00, …). They are scaled so rings+gaps exactly fit the total length.'
    height_factors_input.isFullWidth = True

    # Gap configuration
    gap_group = inputs.addGroupCommandInput('gap_group', 'Gap Configuration')
    gap_group.isExpanded = True
    gap_inputs = gap_group.children

    gap_input = gap_inputs.addStringValueInput('gap_between_rings', 'Gap Between Rings (mm)', last_used_values['gap_between_rings'])
    gap_input.tooltip = 'Apex‑to‑apex link distances for each interface (mm). Single value applies to all gaps.'
    gap_input.isFullWidth = True

    # Fold‑lock options
    fl_group = inputs.addGroupCommandInput('fl_group', 'Fold‑Lock Options (Ends Only)')
    fl_group.isExpanded = True
    fl_inputs = fl_group.children

    use_fl_input = fl_inputs.addBoolValueInput('use_fold_lock_table', 'Use Fold‑Lock Table for End Gaps', True, '', last_used_values['use_fold_lock_table'])
    use_fl_input.tooltip = 'Override the first and last gaps with table‑based fold‑lock values from balloon wall thickness.'

    wall_input = fl_inputs.addIntegerSpinnerCommandInput('balloon_wall_um', 'Balloon Wall Thickness (µm)', 8, 40, 1, last_used_values['balloon_wall_um'])
    wall_input.tooltip = 'Pebax wall thickness in micrometers for the stent zone.'

    body_gap_value = adsk.core.ValueInput.createByReal(last_used_values['body_gap_mm'] / 10.0)  # cm in Fusion; value stored in mm
    body_gap_input = fl_inputs.addValueInput('body_gap_mm', 'Interior Body Gap (mm)', defaultLengthUnits, body_gap_value)
    body_gap_input.tooltip = 'Interior (2–3, 3–4, …) apex‑to‑apex gap used when fold‑lock table is applied to the two ends.'

    draw_fl_limits_input = fl_inputs.addBoolValueInput('draw_fold_lock_limits', 'Draw Fold‑Lock Limit Lines in Crown Boxes', True, '', last_used_values['draw_fold_lock_limits'])
    draw_fl_limits_input.tooltip = 'Short horizontal lines at the top & bottom of the end gaps, drawn only in specified crown columns (boxes).'

    fl_cols_input = fl_inputs.addStringValueInput('fold_lock_columns', 'Fold‑Lock Crown Boxes (indices)', last_used_values['fold_lock_columns'])
    fl_cols_input.tooltip = 'Comma‑separated crown indices for the end‑interface links (e.g., "0,2,4,6" for 8 crowns).'
    fl_cols_input.isFullWidth = True

    # Drawing options
    draw_group = inputs.addGroupCommandInput('draw_group', 'Drawing Options')
    draw_group.isExpanded = True
    draw_inputs = draw_group.children

    border_input = draw_inputs.addBoolValueInput('draw_border', 'Draw Border', True, '', last_used_values['draw_border'])
    gap_lines_input = draw_inputs.addBoolValueInput('draw_gap_centerlines', 'Draw Gap Center Lines', True, '', last_used_values['draw_gap_centerlines'])
    gap_lines_only_mid_input = draw_inputs.addBoolValueInput('gap_centerlines_interior_only', 'Gap Center Lines — Interior Only', True, '', last_used_values['gap_centerlines_interior_only'])

    peak_lines_input = draw_inputs.addBoolValueInput('draw_crown_peaks', 'Draw Crown Peak Lines', True, '', last_used_values['draw_crown_peaks'])
    wave_lines_input = draw_inputs.addBoolValueInput('draw_crown_waves', 'Draw Crown Wave Lines', True, '', last_used_values['draw_crown_waves'])
    midlines_input = draw_inputs.addBoolValueInput('draw_crown_midlines', 'Draw Crown Wave Midlines', True, '', last_used_values['draw_crown_midlines'])
    h_midlines_input = draw_inputs.addBoolValueInput('draw_crown_h_midlines', 'Draw Crown Horizontal Midlines', True, '', last_used_values['draw_crown_h_midlines'])
    partial_midlines_input = draw_inputs.addIntegerSpinnerCommandInput('partial_crown_midlines', 'Crown Midlines Count (from left)', 0, 64, 1, last_used_values['partial_crown_midlines'])
    quarter_lines_input = draw_inputs.addBoolValueInput('draw_crown_quarters', 'Draw Crown Quarter Lines', True, '', last_used_values['draw_crown_quarters'])
    partial_quarters_input = draw_inputs.addIntegerSpinnerCommandInput('partial_crown_quarters', 'Crown Quarter Lines Count (from left)', 0, 64, 1, last_used_values['partial_crown_quarters'])
    coincident_points_input = draw_inputs.addBoolValueInput('create_coincident_points', 'Create Coincident Points at Line Crossings', True, '', last_used_values['create_coincident_points'])

    # Reset
    reset_button = draw_inputs.addBoolValueInput('reset_to_defaults', 'Reset to Default Values', False, '', False)

    # Dialog size
    args.command.setDialogInitialSize(450, 820)
    args.command.setDialogMinimumSize(300, 480)

    # Events
    futil.add_handler(args.command.execute, command_execute, local_handlers=local_handlers)
    futil.add_handler(args.command.inputChanged, command_input_changed, local_handlers=local_handlers)
    futil.add_handler(args.command.executePreview, command_preview, local_handlers=local_handlers)
    futil.add_handler(args.command.validateInputs, command_validate_input, local_handlers=local_handlers)
    futil.add_handler(args.command.destroy, command_destroy, local_handlers=local_handlers)


def command_execute(args: adsk.core.CommandEventArgs):
    futil.log(f'{CMD_NAME} Command Execute Event')
    inputs = args.command.commandInputs

    # Grab inputs
    diameter_input = adsk.core.ValueCommandInput.cast(inputs.itemById('diameter'))
    length_input = adsk.core.ValueCommandInput.cast(inputs.itemById('length'))
    num_rings_input = adsk.core.IntegerSpinnerCommandInput.cast(inputs.itemById('num_rings'))
    crowns_per_ring_input = adsk.core.IntegerSpinnerCommandInput.cast(inputs.itemById('crowns_per_ring'))
    height_factors_input = adsk.core.StringValueCommandInput.cast(inputs.itemById('height_factors'))
    gap_input = adsk.core.StringValueCommandInput.cast(inputs.itemById('gap_between_rings'))

    draw_border_input = adsk.core.BoolValueCommandInput.cast(inputs.itemById('draw_border'))
    draw_gap_centerlines_input = adsk.core.BoolValueCommandInput.cast(inputs.itemById('draw_gap_centerlines'))
    gap_centerlines_interior_only_input = adsk.core.BoolValueCommandInput.cast(inputs.itemById('gap_centerlines_interior_only'))
    draw_crown_peaks_input = adsk.core.BoolValueCommandInput.cast(inputs.itemById('draw_crown_peaks'))
    draw_crown_waves_input = adsk.core.BoolValueCommandInput.cast(inputs.itemById('draw_crown_waves'))
    draw_crown_midlines_input = adsk.core.BoolValueCommandInput.cast(inputs.itemById('draw_crown_midlines'))
    draw_crown_h_midlines_input = adsk.core.BoolValueCommandInput.cast(inputs.itemById('draw_crown_h_midlines'))
    partial_crown_midlines_input = adsk.core.IntegerSpinnerCommandInput.cast(inputs.itemById('partial_crown_midlines'))
    draw_crown_quarters_input = adsk.core.BoolValueCommandInput.cast(inputs.itemById('draw_crown_quarters'))
    partial_crown_quarters_input = adsk.core.IntegerSpinnerCommandInput.cast(inputs.itemById('partial_crown_quarters'))
    coincident_points_input = adsk.core.BoolValueCommandInput.cast(inputs.itemById('create_coincident_points'))

    reset_button_input = adsk.core.BoolValueCommandInput.cast(inputs.itemById('reset_to_defaults'))

    # Fold‑lock
    use_fold_lock_table_input = adsk.core.BoolValueCommandInput.cast(inputs.itemById('use_fold_lock_table'))
    balloon_wall_um_input = adsk.core.IntegerSpinnerCommandInput.cast(inputs.itemById('balloon_wall_um'))
    body_gap_mm_input = adsk.core.ValueCommandInput.cast(inputs.itemById('body_gap_mm'))
    draw_fold_lock_limits_input = adsk.core.BoolValueCommandInput.cast(inputs.itemById('draw_fold_lock_limits'))
    fold_lock_columns_input = adsk.core.StringValueCommandInput.cast(inputs.itemById('fold_lock_columns'))

    # Reset
    if reset_button_input.value:
        for k,v in default_values.items():
            if k in ('diameter','length','body_gap_mm'):
                # value inputs are in cm in Fusion; we stored mm for body_gap_mm
                if k == 'diameter':
                    inputs.itemById('diameter').value = v
                elif k == 'length':
                    inputs.itemById('length').value = v
                elif k == 'body_gap_mm':
                    inputs.itemById('body_gap_mm').value = v/10.0
            elif k in ('num_rings','crowns_per_ring','balloon_wall_um','partial_crown_midlines','partial_crown_quarters'):
                inputs.itemById(k).value = v
            elif isinstance(v, bool):
                inputs.itemById(k).value = v
            else:
                inputs.itemById(k).value = v
        reset_button_input.value = False
        last_used_values.update(default_values.copy())
        return

    # Values (convert cm->mm for numeric value inputs)
    diameter = diameter_input.value * 10.0
    length = length_input.value * 10.0
    num_rings = num_rings_input.value
    crowns_per_ring = crowns_per_ring_input.value
    height_factors_str = height_factors_input.value
    gap_str = gap_input.value

    draw_border = draw_border_input.value
    draw_gap_centerlines = draw_gap_centerlines_input.value
    gap_centerlines_interior_only = gap_centerlines_interior_only_input.value
    draw_crown_peaks = draw_crown_peaks_input.value
    draw_crown_waves = draw_crown_waves_input.value
    draw_crown_midlines = draw_crown_midlines_input.value
    draw_crown_h_midlines = draw_crown_h_midlines_input.value
    partial_crown_midlines = partial_crown_midlines_input.value
    draw_crown_quarters = draw_crown_quarters_input.value
    partial_crown_quarters = partial_crown_quarters_input.value
    create_coincident_points = coincident_points_input.value

    use_fold_lock_table = use_fold_lock_table_input.value
    balloon_wall_um = balloon_wall_um_input.value
    body_gap_mm = body_gap_mm_input.value * 10.0  # cm->mm in Fusion
    draw_fold_lock_limits = draw_fold_lock_limits_input.value
    fold_lock_columns_str = fold_lock_columns_input.value

    # Parse height factors
    try:
        height_factors = [float(x.strip()) for x in height_factors_str.split(',') if x.strip()!='']
        while len(height_factors) < num_rings:
            height_factors.append(1.0)
        height_factors = height_factors[:num_rings]
    except:
        height_factors = [1.0]*num_rings

    # Parse base gaps
    try:
        gap_values = [float(x.strip()) for x in gap_str.split(',') if x.strip()!='']
        needed_gaps = max(1, num_rings-1)
        while len(gap_values) < needed_gaps:
            gap_values.append(gap_values[-1] if gap_values else 0.16)
        gap_values = gap_values[:needed_gaps]
    except:
        gap_values = [0.16]*max(1, num_rings-1)

    # Parse fold‑lock crown indices
    try:
        fold_lock_indices = [int(x.strip()) for x in fold_lock_columns_str.split(',') if x.strip()!='']
    except:
        fold_lock_indices = [0,2,4,6]

    # If using fold‑lock table, override ends and interiors accordingly
    if use_fold_lock_table and (num_rings >= 2):
        num_gaps = num_rings-1
        # compute end gaps from wall thickness (table + interpolation)
        g_prox, g_dist = _fold_lock_end_gaps_from_wall(balloon_wall_um)
        gap_values[0] = g_prox
        gap_values[-1] = g_dist
        # set interior gaps uniformly to body_gap_mm
        for i in range(1, num_gaps-1):
            gap_values[i] = body_gap_mm

    # Save for session
    last_used_values.update({
        'diameter': diameter_input.value,
        'length': length_input.value,
        'num_rings': num_rings,
        'crowns_per_ring': crowns_per_ring,
        'height_factors': height_factors_str,
        'gap_between_rings': ', '.join(f'{g:.3f}' for g in gap_values),
        'draw_border': draw_border,
        'draw_gap_centerlines': draw_gap_centerlines,
        'gap_centerlines_interior_only': gap_centerlines_interior_only,
        'draw_crown_peaks': draw_crown_peaks,
        'draw_crown_waves': draw_crown_waves,
        'draw_crown_midlines': draw_crown_midlines,
        'draw_crown_h_midlines': draw_crown_h_midlines,
        'partial_crown_midlines': partial_crown_midlines,
        'draw_crown_quarters': draw_crown_quarters,
        'partial_crown_quarters': partial_crown_quarters,
        'create_coincident_points': create_coincident_points,
        'use_fold_lock_table': use_fold_lock_table,
        'balloon_wall_um': balloon_wall_um,
        'body_gap_mm': body_gap_mm,
        'draw_fold_lock_limits': draw_fold_lock_limits,
        'fold_lock_columns': fold_lock_columns_str
    })

    draw_stent_frame(diameter, length, num_rings, crowns_per_ring,
                     height_factors, gap_values, draw_border, draw_gap_centerlines, gap_centerlines_interior_only,
                     draw_crown_peaks, draw_crown_waves, draw_crown_midlines, draw_crown_h_midlines,
                     partial_crown_midlines, draw_crown_quarters, partial_crown_quarters, create_coincident_points,
                     draw_fold_lock_limits, fold_lock_indices, balloon_wall_um, use_fold_lock_table)


def command_preview(args: adsk.core.CommandEventArgs):
    futil.log(f'{CMD_NAME} Command Preview Event')


def command_input_changed(args: adsk.core.InputChangedEventArgs):
    changed_input = args.input
    inputs = args.inputs
    futil.log(f'{CMD_NAME} Input Changed: {changed_input.id}')


def command_validate_input(args: adsk.core.ValidateInputsEventArgs):
    futil.log(f'{CMD_NAME} Validate Input Event')
    inputs = args.inputs
    diameter_input = adsk.core.ValueCommandInput.cast(inputs.itemById('diameter'))
    length_input = adsk.core.ValueCommandInput.cast(inputs.itemById('length'))
    num_rings_input = adsk.core.IntegerSpinnerCommandInput.cast(inputs.itemById('num_rings'))
    if (diameter_input and length_input and num_rings_input and
        diameter_input.value > 0 and length_input.value > 0 and num_rings_input.value > 0):
        args.areInputsValid = True
    else:
        args.areInputsValid = False


def _fold_lock_end_gaps_from_wall(w_um: int):
    """
    Return (g_prox, g_dist) in mm for the two end interfaces based on balloon wall thickness.
    Uses the discrete table:
      12 µm -> (0.075, 0.080)
      14 µm -> (0.085, 0.090)
      16 µm -> (0.095, 0.100)
      18 µm -> (0.105, 0.110)
    with linear interpolation between entries and clamping outside the range.
    """
    table = {
        12: (0.075, 0.080),
        14: (0.085, 0.090),
        16: (0.095, 0.100),
        18: (0.105, 0.110)
    }
    keys = sorted(table.keys())
    if w_um <= keys[0]:
        return table[keys[0]]
    if w_um >= keys[-1]:
        return table[keys[-1]]
    # find bracket
    for i in range(len(keys)-1):
        k0, k1 = keys[i], keys[i+1]
        if k0 <= w_um <= k1:
            g0a, g0b = table[k0]
            g1a, g1b = table[k1]
            t = (w_um - k0) / (k1 - k0)
            return (g0a + t*(g1a - g0a), g0b + t*(g1b - g0b))
    return table[16]  # fallback


def draw_stent_frame(diameter_mm, length_mm, num_rings, crowns_per_ring,
                     height_factors, gap_values, draw_border, draw_gap_centerlines, gap_centerlines_interior_only,
                     draw_crown_peaks, draw_crown_waves, draw_crown_midlines, draw_crown_h_midlines,
                     partial_crown_midlines, draw_crown_quarters, partial_crown_quarters, create_coincident_points,
                     draw_fold_lock_limits=False, fold_lock_indices=None, balloon_wall_um=16, used_fl_table=False):
    """Draw stent frame based on parameters using optimized calculations"""
    import math

    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox("Please create a new design or open an existing one before running this command.", "No Design Active")
            return

        root = design.rootComponent
        sk = root.sketches.add(root.xYConstructionPlane)
        sk.name = f'Stent Frame – {num_rings} rings, {crowns_per_ring} crowns'

        # Convert mm to cm for Fusion API
        def mm_to_cm(x): return x * 0.1

        # Compute width from diameter
        width_mm = diameter_mm * math.pi

        # Height proportions scaled to fit (rings+gaps = length)
        ring_heights = height_factors
        num_gaps = num_rings - 1
        total_gap_space = sum(gap_values[:num_gaps]) if num_gaps > 0 else 0.0
        available_ring_space = max(0.0, length_mm - total_gap_space)
        original_total_ring_height = sum(ring_heights) if ring_heights else 1.0
        ring_scale_factor = (available_ring_space / original_total_ring_height) if original_total_ring_height > 0 else 1.0
        scaled_ring_heights = [h * ring_scale_factor for h in ring_heights]

        # Ring centers
        ring_centers = []
        current_y = scaled_ring_heights[0] / 2.0
        ring_centers.append(current_y)
        for i in range(1, num_rings):
            gap_value = gap_values[i-1] if (i-1) < len(gap_values) else gap_values[-1]
            current_y += (scaled_ring_heights[i-1] / 2.0) + gap_value + (scaled_ring_heights[i] / 2.0)
            ring_centers.append(current_y)

        # Boundaries (top/bottom of ring bands)
        ring_start_lines = []
        ring_end_lines   = []
        for i, center in enumerate(ring_centers):
            ring_start_lines.append(center - scaled_ring_heights[i]/2.0)  # top
            ring_end_lines.append(center + scaled_ring_heights[i]/2.0)    # bottom

        # Gap centers
        gap_centers = []
        for i in range(num_rings - 1):
            gap_centers.append(0.5*(ring_end_lines[i] + ring_start_lines[i+1]))

        total_length = length_mm
        lines = sk.sketchCurves.sketchLines

        # Border
        if draw_border:
            # Left & Right
            lines.addByTwoPoints(adsk.core.Point3D.create(mm_to_cm(0.0), mm_to_cm(0.0), 0),
                                 adsk.core.Point3D.create(mm_to_cm(0.0), mm_to_cm(total_length), 0))
            lines.addByTwoPoints(adsk.core.Point3D.create(mm_to_cm(width_mm), mm_to_cm(0.0), 0),
                                 adsk.core.Point3D.create(mm_to_cm(width_mm), mm_to_cm(total_length), 0))
            # Top & Bottom
            lines.addByTwoPoints(adsk.core.Point3D.create(mm_to_cm(0.0), mm_to_cm(total_length), 0),
                                 adsk.core.Point3D.create(mm_to_cm(width_mm), mm_to_cm(total_length), 0))
            lines.addByTwoPoints(adsk.core.Point3D.create(mm_to_cm(0.0), mm_to_cm(0.0), 0),
                                 adsk.core.Point3D.create(mm_to_cm(width_mm), mm_to_cm(0.0), 0))

        # Crown peak lines (tops & bottoms of each ring)
        if draw_crown_peaks:
            for y in ring_start_lines + ring_end_lines:
                if 0.0 < y < total_length:
                    ln = lines.addByTwoPoints(adsk.core.Point3D.create(mm_to_cm(0.0), mm_to_cm(y), 0),
                                              adsk.core.Point3D.create(mm_to_cm(width_mm), mm_to_cm(y), 0))
                    ln.isConstruction = True

        # Gap center lines (optionally interior only)
        if draw_gap_centerlines and num_rings > 1:
            if gap_centerlines_interior_only and num_rings > 3:
                idxs = range(1, num_rings-2)   # 2–3, 3–4, ..., N-2–N-1
            else:
                idxs = range(0, num_rings-1)
            for i in idxs:
                y = gap_centers[i]
                ln = lines.addByTwoPoints(adsk.core.Point3D.create(mm_to_cm(0.0), mm_to_cm(y), 0),
                                          adsk.core.Point3D.create(mm_to_cm(width_mm), mm_to_cm(y), 0))
                ln.isConstruction = True

        # Crown wave verticals (between crowns)
        if draw_crown_waves and crowns_per_ring > 0:
            crown_spacing = width_mm / crowns_per_ring
            for i in range(1, crowns_per_ring):
                x = i * crown_spacing
                ln = lines.addByTwoPoints(adsk.core.Point3D.create(mm_to_cm(x), mm_to_cm(0.0), 0),
                                          adsk.core.Point3D.create(mm_to_cm(x), mm_to_cm(total_length), 0))
                ln.isConstruction = True

        # Crown mid verticals (center of each crown)
        if draw_crown_midlines or partial_crown_midlines > 0:
            crown_spacing = width_mm / crowns_per_ring
            if partial_crown_midlines > 0:
                midlines_count = min(partial_crown_midlines, crowns_per_ring)
            else:
                midlines_count = crowns_per_ring if draw_crown_midlines else 0
            for i in range(midlines_count):
                x = i*crown_spacing + 0.5*crown_spacing
                ln = lines.addByTwoPoints(adsk.core.Point3D.create(mm_to_cm(x), mm_to_cm(0.0), 0),
                                          adsk.core.Point3D.create(mm_to_cm(x), mm_to_cm(total_length), 0))
                ln.isConstruction = True

        # Horizontal midlines at ring centers
        if draw_crown_h_midlines:
            for y in ring_centers:
                ln = lines.addByTwoPoints(adsk.core.Point3D.create(mm_to_cm(0.0), mm_to_cm(y), 0),
                                          adsk.core.Point3D.create(mm_to_cm(width_mm), mm_to_cm(y), 0))
                ln.isConstruction = True

        # Crown quarter verticals
        if draw_crown_quarters or partial_crown_quarters > 0:
            crown_spacing = width_mm / crowns_per_ring
            if partial_crown_quarters > 0:
                quarters_count = min(partial_crown_quarters, crowns_per_ring)
            else:
                quarters_count = crowns_per_ring if draw_crown_quarters else 0
            for i in range(quarters_count):
                q1 = i*crown_spacing + 0.25*crown_spacing
                q3 = i*crown_spacing + 0.75*crown_spacing
                for x in (q1, q3):
                    ln = lines.addByTwoPoints(adsk.core.Point3D.create(mm_to_cm(x), mm_to_cm(0.0), 0),
                                              adsk.core.Point3D.create(mm_to_cm(x), mm_to_cm(total_length), 0))
                    ln.isConstruction = True

        # --- Fold‑lock horizontal limit lines (ends only, inside selected crown boxes) ---
        if draw_fold_lock_limits and (num_rings >= 2) and (crowns_per_ring > 0):
            crown_spacing = width_mm / crowns_per_ring
            def hseg(xL_mm, xR_mm, y_mm):
                ln = lines.addByTwoPoints(adsk.core.Point3D.create(mm_to_cm(xL_mm), mm_to_cm(y_mm), 0),
                                          adsk.core.Point3D.create(mm_to_cm(xR_mm), mm_to_cm(y_mm), 0))
                ln.isConstruction = True

            # sanitize indices
            if fold_lock_indices is None:
                fold_lock_indices = [0,2,4,6]
            valid_cols = sorted({k for k in fold_lock_indices if 0 <= k < crowns_per_ring})

            # End interface y-positions
            y_low_12  = ring_end_lines[0]             # bottom of ring 1
            y_high_12 = ring_start_lines[1]           # top of ring 2
            y_low_56  = ring_end_lines[num_rings-2]   # bottom of ring N-1
            y_high_56 = ring_start_lines[num_rings-1] # top of ring N

            for k in valid_cols:
                xL = k * crown_spacing
                xR = (k+1) * crown_spacing
                # proximal end gap limits
                hseg(xL, xR, y_low_12)
                hseg(xL, xR, y_high_12)
                # distal end gap limits
                hseg(xL, xR, y_low_56)
                hseg(xL, xR, y_high_56)

        # Summary
        if ui:
            crown_waves_count = crowns_per_ring - 1 if draw_crown_waves else 0
            if partial_crown_midlines > 0:
                midlines_count = min(partial_crown_midlines, crowns_per_ring)
            else:
                midlines_count = crowns_per_ring if draw_crown_midlines else 0
            h_midlines_count = num_rings if draw_crown_h_midlines else 0
            if partial_crown_quarters > 0:
                quarters_count = min(partial_crown_quarters, crowns_per_ring) * 2
            else:
                quarters_count = crowns_per_ring*2 if draw_crown_quarters else 0

            # End gaps (report)
            g_prox = gap_values[0] if (num_rings>=2) else 0.0
            g_dist = gap_values[-1] if (num_rings>=2) else 0.0

            ui.messageBox(
                'Stent frame created.\n'
                f'• Diameter: {diameter_mm:.3f} mm  →  Width (circumference): {width_mm:.3f} mm\n'
                f'• Length: {length_mm:.3f} mm\n'
                f'• Rings: {num_rings} ; Crowns/ring: {crowns_per_ring}\n'
                f'• Scaled ring heights: {[f\"{h:.3f}\" for h in scaled_ring_heights]}\n'
                f'• Gaps (mm): {[f\"{g:.3f}\" for g in gap_values]}\n'
                f'• End gaps used (prox, dist): ({g_prox:.3f}, {g_dist:.3f}) mm  '
                + (f'[Fold‑Lock table, wall {balloon_wall_um} µm]' if used_fl_table else '[manual]') + '\\n'
                f'• Ring scale factor: {ring_scale_factor:.3f}\n'
                f'• Crown waves: {crown_waves_count}; Crown midlines: {midlines_count}; Crown quarter lines: {quarters_count}\n'
                f'• Horizontal crown midlines: {h_midlines_count}'
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


def command_destroy(args: adsk.core.CommandEventArgs):
    futil.log(f'{CMD_NAME} Command Destroy Event')
    global local_handlers
    local_handlers = []
