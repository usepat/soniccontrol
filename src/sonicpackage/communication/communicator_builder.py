import logging
from typing import Union

from sonicpackage.commands import CommandSet, CommandSetLegacy
from sonicpackage.communication.connection_factory import ConnectionFactory
from sonicpackage.communication.communicator import Communicator
from sonicpackage.communication.package_parser import PackageParser
from sonicpackage.communication.serial_communicator import (
    LegacySerialCommunicator,
    SerialCommunicator,
)

class CommunicatorBuilder:
    @staticmethod
    async def build(
        connection_factory: ConnectionFactory, logger: logging.Logger
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

        com_logger = logging.getLogger(logger.name + "." + CommunicatorBuilder.__name__)

        com_logger.info("Trying to connect with legacy protocol")
        serial: Communicator = LegacySerialCommunicator(logger=logger)  #type: ignore
        commands: Union[CommandSet, CommandSetLegacy] = CommandSetLegacy(serial)

        try:
            await serial.open_communication(connection_factory)
            await commands.get_info.execute()
        except Exception as e:
            com_logger.error(str(e))
        else:
            # For some reason the get_info command of the legacy protocol can also understand the new ones.
            # FIXME: Is there some better way to fix this?
            response = commands.get_info.answer.string
            try:
                PackageParser.parse_package(response)
            except SyntaxError:
                pass
            else:
                commands.get_info.answer.valid = False # response is package. Do not use legacy communicator

            if commands.get_info.answer.valid:
                com_logger.info("Connected with legacy protocol")
                return (serial, commands)
            
        await serial.close_communication()
        com_logger.warn("Connection could not be established with legacy protocol")

        com_logger.info("Trying to connect with new sonic protocol")
        serial = SerialCommunicator(logger=logger) #type: ignore
        commands = CommandSet(serial)

        try:
            await serial.open_communication(connection_factory)
            await commands.get_info.execute()
        except Exception as e:
            com_logger.error(str(e))
        else:
            if commands.get_info.answer.valid:
                com_logger.info("Connected with sonic protocol")
                return (serial, commands)
            
        await serial.close_communication()
        com_logger.warning("Connection could not be established with sonic protocol")
        raise ConnectionError("Failed to connect due to incompatibility")