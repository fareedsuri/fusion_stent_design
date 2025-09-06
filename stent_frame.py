# Fusion 360 – Stent Frame Designer
# • Customizable stent frame with form input
# • Diameter, length, number of rings, crowns per ring
# • Ring height proportions and gap between rings
# • Draw border, gap centerlines, crown peaks, and crown wave lines
import math
import traceback

# Global variables to store modules
cmdDialog = None
excelProcessor = None

try:
    import adsk.core
    import adsk.fusion
    from .commands.commandDialog import entry as cmdDialog
    # Try to import Excel processor separately
    try:
        from .commands.excelProcessor import entry as excelProcessor
    except Exception:
        excelProcessor = None
except Exception:
    # Try alternative import for when running as script
    try:
        import sys
        import os

        # Add the current directory to the path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.append(current_dir)

        from commands.commandDialog import entry as cmdDialog
        # Try to import Excel processor separately
        try:
            from commands.excelProcessor import entry as excelProcessor
        except Exception:
            excelProcessor = None
    except Exception:
        pass

# Helper functions for calculations


def mm_to_cm(x):
    """Convert millimeters to centimeters for Fusion API"""
    return x * 0.1


def run(context):
    """Main entry point - starts the command dialog and Excel processor"""
    global cmdDialog, excelProcessor

    # First, ensure we have the main command
    if cmdDialog is None:
        try:
            # Try to import again if it failed initially
            from .commands.commandDialog import entry as cmdDialog
        except Exception:
            try:
                from commands.commandDialog import entry as cmdDialog
            except Exception:
                pass

    # Try to import Excel processor if we haven't already
    if excelProcessor is None:
        try:
            from .commands.excelProcessor import entry as excelProcessor
        except Exception:
            try:
                from commands.excelProcessor import entry as excelProcessor
            except Exception:
                pass

    try:
        # Start the main command (this must work)
        if cmdDialog:
            cmdDialog.start()
        else:
            raise Exception("Could not import main command dialog module")

        # Start Excel processor if available
        if excelProcessor:
            try:
                excelProcessor.start()
            except Exception as e:
                print(f"Warning: Excel processor failed to start: {e}")

    except Exception as e:
        ui = None
        try:
            import adsk.core
            app = adsk.core.Application.get()
            ui = app.userInterface
        except Exception:
            pass
        if ui:
            ui.messageBox(
                'Failed to start Stent Frame Designer:\n{}'.format(str(e)))
        else:
            print('Failed to start Stent Frame Designer: {}'.format(str(e)))


def stop(context):
    """Stop the add-in"""
    global cmdDialog, excelProcessor
    try:
        if cmdDialog:
            cmdDialog.stop()
    except Exception:
        pass
    
    try:
        if excelProcessor:
            excelProcessor.stop()
    except Exception:
        pass
