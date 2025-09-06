# Fusion 360 – Stent Frame Designer
# • Customizable stent frame with form input
# • Diameter, length, number of rings, crowns per ring
# • Ring height proportions and gap between rings
# • Draw border, gap centerlines, crown peaks, and crown wave lines
import math
import traceback

# Global variables to store modules
commands = None

try:
    import adsk.core
    import adsk.fusion
    from . import commands
except Exception:
    # Try alternative import for when running as script
    try:
        import sys
        import os

        # Add the current directory to the path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.append(current_dir)

        import commands
    except Exception:
        pass

# Helper functions for calculations


def mm_to_cm(x):
    """Convert millimeters to centimeters for Fusion API"""
    return x * 0.1


def run(context):
    """Main entry point - starts all commands"""
    global commands

    if commands is None:
        try:
            # Try to import again if it failed initially
            from . import commands
        except Exception as e1:
            try:
                import commands
            except Exception as e2:
                # If commands module fails, fall back to just the main dialog
                try:
                    from .commands.commandDialog import entry as cmdDialog
                    cmdDialog.start()
                    return
                except Exception as e3:
                    try:
                        from commands.commandDialog import entry as cmdDialog
                        cmdDialog.start()
                        return
                    except Exception as e4:
                        raise Exception(f"Failed all import attempts: {e1}, {e2}, {e3}, {e4}")

    try:
        if commands:
            commands.start()
        else:
            raise Exception("Could not import commands module")
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
    global commands
    try:
        if commands:
            commands.stop()
    except Exception:
        pass
