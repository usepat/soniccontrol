import asyncio
from soniccontrol.sonic_test_parrot.training import *


async def simulate_soniccontrol_user_interaction(sonicamp: SonicAmp):
    await sonicamp.set_frequency(100)
    await sonicamp.execute_command("?uipt")
    await sonicamp.set_signal_on()


async def main():
    process_name = "/home/david-wild/Documents/sonic-firmware/build/linux/test/cli/cli_simulation_mvp/cli_simulation_mvp"
    await cli_wrapper(process_name, teach_parrot, simulate_soniccontrol_user_interaction)
    await cli_wrapper(process_name, test_parrot)


if __name__ == "__main__":
    asyncio.run(main())
