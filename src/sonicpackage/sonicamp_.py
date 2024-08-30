import asyncio
import json
import logging
from typing import Any, Literal, Optional, Union, Iterable, Dict

import attrs
from icecream import ic
from sonicpackage.amp_data import Info, Status
from sonicpackage.commands import Command, CommandValidator
from sonicpackage.interfaces import Scriptable
from sonicpackage.procedures.procs.ramper import Ramper
from sonicpackage.communication.serial_communicator import Communicator

CommandValitors = Union[CommandValidator, Iterable[CommandValidator]]

parrot_feeder = logging.getLogger("parrot_feeder")


@attrs.define(kw_only=True)
class SonicAmp(Scriptable):
    _serial: Communicator = attrs.field()
    _commands: Dict[str, Command] = attrs.field(factory=dict, converter=dict)
    _logger: logging.Logger = attrs.field(default=logging.getLogger())

    _status: Status = attrs.field()
    _info: Info = attrs.field()
    _ramp: Optional[Ramper] = attrs.field(init=False, default=None)

    def __attrs_post_init__(self) -> None:
        self._logger = logging.getLogger(self._logger.name + "." + SonicAmp.__name__)

    @property
    def serial(self) -> Communicator:
        return self._serial

    @serial.setter
    def serial(self, serial: Communicator) -> None:
        self._serial = serial

    @property
    def commands(self) -> Dict[str, Command]:
        return self._commands

    @property
    def status(self) -> Status:
        return self._status

    @property
    def info(self) -> Info:
        return self._info

    def get_remote_proc_finished_event(self) -> asyncio.Event:
        return self._status.remote_proc_finished_running

    async def disconnect(self) -> None:
        if self.serial.connection_opened.is_set():
            self._logger.info("Disconnect")
            await self.serial.close_communication()
            del self

    def add_command(
        self,
        message: Union[str, Command],
        validators: Optional[CommandValitors] = None,
        **kwargs,
    ) -> None:
        """
        Adds a command to the SonicAmp object.

        Args:
            message (Union[str, Command]): The command message to add. It can be either a string or a Command object.
            validators (Optional[CommandValitors], optional): The validators to apply to the command. Defaults to None.
            **kwargs: Additional keyword arguments to pass to the Command constructor.

        Raises:
            ValueError: If the message argument is not a string or a Command object.

        Returns:
            None
        """
        if isinstance(message, Command):
            if validators is not None:
                message.add_validators(validators)
            self._commands[message.message] = message
        elif isinstance(message, str):
            self._commands[message] = Command(
                message=message, validators=validators, **kwargs
            )
        else:
            raise ValueError("Illegal Argument for message", {message})

    def add_commands(self, commands: Iterable[Command]) -> None:
        for command in commands:
            self.add_command(command)

    def has_command(self, command: Union[str, Command]) -> bool:
        return (
            self.commands.get(
                command.message if isinstance(command, Command) else command
            ) is not None
        )

    async def send_message(self, message: str = "", argument: Any = "") -> str:
        return (
            await Command(
                message=message,  
                argument=argument,  
                estimated_response_time=0.4,
                expects_long_answer=True,
                serial_communication=self._serial
            ).execute()
        )[0].string

    async def execute_command(
        self,
        message: Union[str, Command],
        argument: Any = "",
        **status_kwargs_if_valid_command,
    ) -> str:
        """
        Executes a command by sending a message to the SonicAmp device and updating the status accordingly.

        Args:
            message (Union[str, Command]): The command message to execute. It can be either a string or a Command object.
            argument (Any, optional): The argument to pass to the command. Defaults to an empty string.
            **status_kwargs_if_valid_command: Additional keyword arguments to update the status if the command is valid.

        Returns:
            str: The string representation of the command's answer.

        Raises:
            Exception: If an error occurs during command execution or device disconnection.

        Note:
            - If the command is not found in the SonicAmp device's commands, it will be executed as a new command.
            - The status of the device will be updated with the command's status result and any additional status keyword arguments.
            - The command's answer will be returned as a string.

        Example:
            >>> sonicamp = SonicAmp()
            >>> await sonicamp.execute_command("power_on")
            "Device powered on."
        """
        try:
            message = message if isinstance(message, str) else message.message
            if message != "-":
                self._logger.debug("Execute command %s with argument %s", message, str(argument))
            if message not in self._commands.keys():
                self._logger.debug("Command not found in commands of sonicamp %s", message)
                self._logger.debug("Executing message as a new Command...")
                return await self.send_message(message=message, argument=argument)
            
            command: Command = self._commands[message]
            await command.execute(argument=argument, connection=self._serial)
        except Exception as e:
            self._logger.error(e)
            await self.disconnect()

        await self._status.update(
            **command.status_result, **status_kwargs_if_valid_command
        )

        parrot_feeder.debug("DEVICE_STATE(%s)", json.dumps(self._status.get_dict()))

        return command.answer.string

    async def get_help(self) -> str:
        return await self.execute_command("?help")

    async def set_signal_off(self) -> str:
        return await self.execute_command("!OFF", urms=0.0, irms=0.0, phase=0.0)

    async def set_signal_on(self) -> str:
        return await self.execute_command("!ON")

    async def set_signal_auto(self) -> str:
        return await self.execute_command("!AUTO")

    async def get_info(self) -> str:
        return await self.execute_command("?info")

    async def get_overview(self) -> str:
        return await self.execute_command("?")

    async def get_type(self) -> str:
        return await self.execute_command("?type")

    async def get_status(self) -> str:
        return await self.execute_command("-")

    async def get_sens(self) -> str:
        return await self.execute_command("?sens")

    async def set_serial_mode(self) -> str:
        return await self.execute_command("!SERIAL")

    async def set_analog_mode(self) -> str:
        return await self.execute_command("!ANALOG")

    async def set_frequency(self, frequency: int) -> str:
        return await self.execute_command("!f=", frequency)

    async def set_switching_frequency(self, frequency: int) -> str:
        return await self.execute_command("!swf=", frequency)

    async def set_gain(self, gain: int) -> str:
        return await self.execute_command("!g=", gain)

    async def set_relay_mode_mhz(self) -> str:
        return await self.execute_command("!MHZ")

    async def set_relay_mode_khz(self) -> str:
        return await self.execute_command("!KHZ")

    async def set_atf(self, index: int, frequency: int) -> str:
        return await self.execute_command(f"!atf{index}=", frequency)

    async def get_atf(self, index: int) -> str:
        return await self.execute_command(f"?atf{index}")

    async def set_atk(self, index: int, coefficient: float) -> str:
        return await self.execute_command(f"!atk{index}=", coefficient)

    async def set_att(self, index: int, temperature: float) -> str:
        return await self.execute_command(f"!att{index}=", temperature)

    async def get_att(self, index: int) -> str:
        return await self.execute_command(f"?att{index}")

    async def set_aton(self, index: int, time_ms: int) -> str:
        return await self.execute_command(f"!aton{index}=", time_ms)

