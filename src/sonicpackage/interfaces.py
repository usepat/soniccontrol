import abc
import asyncio
from typing import Any, Dict

from sonicpackage.communication.connection_factory import ConnectionFactory
from sonicpackage.communication.sonicprotocol import CommunicationProtocol
from sonicpackage.events import EventManager


class Sendable(abc.ABC):
    def __init__(self) -> None:
        super().__init__()

    @property
    @abc.abstractmethod
    def byte_message(self) -> None: ...


class Communicator(abc.ABC, EventManager):
    DISCONNECTED_EVENT = "Disconnected"

    def __init__(self) -> None:
        super().__init__()

    @property
    @abc.abstractmethod
    def protocol(self) -> CommunicationProtocol: ...

    @property
    @abc.abstractmethod
    def connection_opened(self) -> asyncio.Event: ...

    @abc.abstractmethod
    async def open_communication(
        self, connection_factory: ConnectionFactory
    ): ...

    @abc.abstractmethod
    async def close_communication(self) -> None: ...

    @property
    @abc.abstractmethod
    def handshake_result(self) -> Dict[str, Any]: ...

    @abc.abstractmethod
    async def send_and_wait_for_answer(self, message: Sendable) -> None: ...

    @abc.abstractmethod
    async def read_message(self) -> str: ...


class Scriptable(abc.ABC):
    def __init__(self) -> None:
        super().__init__()

    # @property
    # @abc.abstractmethod
    # def script_dictionary(self) -> Dict[str, Callable[[Any], Any]]:
    #     ...

    @abc.abstractmethod
    async def execute_command(*args, **kwargs) -> None: ...

    @abc.abstractmethod
    async def get_overview() -> None: ...

    @abc.abstractmethod
    async def set_signal_on() -> None: ...

    @abc.abstractmethod
    async def set_signal_off() -> None: ...

    @abc.abstractmethod
    def get_remote_proc_finished_event() -> asyncio.Event: ...

    # @abc.abstractmethod
    # def hold(self) -> None:
    #     ...


class FirmwareFlasher:
    def __init__(self) -> None:
        super().__init__()

    @abc.abstractmethod
    async def flash_firmware(self) -> None: ...
