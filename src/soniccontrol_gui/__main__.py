from soniccontrol_gui import start_gui
import os
from pathlib import Path

if __name__ == "__main__":
    simulation_exe_path = None
    if "SIMULATION_EXE_PATH" in os.environ:
        simulation_exe_path = Path(os.environ["SIMULATION_EXE_PATH"])
    start_gui(simulation_exe_path)
