import asyncio
import json
import logging
import re
import sys
import time
from typing import (Any, Callable, Dict, Generator, Iterable, List, Literal,
                    Optional, Union)

import attrs
import soniccontrol.utils.constants as const
from icecream import ic
from soniccontrol.sonicpackage.interfaces import Communicator, Sendable

parrot_feeder = logging.getLogger("parrot_feeder")

@attrs.define
class Converter:
    worker: Callable[[Any], Any] = attrs.field()
    _converted: bool = attrs.field(default=False, init=False, repr=False)
    _result: Any = attrs.field(init=False)

    @property
    def result(self) -> Any:
        if self._converted:
            return self._result
        else:
            ic("ERROR: Converter did not convert yet.")
            return False

    def convert(self, *args, **kwargs) -> Any:
        try:
            self._result = self.worker(*args, **kwargs)
        except Exception:
            ic("ERROR", sys.exc_info())
            return False
        else:
            return self._result


@attrs.define
class CommandValidator:
    pattern: str = attrs.field()
    _converters: Dict[str, Converter] = attrs.field(converter=dict, repr=False)
    _after_converters: Dict[
        str, Dict[Literal["worker", "keywords"], Union[Converter, str]]
    ] = attrs.field(repr=False)
    _result: Dict[str, Any] = attrs.field(init=False, factory=dict, repr=False)
    _compiled_pattern: re.Pattern[str] = attrs.field(init=False, repr=False)

    def __init__(
        self,
        pattern: str,
        **kwargs: type[Any] | Callable[[Any], Any] | dict[str, Any],
    ) -> None:
        workers: dict[str, Callable[[Any], Any]] = dict()
        after_workers: dict[str, Callable[[Any], Any]] = dict()
        for keyword, worker in kwargs.items():
            if isinstance(worker, dict):
                worker["worker"] = Converter(worker["worker"])
                after_workers[keyword] = worker
                continue
            workers[keyword] = Converter(worker)
        self.__attrs_init__(
            pattern=pattern,
            converters=workers,
            after_converters=after_workers,
        )

    def __attrs_post_init__(self) -> None:
        self.pattern = self.generate_named_pattern(
            pattern=self.pattern, keywords=self._converters.keys()
        )
        self._compiled_pattern = re.compile(
            pattern=self.pattern,
            flags=re.IGNORECASE,
        )

    @property
    def result(self) -> Dict[str, Any]:
        return self._result

    @staticmethod
    def generate_named_pattern(pattern: str, keywords: List[str]) -> str:
        if not keywords:
            return pattern
        keyword_iter = iter(keywords)
        try:
            segments = re.split(r"(\(.*?\))", pattern)
            ic(segments)
            processed = "".join(
                (
                    f"(?P<{next(keyword_iter)}>{segment[1:-1]})"
                    if not segment.startswith("(?:") and segment.startswith("(")
                    else segment
                )
                for segment in segments
                if segment
            )
        except StopIteration:
            pass
        ic(processed)
        return processed

    def accepts(self, data: str) -> bool:
        if not data:
            return False
        result: Optional[re.Match] = self._compiled_pattern.search(data)
        if result is None:
            return False

        self._result = {
            keyword: self._converters[keyword].convert(result.groupdict().get(keyword))
            for keyword in result.groupdict().keys()
        }
        self.result.update(
            {
                keyword: self._after_converters[keyword]["worker"].convert(
                    **{
                        k: self._result.get(k)
                        for k in worker["keywords"]
                        if k in result.groupdict()
                    }
                )
                for keyword, worker in self._after_converters.items()
            }
        )

        return True


@attrs.define
class Answer:
    _string: str = attrs.field(default="", init=False, repr=False)
    _lines: list[str] = attrs.field(factory=list, init=False)
    unknown_answers: set[str] = attrs.field(factory=set)
    _valid: bool = attrs.field(default=False)
    _received: asyncio.Event = attrs.field(
        factory=asyncio.Event, init=False, repr=False
    )
    _received_timestamp: float | None = attrs.field(
        default=None, init=False, repr=False
    )
    _measured_response: float | None = attrs.field(default=None, init=False)
    _creation_timestamp: float = attrs.field(factory=time.time, init=False)

    @property
    def string(self) -> str:
        return self._string

    @property
    def lines(self) -> list[str]:
        return self._lines

    @property
    def valid(self) -> bool:
        return self._valid

    @valid.setter
    def valid(self, valid: bool) -> None:
        self._valid = valid

    @property
    def received(self) -> asyncio.Event:
        return self._received

    @property
    def received_timestamp(self) -> float | None:
        return self._received_timestamp

    @property
    def measured_response(self) -> float | None:
        return self._measured_response

    def reset(self) -> None:
        self._received.clear()
        self._lines.clear()
        self._valid = False
        self._string = ""
        self._creation_timestamp = time.time()
        self._measured_response = None
        self._received_timestamp = None

    def receive_answer(self, answer: list[Iterable[str] | str]) -> None:
        self._received_timestamp = time.time()
        if isinstance(answer, Iterable) and not isinstance(answer, str):
            self._lines = answer
            self._string = "\n".join(answer)
        elif isinstance(answer, str):
            self._lines = answer.splitlines()
            self._string = answer
        else:
            raise ValueError(f"{answer = } is not of type {str, list, tuple, set}")
        self._measured_response = self._received_timestamp - self._creation_timestamp
        self._received.set()


