from typing import *
import re
import asyncio
import time
import attrs
import sys
from icecream import ic
from soniccontrol.sonicpackage.interfaces import Communicator, Sendable
import soniccontrol.constants as const


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

    def convert(self, data: Any) -> Any:
        try:
            self._result = self.worker(data)
        except Exception:
            ic("ERROR", sys.exc_info())
            return False
        else:
            return self._result


@attrs.define
class CommandValidator:
    pattern: str = attrs.field()
    _converters: Dict[str, Converter] = attrs.field(converter=dict)
    _result: Dict[str, Any] = attrs.field(init=False, factory=dict)
    _compiled_pattern: re.Pattern = attrs.field(init=False, repr=False)

    def __init__(self, pattern: str, **kwargs) -> None:
        self.__attrs_init__(
            pattern=pattern,
            converters={
                keyword: Converter(worker) for keyword, worker in kwargs.items()
            },
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
        return True


@attrs.define
class Answer:
    _string: Optional[str] = attrs.field(default=None, init=False, repr=False)
    _lines: Optional[List[str]] = attrs.field(factory=list, init=False)
    unknown_answers: Set[str] = attrs.field(factory=set)
    _received: asyncio.Event = attrs.field(
        factory=asyncio.Event, init=False, repr=False
    )
    _received_timestamp: Optional[float] = attrs.field(
        default=None, init=False, repr=False
    )
    _measured_response: Optional[float] = attrs.field(default=None, init=False)
    _creation_timestamp: float = attrs.field(factory=time.time, init=False)

    @property
    def string(self) -> str:
        return self._string

    @property
    def lines(self) -> List[str]:
        return self._lines

    @property
    def received(self) -> asyncio.Event:
        return self._received

    @property
    def received_timestamp(self) -> float:
        return self._received_timestamp

    @property
    def measured_response(self) -> str:
        return self._measured_response

    def reset(self) -> None:
        self._received.clear()
        self._lines.clear()
        self._string = ""
        self._creation_timestamp = time.time()
        self._measured_response = None
        self._received_timestamp = None

    def receive_answer(
        self, answer: Union[List[str], Tuple[str], Set[str], str]
    ) -> None:
        self._received_timestamp = time.time()
        if isinstance(answer, (list, tuple, set)):
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
        self._byte_message = f"{self.message}{self.argument}\n".encode(const.ENCODING)

    @property
    def byte_message(self) -> None:
        return self._byte_message

    @property
    def validators(self) -> List[CommandValidator]:
        return self._validators
    
    @validators.setter
    def validators(self, validators: Union[CommandValidator, Iterable[CommandValidator]]) -> None:
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
        self._byte_message = f"{self.message}{self.argument}\n".encode(const.ENCODING)

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

        await Command._serial_communication.send_and_wait_for_answer(self)
        self.validate()
        self.status_result.update({"timestamp": self.answer.received_timestamp})
        return self

    def validate(self) -> bool:
        if not self.answer.lines:
            return False

        self.answer.unknown_answers.clear()
        self._status_result.clear()
        self.answer.unknown_answers = set(self.answer.lines)
        for validator in self.validators:
            if validator.accepts(self.answer.string):
                self._status_result.update(validator.result)
                continue
            accepted = next(
                (
                    answer
                    for answer in self.answer.lines
                    if validator.accepts(data=answer)
                ),
                None,
            )
            if accepted:
                self.answer.unknown_answers.discard(accepted)
                self._status_result.update(validator.result)

        return len(self.answer.lines) == len(self.answer.unknown_answers)
