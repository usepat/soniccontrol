import asyncio
import json
import logging
import pathlib

import soniccontrol.utils.constants as const
from soniccontrol.sonicpackage.builder import AmpBuilder
from soniccontrol.sonicpackage.serial_communicator import SerialCommunicator

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
    
    builder = AmpBuilder()
    sonicAmp = await builder.build_amp(communicator)

    for _ in range(10):
        print(await sonicAmp.get_status())


if __name__ == "__main__":
    asyncio.run(main())