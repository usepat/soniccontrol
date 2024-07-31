import asyncio
import logging
from typing import Union

from soniccontrol.sonicpackage.commands import CommandSet, CommandSetLegacy
from soniccontrol.sonicpackage.interfaces import Communicator
from soniccontrol.sonicpackage.serial_communicator import (
    LegacySerialCommunicator,
    SerialCommunicator,
)

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
            ConnectionError: If the connection fails due to incompatibility or the device is not responding.

        """

        logger = kwargs.get("logger", logging.getLogger())
        logger = logging.getLogger(logger.name + "." + ConnectionBuilder.__name__)

        logger.info("Trying to connect with legacy protocol")
        serial: Communicator = LegacySerialCommunicator()

        await serial.open_communication(reader, writer)
        commands: Union[CommandSet, CommandSetLegacy] = CommandSetLegacy(serial)
        await commands.get_info.execute()
        if commands.get_info.answer.valid:
            logger.info("Connected with legacy protocol")
            serial.subscribe(serial.DISCONNECTED_EVENT, lambda _e: writer.close())
            return (serial, commands)
        else:
            await serial.close_communication()
            logger.warn("Connection could not be established with legacy protocol")

        logger.info("Trying to connect with new sonic protocol")
        serial = SerialCommunicator(**kwargs)
        await serial.open_communication(reader, writer)
        commands = CommandSet(serial)
        await commands.get_info.execute()

        if commands.get_info.answer.valid:
            logger.info("Connected with sonic protocol")
            serial.subscribe(serial.DISCONNECTED_EVENT, lambda _e: writer.close())
            return (serial, commands)

        # TODO: fix this. Define with Thomas an interface for ?info and implement it.
        logger.info("Connected with sonic protocol")
        serial.subscribe(serial.DISCONNECTED_EVENT, lambda _e: writer.close())
        return (serial, commands)
    
        # raise ConnectionError("Failed to connect due to incompatibility")

