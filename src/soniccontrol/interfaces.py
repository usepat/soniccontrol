import abc
import asyncio


class Sendable(abc.ABC):
    def __init__(self) -> None:
        super().__init__()

    @property
    @abc.abstractmethod
    def byte_message(self) -> None: ...


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
