import asyncio
import sys
import time
from typing import *

import logging
import attrs
import serial
import serial_asyncio as aserial
from soniccontrol.sonicpackage.package_fetcher import PackageFetcher
from icecream import ic
from soniccontrol.sonicpackage.command import Command, CommandValidator
from soniccontrol.sonicpackage.interfaces import Communicator
from soniccontrol.sonicpackage.package_parser import PackageParser, Package
from soniccontrol.utils.system import PLATFORM

logger = logging.getLogger()

@attrs.define
class SerialCommunicator(Communicator):
    _init_command: Optional[Command] = attrs.field(init=False, default=None)
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
        self._task = None
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
        )

    @property
    def connection_opened(self) -> asyncio.Event:
        return self._connection_opened

    @property
    def connection_closed(self) -> asyncio.Event:
        return self._connection_closed

    @property
    def init_command(self) -> Optional[Command]:
        return self._init_command

    async def connect(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        async def get_first_message() -> None:
            self._init_command.answer.receive_answer(
                await self.read_long_message(reading_time=6)
            )
            self._init_command.validate()
            ic(f"Init Command: {self._init_command}")

        self._reader = reader
        self._writer = writer
        self._package_fetcher = PackageFetcher(self._reader, print) # TODO: change log callback
        await get_first_message()
        self._connection_opened.set()

        self._task = asyncio.create_task(self._worker())
        self._package_fetcher.run()


    async def _worker(self) -> None:
        package_counter = 0
        async def send_and_get(command: Command) -> None:
            nonlocal package_counter
            package_counter += 1

            package = Package("0", "0", package_counter, command.full_message)
            message_str = PackageParser.write_package(package) + "\n" # \n is needed after the package.
            logger.debug(f"WRITE_PACKAGE({message_str})")
            message = message_str.encode(PLATFORM.encoding)
            self._writer.write(message)
            await self._writer.drain()

            answer = ""
            try:
                answer = await self._package_fetcher.get_answer_of_package(package_counter)
                # answer = await asyncio.wait_for(
                #     self._package_fetcher.get_answer_of_package(package_counter), timeout=command.estimated_response_time
                # )
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
        await self._command_queue.put(command)
        await command.answer.received.wait()


    async def read_long_message( # TODO: delete this method
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

    async def stop(self) -> None:
        if self._task  is not None:
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

