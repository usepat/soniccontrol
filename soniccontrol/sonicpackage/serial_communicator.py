import asyncio
from typing import *
import sys
import time
from icecream import ic
import serial
import serial_asyncio as aserial
import attrs
from soniccontrol.sonicpackage.interfaces import Communicator
from soniccontrol.sonicpackage.command import Command, CommandValidator
import soniccontrol.constants as const


@attrs.define
class SerialCommunicator(Communicator):
    _port: str = attrs.define()
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
    def port(self) -> str:
        return self._port

    @property
    def connection_opened(self) -> asyncio.Event:
        return self._connection_opened

    @property
    def connection_closed(self) -> asyncio.Event:
        return self._connection_opened

    @property
    def init_command(self) -> Optional[Command]:
        return self._init_command

    async def connect(self) -> None:
        async def get_first_message() -> None:
            self._init_command.answer.receive_answer(
                await self.read_long_message(reading_time=6)
            )
            self._init_command.validate()
            ic(f"Init Command: {self._init_command}")

        try:
            self._reader, self._writer = await aserial.open_serial_connection(
                url=self.port,
                baudrate=115200,
            )
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
        while not self._writer.is_closing():
            command: Command = await self._command_queue.get()
            async with self._lock:
                try:
                    await send_and_get(command)
                except serial.SerialException:
                    self.disconnect()
                    break
                except Exception as e:
                    ic(sys.exc_info())
                    break
        self.disconnect()

    async def send_and_wait_for_answer(self, command: Command) -> None:
        await self._command_queue.put(command)
        await command.answer.received.wait()

    async def read_message(self, response_time: float = 0.3) -> str:
        message: str = ""
        await asyncio.sleep(0.2)
        if self._reader is None:
            return message
        try:
            response = await asyncio.wait_for(
                self._reader.readline(), timeout=response_time
            )
            message = response.decode(const.ENCODING).strip()
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
                line = response.decode(const.ENCODING).strip()
                message.append(line)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                ic(f"Exception while reading {sys.exc_info()}")
                break

        return message

    def disconnect(self) -> None:
        self._writer.close()
        self._connection_opened.clear()
        self._connection_closed.set()
        self._reader = None
        self._writer = None
