from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Union, Dict, Any, Literal

import datetime
import copy
import threading
import time
import logging

# from soniccontrol.sonicamp.sonicagent import SerialAgent
from soniccontrol.sonicamp.status import StatusAdapter, BasicStatusAdapter
from soniccontrol.sonicamp.amp_factory import AmpFactory
from soniccontrol.sonicamp.command import SerialCommand, Command, SonicAmpCommand
from soniccontrol.sonicamp.serialagent import SerialAgent, SonicThread

# from soniccontrol.sonicamp.controllers import (
#     FrequencyController,
#     GainController,
#     ModeController,
# )

logger = logging.getLogger(__name__)


class SonicAmp:
    def __init__(self, sonicagent: SonicThread, serialagent: SerialAgent) -> None:
        self._sonicagent: SonicThread = sonicagent
        self._serialagent: SerialAgent = serialagent
        self.ramp_running: threading.Event = threading.Event()
        self.holding: threading.Event = threading.Event()
        self.holding_condition: threading.Condition = threading.Condition(
            threading.Lock()
        )

    @classmethod
    def build_amp(cls, sonicagent: SonicThread, serialagent: SerialAgent) -> SonicAmp:
        print(serialagent.init_message)
        return cls(sonicagent, serialagent)

    def react_on_command(self, command: SonicAmpCommand) -> Command:
        if not (
            isinstance(command.method_name, str) and hasattr(self, command.method_name)
        ):
            raise AttributeError(f"{command.method_name} is not an attribute of {self}")
        method = getattr(self, command.method_name)
        logger.debug(f"Reacting on command... {command.method_name}")
        method(command, *command.method_args, **command.method_kwargs)
        return command

    def set_signal_off(self, command: SonicAmpCommand, *args, **kwargs) -> None:
        command.message = "!OFF"
        self._serialagent.add_job(command, 0)
        command.processed.wait()
        command.processed.clear()

    def set_signal_on(self, command: SonicAmpCommand, *args, **kwargs) -> None:
        command.message = "!ON"
        self._serialagent.add_job(command, 0)
        command.processed.wait()
        command.processed.clear()

    def get_modules(self, command: SonicAmpCommand, *args, **kwargs) -> None:
        command.message = "="
        self._serialagent.add_job(command, 0)
        command.processed.wait()
        command.processed.clear()

    def get_status(self, command: SonicAmpCommand, *args, **kwargs) -> None:
        command.message = "-"
        self._serialagent.add_job(command, 0)
        command.processed.wait()
        command.processed.clear()

    def get_sens(self, command: SonicAmpCommand, *args, **kwargs) -> None:
        command.message = "?sens"
        self._serialagent.add_job(command, 0)
        command.processed.wait()
        command.processed.clear()

    def get_overview(self, command: SonicAmpCommand, *args, **kwargs) -> None:
        command.message = "?"
        command.expected_big_answer = True
        self._serialagent.add_job(command, 0)
        command.processed.wait()
        command.processed.clear()

    def set_signal_auto(self, command: SonicAmpCommand, *args, **kwargs) -> None:
        command.message = "!AUTO"
        self._serialagent.add_job(command, 0)
        command.processed.wait()
        command.processed.clear()

    def set_frequency(
        self, command: SonicAmpCommand, frequency: int, *args, **kwargs
    ) -> None:
        command.message = f"!f={frequency}"
        print(f"setting frq to {command.message}")
        self._serialagent.add_job(command, 0)
        command.processed.wait()
        command.processed.clear()

    def hold(
        self, command: SonicAmpCommand, duration: float, unit: Literal["ms", "s"]
    ) -> None:
        self.holding.set()
        # self.holding_condition.notify_all()

        duration /= 1000.0 if unit == "ms" else 1
        end_time = command.processed_timestamp + duration
        while time.time() < end_time:
            self._sonicagent.add_output_job(
                SonicAmpCommand(type_=f"hold {end_time - time.time()} {unit} remaining")
            )
            self.get_status(command=command)
            time.sleep(0.1 if unit == "s" else 0.001)

        self.holding.clear()
        with self.holding_condition:
            self.holding_condition.notify_all()

    def ramp(
        self,
        command: SonicAmpCommand,
        start: int,
        stop: int,
        step: int,
        hold_on_time: float = 1,
        hold_on_time_unit: Literal["ms", "s"] = "ms",
        hold_off_time: float = 0,
        hold_off_time_unit: Literal["ms", "s"] = "ms",
        *args,
        **kwargs,
    ) -> Ramp:
        ramp: Ramp = Ramp(
            self,
            command,
            start,
            stop,
            step,
            hold_on_time,
            hold_on_time_unit,
            hold_off_time,
            hold_off_time_unit,
        )
        ramp.daemon = True
        ramp.start()
        ramp.resume()
        return ramp

    def chirp_ramp(
        self,
        command: SonicAmpCommand,
        start: int,
        difference: int,
        step: int,
        times: int,
        hold_on_time: int,
        hold_on_time_unit: Literal["ms", "s"],
        hold_off_time: int,
        hold_off_time_unit: Literal["ms", "s"],
    ) -> None:
        for _ in range(times):
            ramp = self.ramp(
                command=command,
                start=start,
                stop=start + difference,
                step=step,
                hold_on_time=hold_on_time,
                hold_on_time_unit=hold_on_time_unit,
                hold_off_time=hold_off_time,
                hold_off_time_unit=hold_off_time_unit,
            )
            ramp.shutdown_request.wait()

    def process_output_command(self, command: Command) -> Command:
        return command


