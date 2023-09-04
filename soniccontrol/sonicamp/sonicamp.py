from __future__ import annotations
import asyncio
import copy
from asyncio import Queue, Event
from typing import (
    Optional,
    Callable,
    List,
    Dict,
    Literal,
    Union,
    Iterable,
    Set,
    Any,
    Tuple,
    TypedDict,
)
import serial_asyncio as serial
import sys
import attrs

# from attrs import define, field
import platform
import datetime
import time
import re


ENCODING: str = "windows-1252" if platform.system() == "Windows" else "utf-8"


class CommandValidationDict(TypedDict):
    pattern: str
    return_type: type


@attrs.define
class Command:
    value: Any = attrs.field(default=None)
    message: str = attrs.field(default="")
    arguments: str = attrs.field(default="", converter=str)
    response_time: float = attrs.field(default=0.3)
    expects_long_answer: bool = attrs.field(default=False, repr=False)
    answer_received: asyncio.Event = attrs.field(factory=asyncio.Event)

    _validation_pattern: Optional[CommandValidationDict] = attrs.field(default=None)
    _answer_string: str = attrs.field(default="")
    _answer_lines: List[str] = attrs.field(factory=list)
    _answer_received_timestamp: float = attrs.field(factory=time.time)
    _creation_timestamp: float = attrs.field(factory=time.time)
    _measured_response_timestamp: float = attrs.field(default=time.time)

    def __init__(
        self,
        value: Any = None,
        message: str = "",
        arguments: str = "",
        response_time: float = 0.3,
        *args,
        **kwargs,
    ) -> None:
        self.__attrs_init__(
            message=message,
            arguments=arguments,
            response_time=response_time,
            *args,
            **kwargs,
        )

    def __attrs_post_init__(self) -> None:
        self.arguments = str(self.value) if self.value is not None else ""

    @property
    def answer_string(self) -> str:
        return self._answer_string

    @property
    def answer_lines(self) -> List[str]:
        return self._answer_lines

    @property
    def validation_pattern(self) -> Optional[CommandValidationDict]:
        return self._validation_pattern

    @property
    def byte_message(self) -> bytes:
        return f"{self.message}{self.arguments}\n".encode(ENCODING)

    def receive_answer(self, answer: Union[List[str], str]) -> None:
        if isinstance(answer, list):
            self._answer_lines = answer
            self._answer_string = "\n".join(answer)
        elif isinstance(answer, str):
            self._answer_lines = answer.splitlines()
            self._answer_string = answer
        else:
            raise ValueError(f"{answer = } is not of type {str, list}")
        self._answer_received_timestamp = time.time()
        self._measured_response_timestamp = (
            self._answer_received_timestamp - self._creation_timestamp
        )


class Commands:
    @attrs.define
    class SetFrequency(Command):
        message: str = attrs.field(default="!f=")
        _validation_pattern: CommandValidationDict = {
            "pattern": r"freq[uency]*\s*=?\s*([\d]+)",
            "return_type": int,
        }

    @attrs.define
    class GetStatus(Command):
        message: str = attrs.field(default="-")
        response_time = 0.15
        _validation_pattern: CommandValidationDict = {
            "pattern": r"(.+)(?:[-#])+(.+)",
            "return_type": str,
        }

    @attrs.define
    class GetSens(Command):
        message: str = attrs.field(default="?sens")
        response_time = 0.4
        _validation_pattern: CommandValidationDict = {
            "pattern": r"([\d]+)(?:[\s])+([\d]+)",
            "return_type": str,
        }

    @attrs.define
    class SetGain(Command):
        message: str = attrs.field(default="!g=")
        _validation_pattern: CommandValidationDict = {
            "pattern": r"gain\s*=?\s*([\d]+)",
            "return_type": int,
        }

    @attrs.define
    class SetKhzMode(Command):
        message: str = attrs.field(default="!KHZ")
        _validation_pattern: CommandValidationDict = {
            "pattern": r"(khz)",
            "return_type": str,
        }

    @attrs.define
    class SetMhzMode(Command):
        message: str = attrs.field(default="!MHZ")
        _validation_pattern: CommandValidationDict = {
            "pattern": r"(mhz)",
            "return_type": str,
        }

    @attrs.define
    class SetSignalOn(Command):
        message: str = attrs.field(default="!ON")
        _validation_pattern: CommandValidationDict = {
            "pattern": r"(Signal\s+is\s+?ON|signal\s+on)",
            "return_type": str,
        }

    @attrs.define
    class SetSignalOff(Command):
        message: str = attrs.field(default="!OFF")
        _validation_pattern: CommandValidationDict = {
            "pattern": r"(Signal\s+is\s+?OFF|signal\s+off)",
            "return_type": str,
        }

    @attrs.define
    class SetSignalAuto(Command):
        message: str = attrs.field(default="!AUTO")
        _validation_pattern: CommandValidationDict = {
            "pattern": r"(auto\s*mode\s*on|auto\s*mode|auto)",
            "return_type": str,
        }


