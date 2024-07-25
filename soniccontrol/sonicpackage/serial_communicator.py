import asyncio
import sys
import time
from typing import Any, Callable, Dict, Final, Optional, List

import attrs
import serial
from soniccontrol.sonicpackage.package_fetcher import PackageFetcher
from icecream import ic
from soniccontrol.sonicpackage.command import Command, CommandValidator
from soniccontrol.sonicpackage.interfaces import Communicator
from soniccontrol.sonicpackage.sonicprotocol import CommunicationProtocol, LegacySonicProtocol, SonicProtocol
from soniccontrol.tkintergui.utils.events import Event
from soniccontrol.utils.system import PLATFORM


@attrs.define
class SerialCommunicator(Communicator):
    _init_command: Command = attrs.field(init=False)
    _connection_opened: asyncio.Event = attrs.field(init=False, factory=asyncio.Event)
    _connection_closed: asyncio.Event = attrs.field(init=False, factory=asyncio.Event)
    _lock: asyncio.Lock = attrs.field(init=False, factory=asyncio.Lock, repr=False)
    _command_queue: asyncio.Queue[Command] = attrs.field(
        init=False, factory=asyncio.Queue, repr=False
    )
    _answer_queue: asyncio.Queue[Command] = attrs.field(
        init=False, factory=asyncio.Queue, repr=False
    )
    _reader: Optional[asyncio.StreamReader] = attrs.field(
        init=False, default=None, repr=False
    )
    _writer: Optional[asyncio.StreamWriter] = attrs.field(
        init=False, default=None, repr=False
    )
    _log_callback: Callable[[str], None] = attrs.field(default=lambda _: None)

    def __attrs_post_init__(self) -> None:
        self._task = None
        self._protocol: CommunicationProtocol = SonicProtocol(self._log_callback)
        super().__init__()

    @property
    def protocol(self) -> CommunicationProtocol: 
        return self._protocol

    @property
    def connection_opened(self) -> asyncio.Event:
        return self._connection_opened

    @property
    def connection_closed(self) -> asyncio.Event:
        return self._connection_closed
    
    @property
    def handshake_result(self) -> Dict[str, Any]:
        # Todo: define with Thomas how we make a handshake
        return {}

    async def connect(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        self._reader = reader
        self._writer = writer
        self._protocol = SonicProtocol(lambda _: None)
        self._package_fetcher = PackageFetcher(self._reader, self._protocol)
        self._connection_opened.set()

        self._task = asyncio.create_task(self._worker())
        self._package_fetcher.run()

    async def _worker(self) -> None:
        message_counter: int = 0
        message_id_max_client: Final[int] = 2 ** 16 - 1 # 65535 is the max for uint16. so we cannot go higher than that.

        async def send_and_get(command: Command) -> None:
            assert (self._writer is not None)

            nonlocal message_counter
            message_counter = (message_counter + 1) % message_id_max_client

            message_str = self._protocol.parse_request(
                command.full_message, message_counter
            )
            message = message_str.encode(PLATFORM.encoding)
            self._writer.write(message)
            await self._writer.drain()

            answer = ""
            try:
                answer = await self._package_fetcher.get_answer_of_package(
                    message_counter
                )
            except Exception as e:
                ic(f"Exception while reading {sys.exc_info()}")

            command.answer.receive_answer(answer)
            await self._answer_queue.put(command)

        if self._writer is None or self._reader is None:
            ic("No connection available")
            return

        try:
            while self._writer is not None and not self._writer.is_closing():
                command: Command = await self._command_queue.get()
                async with self._lock:
                    try:
                        await send_and_get(command)
                    except serial.SerialException:
                        await self.disconnect()
                        return
                    except Exception as e:
                        ic(sys.exc_info())
                        break
        except asyncio.CancelledError:
            await self.disconnect()
            return
        await self.disconnect()

    async def send_and_wait_for_answer(self, command: Command) -> None:
        TIMEOUT = 10 # 10s
        await self._command_queue.put(command)
        received = await asyncio.wait_for(command.answer.received.wait(), TIMEOUT)
        if not received:
            raise ConnectionError("Device is not responding")

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def disconnect(self) -> None:
        if self._task is not None:
            await self._package_fetcher.stop()
        self._writer.close() if self._writer is not None else None
        self._connection_opened.clear()
        self._connection_closed.set()
        self._reader = None
        self._writer = None
        self.emit(Event(Communicator.DISCONNECTED_EVENT))


@attrs.define
class LegacySerialCommunicator(Communicator):
    _init_command: Command = attrs.field(init=False)
    _connection_opened: asyncio.Event = attrs.field(init=False, factory=asyncio.Event)
    _connection_closed: asyncio.Event = attrs.field(init=False, factory=asyncio.Event)
    _lock: asyncio.Lock = attrs.field(init=False, factory=asyncio.Lock, repr=False)
    _command_queue: asyncio.Queue = attrs.field(
        init=False, factory=asyncio.Queue, repr=False
    )
    _answer_queue: asyncio.Queue = attrs.field(
        init=False, factory=asyncio.Queue, repr=False
    )

    _reader: Optional[asyncio.StreamReader] = attrs.field(
        init=False, default=None, repr=False
    )
    _writer: Optional[asyncio.StreamWriter] = attrs.field(
        init=False, default=None, repr=False
    )

    def __attrs_post_init__(self) -> None:
        self._init_command = Command(
            estimated_response_time=0.5,
            validators=(
                CommandValidator(pattern=r".*(khz|mhz).*", relay_mode=str),
                CommandValidator(
                    pattern=r".*freq[uency]*\s*=?\s*([\d]+).*", frequency=int
                ),
                CommandValidator(pattern=r".*gain\s*=?\s*([\d]+).*", gain=int),
                CommandValidator(
                    pattern=r".*signal.*(on|off).*",
                    signal=lambda b: b.lower() == "on",
                ),
                CommandValidator(
                    pattern=r".*(serial|manual).*",
                    communication_mode=str,
                ),
            ),
            serial_communication=self,
        )
        self._protocol: CommunicationProtocol = LegacySonicProtocol()
        super().__init__()

    @property
    def protocol(self) -> CommunicationProtocol: 
        return self._protocol

    @property
    def connection_opened(self) -> asyncio.Event:
        return self._connection_opened

    @property
    def connection_closed(self) -> asyncio.Event:
        return self._connection_closed

    @property
    def handshake_result(self) -> Dict[str, Any]:
        return self._init_command.status_result

    async def connect(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        async def get_first_message() -> None:
            self._init_command.answer.receive_answer(
                await self.read_long_message(reading_time=6)
            )
            self._init_command.validate()
            ic(f"Init Command: {self._init_command}")

        try:
            self._reader, self._writer = reader, writer
        except Exception as e:
            ic(sys.exc_info())
            self._reader = None
            self._writer = None
        else:
            await get_first_message()
            self._connection_opened.set()
            asyncio.create_task(self._worker())

    async def _worker(self) -> None:
        async def send_and_get(command: Command) -> None:
            assert (self._writer is not None)

            self._writer.write(command.byte_message)
            await self._writer.drain()
            response = await (
                self.read_long_message(response_time=command.estimated_response_time)
                if command.expects_long_answer
                else self.read_message(response_time=command.estimated_response_time)
            )
            command.answer.receive_answer(response)
            await self._answer_queue.put(command)

        if self._writer is None or self._reader is None:
            ic("No connection available")
            return
        while self._writer is not None and not self._writer.is_closing():
            command: Command = await self._command_queue.get()
            async with self._lock:
                try:
                    await send_and_get(command)
                except serial.SerialException:
                    self.disconnect()
                    return
                except Exception as e:
                    ic(sys.exc_info())
                    break
        self.disconnect()

    async def send_and_wait_for_answer(self, command: Command) -> None:
        TIMEOUT = 10 # 10s
        await self._command_queue.put(command)
        received = await asyncio.wait_for(command.answer.received.wait(), TIMEOUT)
        if not received:
            raise ConnectionError("Device is not responding")

    async def read_message(self, response_time: float = 0.3) -> str:
        message: str = ""
        await asyncio.sleep(0.2)
        if self._reader is None:
            return message
        try:
            response = await asyncio.wait_for(
                self._reader.readline(), timeout=response_time
            )
            message = response.decode(PLATFORM.encoding).strip()
        except Exception as e:
            ic(f"Exception while reading {sys.exc_info()}")
        return message

    async def read_long_message(
        self, response_time: float = 0.3, reading_time: float = 0.2
    ) -> List[str]:
        if self._reader is None:
            return []

        target = time.time() + reading_time
        message: List[str] = []
        while time.time() < target:
            try:
                response = await asyncio.wait_for(
                    self._reader.readline(), timeout=response_time
                )
                line = response.decode(PLATFORM.encoding).strip()
                message.append(line)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                ic(f"Exception while reading {sys.exc_info()}")
                break

        return message

    def disconnect(self) -> None:
        self._writer.close() if self._writer is not None else None
        self._connection_opened.clear()
        self._connection_closed.set()
        self._reader = None
        self._writer = None
        self.emit(Event(Communicator.DISCONNECTED_EVENT))