class Ramp(SonicThread):
    def __init__(
        self,
        sonicamp: SonicAmp,
        command: SonicAmpCommand,
        start_value: int,
        stop_value: int,
        step_value: int,
        hold_on_time: float = 1,
        hold_on_time_unit: Literal["ms", "s"] = "ms",
        hold_off_time: float = 0,
        hold_off_time_unit: Literal["ms", "s"] = "ms",
        *args,
        **kwargs,
    ) -> None:
        super().__init__()
        self.wait_condition: threading.Condition = threading.Condition(threading.Lock())

        self.sonicamp: SonicAmp = sonicamp
        self.command: SonicAmpCommand = command

        self.start_value: int = start_value
        self.step_value: int = step_value if start_value < stop_value else -step_value
        self.stop_value: int = stop_value + step_value
        self.values: Iterable[int] = range(
            self.start_value, self.stop_value, self.step_value
        )
        self.current_value: Optional[int] = None

        self.hold_off_time: float = hold_off_time
        self.hold_on_tuple: Tuple[int, str] = (hold_on_time, hold_on_time_unit)
        self.hold_off_tuple: Tuple[int, str] = (hold_off_time, hold_off_time_unit)

    def setup(self) -> None:
        if self.shutdown_request.is_set():
            return

    def worker(self) -> None:
        self.sonicamp.ramp_running.set()
        print(f"ramp {self.start_value, self.stop_value, self.step_value}")
        self.sonicamp.set_signal_on(command=self.command)
        for value in self.values:
            print(f"ramp setting {value}")

            self.sonicamp.set_frequency(command=self.command, frequency=value)

            if self.hold_off_time:
                self.sonicamp.set_signal_on(command=self.command)

            self.sonicamp.hold(self.command, *self.hold_on_tuple)
            with self.sonicamp.holding_condition:
                self.sonicamp.holding_condition.wait_for(
                    lambda: not self.sonicamp.holding.is_set()
                )
            # self.sonicamp.holding.wait()

            if self.hold_off_time:
                self.sonicamp.set_signal_off(command=self.command)

                self.sonicamp.hold(self.command, *self.hold_off_tuple)
                with self.sonicamp.holding_condition:
                    self.sonicamp.holding_condition.wait_for(
                        lambda: not self.sonicamp.holding.is_set()
                    )
                # self.sonicamp.holding.wait()

        self.sonicamp.ramp_running.clear()
        return


# class SonicAmp:
#     @dataclass
#     class Data:
#         type_: str = field(default="")
#         version: float = field(default=0.0)
#         firmware_msg: str = field(default="")
#         modules: Optional[SonicAmp.Modules] = field(default=None)
#         status: Optional[SonicAmp.Status] = field(default=None)

