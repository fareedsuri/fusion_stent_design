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
    'diameter': 0.18,  # 1.80mm diameter per recommendations
    'length': 0.8,     # 8.000mm per recommendations
    'num_rings': 6,    # 6 rings per recommendations
    'crowns_per_ring': 8,  # 8 crowns/ring per recommendations
    'height_factors': '1.20, 1.00, 1.00, 1.00, 1.00, 1.10',  # Recommended pattern
    # g₀=0.14mm with end reductions
    'gap_between_rings': '0.126, 0.14, 0.14, 0.14, 0.133',
    'draw_border': True,
    'draw_gap_centerlines': True,  # Recommended for CAD workflow
    'draw_crown_peaks': True,
    'draw_crown_waves': True,      # Essential for crown definitions
    'draw_crown_midlines': False,
    'draw_crown_h_midlines': False,
    'partial_crown_midlines': 0,
    'draw_crown_quarters': False,
    'partial_crown_quarters': 0,
    'create_coincident_points': False,
    # Fold-lock options
    'use_fold_lock_table': False,
    'balloon_wall_um': 16,              # Pebax wall thickness in µm
    'body_gap_mm': 0.140,               # interior/body gap if table is used
    # draw short horizontal segments in specified crown boxes
    'draw_fold_lock_limits': False,
    'fold_lock_columns': '0,2,4,6',     # crown boxes used by end links
    # only draw interior gap lines (2–3, 3–4, 4–5)
    'gap_centerlines_interior_only': False
}

