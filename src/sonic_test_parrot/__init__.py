from logging.config import dictConfig
from sonic_test_parrot.training import *
from importlib import resources
import json

def setup_parrot_feeder() -> None:
    config_file = resources.files("sonic_test_parrot").joinpath("parrot_feeder_config.json")
    with resources.as_file(config_file) as file:
        file_content = file.read_text()
        config = json.loads(file_content)
    dictConfig(config)

async def simulate_soniccontrol_user_interaction(sonicamp: SonicDevice):
    await sonicamp.set_frequency(100)
    await sonicamp.execute_command("?uipt")
    await sonicamp.set_signal_on()


async def main_cli():
    setup_logging()
    parrot_food_file = "./parrot_cli_test.log"
    process_name = "/home/david-wild/Documents/sonic-firmware/build/linux/test/cli/cli_simulation_mvp/cli_simulation_mvp"
    await cli_wrapper(process_name, teach_parrot, simulate_soniccontrol_user_interaction, parrot_food_file=parrot_food_file)
    await cli_wrapper(process_name, test_parrot, parrot_food_file=parrot_food_file)


async def main_serial():
    setup_logging()
    port = "/dev/cu.usbserial-AB0M45SW"
    baudrate = 40000
    commands = [
        ["!f=", "100"],
        ["?uipt"],
        ["!ON"]
    ]
    await uart_wrapper(port, baudrate, teach_parrot, commands)
    await uart_wrapper(port, baudrate, test_parrot)


