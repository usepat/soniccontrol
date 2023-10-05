from typing import *
import asyncio
from icecream import ic
import attrs
from soniccontrol.sonicpackage.interfaces import Scriptable, Updater
from soniccontrol.sonicpackage.serial_communicator import SerialCommunicator
from soniccontrol.sonicpackage.commands import Command, Commands, CommandValidator
from soniccontrol.sonicpackage.amp_data import Status, Info


CommandValitors = Union[CommandValidator, Iterable[CommandValidator]]


@attrs.define
class MeasureUpdater(Updater):
    async def worker(self) -> None:
        await self._device.get_sens()


@attrs.define
class StatusUpdater(Updater):
    async def worker(self) -> None:
        await self._device.get_status()


@attrs.define
class OverviewUpdater(Updater):
    async def worker(self) -> None:
        await self._device.get_overview()


@attrs.define(kw_only=True)
class SonicAmp(Scriptable):
    _serial: SerialCommunicator = attrs.field()
    _commands: Dict[str, Command] = attrs.field(factory=dict, converter=dict)
    _status: Status = attrs.field()
    _info: Info = attrs.field()
    _updater: Updater = attrs.field(init=False, default=None)
    # _ramper: Ramper = attrs.field(init=False, factory=Ramper)
    # _holder: Holder = attrs.field(init=False, factory=Holder)
    # _sequencer: Sequencer = attrs.field(init=False, factory=Sequencer)

    def __attrs_post_init__(self) -> None:
        self.updater = OverviewUpdater(self)

    @property
    def serial(self) -> None:
        return self._serial

    @serial.setter
    def serial(self, serial: SerialCommunicator) -> None:
        self._serial = serial

    @property
    def updater(self) -> Updater:
        return self._updater

    @updater.setter
    def updater(self, updater: Updater) -> None:
        if self._updater is not None and (
            type(self._updater) == type(updater) or self._updater is updater
        ):
            return
        if self._updater is not None:
            self._updater.stop_execution()
        self._updater = updater
        self._updater.execute()

    @property
    def commands(self) -> Dict[str, Command]:
        return self._commands

    @property
    def status(self) -> Status:
        return self._status

    @property
    def info(self) -> Info:
        return self._info

    def add_command(
        self,
        message: Union[str, Command],
        validators: Optional[CommandValitors] = None,
        **kwargs,
    ) -> None:
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

    def has_command(self, command: Union[str, Command]) -> bool:
        return (
            self.commands.get(
                command.message if isinstance(command, Command) else command
            )
            != None
        )

    async def send_message(self, message: str = "", argument: Any = "") -> str:
        return (
            await Command(
                message=message,
                argument=argument,
                estimated_response_time=0.4,
                expects_long_answer=True,
            ).execute(connection=self.serial)
        ).answer.string

    async def execute_command(
        self, message: str, argument: Any = "", **status_kwargs_if_valid_command
    ) -> str:
        if not message in self._commands.keys():
            ic("Command not found in commands of sonicamp", message, self)
            ic("Executing message as a new Command...")
            return await self.send_message(message=message, argument=argument)

        command: Command = self._commands[message]
        await command.execute(argument=argument, connection=self._serial)

        self._status.update(**command.status_result, **status_kwargs_if_valid_command)
        self._check_updater_strategy()
        ic(command.byte_message, command.answer, command.status_result, self._status)

        return command.answer.string

    def _check_updater_strategy(self) -> None:
        if (
            self.status.signal
            and self.status.relay_mode == "MHz"
            and self.has_command("?sens")
        ):
            self.updater = MeasureUpdater(self)
        elif self.has_command("-"):
            self.updater = StatusUpdater(self)
        else:
            self.updater = OverviewUpdater(self)

    async def set_signal_off(self) -> str:
        return await self.execute_command("!OFF", urms=0.0, irms=0.0, phase=0.0)

    async def set_signal_on(self) -> str:
        answer = await self.execute_command("!ON")

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

    async def set_atf1(self, frequency: int) -> str:
        return await self.execute_command("!atf1=", frequency)

    async def set_atk1(self, coefficient: float) -> str:
        return await self.execute_command("!atk1=", coefficient)

    async def get_atf1(self) -> str:
        return await self.execute_command("?atf1")

    async def set_att1(self, temperature: float) -> str:
        return await self.execute_command("!att1=", temperature)

    async def get_att1(self) -> str:
        return await self.execute_command("?att1")

    async def set_atf2(self, frequency: int) -> str:
        return await self.execute_command("!atf2=", frequency)

    async def set_atk2(self, coefficient: float) -> str:
        return await self.execute_command("!atk2=", coefficient)

    async def get_atf2(self) -> str:
        return await self.execute_command("?atf2")

    async def set_atf3(self, frequency: int) -> str:
        return await self.execute_command("!atf3=", frequency)

    async def set_atk3(self, coefficient: float) -> str:
        return await self.execute_command("!atk3=", coefficient)

    async def get_atf3(self) -> str:
        return await self.execute_command("?atf3")

    # async def start_sequence(self, script: str) -> None:
    #     await self._sequencer.execute(script)

    # async def hold(
    #     self,
    #     duration: float = 100,
    #     unit: Literal["ms", "s"] = "ms",
    #     event: asyncio.Event = asyncio.Event(),
    # ) -> None:
    #     await self._holder.execute(duration=duration, unit=unit, external_event=event)


import serial.tools.list_ports as list_ports


async def main():
    ic([port.device for port in list_ports.comports()])
    ser = SerialCommunicator("/dev/cu.usbserial-AB0M45SW")
    await ser.connect()
    await ser.connection_opened.wait()
    Command.set_serial_communication(ser)

    sonicamp = SonicAmp(
        serial=ser,
        info=Info(),
        status=Status(),
    )

    sonicamp.add_command(Commands.signal_on)
    sonicamp.add_command(Commands.signal_off)
    sonicamp.add_command(Commands.get_atf1)
    sonicamp.add_command(Commands.get_atf2)
    sonicamp.add_command(Commands.get_atf3)
    sonicamp.add_command(Commands.get_att1)
    sonicamp.add_command(
        message="?sens",
        estimated_response_time=0.35,
        validators=CommandValidator(
            pattern=r"([\d]+)(?:[\s]+)([-]?[\d]+[.]?[\d]?)(?:[\s]+)([-]?[\d]+[.]?[\d]?)(?:[\s]+)([-]?[\d]+[.]?[\d]?)",
            frequency=int,
            urms=attrs.converters.pipe(float, lambda urms: urms / 1000),
            irms=attrs.converters.pipe(float, lambda irms: irms / 1000),
            phase=attrs.converters.pipe(float, lambda phase: phase / 1_000_000),
        ),
    )
    sonicamp.add_command(Commands.get_status)
    sonicamp.add_command(Commands.get_overview)

    # await sonicamp.set_serial_mode()
    # await sonicamp.set_relay_mode_khz()
    # await sonicamp.get_overview()
    # await sonicamp.get_info()

    await sonicamp.set_signal_on()
    await sonicamp.get_atf1()
    await sonicamp.get_atf2()
    await sonicamp.get_atf3()
    await sonicamp.get_att1()

    # await sonicamp.set_relay_mode_mhz()
    # await sonicamp.set_frequency(1000000)
    # await sonicamp.get_status()
    # await sonicamp.get_status()
    await sonicamp.set_signal_off()
    # await sonicamp.get_status()


if __name__ == "__main__":
    asyncio.run(main())
