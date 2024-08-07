import asyncio
from src.sonic_test_parrot.training import *


async def simulate_soniccontrol_user_interaction(sonicamp: SonicAmp):
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


if __name__ == "__main__":
    asyncio.run(main_cli())
