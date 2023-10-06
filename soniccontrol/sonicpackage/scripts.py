from typing import *
import time
import copy
import asyncio
import sys
import attrs
from icecream import ic
from soniccontrol.sonicpackage.interfaces import Scriptable, Script


HoldTuple = Tuple[Union[int, float], Literal["ms", "s"]]
RampTuple = Tuple[Union[int, float], Union[int, float], Union[float, int]]


@attrs.define
class Holder(Script):
    _duration: float = attrs.field(
        default=100.0,
        converter=float,
        validator=attrs.validators.instance_of(float),
    )
    _unit: Literal["ms", "s"] = attrs.field(
        default="ms",
        validator=attrs.validators.in_(("ms", "s")),
    )
    _external_event: asyncio.Event = attrs.field(repr=False, default=None)
    _holding: asyncio.Event = attrs.field(init=False, repr=False, factory=asyncio.Event)
    _remaining_time: float = attrs.field(init=False, default=0.0)

    def __attrs_post_init__(self) -> None:
        self._duration = self._duration if self.unit == "s" else self._duration / 1000
        self._external_event = (
            self.holding if self._external_event is None else self._external_event
        )

    def __str__(self) -> str:
        return f"Holding state: {self.remaining_time} seconds remaining"

    @property
    def remaining_time(self) -> Optional[float]:
        return self._remaining_time

    @property
    def duration(self) -> float:
        return self._duration

    @property
    def unit(self) -> Literal["ms", "s"]:
        return self._unit

    @property
    def holding(self) -> asyncio.Event:
        return self._holding

    def reset(
        self,
        duration: Optional[float] = None,
        unit: Literal["ms", "s"] = "s",
        external_event: Optional[asyncio.Event] = None,
    ) -> None:
        if duration is None:
            return
        self._unit = unit
        self._duration = duration if unit == "s" else duration / 1000
        self._remaining_time = 0.0
        self._external_event = (
            external_event if external_event is not None else self._holding
        )

    async def execute(
        self,
        duration: float = None,
        unit: Literal["ms", "s"] = "s",
        external_event: Optional[asyncio.Event] = None,
    ) -> None:
        self.reset(duration=duration, unit=unit, external_event=external_event)
        self._holding.set()
        end_time: float = time.time() + self._duration
        while (
            time.time() < end_time
            and self._holding.is_set()
            and self._external_event.is_set()
        ):
            self._remaining_time = round(end_time - time.time(), 2)
            await asyncio.sleep(0.01)
        self._remaining_time = 0.0
        self._holding.clear()


@attrs.define
class Ramper(Script):
    _device: Scriptable = attrs.field(repr=False)
    _action: Callable[[Union[int, float]], Any] = attrs.field(repr=False)
    _external_event: asyncio.Event = attrs.field(default=None)

    _hold_on: Holder = attrs.field(init=False, factory=Holder)
    _hold_off: Holder = attrs.field(init=False, factory=Holder)
    _values: Iterable[int] = attrs.field(init=False, factory=tuple)
    _running: asyncio.Event = attrs.field(init=False, factory=asyncio.Event)
    _current_value: int = attrs.field(init=False, default=0)

    def __attrs_post_init__(self) -> None:
        if self._external_event is None:
            self._external_event = self._running

    def __str__(self) -> str:
        return f"Ramp at {self.current_value} Hz"

    @property
    def running(self) -> asyncio.Event:
        return self._running

    @property
    def current_value(self) -> int:
        return self._current_value

    def reset(
        self,
        ramp_values: RampTuple,
        hold_on: HoldTuple = (100, "ms"),
        hold_off: HoldTuple = (0, "ms"),
        external_event: Optional[asyncio.Event] = None,
    ) -> None:
        _start_value, _stop_value, _step_value = ramp_values
        _step_value = _step_value if _start_value < _stop_value else -_step_value
        _stop_value = _stop_value + _step_value
        self._values = range(_start_value, _stop_value, _step_value)
        self._hold_on.reset(*hold_on)
        self._hold_off.reset(*hold_off)
        if external_event is None:
            self._external_event = self._running

    async def execute(
        self,
        ramp_values: RampTuple,
        hold_on: HoldTuple,
        hold_off: HoldTuple,
        external_event: Optional[asyncio.Event] = None,
    ) -> None:
        self.reset(
            ramp_values=ramp_values,
            hold_on=hold_on,
            hold_off=hold_off,
            external_event=external_event,
        )
        await self._device.get_overview()
        await self._action(ramp_values[0])
        await self._device.set_signal_on()
        await self.ramp()
        await self._device.set_signal_off()

    async def ramp(self) -> None:
        self.running.set()

        i: int = 0
        value: int = 0
        while (
            self._external_event.is_set()
            and self.running.is_set()
            and i < len(self._values)
        ):
            value = self._values[i]
            self._current_value = value

            await self._action(value)
            if self._hold_off.duration:
                await self._device.set_signal_on()
            await self._hold_on.execute()

            if self._hold_off.duration:
                await self._device.set_signal_off()
                await self._hold_off.execute()

            i += 1

        self._current_value = 0
        self.running.clear()


