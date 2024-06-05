import abc
import asyncio
from typing import *

import attrs

from soniccontrol.tkintergui.utils.events import EventManager


class Sendable(abc.ABC):
    def __init__(self) -> None:
        super().__init__()

    @property
    @abc.abstractmethod
    def byte_message(self) -> None:
        ...


class Communicator(abc.ABC):
    def __init__(self) -> None:
        super().__init__()

    @property
    @abc.abstractmethod
    def connection_opened(self) -> asyncio.Event:
        ...

    @abc.abstractmethod
    async def connect(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        ...

    def disconnect(self) -> None:
        ...

    @abc.abstractmethod
    async def _worker(self) -> None:
        ...

    @abc.abstractmethod
    async def send_and_wait_for_answer(self, message: Sendable) -> None:
        ...

    @abc.abstractmethod
    async def read_message(
        self, timeout: Optional[float] = None, *args, **kwargs
    ) -> Any:
        ...
        


class Script(abc.ABC):
    def __init__(self) -> None:
        super().__init__()

    @property
    @abc.abstractmethod
    def running(self) -> asyncio.Event:
        ...

    @abc.abstractmethod
    def execute(self, *args, **kwargs) -> None:
        ...

    def stop_execution(self) -> None:
        self.running.clear()


class Scriptable(abc.ABC):
    def __init__(self) -> None:
        super().__init__()

    # @property
    # @abc.abstractmethod
    # def script_dictionary(self) -> Dict[str, Callable[[Any], Any]]:
    #     ...

    @abc.abstractmethod
    def execute_command(*args, **kwargs) -> None:
        ...

    @abc.abstractmethod
    def set_signal_on() -> None:
        ...

    @abc.abstractmethod
    def set_signal_off() -> None:
        ...

    # @abc.abstractmethod
    # def hold(self) -> None:
    #     ...
