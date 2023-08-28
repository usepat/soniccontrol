from __future__ import annotations
import asyncio
from asyncio import Queue, Event
from typing import Optional, Callable, List, Dict, Literal, Union, Iterable, Set
import serial_asyncio as serial
import sys
import attrs

# from attrs import define, field
import platform
import datetime
import time


ENCODING: str = "windows-1252" if platform.system() == "Windows" else "utf-8"


@attrs.define
class Command:
    message: str = attrs.field(default="")
    arguments: str = attrs.field(default="")
    answer_string: str = attrs.field(default="")
    answer_lines: List[str] = attrs.field(factory=list)
    resonse_time: float = attrs.field(default=0.3)
    answer_is_received: asyncio.Event = attrs.field(factory=asyncio.Event)
    answer_received_timestamp: datetime.datetime = attrs.field(
        factory=datetime.datetime.now
    )

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
        self.connection_established: asyncio.Event = asyncio.Event()
        self._connection_open: asyncio.Event = asyncio.Event()

        self.command_queue: Queue[Command] = Queue()
        self.answer_queue: Queue[Command] = Queue()
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
                    command.answer_is_received.set()
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


@attrs.define
class Status:
    error: int = attrs.field(default=0, repr=False)
    frequency: int = attrs.field(default=0)
    gain: int = attrs.field(default=0)
    current_protocol: int = attrs.field(default=0, repr=False)
    wipe_mode: bool = attrs.field(default=False, repr=False)
    temperature: float = attrs.field(default=0)
    signal: bool = attrs.field(default=False)
    urms: float = attrs.field(default=0, validator=attrs.validators.instance_of(float))
    irms: float = attrs.field(default=0, validator=attrs.validators.instance_of(float))
    phase: float = attrs.field(default=0, validator=attrs.validators.instance_of(float))
    timestamp: datetime.datetime = attrs.field(factory=datetime.datetime.now, eq=False)
    changed_fields: Set[str] = attrs.field(factory=set)

    def update_from_sens_command(
        self,
        command: Command,
        fullscale: bool = False,
        old_status: Optional[Status] = None,
    ) -> Status:
        freq, urms, irms, phase = map(int, command.answer_string.split(" "))

        if fullscale:
            urms = urms if urms > 282300 else 282300
            urms = (urms * 0.000400571 - 1130.669402) * 1000 + 0.5
            irms = irms if irms > 3038000 else 303800
            irms = (irms * 0.000015601 - 47.380671) * 1000 + 0.5
            phase = (phase * 0.125) * 100

        if old_status:
            return attrs.evolve(self, )
            


@attrs.define
class Hold:
    def __init__(self, duration: float, unit: Literal["ms", "s"]) -> None:
        self.holding: asyncio.Event = asyncio.Event()
        self.duration: float = duration
        self.unit: Literal["ms", "s"] = unit
        self.duration: float = duration if self.unit == "s" else duration / 1000
        self._remaining_time: Optional[float] = None

    @property
    def remaining_time(self) -> Optional[float]:
        return self._remaining_time

    async def execute(self) -> None:
        self.holding.set()
        end_time: float = time.time() + self.duration
        while time.time() < end_time:
            self._remaining_time = round(end_time - time.time(), 2)
            await asyncio.sleep(0.01)

        self._remaining_time = 0
        self.holding.clear()


@attrs.define
class Ramp:
    def __init__(
        self,
        sonicamp: SonicAmp,
        start_value: int,
        stop_value: int,
        step_value: int,
        hold_on_time: float = 0.1,
        hold_on_time_unit: Literal["ms", "s"] = "ms",
        hold_off_time: float = 0,
        hold_off_time_unit: Literal["ms", "s"] = "ms",
    ) -> None:
        self.sonicamp: SonicAmp = sonicamp

        self.running: asyncio.Event = asyncio.Event()
        self._current_value: Optional[int] = None

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
        self.hold_on_time_unit: Literal["ms", "s"] = hold_on_time_unit
        self.hold_off_time: float = (
            hold_off_time if hold_off_time_unit == "s" else hold_off_time / 1000
        )
        self.hold_off_time_unit: Literal["ms", "s"] = hold_off_time_unit

    @property
    def current_value(self) -> Optional[int]:
        return self._current_value

    async def update(self) -> None:
        while self.running.is_set():
            await self.sonicamp.get_sens()

    async def execute(self) -> None:
        self.running.set()
        update_task = asyncio.create_task(self.update())
        ramping_task = asyncio.create_task(self.ramp())
        # await self.ramp()
        await asyncio.gather(ramping_task, update_task)

    async def ramp(self) -> None:
        await self.sonicamp.set_signal_on()

        for value in self.values:
            self._current_value = value
            if self.hold_off_time:
                await self.sonicamp.set_signal_on()

            await self.sonicamp.set_frequency(value)
            await self.sonicamp.hold(self.hold_on_time, self.hold_on_time_unit)

            if self.hold_off_time:
                await self.sonicamp.set_signal_off()
                await self.sonicamp.hold(self.hold_off_time, self.hold_off_time_unit)

        self.running.clear()


