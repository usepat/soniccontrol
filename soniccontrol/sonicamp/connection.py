from typing import List
import sys
import time
import asyncio
import platform
from serial_asyncio import serial

from soniccontrol.sonicamp.command import Command


class SerialCommunicator:
    def __init__(self, port: str) -> None:
        self.port: str = port
        self.connection_established: asyncio.Event = asyncio.Event()
        self._connection_open: asyncio.Event = asyncio.Event()

        self.command_queue: asyncio.Queue[Command] = asyncio.Queue()
        self.answer_queue: asyncio.Queue[Command] = asyncio.Queue()
        self.lock: asyncio.Lock = asyncio.Lock()
        self.encoding: str = (
            "windows-1252" if platform.system() == "Windows" else "utf-8"
        )
        self.reader = None
        self.writer = None
        self.init_message: List[str] = []

    @property
    def connection_open(self) -> asyncio.Event:
        return self._connection_open

    async def setup(self) -> None:
        try:
            self.reader, self.writer = await serial.open_serial_connection(
                url=self.port,
                baudrate=115200,
            )
        except Exception as e:
            print(sys.exc_info())
            self.reader = None
            self.writer = None
        else:
            self.init_message = await self.read_long_message(reading_time=6)
            print("\n".join(self.init_message))
            self.connection_established.set()
            self.connection_open.set()
            asyncio.create_task(self.worker())

    async def worker(self) -> None:
        if self.writer is None or self.reader is None:
            print("No connection available")
            return
        while not self.writer.is_closing():
            command = await self.command_queue.get()
            async with self.lock:
                try:
                    self.writer.write(command.byte_message)
                    await self.writer.drain()

                    response = await self.read_long_message(
                        response_time=command.response_time
                    )
                    command.receive_answer(response)
                    command.answer_received.set()
                    await self.answer_queue.put(command)
                except Exception as e:
                    print(sys.exc_info())
                    break

    async def read_long_message(
        self, response_time: float = 0.3, reading_time: float = 0.1
    ) -> List[str]:
        if self.reader is None:
            return []

        target = time.time() + reading_time
        message: List[str] = []
        while time.time() < target:
            try:
                response = await asyncio.wait_for(
                    self.reader.readline(), timeout=response_time
                )
                line = response.decode(self.encoding).strip()
                message.append(line)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"Exception while reading {sys.exc_info()}")
                break

        return message
