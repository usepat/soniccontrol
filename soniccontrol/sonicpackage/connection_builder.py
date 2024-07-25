import asyncio
from typing import Callable, Any
from serial_asyncio import open_serial_connection

from soniccontrol.sonicpackage.commands import CommandSet
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
    ) -> tuple[Communicator, CommandSet]:
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
        commands: CommandSet = CommandSet().with_legacy_commands(serial)
        await commands.get_info.execute()
        if commands.get_info.answer.valid:
            logger.info("Connected with legacy protocol")
            return (serial, commands)
        else:
            serial.disconnect()

        serial = SerialCommunicator(**kwargs)
        await serial.connect(reader, writer)
        commands = CommandSet().with_new_commands(serial)
        await commands.get_info.execute()

        # if commands.get_info.answer.valid:
        #     logger.info("Connected with sonic protocol")
        #     return (serial, commands)

        # raise ConnectionError("Failed to connect due to incompatibility")

        # TODO: fix this. Define with Thomas an interface for ?info and implement it.

        logger.info("Connected with sonic protocol")
        return (serial, commands)


async def main():
    cb = ConnectionBuilder("COM7", 115200)
    serial = await cb.build()


if __name__ == "__main__":
    asyncio.run(main())