class CommandValidator:
    def __init__(self, sonicamp: SonicAmp) -> None:
        self.sonicamp: SonicAmp = sonicamp
        self.validation_patterns: Dict[type, re.Pattern] = {
            command_type: re.compile(
                command_type().validation_pattern["pattern"], re.IGNORECASE
            )
            for command_type in self.sonicamp.commands
        }

    def accepts(self, command: Command) -> bool:
        if command.validation_pattern is None:
            return False

        pattern = self.validation_patterns.get(type(command))
        if pattern is None:
            raise AttributeError(
                f"{Command = } is not part of {self.sonicamp = }'s commands"
            )

        match = pattern.search(command.answer_string)
        if match is None:
            return False

        command.value = command.validation_pattern["return_type"](match.group(1))
        return True

    def find_command(self, answer: str) -> Optional[Command]:
        for command_type in self.sonicamp.commands:
            command: Command = command_type()
            command.receive_answer(answer=answer)
            if self.accepts(command):
                return command


class SerialCommunicator:
    def __init__(self, port: str) -> None:
        self.port: str = port
        self.connection_established: asyncio.Event = asyncio.Event()
        self._connection_open: asyncio.Event = asyncio.Event()

        self.command_queue: Queue[Command] = Queue()
        self.answer_queue: Queue[Command] = Queue()
        self.lock: asyncio.Lock = asyncio.Lock()
        self.encoding: str = (
            "windows-1252" if platform.system() == "Windows" else "utf-8"
        )
        self.reader = None
        self.writer = None
        self.init_message: List[str] = []

    @property
    def connection_open(self) -> asyncio.Event:
        return self._connection_open

    async def setup(self) -> None:
        try:
            self.reader, self.writer = await serial.open_serial_connection(
                url=self.port,
                baudrate=115200,
            )
        except Exception as e:
            print(sys.exc_info())
            self.reader = None
            self.writer = None
        else:
            self.init_message = await self.read_long_message(reading_time=6)
            print("\n".join(self.init_message))
            self.connection_established.set()
            self.connection_open.set()
            asyncio.create_task(self.worker())

    async def worker(self) -> None:
        if self.writer is None or self.reader is None:
            print("No connection available")
            return
        while not self.writer.is_closing():
            command = await self.command_queue.get()
            # print(f"Getting command {command}")
            async with self.lock:
                try:
                    self.writer.write(command.byte_message)
                    await self.writer.drain()

                    response = await (
                        self.read_long_message(response_time=command.response_time)
                        if command.expects_long_answer
                        else self.read_message(response_time=command.response_time)
                    )
                    command.receive_answer(response)
                    # print(f"Putting... command {command}")
                    command.answer_received.set()
                    await self.answer_queue.put(command)
                except Exception as e:
                    print(sys.exc_info())
                    break

    async def read_message(self, response_time: float = 0.3) -> str:
        message: str = ""
        await asyncio.sleep(0.2)
        if self.reader is None:
            return message
        try:
            response = await asyncio.wait_for(
                self.reader.readline(), timeout=response_time
            )
            message = response.decode(self.encoding).strip()
        except Exception as e:
            print(f"Exception while reading {sys.exc_info()}")
        return message

    async def read_long_message(
        self, response_time: float = 0.3, reading_time: float = 0.1
    ) -> List[str]:
        if self.reader is None:
            return []

        target = time.time() + reading_time
        message: List[str] = []
        while time.time() < target:
            try:
                response = await asyncio.wait_for(
                    self.reader.readline(), timeout=response_time
                )
                line = response.decode(self.encoding).strip()
                message.append(line)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"Exception while reading {sys.exc_info()}")
                break

        return message


class CalcStrategy:
    @staticmethod
    def execute(*args, **kwargs) -> Any:
        ...


class ParsingStrategy:
    @staticmethod
    def parse(*args, **kwargs) -> Any:
        ...

    @staticmethod
    def try_to_evaluate(value: Any) -> Any:
        ...


