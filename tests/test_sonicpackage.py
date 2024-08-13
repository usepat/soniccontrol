# import asyncio
# import re
# import time
# from typing import Any, Optional

# import attrs
# import numpy as np
# import pytest
# from sonicpackage.amp_data import Info, Status
# from sonicpackage.command import Answer, Command
# from sonicpackage.commands import Commands
# from sonicpackage.interfaces import Communicator
# from sonicpackage.sonicamp_ import SonicAmp


# @attrs.define
# class StatusMock:
#     freq: int = 0
#     gain: int = 0
#     khz: bool = False
#     mhz: bool = False
#     signal: bool = False


# class MockSerial(Communicator):
#     def __init__(self):
#         super().__init__()
#         self._connection_opened = asyncio.Event()
#         self.count = 0
#         self.status = Status()

#     @property
#     def connection_opened(self) -> asyncio.Event:
#         return self._connection_opened

#     async def connect(self):
#         self._connection_opened.set()
#         await asyncio.sleep(0.5)

#     def disconnect(self):
#         self._connection_opened.clear()

#     async def send_and_wait_for_answer(self, message: Command) -> None:
#         # await asyncio.sleep(0.5)
#         time.sleep(0.5)
#         message.answer.receive_answer(self.process_answer(message))

#     async def read_message(
#         self, timeout: Optional[float] = None, *args, **kwargs
#     ) -> Any:
#         return

#     async def _worker(self) -> None:
#         return

#     def process_answer(self, command: Command) -> str:
#         cmd_text = command.byte_message.decode()
#         self.status.urms = np.sin(self.count)
#         self.status.irms = np.cos(self.count)
#         self.status.phase = np.tan(self.count)
#         self.status.temperature = np.random.randint(18, 25)
#         self.count += 1
#         if match := re.match(r"!f=(\d+)", cmd_text):
#             number = match.group(1)
#             self.status.frequency = int(number)
#             return f"freq={number}"
#         elif match := re.match(r"!g=(\d+)", cmd_text):
#             number = match.group(1)
#             self.status.gain = int(number)
#             return f"gain={number}"
#         elif match := re.match(r"!KHZ", cmd_text):
#             self.status.relay_mode = "KHz"
#             return "Mode set to KHZ"
#         elif match := re.match(r"!MHZ", cmd_text):
#             self.status.relay_mode = "MHz"
#             return "Mode set to MHZ"
#         elif match := re.match(r"!ON", cmd_text):
#             self.status.signal = True
#             return "Signal ON"
#         elif match := re.match(r"!OFF", cmd_text):
#             self.status.signal = False
#             return "Signal OFF"
#         elif match := re.match(r"-", cmd_text):
#             return f"{self.status.error}#{self.status.frequency}#{self.status.gain}#{self.status.protocol}#{int(self.status.wipe_mode)}#{self.status.temperature}#{self.status.urms}#{self.status.irms}#{self.status.phase}"
#         elif match := re.match(r"\?info", cmd_text):
#             return "this is a soniccatch information Ver.0.5"
#         elif match := re.match(r"\?type", cmd_text):
#             return "soniccatch"
#         elif match := re.match(r"\?sens", cmd_text):
#             return f"{self.status.frequency} {self.status.urms} {self.status.irms} {self.status.phase}"
#         elif match := re.match(r"\?", cmd_text):
#             return f"{'Signal OFF' if self.status.signal else 'Signal ON'} with freq={self.status.frequency} and gain={self.status.gain} and {self.status.relay_mode}"
#         else:
#             return ""


# def test_command_answer_reset():
#     answer: Answer = Answer()
#     answer._received.set()
#     answer._lines.extend(("test", "test", "test"))
#     answer._valid = True
#     answer._string = "test"
#     time_before: float = time.time()
#     answer._measured_response = 1
#     answer._received_timestamp = 1

#     answer.reset()

#     time_after: float = time.time()
#     assert answer.received.is_set() is False
#     assert not answer.lines
#     assert answer.valid is False
#     assert answer.string == ""
#     assert time_before <= answer._creation_timestamp <= time_after
#     assert not answer.measured_response
#     assert not answer.received_timestamp


# def test_command_answer_receive_answer():
#     answer: Answer = Answer()
#     answer.reset()
#     time_before: float = time.time()
#     answer.receive_answer("test")
#     time_after: float = time.time()

#     assert answer.received.is_set()
#     assert answer.lines
#     assert len(answer.lines) == 1
#     assert answer.string == "test"
#     assert answer.received_timestamp
#     assert time_before <= answer._received_timestamp <= time_after


# @pytest.mark.asyncio
# async def test_amp():
#     serial: MockSerial = MockSerial()
#     amp = SonicAmp(serial=serial, status=Status(), info=Info("catch"))
#     amp.updater.running.clear()
#     amp.add_commands(
#         (
#             Commands.set_frequency,
#             Commands.set_gain,
#             Commands.set_khz_mode,
#             Commands.set_mhz_mode,
#             Commands.signal_on,
#             Commands.signal_off,
#             Commands.get_sens,
#             Commands.get_info,
#             Commands.get_overview,
#             Commands.get_status,
#         )
#     )
#     await amp.set_frequency(100000)
#     assert amp.status.frequency == 100000

#     await amp.set_signal_on()
#     assert amp.status.signal is True

#     await amp.get_status()
#     assert serial.status.urms == amp.status.urms
#     assert serial.status.irms == amp.status.irms
#     assert serial.status.phase == amp.status.phase


# if __name__ == "__main__":
#     asyncio.run(test_amp())
