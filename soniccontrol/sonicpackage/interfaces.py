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

    @abc.abstractmethod
    def disconnect(self) -> None:
        ...

    @abc.abstractmethod
    async def send_and_wait_for_answer(self, message: Sendable) -> None:
        ...


@attrs.define
class Updater(abc.ABC):
    _device: Any = attrs.field(repr=False)
    _running: asyncio.Event = attrs.field(factory=asyncio.Event, init=False)
    _task: asyncio.Task = attrs.field(init=False, default=None)

    def __init__(self) -> None:
        super().__init__()
        self.__attrs_init__()
        self._event_emitter = EventManager()

    @property
    def running(self) -> asyncio.Event:
        return self._running

    @property
    def task(self) -> Optional[asyncio.Task]:
        return self._task

    def execute(self, *args, **kwargs) -> None:
        self._task = asyncio.create_task(self._loop())
        self._running.set()

    def stop_execution(self, *args, **kwargs) -> None:
        self._running.clear()

    async def _loop(self) -> None:
        while self._running.is_set():
            await self.worker()

    @abc.abstractmethod
    async def worker(self) -> None:
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

    @property
    @abc.abstractmethod
    def updater(self) -> Updater:
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
