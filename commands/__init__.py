# Here you define the commands that will be added to your add-in.

# TODO Import the modules corresponding to the commands you created.
# If you want to add an additional command, duplicate one of the existing directories and import it here.
# You need to use aliases (import "entry" as "my_module") assuming you have the default module named "entry".
from .commandDialog import entry as commandDialog
from .paletteShow import entry as paletteShow
from .paletteSend import entry as paletteSend

# Try to import GPT Data processor, but don't fail if it has issues
gptDataProcessor = None
try:
    from .gptDataProcessor import entry as gptDataProcessor
except Exception as e:
    print(f"Warning: Could not import gptDataProcessor: {e}")
    gptDataProcessor = None

# TODO add your imported modules to this list.
# Fusion will automatically call the start() and stop() functions.
commands = [
    commandDialog,
    paletteShow,
    paletteSend
]

# Add GPT Data processor only if it imported successfully
if gptDataProcessor:
    commands.append(gptDataProcessor)


# Assumes you defined a "start" function in each of your modules.
# The start function will be run when the add-in is started.
def start():
    try:
        # Import fusion utilities for logging
        from ..lib import fusionAddInUtils as futil
        futil.log('Starting all commands...')

        for i, command in enumerate(commands):
            try:
                futil.log(
                    f'Starting command {i+1}: {getattr(command, "CMD_NAME", "Unknown")}')
                command.start()
                futil.log(f'Successfully started command {i+1}')
            except Exception as e:
                futil.log(f'Error starting command {i+1}: {str(e)}')
                import traceback
                futil.log(traceback.format_exc())

        futil.log('Finished starting all commands')
    except Exception as e:
        print(f'Error in commands.start(): {str(e)}')


# Assumes you defined a "stop" function in each of your modules.
# The stop function will be run when the add-in is stopped.
def stop():
    try:
        from ..lib import fusionAddInUtils as futil
        futil.log('Stopping all commands...')

        for command in commands:
            try:
                command.stop()
            except Exception as e:
                futil.log(f'Error stopping command: {str(e)}')

        futil.log('Finished stopping all commands')
    except Exception as e:
        print(f'Error in commands.stop(): {str(e)}')
