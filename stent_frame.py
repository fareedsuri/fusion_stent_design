# Fusion 360 – Stent Frame Designer
# • Customizable stent frame with form input
# • Diameter, length, number of rings, crowns per ring
# • Ring height proportions and gap between rings
# • Draw border, gap centerlines, crown peaks, and crown wave lines
import math
import traceback

# Global variables to store modules
cmdDialog = None
gptDataProcessor = None

try:
    import adsk.core
    import adsk.fusion
    from .commands.commandDialog import entry as cmdDialog
    # Try to import GPT Data processor separately
    try:
        from .commands.gptDataProcessor import entry as gptDataProcessor
    except Exception:
        gptDataProcessor = None
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
        # Try to import GPT Data processor separately
        try:
            from commands.gptDataProcessor import entry as gptDataProcessor
        except Exception:
            gptDataProcessor = None
    except Exception:
        pass

# Helper functions for calculations


def mm_to_cm(x):
    """Convert millimeters to centimeters for Fusion API"""
    return x * 0.1


def run(context):
    """Main entry point - starts the command dialog and GPT Data processor"""
    global cmdDialog, gptDataProcessor

    print("DEBUG: Starting Stent Frame add-in...")

    # First, ensure we have the main command
    if cmdDialog is None:
        try:
            print("DEBUG: Attempting to import cmdDialog...")
            # Try to import again if it failed initially
            from .commands.commandDialog import entry as cmdDialog
            print("DEBUG: cmdDialog imported successfully")
        except Exception as e:
            print(f"DEBUG: cmdDialog import 1 failed: {e}")
            try:
                from commands.commandDialog import entry as cmdDialog
                print("DEBUG: cmdDialog imported successfully (fallback)")
            except Exception as e2:
                print(f"DEBUG: cmdDialog import 2 failed: {e2}")
                pass

    # Try to import GPT Data processor if we haven't already
    if gptDataProcessor is None:
        try:
            print("DEBUG: Attempting to import gptDataProcessor...")
            from .commands.gptDataProcessor import entry as gptDataProcessor
            print("DEBUG: gptDataProcessor imported successfully")
        except Exception as e:
            print(f"DEBUG: gptDataProcessor import 1 failed: {e}")
            try:
                from commands.gptDataProcessor import entry as gptDataProcessor
                print("DEBUG: gptDataProcessor imported successfully (fallback)")
            except Exception as e2:
                print(f"DEBUG: gptDataProcessor import 2 failed: {e2}")
                pass

    try:
        # Start the main command (this must work)
        if cmdDialog:
            print("DEBUG: Starting cmdDialog...")
            cmdDialog.start()
            print("DEBUG: cmdDialog started successfully")
        else:
            raise Exception("Could not import main command dialog module")

        # Start GPT Data processor if available
        if gptDataProcessor:
            try:
                print("DEBUG: Starting gptDataProcessor...")
                gptDataProcessor.start()
                print("DEBUG: gptDataProcessor started successfully")
            except Exception as e:
                print(f"WARNING: GPT Data processor failed to start: {e}")
                import traceback
                print(
                    f"GPT Data processor traceback: {traceback.format_exc()}")
        else:
            print("DEBUG: gptDataProcessor is None, not starting")

        print("DEBUG: Stent Frame add-in startup completed")

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
    global cmdDialog, gptDataProcessor
    try:
        if cmdDialog:
            cmdDialog.stop()
    except Exception:
        pass

    try:
        if gptDataProcessor:
            gptDataProcessor.stop()
    except Exception:
        pass
