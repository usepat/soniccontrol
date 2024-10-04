import asyncio
import logging
from typing import  Union, Iterable

import attrs
from sonic_protocol.answer import Answer
from sonic_protocol.commands import Command
from sonic_protocol.protocol_builder import CommandLookUpTable
from soniccontrol.command_executor import CommandExecutor
from soniccontrol.device_data import Info, Status
from soniccontrol.commands import  LegacyAnswerValidator
from soniccontrol.interfaces import Scriptable
from soniccontrol.communication.serial_communicator import Communicator

CommandValitors = Union[LegacyAnswerValidator, Iterable[LegacyAnswerValidator]]

parrot_feeder = logging.getLogger("parrot_feeder")


@attrs.define(kw_only=True)
class SonicDevice(Scriptable):
    _communicator: Communicator = attrs.field()
    _logger: logging.Logger = attrs.field(default=logging.getLogger())
    command_executor: CommandExecutor = attrs.field(init=False, on_setattr=None)
    _status: Status = attrs.field()
    _info: Info = attrs.field()

    def __attrs_post_init__(self, lookup_table: CommandLookUpTable) -> None:
        self._logger = logging.getLogger(self._logger.name + "." + SonicDevice.__name__)
        self.command_executor = CommandExecutor(lookup_table, self._communicator)

    @property
    def communicator(self) -> Communicator:
        return self._communicator

    @communicator.setter
    def communicator(self, communicator: Communicator) -> None:
        self._communicator = communicator
        self.command_executor._communicator = communicator

    @property
    def status(self) -> Status:
        return self._status

    @property
    def info(self) -> Info:
        return self._info

    def get_remote_proc_finished_event(self) -> asyncio.Event:
        return self._status.remote_proc_finished_running

    async def disconnect(self) -> None:
        if self.communicator.connection_opened.is_set():
            self._logger.info("Disconnect")
            await self.communicator.close_communication()
            del self

    async def execute_command(
        self,
        command: Command | str,
        should_log: bool = True,
        **status_kwargs_if_valid_command,
    ) -> Answer:
        """
        Executes a command by sending a message to the SonicDevice device and updating the status accordingly.

        Args:
            message (Union[str, Command]): The command message to execute. It can be either a string or a Command object.
            argument (Any, optional): The argument to pass to the command. Defaults to an empty string.
            **status_kwargs_if_valid_command: Additional keyword arguments to update the status if the command is valid.

        Returns:
            str: The string representation of the command's answer.

        Raises:
            Exception: If an error occurs during command execution or device disconnection.

        Note:
            - If the command is not found in the SonicDevice device's commands, it will be executed as a new command.
            - The status of the device will be updated with the command's status result and any additional status keyword arguments.
            - The command's answer will be returned as a string.

        Example:
            >>> sonicamp = SonicDevice()
            >>> await sonicamp.execute_command("power_on")
            "Device powered on."
        """
        try:
            if isinstance(command, str):
                if should_log:
                    self._logger.info("Execute command %s", str(command.__class__))

                answer = await self.command_executor.send_message(
                    command, 
                    estimated_response_time=0.4,
                    expects_long_answer=True
                )
            else:
                if should_log:
                    self._logger.info("Execute command %s", str(command.__class__))
            
                answer = await self.command_executor.send_command(command)
        except Exception as e:
            self._logger.error(e)
            await self.disconnect()
            return Answer(str(e), False, True)

        await self._status.update(**answer.value_dict, **status_kwargs_if_valid_command)
        return answer


    async def set_signal_off(self) -> Answer:
        return await self.execute_command("!OFF")

    async def set_signal_on(self) -> Answer:
        return await self.execute_command("!ON")

    async def get_overview(self) -> Answer:
        return await self.execute_command("?")

