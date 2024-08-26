from importlib.resources import files
import sonicpackage.bin

SIMULATION_MVP_EXE: str = str(files(sonicpackage.bin).joinpath("cli_simulation_mvp"))
