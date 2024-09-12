from pathlib import Path
from soniccontrol_gui import start_gui
from sonic_test_parrot import setup_parrot_feeder
import os

if __name__ == "__main__":
    setup_parrot_feeder()
    simulation_exe_path = Path(os.environ["SIMULATION_EXE_PATH"])
    start_gui(simulation_exe_path)