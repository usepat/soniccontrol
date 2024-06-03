import asyncio
import json
import logging
import pathlib

import soniccontrol.utils.constants as const
from soniccontrol.sonicpackage.builder import AmpBuilder
from soniccontrol.sonicpackage.serial_communicator import SerialCommunicator
from soniccontrol.sonic_test_parrot.parrot import Parrot

def setup_logging() -> None:
    config_file: pathlib.Path = const.files.LOGGING_CONFIG
    with config_file.open() as file:
        config = json.load(file)
    logging.config.dictConfig(config)

async def simulate_soniccontrol_user_interaction():
    process = await asyncio.create_subprocess_shell(
        "/home/david-wild/Documents/sonic-firmware/build/linux/test/cli/cli_simulation_mvp/cli_simulation_mvp",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT
    )
    communicator = SerialCommunicator()
    await communicator.connect(process.stdout, process.stdin)

    builder = AmpBuilder()
    sonicamp = await builder.build_amp(communicator)
    await sonicamp.execute_command("!f=", "100")
    await sonicamp.execute_command("?uipt")
    await sonicamp.execute_command("!ON")
    communicator.disconnect()
    process.terminate()
    await process.wait()

async def main():
    setup_logging()

    await simulate_soniccontrol_user_interaction()

    process = await asyncio.create_subprocess_shell(
        "/home/david-wild/Documents/sonic-firmware/build/linux/test/cli/cli_simulation_mvp/cli_simulation_mvp",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT
    )
    communicator = SerialCommunicator()
    await communicator.connect(process.stdout, process.stdin)

    # if you do not want to feed the parrot when starting soniccontrol, then just set the logging to a higher level than debug 
    with open("./logs/parrot_food_logs_for_integration_tesing.log", "r") as file:
        log_lines = file.readlines()

    parrot = Parrot(communicator, log_lines)
    parrot.register_parrot_log_handler(logging.getLogger("parrot_feeder"))
    await parrot.setup_amp()
    await parrot.run_imitation()


if __name__ == "__main__":
    asyncio.run(main())