#     @dataclass(frozen=True)
#     class Modules:
#         buffer: bool = field(default=False)
#         display: bool = field(default=False)
#         eeprom: bool = field(default=False)
#         fram: bool = field(default=False)
#         i_current: bool = field(default=False)
#         current1: bool = field(default=False)
#         current2: bool = field(default=False)
#         io_serial: bool = field(default=False)
#         thermo_ext: bool = field(default=False)
#         thermo_int: bool = field(default=False)
#         khz: bool = field(default=False)
#         mhz: bool = field(default=False)
#         portexpander: bool = field(default=False)
#         protocol: bool = field(default=False)
#         protocol_fix: bool = field(default=False)
#         relais: bool = field(default=False)
#         scanning: bool = field(default=False)
#         sonsens: bool = field(default=False)
#         tuning: bool = field(default=False)
#         switch: bool = field(default=False)
#         switch2: bool = field(default=False)

#     @dataclass
#     class Status:
#         error: int = field(default=0, repr=False)
#         frequency: int = field(default=0)
#         gain: int = field(default=0)
#         current_protocol: int = field(default=0, repr=False)
#         wipe_mode: bool = field(default=False, repr=False)
#         temperature: float = field(default=0)
#         signal: bool = field(default=False)
#         urms: Union[float, int] = field(default=0)
#         irms: Union[float, int] = field(default=0)
#         phase: Union[float, int] = field(default=0)
#         timestamp: datetime.datetime = field(
#             default_factory=datetime.datetime.now, compare=False
#         )

#         default_adapter: StatusAdapter = field(
#             default=BasicStatusAdapter, repr=False, compare=False, hash=False
#         )

#         @classmethod
#         def from_data(
#             cls, data: str, adapter: Optional[StatusAdapter] = None
#         ) -> SonicAmp.Status:
#             return cls(
#                 adapter.convert_data(data)
#                 if adapter
#                 else cls.default_adapter.convert_data(data)
#             )

#         @classmethod
#         def from_updated_data(
#             cls,
#             old_status: SonicAmp.Status,
#             data: str,
#             adapter: Optional[StatusAdapter] = None,
#         ) -> SonicAmp.Status:
#             return cls(
#                 adapter.update_data(old_status, data)
#                 if adapter
#                 else cls.default_adapter.update_data(old_status, data)
#             )

#         def dump(self) -> Dict[str, Any]:
#             return self.__dict__

#     def __init__(
#         self,
#         serial_agent: SerialAgent,
#         data: SonicAmp.Data,
#         update_strategy: StatusAdapter,
#         frequency_controller: FrequencyController,
#         gain_controller: GainController,
#         mode_controller: ModeController,
#     ) -> None:
#         self._serial_agent: SerialAgent = serial_agent
#         self._frequency_controller: FrequencyController = frequency_controller
#         self._gain_controller: GainController = gain_controller
#         self._mode_controller: ModeController = mode_controller
#         self._update_strategy: StatusAdapter = update_strategy

#         self._data: SonicAmp.Data = data

#     @property
#     def serial_agent(self) -> SerialAgent:
#         return self._serial_agent

#     @staticmethod
#     def build_amp(data: SonicAmp.Data) -> SonicAmp:
#         return AmpFactory.build_amp(data)

#     def update(self) -> None:
#         self._update_strategy.update(self._data.status)

#     def get_status(self) -> Status:
#         ...

#     def get_sens(self) -> Dict[str, Union[float, int]]:
#         ...

#     def get_modules(self) -> SonicAmp.Modules:
#         ...

#     def set_frequency(self, frequency: int) -> str:
#         self._update_strategy.operation(
#             self._frequency_controller.operation(frequency), self._data.status
#         )

#     def set_gain(self, gain: int) -> None:
#         self._update_strategy.operation(
#             self._gain_controller.operation(gain), self._data.status
#         )

#     def set_signal_on(self) -> None:
#         self._update_strategy.operation(
#             self._mode_controller.signal_on(), self._data.status
#         )

#     def set_signal_off(self) -> None:
#         self._update_strategy.operation(
#             self._mode_controller.signal_off(), self._data.status
#         )

#     def set_signal_auto(self) -> None:
#         self._update_strategy.operation(
#             self._mode_controller.signal_auto(), self._data.status
#         )

#     def hold(self) -> None:
#         pass

#     def ramp_freq(self) -> None:
#         pass

#     def ramp_gain(self) -> None:
#         pass

#     def chirp_ramp_freq(self) -> None:
#         pass

#     def chirp_ramp_gain(self) -> None:
#         pass
