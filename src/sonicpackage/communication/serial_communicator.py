import asyncio
import logging
import sys
import time
from typing import Any, Dict, Final, Optional, List

import attrs
import serial
from sonicpackage.communication.package_fetcher import PackageFetcher
from icecream import ic
from sonicpackage.command import Command, CommandValidator
from sonicpackage.interfaces import Communicator
from sonicpackage.communication.sonicprotocol import CommunicationProtocol, LegacySonicProtocol, SonicProtocol
from sonicpackage.events import Event
from shared.system import PLATFORM


@attrs.define
class SerialCommunicator(Communicator):
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
    _logger: logging.Logger = attrs.field(default=logging.getLogger())

    def __attrs_post_init__(self) -> None:
        self._task = None
        self._logger = logging.getLogger(self._logger.name + "." + SerialCommunicator.__name__)
        self._protocol: CommunicationProtocol = SonicProtocol(self._logger)
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

    async def open_communication(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        self._logger.debug("try open communication")
        self._reader = reader
        self._writer = writer
        self._protocol = SonicProtocol(self._logger)
        self._package_fetcher = PackageFetcher(self._reader, self._protocol, self._logger)
        self._connection_opened.set()

        self._task = asyncio.create_task(self._worker())
        self._package_fetcher.run()

    async def _worker(self) -> None:
        self._logger.debug("Started worker")
        message_counter: int = 0
        message_id_max_client: Final[int] = 2 ** 16 - 1 # 65535 is the max for uint16. so we cannot go higher than that.

        async def send_and_get(command: Command) -> None:
            assert (self._writer is not None)

            if command.message != "-":
                self._logger.info("Send command: %s", command.full_message)

            nonlocal message_counter
            message_counter = (message_counter + 1) % message_id_max_client

            message_str = self._protocol.parse_request(
                command.full_message, message_counter
            )

            if command.message != "-":
                self._logger.info("Write package: %s", message_str)
            message = message_str.encode(PLATFORM.encoding)
            self._writer.write(message)
            await self._writer.drain()

            answer = ""
            try:
                answer = await self._package_fetcher.get_answer_of_package(
                    message_counter
                )
                if command.message != "-":
                    self._logger.info("Receive Answer: %s", answer)
            except Exception as e:
                self._logger.error(e)
                answer = "" # FIXME: is this a good idea to handle the error like this?

            command.answer.receive_answer(answer)
            self._answer_queue.put_nowait(command)

        if self._writer is None or self._reader is None:
            self._logger.warn("No connection is available")
            return

        try:
            while self._writer is not None and not self._writer.is_closing():
                command: Command = await self._command_queue.get()
                async with self._lock:
                    try:
                        await send_and_get(command)
                    except serial.SerialException as e:
                        self._logger.error(e)
                        await self._close_communication()
                        return
                    except Exception as e:
                        self._logger.error(e)
                        break
        except asyncio.CancelledError:
            self._logger.warn("The serial communicator was stopped")
            await self._close_communication()
            return
        await self._close_communication()

    async def send_and_wait_for_answer(self, command: Command) -> None:
        timeout = command.estimated_response_time 
        MAX_RETRIES = 3 # in seconds
        for i in range(MAX_RETRIES):
            await self._command_queue.put(command)
            received = await asyncio.wait_for(command.answer.received.wait(), timeout)
            if received:
                return
            self._logger.warn("%d th attempt of %d. Device did not respond in the given timeout of %d s", i, MAX_RETRIES, timeout)
        raise ConnectionError("Device is not responding")
    
    async def read_message(self) -> str:
        return await self._package_fetcher.pop_message()

    async def close_communication(self) -> None:
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def _close_communication(self) -> None:
        if self._task is not None:
            await self._package_fetcher.stop()
        self._connection_opened.clear()
        self._connection_closed.set()
        self._reader = None
        self._writer = None
        self._logger.info("Disconnected from device")
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
    _logger: logging.Logger = attrs.field(default=logging.getLogger())

    def __attrs_post_init__(self) -> None:
        self._task: Optional[asyncio.Task[None]] = None
        self._logger = logging.getLogger(self._logger.name + "." + LegacySerialCommunicator.__name__)
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

    async def open_communication(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        async def get_first_message() -> None:
            self._init_command.answer.receive_answer(
                await self.read_long_message(reading_time=6)
            )
            self._init_command.validate()
            self._logger.info(self._init_command.answer)

        self._reader, self._writer = reader, writer

        self._logger.info("Open communication with handshake")
        await get_first_message()
        self._connection_opened.set()
        self._task = asyncio.create_task(self._worker())

    async def _worker(self) -> None:
        async def send_and_get(command: Command) -> None:
            assert (self._writer is not None)
            if command.message != "-":
                self._logger.info("Write command: %s", command.byte_message)

            self._writer.write(command.byte_message)
            await self._writer.drain()
            response = await (
                self.read_long_message(response_time=command.estimated_response_time)
                if command.expects_long_answer
                else self.read_message()
            )

            if command.message != "-":
                self._logger.info("Received Answer: %s", response)
            command.answer.receive_answer(response)
            await self._answer_queue.put(command)

        if self._writer is None or self._reader is None:
            self._logger.warn("No connection available")
            return
        while self._writer is not None and not self._writer.is_closing():
            command: Command = await self._command_queue.get()
            async with self._lock:
                try:
                    await send_and_get(command)
                except serial.SerialException:
                    self._close_communication()
                    return
                except Exception as e:
                    self._logger.error(str(e))
                    break
        self._close_communication()

    async def send_and_wait_for_answer(self, command: Command) -> None:
        timeout = command.estimated_response_time + 0.1 # Add extra time because of long message 
        await self._command_queue.put(command)
        received = await asyncio.wait_for(command.answer.received.wait(), timeout)
        if not received:
            raise ConnectionError("Device is not responding")

    async def read_message(self) -> str:
        message: str = ""
        await asyncio.sleep(0.2)
        if self._reader is None:
            return message
        try:
            response = await self._reader.readline()
            message = response.decode(PLATFORM.encoding).strip()
        except Exception as e:
            self._logger.error(str(e))
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
                self._logger.error(str(e))
                break

        return message

    async def close_communication(self) -> None:
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    def _close_communication(self) -> None:
        self._connection_opened.clear()
        self._connection_closed.set()
        self._reader = None
        self._writer = None
        self.emit(Event(Communicator.DISCONNECTED_EVENT))
