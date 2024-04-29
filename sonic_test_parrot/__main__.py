import asyncio
import json
import logging
import pathlib

import soniccontrol.utils.constants as const
from soniccontrol.sonicpackage.builder import AmpBuilder
from soniccontrol.sonicpackage.serial_communicator import SerialCommunicator
from sonic_test_parrot.parrot import Parrot

def setup_logging() -> None:
    config_file: pathlib.Path = const.files.LOGGING_CONFIG
    with config_file.open() as file:
        config = json.load(file)
    logging.config.dictConfig(config)

async def main():
    setup_logging()

    process = await asyncio.create_subprocess_shell(
        "/home/david-wild/Documents/sonic-firmware/build/linux/test/cli/cli_simulation_mvp/cli_simulation_mvp",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT
    )
    communicator = SerialCommunicator()
    await communicator.connect(process.stdout, process.stdin)
    
    with open("./logs/soniccontrol.log", "r") as file:
        log_lines = file.readlines()

    parrot = Parrot(communicator, log_lines)
    parrot.register_parrot_log_handler(logging.getLogger())
    await parrot.setup_amp()
    await parrot.run_imitation()


if __name__ == "__main__":
    asyncio.run(main())