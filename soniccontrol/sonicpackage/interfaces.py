import abc
from typing import *
import asyncio


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
    async def connect(self):
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


class UpdateStrategy(abc.ABC):
    def __init__(self) -> None:
        super().__init__()

    @abc.abstractmethod
    def execute(self, *args, **kwargs) -> None:
        ...


class Script(abc.ABC):
    def __init__(self) -> None:
        super().__init__()

    @abc.abstractmethod
    def execute(self, *args, **kwargs) -> None:
        ...


class Scriptable(abc.ABC):
    def __init__(self) -> None:
        super().__init__()

    @property
    @abc.abstractmethod
    def script_dictionary(self) -> Dict[str, Callable[[Any], Any]]:
        ...

    def update(self) -> None:
        ...

    def set_signal_on() -> None:
        ...

    def set_signal_off() -> None:
        ...

    def hold(self) -> None:
        ...