@attrs.define(hash=True, order=True, kw_only=True)
class Command(Sendable):
    argument: str = attrs.field(default="", converter=str)
    message: str = attrs.field(default="")
    estimated_response_time: float = attrs.field(default=0.3)
    expects_long_answer: bool = attrs.field(default=False, repr=False)
    _validators: List[CommandValidator] = attrs.field(factory=list)
    answer: Answer = attrs.field(init=False, factory=Answer)
    _byte_message: bytes = attrs.field(init=False)
    _status_result: Dict[str, Any] = attrs.field(init=False, factory=dict)
    _serial_communication: Optional[Communicator] = None

    def __attrs_post_init__(self) -> None:
        if not isinstance(self._validators, (tuple, list, set, Generator)):
            self._validators = [self._validators]
        self._byte_message = f"{self.message}{self.argument}\n".encode(
            const.misc.ENCODING
        )

    @property
    def full_message(self) -> str:
        return f"{self.message}{self.argument}" # MAYBE: add newline at the end

    @property
    def byte_message(self) -> bytes:
        return self._byte_message

    @property
    def validators(self) -> List[CommandValidator]:
        return self._validators

    @validators.setter
    def validators(
        self, validators: Union[CommandValidator, Iterable[CommandValidator]]
    ) -> None:
        if isinstance(validators, CommandValidator):
            self._validators = [CommandValidator]
        elif isinstance(self, (list, tuple, set, Generator)):
            self._validators = list(validators)
        else:
            raise ValueError("Illegal value for validators", validators)

    @property
    def status_result(self) -> Dict[str, Any]:
        return self._status_result

    @classmethod
    def set_serial_communication(cls, serial: Any) -> None:
        cls._serial_communication = serial

    def add_validators(
        self, validators: Union[CommandValidator, Iterable[CommandValidator]]
    ) -> None:
        if isinstance(validators, CommandValidator):
            self._validators.append(validators)
        elif isinstance(validators, (list, tuple, set, Generator)):
            self._validators.extend(validators)
        else:
            raise ValueError("Illegal argument for validators", validators)

    def set_argument(self, argument: Any) -> None:
        self.argument = argument
        self._byte_message = f"{self.message}{self.argument}\n".encode(
            const.misc.ENCODING
        )

    def get_dict(self) -> dict:
        return {
            "argument": self.argument,
            "message": self.message
        }

    async def execute(
        self, argument: Any = None, connection: Optional[Communicator] = None
    ) -> object:
        if not (Command._serial_communication or connection):
            raise ValueError(
                f"The serial communication reference is not viable. {Command._serial_communication = } {type(self._serial_communication) = }"
            )
        if not connection:
            connection = Command._serial_communication

        self.answer.reset()
        if argument is not None:
            self.set_argument(argument)

        parrot_feeder.debug("COMMAND_CALL(%s)", json.dumps(self.get_dict()))
        await connection.send_and_wait_for_answer(self)

        self.answer.valid = self.validate()
        self.status_result.update({"timestamp": self.answer.received_timestamp})
        return self

    def validate(self) -> bool:
        if not self.answer.lines:
            return False

        self.answer.unknown_answers.clear()
        self._status_result.clear()
        self.answer.unknown_answers = set(self.answer.lines)
        entire_string_accepted: bool = False

        for validator in self.validators:
            if validator.accepts(self.answer.string):
                entire_string_accepted = True
                self._status_result.update(validator.result)
                continue
            for answer in self.answer.lines:
                if validator.accepts(data=answer):
                    self.answer.unknown_answers.discard(answer)
                    self._status_result.update(validator.result)

        if entire_string_accepted:
            self.answer.unknown_answers.clear()

        return len(self.answer.lines) != len(self.answer.unknown_answers)
