import asyncio
from typing import Union

from soniccontrol.sonicpackage.commands import CommandSet, CommandSetLegacy
from soniccontrol.sonicpackage.interfaces import Communicator
from soniccontrol.sonicpackage.serial_communicator import (
    LegacySerialCommunicator,
    SerialCommunicator,
)
from soniccontrol.sonicpackage import logger


class ConnectionBuilder:

    @staticmethod
    async def build(
        reader: asyncio.StreamReader, writer: asyncio.StreamWriter, **kwargs
    ) -> tuple[Communicator, Union[CommandSet, CommandSetLegacy]]:
        """
        Builds a connection using the provided `reader` and `writer` objects.

        Args:
            reader (asyncio.StreamReader): The reader object for the connection.
            writer (asyncio.StreamWriter): The writer object for the connection.
            **kwargs: Additional keyword arguments to be passed to the `SerialCommunicator` constructor.

        Returns:
            tuple[Communicator, Commands]: A tuple containing the `Communicator` object and the `Commands` object
            representing the successful connection.

        Raises:
            ConnectionError: If the connection fails due to incompatibility.

        """

        serial: Communicator = LegacySerialCommunicator()

        await serial.connect(reader, writer)
        commands: Union[CommandSet, CommandSetLegacy] = CommandSetLegacy(serial)
        await commands.get_info.execute()
        if commands.get_info.answer.valid:
            logger.info("Connected with legacy protocol")
            return (serial, commands)

        serial = SerialCommunicator(**kwargs)
        await serial.connect(reader, writer)
        commands = CommandSet(serial)
        await commands.get_info.execute()

        # TODO: fix this. Define with Thomas an interface for ?info and implement it.

        # if commands.get_info.answer.valid:
        #     logger.info("Connected with sonic protocol")
        #     return (serial, commands)

        logger.info("Connected with sonic protocol")
        return (serial, commands)
    
        # raise ConnectionError("Failed to connect due to incompatibility")

