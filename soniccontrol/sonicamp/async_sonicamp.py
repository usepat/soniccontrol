import asyncio
from asyncio import Queue, Event
from typing import Optional, Callable, List, Dict, Literal, Union, Iterable
import serial_asyncio as serial
import sys
from dataclasses import dataclass, field
import platform
import time


ENCODING: str = "windows-1252" if platform.system() == "Windows" else "utf-8"


@dataclass
class Command:
    message: str = field(default="")
    arguments: str = field(default="")
    answer_string: str = field(default="")
    answer_lines: List[str] = field(default_factory=list)
    resonse_time: float = field(default=0.3)
    received_answer: asyncio.Event = field(default_factory=asyncio.Event)

    @property
    def byte_message(self) -> bytes:
        return f"{self.message}{self.arguments}\n".encode(ENCODING)

    def receive_answer(self, answer: Union[List[str], str]) -> None:
        if isinstance(answer, list):
            self.answer_lines = answer
            self.answer_string = "\n".join(answer)
        elif isinstance(answer, str):
            self.answer_lines = answer.splitlines()
            self.answer_string = answer


class SerialCommunicator:
    def __init__(self, port: str) -> None:
        self.port: str = port
        self.command_queue: Queue[Command] = Queue()
        self.answer_queue: Queue[Command] = Queue()
        self.lock: asyncio.Lock = asyncio.Lock()
        self.encoding: str = (
            "windows-1252" if platform.system() == "Windows" else "utf-8"
        )
        self.reader = None
        self.writer = None
        self.init_message: List[str] = []

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
            asyncio.create_task(self.worker())

    async def worker(self) -> None:
        if self.writer is None or self.reader is None:
            print("No connection available")
            return
        while not self.writer.is_closing():
            command = await self.command_queue.get()
            # print(f"Getting command {command}")
            async with self.lock:
                try:
                    self.writer.write(command.byte_message)
                    await self.writer.drain()

                    response = await self.read_long_message(
                        response_time=command.resonse_time
                    )
                    command.receive_answer(response)
                    # print(f"Putting... command {command}")
                    command.received_answer.set()
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


class Ramp:
    def __init__(
        self,
        serial: SerialCommunicator,
        start_value: int,
        stop_value: int,
        step_value: int,
        hold_on_time: float = 0.1,
        hold_on_time_unit: Literal["ms", "s"] = "ms",
        hold_off_time: float = 0,
        hold_off_time_unit: Literal["ms", "s"] = "ms",
    ) -> None:
        self.serial: SerialCommunicator = serial

        self.running: asyncio.Event = asyncio.Event()

        self.start_value: int = start_value
        self.step_value: int = (
            abs(step_value) if start_value < stop_value else -abs(step_value)
        )
        self.stop_value: int = stop_value + step_value
        self.values: Iterable[int] = range(
            self.start_value, self.stop_value, self.step_value
        )

        self.hold_on_time: float = (
            hold_on_time if hold_on_time_unit == "s" else hold_on_time / 1000
        )
        self.hold_off_time: float = (
            hold_off_time if hold_off_time_unit == "s" else hold_off_time / 1000
        )

    async def update(self) -> None:
        while self.running.is_set():
            command = Command(message="?sens", resonse_time=0.4)
            await self.serial.command_queue.put(command)
            await command.received_answer.wait()

    async def execute(self) -> None:
        self.running.set()
        update_task = asyncio.create_task(self.update())
        ramping_task = asyncio.create_task(self.ramp())
        await asyncio.gather(ramping_task, update_task)

    async def ramp(self) -> None:
        for value in self.values:
            command = Command(message="!ON")
            await self.serial.command_queue.put(command)
            await command.received_answer.wait()

            command = Command(message="!f=", arguments=str(value))
            await self.serial.command_queue.put(command)
            await command.received_answer.wait()
            await asyncio.sleep(self.hold_on_time)

            command = Command(message="!OFF")
            await self.serial.command_queue.put(command)
            await command.received_answer.wait()
            await asyncio.sleep(self.hold_off_time)

        self.running.clear()


import ttkbootstrap as ttk
import tkinter as tk
from async_tkinter_loop import async_handler, async_mainloop


class Root(tk.Tk):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.serial = SerialCommunicator("COM6")

        self.connect_button = ttk.Button(
            self,
            text="Connect",
            bootstyle=ttk.SUCCESS,
            command=async_handler(self.connect, "COM6"),
        )
        self.connect_button.pack()
        self.button = ttk.Button(
            self,
            text="Send Command",
            command=async_handler(self.send_command, Command("!g=100")),
        )
        self.button.pack()
        self.label = ttk.Label(self, text="None")
        self.label.pack()
        # self.after(100, async_handler(self.engine))

    # async def engine(self) -> None:

    #     command = await device.answer_queue.get()
    #     self.after(100, async_handler(self.engine))

    async def connect(self, port: str) -> None:
        await self.serial.setup()
        await self.serial.command_queue.put(Command("?"))
        await self.serial.command_queue.put(Command("?info"))
        await self.serial.command_queue.put(Command("!ON"))
        await self.serial.command_queue.put(Command("!f=", "1000000"))

    async def send_command(self, command: Command) -> None:
        await self.serial.command_queue.put(command)
        command = await self.serial.answer_queue.get()
        self.label.configure(text=command.answer_string)


# async def main():
#     command = Command("-")
#     await device.command_queue.put(command)
#     await device.command_queue.put(Command("?"))
#     await device.command_queue.put(Command("?info"))
#     await device.command_queue.put(Command("!ON"))
#     await device.command_queue.put(Command("!f=", "1000000"))

#     ramp = Ramp(device, 1000000, 2000000, 1000)
#     task = asyncio.create_task(ramp.execute())
#     # await ramp.execute()
#     while True:
#         # await device.command_queue.put(Command("-", resonse_time=0.1))
#         # await device.command_queue.put(Command("?sens", resonse_time=0.4))
#         command = await device.answer_queue.get()
#         print(command)


# asyncio.run(main())

root = Root()
async_mainloop(root)