class FullscaleCalcStrategy(CalcStrategy):
    @staticmethod
    def execute(
        frequency: int, urms: float, irms: float, phase: float, *args, **kwargs
    ) -> Dict[str, Union[int, float]]:
        urms = urms if urms > 282_300 else 282_300
        urms = (urms * 0.000_400_571 - 1130.669402) * 1000 + 0.5

        irms = irms if irms > 3_038_000 else 303_800
        irms = (irms * 0.000_015_601 - 47.380671) * 1000 + 0.5

        phase = (phase * 0.125) * 100
        return {"frequency": frequency, "urms": urms, "irms": irms, "phase": phase}


class FactorisedCalcStrategy(CalcStrategy):
    @staticmethod
    def execute(
        frequency: int, urms: float, irms: float, phase: float, *args, **kwargs
    ) -> Dict[str, Union[int, float]]:
        urms /= 1000
        irms /= 1000
        phase /= 1_000_000
        return {"frequency": frequency, "urms": urms, "irms": irms, "phase": phase}


class MinusHashParsingStrategy(ParsingStrategy):
    @staticmethod
    def parse(status_string: str, *args, **kwargs) -> Dict[str, Any]:
        return dict(
            zip(
                ("error", "frequency", "gain", "protocol", "wipe_mode", "temperature"),
                re.split(r"(?<!['])[-#]", status_string),
            )
        )


def default_if_none(default: Any, type_: type = int) -> Callable[[Any], Any]:
    none_converter = attrs.converters.default_if_none(default)

    def converter(value) -> None:
        value = none_converter(value)
        try:
            value = type_(none_converter(value))
        except Exception as e:
            print(f"VALUE ERROR {e}, {value} is not {type_}")
        return value

    return converter


@attrs.define()
class Status:
    error: int = attrs.field(
        default=0,
        repr=False,
        converter=default_if_none(0, int),
        validator=attrs.validators.instance_of(int),
    )
    frequency: int = attrs.field(
        default=0,
        converter=default_if_none(0, int),
        validator=attrs.validators.instance_of(int),
    )
    gain: int = attrs.field(
        default=0,
        converter=default_if_none(0, int),
        validator=attrs.validators.instance_of(int),
    )
    protocol: int = attrs.field(
        default=0,
        repr=False,
        converter=default_if_none(0, int),
        validator=attrs.validators.instance_of(int),
    )
    wipe_mode: bool = attrs.field(
        default=False,
        repr=False,
        converter=default_if_none(False, bool),
        validator=attrs.validators.instance_of(bool),
    )
    temperature: float = attrs.field(
        default=0.0,
        converter=lambda x: (
            default_if_none(0.0, float)(
                x.strip("'") if isinstance(x, str) and "'" in x else x
            )
        ),
        validator=attrs.validators.instance_of(float),
    )
    signal: bool = attrs.field(
        default=False,
        converter=default_if_none(False, bool),
        validator=attrs.validators.instance_of(bool),
    )
    urms: float = attrs.field(
        default=0.0,
        converter=default_if_none(0.0, float),
        validator=attrs.validators.instance_of(float),
    )
    irms: float = attrs.field(
        default=0.0,
        converter=default_if_none(0.0, float),
        validator=attrs.validators.instance_of(float),
    )
    phase: float = attrs.field(
        default=0.0,
        converter=default_if_none(0.0, float),
        validator=attrs.validators.instance_of(float),
    )
    relay_mode: Optional[Literal["kHz", "MHz"]] = attrs.field(
        default=None,
        converter=attrs.converters.optional(str),
        kw_only=True,
    )
    timestamp: datetime.datetime = attrs.field(
        factory=datetime.datetime.now,
        eq=False,
        converter=lambda b: (
            datetime.datetime.fromtimestamp(b) if isinstance(b, float) else b
        ),
    )

    @classmethod
    def from_status_command(
        cls,
        command: Command,
        parsing_strategy: ParsingStrategy = MinusHashParsingStrategy(),
        calculation_strategy: Optional[CalcStrategy] = None,
        old_status: Optional[Status] = None,
    ) -> Status:
        if not command.answer_string or "Error" in command.answer_string:
            return cls(timestamp=command._answer_received_timestamp)
        status: Dict[str, Any] = parsing_strategy.parse(command.answer_string)
        if calculation_strategy is not None:
            status = calculation_strategy.execute(**status)
        return (
            cls(**status) if old_status is None else attrs.evolve(old_status, **status)
        )

    @classmethod
    def from_sens_command(
        cls,
        command: Command,
        calculation_strategy: Optional[CalcStrategy] = None,
        old_status: Optional[Status] = None,
    ) -> Status:
        if not command.answer_string or "Error" in command.answer_string:
            return cls(timestamp=command._answer_received_timestamp)

        convert_sonicmeasure_field = lambda x: float(x) if "." in x else int(x)
        return_dict: Dict[str, Any] = dict(
            zip(
                ("frequency", "urms", "irms", "phase"),
                map(convert_sonicmeasure_field, command.answer_string.split(" ")),
            )
        )

        if calculation_strategy is not None:
            return_dict = calculation_strategy.execute(**return_dict)

        return_dict["timestamp"] = command._answer_received_timestamp
        return (
            cls(**return_dict)
            if old_status is None
            else attrs.evolve(old_status, **return_dict)
        )


