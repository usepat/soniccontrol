from soniccontrol_gui import start_gui
from sonic_test_parrot import setup_parrot_feeder


if __name__ == "__main__":
    setup_parrot_feeder()
    start_gui(simulation_enabled=True)