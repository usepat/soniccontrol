import asyncio
import json
import logging
import pathlib
from typing import Callable, List, Optional, Union
import typing
import shutil
from serial_asyncio import open_serial_connection

from soniccontrol.sonicpackage.sonicamp_ import SonicAmp
import soniccontrol.utils.constants as const
from soniccontrol.sonicpackage.builder import AmpBuilder
from soniccontrol.sonicpackage.serial_communicator import SerialCommunicator
from soniccontrol.sonic_test_parrot.parrot import Parrot


def setup_logging() -> None:
    config_file: pathlib.Path = const.files.LOGGING_CONFIG
    with config_file.open() as file:
        config = json.load(file)
    logging.config.dictConfig(config)


CommandList = List[List[str]]
CommandCaller = Callable[[SonicAmp], typing.Coroutine]
async def teach_parrot(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, commands: Union[CommandList, CommandCaller], parrot_food_file: Optional[str] = None):
    communicator = SerialCommunicator()
    await communicator.connect(reader, writer)

    builder = AmpBuilder()
    sonicamp = await builder.build_amp(communicator)
    
    if isinstance(commands, list):
        for command in commands:
            await sonicamp.execute_command(*command)
    elif callable(commands):
        await commands(sonicamp)

    await communicator.stop()

    if parrot_food_file is not None:
        parrot_feeder = logging.getLogger("parrot_feeder")
        log_filename = parrot_feeder.handlers[0].baseFilename
        shutil.copy(log_filename, parrot_food_file)


async def test_parrot(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, parrot_food_file: Optional[str] = None):
    communicator = SerialCommunicator()
    await communicator.connect(reader,writer)

    parrot_feeder = logging.getLogger("parrot_feeder")
    if parrot_food_file is None:
        parrot_food_file = parrot_feeder.handlers[0].baseFilename
    # if you do not want to feed the parrot when starting soniccontrol, then just set the logging to a higher level than debug 
    with open(parrot_food_file, "r") as file:
        log_lines = file.readlines()

    if len(log_lines) == 0:
        raise Exception("Parrot cannot imitate, because the logs are empty")

    parrot = Parrot(communicator, log_lines)
    parrot.register_parrot_log_handler(parrot_feeder)
    await parrot.setup_amp()
    await parrot.run_imitation()

    await communicator.stop()


async def uart_wrapper(port, baudrate, func, *args, **kwargs):
    reader, writer = await open_serial_connection(url=port, baudrate=baudrate)
    return await func(reader, writer, *args, **kwargs)


async def cli_wrapper(process_name, func, *args, **kwargs):
    process = await asyncio.create_subprocess_shell(
        process_name,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT
    )

    result = await func(process.stdout, process.stdin, *args, **kwargs)

    process.terminate()
    await process.wait()

    return result
