from typing import Any, List, TypedDict, Optional, Union
import asyncio
import time
import attrs

import soniccontrol.sonicamp.constants as const


class CommandValidationDict(TypedDict):
    pattern: str
    return_type: type


@attrs.define
class Command:
    value: Any = attrs.field(default=None)
    message: str = attrs.field(default="")
    arguments: str = attrs.field(default="", converter=str)
    response_time: float = attrs.field(default=0.3)
    answer_received: asyncio.Event = attrs.field(factory=asyncio.Event)

    _answer_string: str = attrs.field(default="")
    _answer_lines: List[str] = attrs.field(factory=list, repr=False)
    _creation_timestamp: float = attrs.field(factory=time.time, repr=False)
    _answer_received_timestamp: float = attrs.field(factory=time.time)
    _measured_response_timestamp: float = attrs.field(default=time.time, repr=False)
    _validation_pattern: Optional[CommandValidationDict] = attrs.field(default=None)

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
        return f"{self.message}{self.arguments}\n".encode(encoding=const.ENCODING)

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


class SonicAmp(abc.ABC):
    