@attrs.frozen
class Modules:
    buffer: bool = attrs.field(default=False, converter=attrs.converters.to_bool)
    display: bool = attrs.field(default=False, converter=attrs.converters.to_bool)
    eeprom: bool = attrs.field(default=False, converter=attrs.converters.to_bool)
    fram: bool = attrs.field(default=False, converter=attrs.converters.to_bool)
    i_current: bool = attrs.field(default=False, converter=attrs.converters.to_bool)
    current1: bool = attrs.field(default=False, converter=attrs.converters.to_bool)
    current2: bool = attrs.field(default=False, converter=attrs.converters.to_bool)
    io_serial: bool = attrs.field(default=False, converter=attrs.converters.to_bool)
    thermo_ext: bool = attrs.field(default=False, converter=attrs.converters.to_bool)
    thermo_int: bool = attrs.field(default=False, converter=attrs.converters.to_bool)
    khz: bool = attrs.field(default=False, converter=attrs.converters.to_bool)
    mhz: bool = attrs.field(default=False, converter=attrs.converters.to_bool)
    portexpander: bool = attrs.field(default=False, converter=attrs.converters.to_bool)
    protocol: bool = attrs.field(default=False, converter=attrs.converters.to_bool)
    protocol_fix: bool = attrs.field(default=False, converter=attrs.converters.to_bool)
    relais: bool = attrs.field(default=False, converter=attrs.converters.to_bool)
    scanning: bool = attrs.field(default=False, converter=attrs.converters.to_bool)
    sonsens: bool = attrs.field(default=False, converter=attrs.converters.to_bool)
    tuning: bool = attrs.field(default=False, converter=attrs.converters.to_bool)
    switch: bool = attrs.field(default=False, converter=attrs.converters.to_bool)
    switch2: bool = attrs.field(default=False, converter=attrs.converters.to_bool)

    @classmethod
    def from_string(cls, module_string: str) -> Modules:
        return cls(*module_string.split("="))


@attrs.frozen
class Info:
    device_type: Literal["soniccatch", "sonicwipe", "sonicdescale"] = attrs.field(
        default="soniccatch"
    )
    firmware_info: str = attrs.field(default="")
    version: float = attrs.field(default=0.2)
    modules: Modules = attrs.field(factory=Modules)


@attrs.define
class Hold:
    duration: float = attrs.field(
        default=100.0,
        converter=float,
        validator=attrs.validators.instance_of(float),
    )
    unit: Literal["ms", "s"] = attrs.field(
        default="ms",
        validator=attrs.validators.in_(("ms", "s")),
    )
    holding: asyncio.Event = attrs.field(factory=asyncio.Event)
    _remaining_time: float = attrs.field(default=0.0)

    def __attrs_post_init__(self) -> None:
        self.duration = self.duration if self.unit == "s" else self.duration / 1000

    @property
    def remaining_time(self) -> Optional[float]:
        return self._remaining_time

    async def execute(self) -> None:
        self.holding.set()
        end_time: float = time.time() + self.duration
        while time.time() < end_time:
            self._remaining_time = round(end_time - time.time(), 2)
            await asyncio.sleep(0.01)

        self._remaining_time = 0
        self.holding.clear()