# Default values for reset functionality
default_values = {
    'diameter': 0.18,  # 1.80mm diameter per recommendations
    'length': 0.8,     # 8.000mm per recommendations
    'num_rings': 6,    # 6 rings per recommendations
    'crowns_per_ring': 8,  # 8 crowns/ring per recommendations
    'height_factors': '1.20, 1.00, 1.00, 1.00, 1.00, 1.10',  # Recommended pattern
    # g₀=0.14mm with end reductions
    'gap_between_rings': '0.126, 0.14, 0.14, 0.14, 0.133',
    'draw_border': True,
    'draw_gap_centerlines': True,  # Recommended for CAD workflow
    'draw_crown_peaks': True,
    'draw_crown_waves': True,      # Essential for crown definitions
    'draw_crown_midlines': False,
    'draw_crown_h_midlines': False,
    'partial_crown_midlines': 0,
    'draw_crown_quarters': False,
    'partial_crown_quarters': 0,
    'create_coincident_points': False,
    # Fold-lock options
    'use_fold_lock_table': False,
    'balloon_wall_um': 16,              # Pebax wall thickness in µm
    'body_gap_mm': 0.140,               # interior/body gap if table is used
    # draw short horizontal segments in specified crown boxes
    'draw_fold_lock_limits': False,
    'fold_lock_columns': '0,2,4,6',     # crown boxes used by end links
    # only draw interior gap lines (2–3, 3–4, 4–5)
    'gap_centerlines_interior_only': False
}


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

    # Diameter input with wider appearance - load from saved values
    defaultLengthUnits = app.activeProduct.unitsManager.defaultLengthUnits
    # Convert from mm to cm for Fusion 360 internal units
    diameter_value = adsk.core.ValueInput.createByReal(
        last_used_values['diameter'])
    diameter_input = diameter_inputs.addValueInput(
        'diameter', 'Diameter (mm)', defaultLengthUnits, diameter_value)
    diameter_input.tooltip = 'The outer diameter of the stent when expanded'

    # Length input with wider appearance - load from saved values
    # Convert from mm to cm for Fusion 360 internal units
    length_value = adsk.core.ValueInput.createByReal(
        last_used_values['length'])
    length_input = diameter_inputs.addValueInput(
        'length', 'Length (mm)', defaultLengthUnits, length_value)
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

    # Crowns per ring with tooltip - load from saved values
    crowns_input = ring_inputs.addIntegerSpinnerCommandInput(
        'crowns_per_ring', 'Crowns per Ring', 4, 32, 1, last_used_values['crowns_per_ring'])
    crowns_input.tooltip = 'Number of crown peaks per ring segment (4-32)'

    # Ring height proportions group
    height_group = inputs.addGroupCommandInput(
        'height_group', 'Ring Height Proportions')
    height_group.isExpanded = True
    height_group.isEnabledCheckBoxDisplayed = False
    height_inputs = height_group.children

    # Height factors - create a wider text input - load from saved values
    height_factors_input = height_inputs.addStringValueInput(
        'height_factors', 'Height Proportions (comma-separated)', last_used_values['height_factors'])
    height_factors_input.tooltip = 'Relative proportions for each ring height (e.g., 1.20, 1.00, 1.00) - automatically scaled to fit total length'
    # ⬅️ WIDTH CONTROL: StringValueInput width properties:
    # Makes text input span full width of group
    height_factors_input.isFullWidth = True

    # Gap configuration group
    gap_group = inputs.addGroupCommandInput('gap_group', 'Gap Configuration')
    gap_group.isExpanded = True
    gap_group.isEnabledCheckBoxDisplayed = False
    gap_inputs = gap_group.children

    # Gap between rings with tooltip - load from saved values
    # Gap values input (comma-separated list)
    gap_input = gap_inputs.addStringValueInput(
        'gap_between_rings', 'Gap Between Rings (mm)', last_used_values['gap_between_rings'])
    gap_input.tooltip = 'Comma-separated gap values in mm (e.g., "0.2,0.3,0.2"). Single value applies to all gaps.'
    # ⬅️ WIDTH CONTROL:
    gap_input.isFullWidth = True        # Makes input span full width of group

    # Drawing options group
    draw_group = inputs.addGroupCommandInput('draw_group', 'Drawing Options')
    draw_group.isExpanded = True
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

    # Partial crown midlines control - load from saved values
    partial_midlines_input = draw_inputs.addIntegerSpinnerCommandInput(
        'partial_crown_midlines', 'Crown Midlines Count (from left)', 0, 20, 1, last_used_values['partial_crown_midlines'])
    partial_midlines_input.tooltip = 'Number of crowns from left to add midline vertical lines (0 = use full midlines option above)'

    # Crown quarter lines option - load from saved values
    quarter_lines_input = draw_inputs.addBoolValueInput(
        'draw_crown_quarters', 'Draw Crown Quarter Lines', True, '', last_used_values['draw_crown_quarters'])
    quarter_lines_input.tooltip = 'Draw vertical lines at 1/4 and 3/4 positions within each crown section'

    # Partial crown quarter lines control - load from saved values
    partial_quarters_input = draw_inputs.addIntegerSpinnerCommandInput(
        'partial_crown_quarters', 'Crown Quarter Lines Count (from left)', 0, 20, 1, last_used_values['partial_crown_quarters'])
    partial_quarters_input.tooltip = 'Number of crowns from left to add quarter vertical lines (0 = use full quarter lines option above)'

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
    use_fl_input.tooltip = 'Override the first and last gaps with table‑based fold‑lock values from balloon wall thickness.'

    wall_input = fl_inputs.addIntegerSpinnerCommandInput(
        'balloon_wall_um', 'Balloon Wall Thickness (µm)', 8, 40, 1, last_used_values['balloon_wall_um'])
    wall_input.tooltip = 'Pebax balloon wall thickness for fold‑lock gap calculation (typically 12‑20 µm)'

    body_gap_input = fl_inputs.addValueInput(
        'body_gap_mm', 'Body Gap (mm)', 'mm', adsk.core.ValueInput.createByReal(last_used_values['body_gap_mm']))
    body_gap_input.tooltip = 'Interior (2–3, 3–4, …) apex‑to‑apex gap used when fold‑lock table is applied to the two ends.'

    draw_fl_limits_input = fl_inputs.addBoolValueInput(
        'draw_fold_lock_limits', 'Draw Fold‑Lock Limit Lines in Crown Boxes', True, '', last_used_values['draw_fold_lock_limits'])
    draw_fl_limits_input.tooltip = 'Draw horizontal lines within gaps at fold‑lock limits (65% of crown width) for specified crown boxes'

    fl_cols_input = fl_inputs.addStringValueInput(
        'fold_lock_columns', 'Fold‑Lock Crown Boxes (indices)', last_used_values['fold_lock_columns'])
    fl_cols_input.tooltip = 'Comma‑separated crown box indices (0‑based) for fold‑lock limit line placement (e.g., "0,2,4,6")'

    # Reset button to restore default values
    reset_button = draw_inputs.addBoolValueInput(
        'reset_to_defaults', 'Reset to Default Values', False, '', False)
    reset_button.tooltip = 'Click to reset all inputs to their default values'

    # ⬅️ DIALOG BOX STARTUP WIDTH CONTROL:
    # Set the initial width and height of the dialog box
    args.command.setDialogInitialSize(400, 800)  # Width: 500px, Height: 600px

    # ⬅️ ADDITIONAL DIALOG SIZE CONTROLS:
    # Set minimum dialog size (prevents user from making it too small)
    # Min Width: 400px, Min Height: 450px
    args.command.setDialogMinimumSize(250, 450)

    # Set maximum dialog size (prevents dialog from getting too large)
    # args.command.setDialogMaximumSize(800, 900)  # Max Width: 800px, Max Height: 900px

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
    partial_crown_midlines_input = adsk.core.IntegerSpinnerCommandInput.cast(
        inputs.itemById('partial_crown_midlines'))
    draw_crown_quarters_input = adsk.core.BoolValueCommandInput.cast(
        inputs.itemById('draw_crown_quarters'))
    partial_crown_quarters_input = adsk.core.IntegerSpinnerCommandInput.cast(
        inputs.itemById('partial_crown_quarters'))
    coincident_points_input = adsk.core.BoolValueCommandInput.cast(
        inputs.itemById('create_coincident_points'))

    # Fold-lock inputs
    gap_centerlines_interior_only_input = adsk.core.BoolValueCommandInput.cast(
        inputs.itemById('gap_centerlines_interior_only'))
    use_fold_lock_table_input = adsk.core.BoolValueCommandInput.cast(
        inputs.itemById('use_fold_lock_table'))
    balloon_wall_um_input = adsk.core.IntegerSpinnerCommandInput.cast(
        inputs.itemById('balloon_wall_um'))
    body_gap_mm_input = adsk.core.ValueCommandInput.cast(
        inputs.itemById('body_gap_mm'))
    draw_fold_lock_limits_input = adsk.core.BoolValueCommandInput.cast(
        inputs.itemById('draw_fold_lock_limits'))
    fold_lock_columns_input = adsk.core.StringValueCommandInput.cast(
        inputs.itemById('fold_lock_columns'))

    reset_button_input = adsk.core.BoolValueCommandInput.cast(
        inputs.itemById('reset_to_defaults'))

    # Check if reset button was clicked
    if reset_button_input.value:
        # Reset all values to defaults
        diameter_input.value = default_values['diameter']
        length_input.value = default_values['length']
        num_rings_input.value = default_values['num_rings']
        crowns_per_ring_input.value = default_values['crowns_per_ring']
        height_factors_input.value = default_values['height_factors']
        gap_input.value = default_values['gap_between_rings']
        draw_border_input.value = default_values['draw_border']
        draw_gap_centerlines_input.value = default_values['draw_gap_centerlines']
        draw_crown_peaks_input.value = default_values['draw_crown_peaks']
        draw_crown_waves_input.value = default_values['draw_crown_waves']
        draw_crown_midlines_input.value = default_values['draw_crown_midlines']
        draw_crown_h_midlines_input.value = default_values['draw_crown_h_midlines']
        partial_crown_midlines_input.value = default_values['partial_crown_midlines']
        draw_crown_quarters_input.value = default_values['draw_crown_quarters']
        partial_crown_quarters_input.value = default_values['partial_crown_quarters']
        coincident_points_input.value = default_values['create_coincident_points']

        # Reset the button itself
        reset_button_input.value = False

        # Update last_used_values with defaults
        last_used_values.update(default_values.copy())

        return  # Exit early to just reset, don't execute

    # Get values
    diameter = diameter_input.value * 10  # Convert cm to mm
    length = length_input.value * 10      # Convert cm to mm
    num_rings = num_rings_input.value
    crowns_per_ring = crowns_per_ring_input.value
    height_factors_str = height_factors_input.value
    gap_str = gap_input.value

    draw_border = draw_border_input.value
    draw_gap_centerlines = draw_gap_centerlines_input.value
    draw_crown_peaks = draw_crown_peaks_input.value
    draw_crown_waves = draw_crown_waves_input.value
    draw_crown_midlines = draw_crown_midlines_input.value
    draw_crown_h_midlines = draw_crown_h_midlines_input.value
    partial_crown_midlines = partial_crown_midlines_input.value
    draw_crown_quarters = draw_crown_quarters_input.value
    partial_crown_quarters = partial_crown_quarters_input.value
    create_coincident_points = coincident_points_input.value

    # Fold-lock values
    gap_centerlines_interior_only = gap_centerlines_interior_only_input.value
    use_fold_lock_table = use_fold_lock_table_input.value
    balloon_wall_um = balloon_wall_um_input.value
    body_gap_mm = body_gap_mm_input.value
    draw_fold_lock_limits = draw_fold_lock_limits_input.value
    fold_lock_columns = fold_lock_columns_input.value

    # Parse height factors
    try:
        height_factors = [float(x.strip())
                          for x in height_factors_str.split(',')]
        # Ensure we have the right number of factors
        while len(height_factors) < num_rings:
            height_factors.append(1.0)
        height_factors = height_factors[:num_rings]
    except:
        height_factors = [1.0] * num_rings

    # Parse gap values
    try:
        gap_values = [float(x.strip()) for x in gap_str.split(',')]
        # Ensure we have the right number of gap values (num_rings - 1 gaps between rings)
        needed_gaps = max(1, num_rings - 1)  # At least 1 gap value needed
        while len(gap_values) < needed_gaps:
            # Repeat last value or default
            gap_values.append(gap_values[-1] if gap_values else 0.2)
        gap_values = gap_values[:needed_gaps]
    except:
        gap_values = [0.2] * max(1, num_rings - 1)  # Default 0.2mm gaps

    # Apply fold-lock table if enabled
    if use_fold_lock_table and num_rings >= 2:
        # Fold-lock table: tighter end gaps based on balloon wall thickness
        if balloon_wall_um <= 12:
            end_gap = 0.095  # mm
        elif balloon_wall_um <= 16:
            end_gap = 0.095  # mm
        elif balloon_wall_um <= 20:
            end_gap = 0.100  # mm
        else:
            end_gap = 0.110  # mm

        # Override first and last gaps
        gap_values[0] = end_gap
        if len(gap_values) > 1:
            gap_values[-1] = end_gap

        # Set interior gaps to body_gap_mm
        for i in range(1, len(gap_values) - 1):
            gap_values[i] = body_gap_mm

    # Save current values for next session (before calling drawing function)
    last_used_values.update({
        'diameter': diameter_input.value,
        'length': length_input.value,
        'num_rings': num_rings,
        'crowns_per_ring': crowns_per_ring,
        'height_factors': height_factors_str,
        'gap_between_rings': gap_str,
        'draw_border': draw_border,
        'draw_gap_centerlines': draw_gap_centerlines,
        'draw_crown_peaks': draw_crown_peaks,
        'draw_crown_waves': draw_crown_waves,
        'draw_crown_midlines': draw_crown_midlines,
        'draw_crown_h_midlines': draw_crown_h_midlines,
        'partial_crown_midlines': partial_crown_midlines,
        'draw_crown_quarters': draw_crown_quarters,
        'partial_crown_quarters': partial_crown_quarters,
        'create_coincident_points': create_coincident_points,
        'gap_centerlines_interior_only': gap_centerlines_interior_only,
        'use_fold_lock_table': use_fold_lock_table,
        'balloon_wall_um': balloon_wall_um,
        'body_gap_mm': body_gap_mm,
        'draw_fold_lock_limits': draw_fold_lock_limits,
        'fold_lock_columns': fold_lock_columns
    })

    # Call the stent frame drawing function
    draw_stent_frame(diameter, length, num_rings, crowns_per_ring,
                     height_factors, gap_values, draw_border, draw_gap_centerlines, gap_centerlines_interior_only,
                     draw_crown_peaks, draw_crown_waves, draw_crown_midlines, draw_crown_h_midlines,
                     partial_crown_midlines, draw_crown_quarters, partial_crown_quarters, create_coincident_points,
                     draw_fold_lock_limits, fold_lock_columns)


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

    # Basic validation
    if (diameter_input and length_input and num_rings_input and
            diameter_input.value > 0 and length_input.value > 0 and num_rings_input.value > 0):
        args.areInputsValid = True
    else:
        args.areInputsValid = False


