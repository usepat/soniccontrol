
import abc
import asyncio
from typing import Any, Dict

from soniccontrol.communication.connection_factory import ConnectionFactory
from soniccontrol.communication.sonicprotocol import CommunicationProtocol
from soniccontrol.events import EventManager
from soniccontrol.interfaces import Sendable


class Communicator(abc.ABC, EventManager):
    DISCONNECTED_EVENT = "Disconnected"

    def __init__(self) -> None:
        super().__init__()

    @property 
    @abc.abstractmethod
    def writer(self) -> asyncio.StreamWriter: ...

    @property 
    @abc.abstractmethod
    def reader(self) -> asyncio.StreamReader: ...

    @property
    @abc.abstractmethod
    def protocol(self) -> CommunicationProtocol: ...

    @property
    @abc.abstractmethod
    def connection_opened(self) -> asyncio.Event: ...

    @abc.abstractmethod
    async def open_communication(
        self, connection_factory: ConnectionFactory, baudrate: int
    ): ...

    @abc.abstractmethod
    async def close_communication(self, restart: bool = False) -> None: ...

    @property
    @abc.abstractmethod
    def handshake_result(self) -> Dict[str, Any]: ...

    @abc.abstractmethod
    async def send_and_wait_for_answer(self, message: Sendable) -> None: ...

    @abc.abstractmethod
    async def read_message(self) -> str: ...

    @abc.abstractmethod
    async def change_baudrate(self) -> None: ...