class SonicAmpFactory:
    @staticmethod
    def build_amp(serial: SerialCommunicator) -> SonicAmp:
        return SonicAmp(serial)


class SonicAmp:
    def __init__(self, serial: SerialCommunicator) -> None:
        self.serial: SerialCommunicator = serial
        self.script_running: asyncio.Event = asyncio.Event()
        self.status = ""

        self.ramper: Optional[Ramp] = None
        self.holder: Optional[Hold] = None

    @staticmethod
    def build_amp(serial: SerialCommunicator) -> SonicAmp:
        return SonicAmpFactory.build_amp(serial)

    async def execute_command(self, command: Command) -> Command:
        await self.serial.command_queue.put(command)
        await command.answer_is_received.wait()
        return command

    async def set_frequency(self, frequency: int) -> str:
        command = await self.execute_command(
            Command(message="!f=", arguments=str(frequency))
        )
        return command.answer_string

    async def set_gain(self, gain: int) -> str:
        command = await self.execute_command(
            Command(message="!g=", arguments=str(gain))
        )
        return command.answer_string

    async def get_status(self) -> str:
        command = await self.execute_command(Command(message="-"))
        return command.answer_string

    async def get_sens(self) -> str:
        command = await self.execute_command(Command(message="?sens", resonse_time=0.4))
        return command.answer_string

    async def set_signal_off(self) -> str:
        command = await self.execute_command(Command(message="!OFF"))
        return command.answer_string

    async def set_signal_on(self) -> str:
        command = await self.execute_command(Command(message="!ON"))
        return command.answer_string

    async def set_signal_auto(self) -> str:
        command = await self.execute_command(Command(message="!AUTO"))
        return command.answer_string

    async def hold(
        self, duration: float = 100, unit: Literal["ms", "s"] = "ms"
    ) -> None:
        self.holder = Hold(duration=duration, unit=unit)
        await self.holder.execute()

    async def ramp(
        self,
        start: int,
        stop: int,
        step: int,
        hold_on_time: float,
        hold_on_time_unit: Literal["ms", "s"],
        hold_off_time: float,
        hold_off_time_unit: Literal["ms", "s"],
    ) -> None:
        self.ramper = Ramp(
            self,
            start,
            stop,
            step,
            hold_on_time,
            hold_on_time_unit,
            hold_off_time,
            hold_off_time_unit,
        )
        asyncio.create_task(self.ramper.execute())


import ttkbootstrap as ttk
import tkinter as tk
from async_tkinter_loop import async_handler, async_mainloop


class Root(tk.Tk):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.serial = SerialCommunicator("COM6")
        self.sonicamp = SonicAmp.build_amp(self.serial)

        self.connect_button = ttk.Button(
            self,
            text="Connect",
            bootstyle=ttk.SUCCESS,
            command=async_handler(self.connect, "COM6"),
        )
        self.connect_button.pack()
        self.button = ttk.Button(
            self,
            text="Set gain",
            command=async_handler(self.set_gain),
        )
        self.button.pack()

        self.button = ttk.Button(
            self,
            text="Ramp",
            command=async_handler(
                self.sonicamp.ramp, 1000000, 2000000, 1000, 1, "s", 1, "s"
            ),
        )
        self.button.pack()

        self.label = ttk.Label(self, text="None")
        self.label.pack()

        self.after(100, async_handler(self.update_engine))

    async def update_engine(self) -> None:
        if self.sonicamp.ramper and self.sonicamp.ramper.running.is_set():
            self.label.configure(text=str(self.sonicamp.ramper.current_value))
        if self.sonicamp.holder and self.sonicamp.holder.holding.is_set():
            self.label.configure(text=str(self.sonicamp.holder.remaining_time))
        self.after(100, async_handler(self.update_engine))

    async def set_gain(self) -> None:
        answer = await self.sonicamp.set_gain(100)
        self.label.configure(text=answer)

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


async def main():
    device = SerialCommunicator(port="COM6")
    await device.setup()
    sonicamp = SonicAmp.build_amp(device)

    # status_engine = asyncio.create_task(sonicamp.update_engine())
    answer = await sonicamp.set_signal_off()
    print(answer)
    answer = await sonicamp.get_sens()
    print(answer)
    answer = await sonicamp.get_status()
    print(answer)
    command = Command("-")

    # asyncio.create_task(sonicamp.ramp(1000000, 2000000, 1000, 5, "s", 5, "s"))
    await sonicamp.ramp(1000000, 2000000, 1000, 5, "s", 5, "s")

    await device.command_queue.put(command)
    await device.command_queue.put(Command("?"))
    await device.command_queue.put(Command("?info"))
    await device.command_queue.put(Command("!ON"))
    await device.command_queue.put(Command("!f=", "1000000"))

    # ramp = Ramp(device, 1000000, 2000000, 1000)
    # task = asyncio.create_task(ramp.execute())
    # await ramp.execute()
    while True:
        # await device.command_queue.put(Command("-", resonse_time=0.1))
        # await device.command_queue.put(Command("?sens", resonse_time=0.4))
        command = await device.answer_queue.get()
        print(command)


# asyncio.run(main())

root = Root()
async_mainloop(root)