@attrs.define
class SonicParser:
    SUPPORTED_TOKENS: List[str] = [
        "frequency",
        "gain",
        "ramp_freq",
        # "ramp_gain",
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
        return_dict: Dict[str, Any] = {
            "commands": commands,
            "arguments": arguments,
            "loops": loops,
            "comments": comment,
        }
        ic(return_dict)
        return return_dict

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
class Sequencer(Script):
    _sonicamp: Scriptable = attrs.field(repr=False)
    _script_text: str = attrs.field(
        default="", validator=attrs.validators.instance_of(str)
    )
    _external_event: asyncio.Event = attrs.field(default=None, repr=False)

    _parser: SonicParser = attrs.field(init=False, factory=SonicParser, repr=False)
    _commands: List[Any] = attrs.field(init=False, factory=list)
    _original_commands: List[Any] = attrs.field(init=False, factory=list)
    _current_command: str = attrs.field(init=False, default="")
    _current_line: int = attrs.field(init=False, default=0)
    _running: asyncio.Event = attrs.field(init=False, factory=asyncio.Event)

    def __attrs_post_init__(self) -> None:
        self.reset(self._script_text, self._external_event)

    def __str__(self) -> str:
        return self.current_command

    @property
    def running(self) -> asyncio.Event:
        return self._running

    @property
    def current_line(self) -> int:
        return self._current_line

    @property
    def current_command(self) -> str:
        return self._current_command

    def reset(self, script: str, external_event: Optional[asyncio.Event] = None) -> None:
        if script is None:
            return
        self._script_text = script
        parsed_test = self._parser.parse_text(self._script_text)
        parsed_test = zip(
            parsed_test["commands"], parsed_test["arguments"], parsed_test["loops"]
        )
        self._commands = list(
            {"command": command, "argument": argument, "loop": loop}
            for command, argument, loop in parsed_test
        )
        self._original_commands = copy.deepcopy(self._commands)
        self._external_event = external_event if external_event is not None else self._running

    async def execute(self, script: Optional[str] = None, external_event: Optional[asyncio.Event] = None) -> None:
        self.reset(script=script, external_event=external_event)
        await self._sonicamp.get_overview()
        await self._loop()

    async def _loop(self) -> None:
        self.running.set()
        while self._external_event.is_set() and self.running.is_set() and self._current_line < len(self._commands):
            try:
                if self._commands[self._current_line]["command"] == "startloop":
                    self.startloop_response()
                elif self._commands[self._current_line]["command"] == "endloop":
                    self.endloop_response()
                else:
                    await self.execute_command(self._current_line)
                    self._current_line += 1
            except Exception as e:
                ic(sys.exc_info())
        self.running.clear()

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
            ic(f"Jumping to {loop['end'] + 1}; quantifier = 0")
            self._current_line = loop["end"] + 1

    def endloop_response(self) -> None:
        ic(f"'endloop' @ {self._current_line}")
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
        self._current_command = f'Executing {command["command"]} {command["argument"]}'
        ic(f"Executing command: '{command}'")

        match command["command"]:
            case "frequency":
                await self._sonicamp.set_frequency(command["argument"])
            case "gain":
                await self._sonicamp.set_gain(command["argument"])
            case "ramp_freq":
                self._current_command = str(self._sonicamp.frequency_ramper)
                await self._sonicamp.ramp_freq(*command["argument"], event=self.running)
            # case "ramp_gain":
            #     self._current_command = self._sonicamp.ramper
            #     await self._sonicamp.ramp_gain(*command["argument"], event=self.running)
            case "!AUTO" | "AUTO" | "auto":
                await self._sonicamp.set_signal_auto()
            case "hold":
                self._current_command = str(self._sonicamp.holder)
                await self._sonicamp.hold(*command["argument"], event=self.running)
            case "on":
                await self._sonicamp.set_signal_on()
            case "off":
                await self._sonicamp.set_signal_off()
            case _:
                self.running.clear()
                raise ValueError(f"{command} is not valid.")