@attrs.define
class Ramp:
    sonicamp: SonicAmp = attrs.field()
    start_value: int = attrs.field()
    stop_value: int = attrs.field()
    step_value: int = attrs.field(converter=abs)
    hold_on_time: Union[float, int] = attrs.field(
        default=100,
        validator=attrs.validators.instance_of((int, float)),
    )
    hold_on_time_unit: Literal["ms", "s"] = attrs.field(
        default="ms",
        validator=attrs.validators.in_(("ms", "s")),
    )
    hold_off_time: Union[float, int] = attrs.field(
        default=0,
        validator=attrs.validators.instance_of((int, float)),
    )
    hold_off_time_unit: Literal["ms", "s"] = attrs.field(
        default="ms",
        validator=attrs.validators.in_(("ms", "s")),
    )

    values: Iterable[int] = attrs.field(factory=tuple)
    running: asyncio.Event = attrs.field(factory=asyncio.Event)
    _current_value: Optional[int] = attrs.field(default=None)

    def __attrs_post_init__(self):
        self.step_value = (
            self.step_value if self.start_value < self.stop_value else -self.step_value
        )
        self.stop_value = self.stop_value + self.step_value
        self.values = range(self.start_value, self.stop_value, self.step_value)

    @property
    def current_value(self) -> Optional[int]:
        return self._current_value

    async def update(self) -> None:
        while self.running.is_set():
            if self.sonicamp.status.signal:
                status = await self.sonicamp.get_sens()
            else:
                status = await self.sonicamp.get_status()
            print(status)

    async def execute(self) -> None:
        self.running.set()
        update_task = asyncio.create_task(self.update())
        ramping_task = asyncio.create_task(self.ramp())
        # await self.ramp()
        await asyncio.gather(ramping_task, update_task)

    async def ramp(self) -> None:
        await self.sonicamp.set_signal_on()

        for value in self.values:
            self._current_value = value
            if self.hold_off_time:
                await self.sonicamp.set_signal_on()

            await self.sonicamp.set_frequency(value)
            await self.sonicamp.hold(self.hold_on_time, self.hold_on_time_unit)

            if self.hold_off_time:
                await self.sonicamp.set_signal_off()
                await self.sonicamp.hold(self.hold_off_time, self.hold_off_time_unit)

        self.running.clear()


@attrs.define
class SonicParser:
    SUPPORTED_TOKENS: List[str] = [
        "frequency",
        "gain",
        "ramp_freq",
        "ramp_gain",
        "on",
        "off",
        "hold",
        "startloop",
        "endloop",
        # "chirp_ramp_freq",
        # "chirp_ramp_gain",
        "!AUTO",
        "AUTO",
    ]

    def parse_text(self, text: str) -> dict[str, Union[tuple[Any, ...], str]]:
        lines: list[str] = list(filter(None, text.rstrip().splitlines()))
        commands, arguments, comment = self.parse_lines(lines)
        loops: tuple[dict[str, int], ...] = self.parse_for_loops(commands, arguments)

        self.check_syntax_acception(loops, commands, arguments)
        print(
            {
                "commands": commands,
                "arguments": arguments,
                "loops": loops,
                "comments": comment,
            }
        )
        return {
            "commands": commands,
            "arguments": arguments,
            "loops": loops,
            "comments": comment,
        }

    def values_correctly_converted(
        self, arg: Union[int, tuple[Union[int, str], ...]]
    ) -> bool:
        return (
            not isinstance(arg, int) and arg.isnumeric()
            if not isinstance(arg, tuple)
            else any(self.values_correctly_converted(value) for value in arg)
        )

    def parse_lines(self, lines: list[str]) -> tuple[Any, ...]:
        commands: list[str] = list()
        arguments: list[Union[str, int]] = list()
        comments: str = str()
        for line in lines:
            if "#" in line:
                comments += f"{line}\n"
                continue

            command, argument = self._parse_line(line)
            commands.append(command)
            arguments.append(argument)

        return (tuple(commands), tuple(arguments), comments)

    def parse_for_loops(
        self, commands: list[str], arguments: list[Union[str, int]]
    ) -> tuple[dict[str, int], ...]:
        loops: list[dict[str, int]] = list()
        for i, command in enumerate(commands):
            if command == "startloop":
                quantifier: int = int(
                    arguments[i]
                    if arguments[i] is not None and isinstance(arguments[i], int)
                    else -1
                )
                loops.insert(i, {"begin": i, "quantifier": quantifier})

            elif command == "endloop":
                loops.insert(i, {})
                for loop in reversed(loops):
                    if len(loop) != 2:
                        continue
                    loop.update({"end": i})
                    break

            else:
                loops.insert(i, {})
        return tuple(loops)

    def _parse_line(self, line: str) -> Tuple[Union[str, int, Tuple], ...]:
        if line is None or line == "":
            return ((), ())

        tmp_line_list: List[List[str]] = [i.split(",") for i in line.split(" ")]
        line_list: List[Union[str, int]] = list(
            filter(None, [item for sublist in tmp_line_list for item in sublist])
        )

        for i, part in enumerate(line_list):
            if part[-1:] == "s" and part[-2:] != "ms" and part[:-1].isnumeric():
                line_list.insert(i + 1, part[-1:])
                line_list[i] = int(part[:-1])
            elif part[-2:] == "ms" and part[:-2].isnumeric():
                line_list.insert(i + 1, part[-2:])
                line_list[i] = int(part[:-2])
            elif part.isnumeric():
                line_list[i] = int(part)

        command: str = line_list[0]
        line_list.pop(0)
        return (command, line_list[0] if len(line_list) == 1 else tuple(line_list))

    def check_syntax_acception(self, loops, commands, arguments) -> None:
        if any(
            (len(loop) != 3 and loop is not None and len(loop) != 0) for loop in loops
        ):
            raise ValueError(
                "Syntax of loops is invalid. Maybe you forgot to close a loop?"
            )

        elif any(self.values_correctly_converted(arg) for arg in arguments):
            raise ValueError(
                "Argument(s) could not have been correctly converted to  integers,\nplease call for support or try again"
            )

        elif any(command not in self.SUPPORTED_TOKENS for command in commands):
            raise ValueError("One or more commands are illegal or written wrong")