def draw_stent_frame(diameter_mm, length_mm, num_rings, crowns_per_ring,
                     height_factors, gap_values, draw_border, draw_gap_centerlines, gap_centerlines_interior_only,
                     draw_crown_peaks, draw_crown_waves, draw_crown_midlines, draw_crown_h_midlines,
                     partial_crown_midlines, draw_crown_quarters, partial_crown_quarters, create_coincident_points,
                     draw_fold_lock_limits, fold_lock_columns):
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
        sk.name = f'Stent Frame - {num_rings} rings, {crowns_per_ring} crowns'

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

        # Calculate gap center positions (between ring end and next ring start)
        gap_centers = []
        for i in range(num_rings - 1):
            gap_center_y = (ring_end_lines[i] + ring_start_lines[i+1]) / 2
            gap_centers.append(gap_center_y)

        # Use the specified length as total length
        total_length = length_mm

        lines = sk.sketchCurves.sketchLines

        # Draw border
        if draw_border:
            # Left border
            lines.addByTwoPoints(
                adsk.core.Point3D.create(mm_to_cm(0.0), mm_to_cm(0.0), 0),
                adsk.core.Point3D.create(
                    mm_to_cm(0.0), mm_to_cm(total_length), 0)
            )
            # Right border
            lines.addByTwoPoints(
                adsk.core.Point3D.create(mm_to_cm(width_mm), mm_to_cm(0.0), 0),
                adsk.core.Point3D.create(
                    mm_to_cm(width_mm), mm_to_cm(total_length), 0)
            )
            # Top border
            lines.addByTwoPoints(
                adsk.core.Point3D.create(
                    mm_to_cm(0.0), mm_to_cm(total_length), 0),
                adsk.core.Point3D.create(
                    mm_to_cm(width_mm), mm_to_cm(total_length), 0)
            )
            # Bottom border
            lines.addByTwoPoints(
                adsk.core.Point3D.create(mm_to_cm(0.0), mm_to_cm(0.0), 0),
                adsk.core.Point3D.create(mm_to_cm(width_mm), mm_to_cm(0.0), 0)
            )

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
                # For N rings: gaps 1 to N-2 (skipping gap 0 and gap N-1)
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

        # Draw crown wave lines (vertical divisions) - no gaps at start and end
        if draw_crown_waves:
            crown_spacing = width_mm / crowns_per_ring
            # Draw lines for each crown wave (between crowns, not at edges)
            for i in range(1, crowns_per_ring):
                x = i * crown_spacing
                line = lines.addByTwoPoints(
                    adsk.core.Point3D.create(mm_to_cm(x), mm_to_cm(0.0), 0),
                    adsk.core.Point3D.create(
                        mm_to_cm(x), mm_to_cm(total_length), 0)
                )
                line.isConstruction = True

        # Draw crown wave midlines (vertical lines at midpoint between crown waves)
        if draw_crown_midlines or partial_crown_midlines > 0:
            crown_spacing = width_mm / crowns_per_ring
            # Determine how many crowns to draw midlines for
            if partial_crown_midlines > 0:
                # Use partial count (limited from left)
                midlines_count = min(partial_crown_midlines, crowns_per_ring)
            else:
                # Use full count if partial is 0 and main option is enabled
                midlines_count = crowns_per_ring if draw_crown_midlines else 0

            # Draw midlines for the specified number of crowns from left
            for i in range(midlines_count):
                # Midline at the center of each crown section
                x = i * crown_spacing + crown_spacing / 2

                line = lines.addByTwoPoints(
                    adsk.core.Point3D.create(mm_to_cm(x), mm_to_cm(0.0), 0),
                    adsk.core.Point3D.create(
                        mm_to_cm(x), mm_to_cm(total_length), 0)
                )
                line.isConstruction = True

        # Draw crown horizontal midlines (horizontal lines at midpoint of each crown height)
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

        # Draw crown quarter lines (vertical lines at 1/4 and 3/4 positions within each crown)
        if draw_crown_quarters or partial_crown_quarters > 0:
            crown_spacing = width_mm / crowns_per_ring
            # Determine how many crowns to draw quarter lines for
            if partial_crown_quarters > 0:
                # Use partial count (limited from left)
                quarters_count = min(partial_crown_quarters, crowns_per_ring)
            else:
                # Use full count if partial is 0 and main option is enabled
                quarters_count = crowns_per_ring if draw_crown_quarters else 0

            # Draw quarter lines for the specified number of crowns from left
            for i in range(quarters_count):
                # Quarter line at 1/4 position
                x_quarter = i * crown_spacing + crown_spacing / 4
                line = lines.addByTwoPoints(
                    adsk.core.Point3D.create(
                        mm_to_cm(x_quarter), mm_to_cm(0.0), 0),
                    adsk.core.Point3D.create(
                        mm_to_cm(x_quarter), mm_to_cm(total_length), 0)
                )
                line.isConstruction = True

                # Quarter line at 3/4 position
                x_three_quarter = i * crown_spacing + 3 * crown_spacing / 4
                line = lines.addByTwoPoints(
                    adsk.core.Point3D.create(
                        mm_to_cm(x_three_quarter), mm_to_cm(0.0), 0),
                    adsk.core.Point3D.create(
                        mm_to_cm(x_three_quarter), mm_to_cm(total_length), 0)
                )
                line.isConstruction = True

        # Draw fold-lock limit lines in specified crown boxes
        if draw_fold_lock_limits and fold_lock_columns:
            try:
                # Parse fold-lock column indices
                fold_lock_indices = [int(x.strip()) for x in fold_lock_columns.split(
                    ',') if x.strip().isdigit()]
                crown_spacing = width_mm / crowns_per_ring

                # Calculate fold-lock limits (typically 60-70% of crown width)
                fold_lock_fraction = 0.65  # 65% of crown width

                for crown_idx in fold_lock_indices:
                    if 0 <= crown_idx < crowns_per_ring:
                        # Calculate crown box boundaries
                        crown_left = crown_idx * crown_spacing
                        crown_right = (crown_idx + 1) * crown_spacing
                        crown_center = (crown_left + crown_right) / 2

                        # Calculate fold-lock limit positions
                        limit_offset = crown_spacing * fold_lock_fraction / 2
                        left_limit = crown_center - limit_offset
                        right_limit = crown_center + limit_offset

                        # Draw horizontal lines within the gaps for this crown box
                        # For each gap between rings, draw horizontal fold-lock limit lines
                        for gap_idx in range(len(gap_centers)):
                            gap_center_y = gap_centers[gap_idx]
                            
                            # Draw horizontal fold-lock limit line (left to right within the crown box)
                            line = lines.addByTwoPoints(
                                adsk.core.Point3D.create(
                                    mm_to_cm(left_limit), mm_to_cm(gap_center_y), 0),
                                adsk.core.Point3D.create(
                                    mm_to_cm(right_limit), mm_to_cm(gap_center_y), 0)
                            )
                            line.isConstruction = True

            except ValueError:
                # Ignore invalid fold-lock column format
                pass

        # Show summary
        if ui:
            # Count the lines that were actually drawn
            lines_inside_box = len([r for r in ring_start_lines if 0 < r < total_length]) + \
                len([r for r in ring_end_lines if 0 < r < total_length]) + \
                len(gap_centers)

            # Count crown waves and midlines
            crown_waves_count = crowns_per_ring - 1 if draw_crown_waves else 0

            # Count actual midlines drawn (partial or full)
            if partial_crown_midlines > 0:
                midlines_count = min(partial_crown_midlines, crowns_per_ring)
            else:
                midlines_count = crowns_per_ring if draw_crown_midlines else 0

            h_midlines_count = num_rings if draw_crown_h_midlines else 0

            # Count actual quarter lines drawn (partial or full)
            if partial_crown_quarters > 0:
                # 2 lines per crown
                quarters_count = min(
                    partial_crown_quarters, crowns_per_ring) * 2
            else:
                quarters_count = (crowns_per_ring *
                                  2) if draw_crown_quarters else 0

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

                    # Add crown wave lines
                    if draw_crown_waves:
                        crown_width = width_mm / crowns_per_ring
                        # Only add lines that are actually drawn (between crowns, not at borders)
                        for crown in range(1, crowns_per_ring):
                            x = crown * crown_width
                            vertical_lines.append(x)

                    # Add crown midlines (full or partial)
                    if draw_crown_midlines or partial_crown_midlines > 0:
                        crown_width = width_mm / crowns_per_ring
                        midlines_to_draw = partial_crown_midlines if partial_crown_midlines > 0 else crowns_per_ring
                        for crown in range(min(midlines_to_draw, crowns_per_ring)):
                            midline_x = (crown + 0.5) * crown_width
                            vertical_lines.append(midline_x)

                    # Add crown quarter lines (full or partial)
                    if draw_crown_quarters or partial_crown_quarters > 0:
                        crown_width = width_mm / crowns_per_ring
                        quarters_to_draw = partial_crown_quarters if partial_crown_quarters > 0 else crowns_per_ring
                        for crown in range(min(quarters_to_draw, crowns_per_ring)):
                            quarter1_x = (crown + 0.25) * crown_width
                            quarter3_x = (crown + 0.75) * crown_width
                            vertical_lines.extend([quarter1_x, quarter3_x])

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

            ui.messageBox(
                f'Stent frame created successfully!\n'
                f'• Diameter: {diameter_mm:.3f} mm\n'
                f'• Length: {length_mm:.3f} mm\n'
                f'• Width (circumference): {width_mm:.3f} mm\n'
                f'• Rings: {num_rings}\n'
                f'• Crowns per ring: {crowns_per_ring}\n'
                f'• Scaled ring heights: {[f"{h:.3f}" for h in scaled_ring_heights]}\n'
                f'• Gap values: {[f"{g:.3f}" for g in gap_values[:num_gaps]]} mm\n'
                f'• Ring scale factor: {ring_scale_factor:.3f}\n'
                f'• Horizontal lines inside box: {lines_inside_box}\n'
                f'• Vertical crown waves: {crown_waves_count}\n'
                f'• Vertical crown midlines: {midlines_count}\n'
                f'• Vertical crown quarter lines: {quarters_count}\n'
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
