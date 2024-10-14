import abc
import asyncio

from sonic_protocol.python_parser.answer import Answer
from sonic_protocol.python_parser.commands import Command


class Scriptable(abc.ABC):
    def __init__(self) -> None:
        super().__init__()

    @abc.abstractmethod
    async def execute_command(self, command: Command | str, **kwargs) -> Answer: ...

    @abc.abstractmethod
    async def get_overview(self) -> Answer: ...

    @abc.abstractmethod
    async def set_signal_on(self) -> Answer: ...

    @abc.abstractmethod
    async def set_signal_off(self) -> Answer: ...

    @abc.abstractmethod
    def get_remote_proc_finished_event(self) -> asyncio.Event: ...



class FirmwareFlasher:
    def __init__(self) -> None:
        super().__init__()

    @abc.abstractmethod
    async def flash_firmware(self) -> None: ...