@attrs.define
class Sequence:
    _sonicamp: SonicAmp = attrs.field()
    _script_text: str = attrs.field(validator=attrs.validators.instance_of(str))
    _parser: SonicParser = attrs.field(init=False, factory=SonicParser, repr=False)

    _commands: List[Any] = attrs.field(init=False, factory=list)
    _original_commands: List[Any] = attrs.field(init=False, factory=list)
    _current_command: str = attrs.field(init=False, default="")
    _current_line: int = attrs.field(init=False, default=0)

    running: asyncio.Event = attrs.field(init=False, factory=asyncio.Event)

    def __attrs_post_init__(self) -> None:
        parsed_test = self._parser.parse_text(self._script_text)
        parsed_test = zip(
            parsed_test["commands"], parsed_test["arguments"], parsed_test["loops"]
        )
        self._commands = list(
            {"command": command, "argument": argument, "loop": loop}
            for command, argument, loop in parsed_test
        )
        self._original_commands = copy.deepcopy(self._commands)

    async def update(self) -> None:
        while self.running.is_set():
            if self._sonicamp.status.signal:
                status = await self._sonicamp.get_sens()
            else:
                status = await self._sonicamp.get_status()
            print(status)

    async def execute(self) -> None:
        self.running.set()
        update_task = asyncio.create_task(self.update())
        ramping_task = asyncio.create_task(self.loop())
        await asyncio.gather(ramping_task, update_task)

    async def loop(self) -> None:
        while self.running.is_set() and self._current_line < len(self._commands):
            try:
                if self._commands[self._current_line]["command"] == "startloop":
                    self.startloop_response()
                elif self._commands[self._current_line]["command"] == "endloop":
                    self.endloop_response()
                else:
                    await self.execute_command(self._current_line)
                    self._current_line += 1
            except Exception as e:
                print(sys.exc_info())

    def startloop_response(self) -> None:
        loop: Dict[str, int] = self._commands[self._current_line]["loop"]
        if (
            loop.get("quantifier")
            and isinstance(loop.get("quantifier"), int)
            and loop.get("quantifier") != -1
        ):
            loop["quantifier"] -= 1
            self._current_line += 1
        elif loop.get("quantifier") == -1:
            self._current_line += 1
        else:
            print(f"Jumping to {loop['end'] + 1}; quantifier = 0")
            self._current_line = loop["end"] + 1

    def endloop_response(self) -> None:
        print(f"'endloop' @ {self._current_line}")
        loop_command: dict[str, int] = list(
            filter(
                lambda x: (x["loop"].get("end") == self._current_line), self._commands
            )
        )[0]
        loop: Dict[str, Any] = loop_command["loop"]
        self._commands[loop["begin"] + 1 : loop["end"] - 1] = copy.deepcopy(
            self._original_commands[loop["begin"] + 1 : loop["end"] - 1]
        )
        self._current_line = loop["begin"]

    async def execute_command(self, line: int) -> None:
        command: Dict[str, Any] = self._commands[self._current_line]
        self._current_command = command["command"]
        print(f"Executing command: '{command}'")

        match command["command"]:
            case "frequency":
                await self._sonicamp.set_frequency(command["argument"])
            case "gain":
                await self._sonicamp.set_gain(command["argument"])
            case "ramp_freq":
                await self._sonicamp.ramp_freq(*command["argument"])
            case "ramp_gain":
                await self._sonicamp.ramp_gain(*command["argument"])
            case "!AUTO" | "AUTO" | "auto":
                await self._sonicamp.set_signal_auto()
            case "hold":
                await self._sonicamp.hold(*command["argument"])
            case "on":
                await self._sonicamp.set_signal_on()
            case "off":
                await self._sonicamp.set_signal_off()
            case _:
                raise ValueError(f"{command} is not valid.")


class SonicAmpFactory:
    @staticmethod
    def build_amp(serial: SerialCommunicator) -> SonicAmp:
        return SonicAmp(serial)


class SonicAmp:
    def __init__(
        self, serial: SerialCommunicator, status: Status = Status(), info: Info = Info()
    ) -> None:
        self.serial: SerialCommunicator = serial
        self.status: Status = status
        self.info: Info = info

        self.commands: Iterable[type] = (
            Commands.SetFrequency,
            Commands.SetGain,
            Commands.SetKhzMode,
            Commands.SetMhzMode,
            Commands.SetSignalOn,
            Commands.SetSignalOff,
            Commands.SetSignalAuto,
            Commands.GetSens,
            Commands.GetStatus,
        )
        self.command_validator: CommandValidator = CommandValidator(self)

        self.ramper: Optional[Ramp] = None
        self.holder: Optional[Hold] = None
        self.sequencer: Optional[Sequence] = None

    @staticmethod
    def build_amp(serial: SerialCommunicator) -> SonicAmp:
        return SonicAmpFactory.build_amp(serial)

    async def execute_command(self, command: Command) -> Command:
        await self.serial.command_queue.put(command)
        await command.answer_received.wait()
        self.check_command(command)
        return command

    def update_status(self, command, *args, **kwargs) -> None:
        self.status = attrs.evolve(
            self.status, timestamp=command._answer_received_timestamp, *args, **kwargs
        )

    def scan_command(self, command) -> None:
        if isinstance(command, Commands.SetFrequency):
            self.update_status(command, frequency=command.value)
        elif isinstance(command, Commands.SetGain):
            self.update_status(command, gain=command.value)
        elif isinstance(command, Commands.GetStatus):
            self.status = Status.from_status_command(command, old_status=self.status)
        elif isinstance(command, Commands.GetSens):
            self.status = Status.from_sens_command(
                command,
                old_status=self.status,
                calculation_strategy=FactorisedCalcStrategy(),
            )
        elif isinstance(command, Commands.SetSignalOn):
            self.update_status(command, signal=True)
        elif isinstance(command, Commands.SetSignalOff):
            self.update_status(command, signal=False, urms=0.0, irms=0.0, phase=0.0)
        elif isinstance(command, Commands.SetSignalAuto):
            self.update_status(command, protocol=110)

    def check_command(self, command: Command) -> None:
        for answer in command.answer_lines:
            potential_command: Optional[Command] = self.command_validator.find_command(
                answer
            )
            if potential_command:
                self.scan_command(potential_command)

    async def set_frequency(self, frequency: int) -> str:
        command = await self.execute_command(Commands.SetFrequency(value=frequency))
        return command.answer_string

    async def set_gain(self, gain: int) -> str:
        command = await self.execute_command(Commands.SetGain(value=gain))
        return command.answer_string

    async def get_status(self) -> Status:
        command = await self.execute_command(Commands.GetStatus())
        return self.status

    async def get_sens(self) -> Status:
        command = await self.execute_command(Commands.GetSens())
        return self.status

    async def set_signal_off(self) -> str:
        command = await self.execute_command(Commands.SetSignalOff())
        return command.answer_string

    async def set_signal_on(self) -> str:
        command = await self.execute_command(Commands.SetSignalOn())
        return command.answer_string

    async def set_signal_auto(self) -> str:
        command = await self.execute_command(Commands.SetSignalAuto())
        return command.answer_string

    async def sequence(self, script: str) -> None:
        self.sequencer = Sequence(self, script)
        await self.sequencer.execute()

    async def hold(
        self, duration: float = 100, unit: Literal["ms", "s"] = "ms"
    ) -> None:
        self.holder = Hold(duration=duration, unit=unit)
        await self.holder.execute()

    async def ramp_freq(
        self,
        start: int,
        stop: int,
        step: int,
        hold_on_time: float,
        hold_on_time_unit: Literal["ms", "s"],
        hold_off_time: float,
        hold_off_time_unit: Literal["ms", "s"],
    ) -> None:
        self.ramper = Ramp(
            self,
            start,
            stop,
            step,
            hold_on_time,
            hold_on_time_unit,
            hold_off_time,
            hold_off_time_unit,
        )
        # asyncio.create_task(self.ramper.execute())
        await self.ramper.execute()

    async def ramp_gain(
        self,
        start: int,
        stop: int,
        step: int,
        hold_on_time: float,
        hold_on_time_unit: Literal["ms", "s"],
        hold_off_time: float,
        hold_off_time_unit: Literal["ms", "s"],
    ) -> None:
        self.ramper = Ramp(
            self,
            start,
            stop,
            step,
            hold_on_time,
            hold_on_time_unit,
            hold_off_time,
            hold_off_time_unit,
        )
        asyncio.create_task(self.ramper.execute())


import ttkbootstrap as ttk
import tkinter as tk
from async_tkinter_loop import async_handler, async_mainloop


class Root(tk.Tk):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.serial = SerialCommunicator("COM6")
        self.sonicamp = SonicAmp.build_amp(self.serial)

        self.connect_button = ttk.Button(
            self,
            text="Connect",
            bootstyle=ttk.SUCCESS,
            command=async_handler(self.connect, "COM6"),
        )
        self.connect_button.pack()
        self.button = ttk.Button(
            self,
            text="Set gain",
            command=async_handler(self.set_gain),
        )
        self.button.pack()

        self.button = ttk.Button(
            self,
            text="Ramp",
            command=async_handler(
                self.sonicamp.ramp_freq, 1000000, 2000000, 1000, 1, "s", 1, "s"
            ),
        )
        self.button.pack()

        self.label = ttk.Label(self, text="None")
        self.label.pack()
        self.bind("<Configure>", async_handler(self.resize))
        self.after(100, async_handler(self.update_engine))

    async def resize(self, event: Any) -> None:
        print(event)

    async def update_engine(self) -> None:
        if self.sonicamp.ramper and self.sonicamp.ramper.running.is_set():
            self.label.configure(text=str(self.sonicamp.ramper.current_value))
        if self.sonicamp.holder and self.sonicamp.holder.holding.is_set():
            self.label.configure(text=str(self.sonicamp.holder.remaining_time))
        self.after(100, async_handler(self.update_engine))

    async def set_gain(self) -> None:
        answer = await self.sonicamp.set_gain(150)
        self.label.configure(text=answer)
        print(self.sonicamp)
        print(self.sonicamp.status)

    async def connect(self, port: str) -> None:
        await self.serial.setup()
        await self.sonicamp.set_signal_off()

    async def send_command(self, command: Command) -> None:
        await self.serial.command_queue.put(command)
        command = await self.serial.answer_queue.get()
        self.label.configure(text=command.answer_string)


async def main():
    device = SerialCommunicator(port="COM6")
    await device.setup()
    sonicamp = SonicAmp.build_amp(device)

    # status_engine = asyncio.create_task(sonicamp.update_engine())
    answer = await sonicamp.set_signal_on()
    print(answer)
    print(sonicamp.status)
    answer = await sonicamp.set_frequency(1_000_000)
    print(answer)
    print(sonicamp.status)
    answer = await sonicamp.set_gain(100)
    print(answer)
    print(sonicamp.status)
    answer = await sonicamp.set_signal_off()
    print(answer)
    print(sonicamp.status)

    await sonicamp.sequence(
        """startloop 5
        frequency 5000000
        on
        hold 5s
        gain 150
        off
        hold 5s
        on
        ramp_freq 1000000 2000000 10000 1s 1s
        off
        endloop
        """
    )

    # asyncio.create_task(sonicamp.ramp(1000000, 2000000, 1000, 5, "s", 5, "s"))
    await sonicamp.ramp(1000000, 2000000, 1000, 5, "s", 5, "s")
    while True:
        command = await device.answer_queue.get()
        print(command)


# asyncio.run(main())

root = Root()
async_mainloop(root)
