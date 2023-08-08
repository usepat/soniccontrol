from typing import Any, Optional, Iterable, Set, Dict
import tkinter as tk
import ttkbootstrap as ttk
import abc
import csv
import logging
import pathlib
import soniccontrol.constants as const
import copy
from soniccontrol.sonicamp import SonicAmpAgent, Command
from soniccontrol.interfaces import (
    Resizable,
    Updatable,
    Disconnectable,
    Configurable,
    Connectable,
    Scriptable,
    Feedbackable,
    Resizer,
    Layout,
)
import sonicpackage as sp

logger = logging.getLogger(__name__)


class Root(tk.Tk, Resizable, Updatable):
    def __init__(self) -> None:
        super().__init__()
        self._width_layouts: Optional[Iterable[Layout]] = None
        self._height_layouts: Optional[Iterable[Layout]] = None
        self._resizer: Resizer = Resizer(self)

        # (global set) tkinter variables
        self._freq: tk.IntVar = tk.IntVar()
        self._gain: tk.IntVar = tk.IntVar()
        self._wipe_inf_or_def: tk.BooleanVar = tk.BooleanVar()
        self._wipe_cycles: tk.IntVar = tk.IntVar()

        # (glabal read) tkinter variables
        self.frequency: ttk.DoubleVar = ttk.DoubleVar(value=1000)
        self.frequency_text: ttk.StringVar = ttk.StringVar()
        self.frequency.trace(ttk.W, self.on_frequency_change)

        self.gain: ttk.IntVar = ttk.IntVar(value=100)
        self.gain_text: ttk.StringVar = ttk.StringVar()
        self.gain.trace(ttk.W, self.on_gain_change)

        self.temperature: ttk.IntVar = ttk.IntVar(value=23.5)
        self.temperature_text: ttk.StringVar = ttk.StringVar()
        self.temperature.trace(ttk.W, self.on_temperature_change)

        self.urms: ttk.IntVar = ttk.IntVar(value=1003)
        self.urms_text: ttk.IntVar = ttk.StringVar()
        self.urms.trace(ttk.W, self.on_urms_change)

        self.irms: ttk.IntVar = ttk.IntVar(value=134)
        self.irms_text: ttk.IntVar = ttk.StringVar()
        self.irms.trace(ttk.W, self.on_irms_change)

        self.phase: ttk.IntVar = ttk.IntVar(value=75)
        self.phase_text: ttk.IntVar = ttk.StringVar()
        self.phase.trace(ttk.W, self.on_phase_change)

        self.signal: ttk.BooleanVar = ttk.BooleanVar(value=False)
        self.signal.trace(ttk.W, self.on_signal_change)

        self.mode: ttk.StringVar = ttk.StringVar(value="Catch")
        self.soniccontrol_state: ttk.StringVar = ttk.StringVar(value="Manual")
        self.port: ttk.StringVar = ttk.StringVar()
        self.connection_status: ttk.StringVar = ttk.StringVar()

        self.status_log_filepath: pathlib.Path = pathlib.Path("logs//status_log.csv")
        self.status_log_filepath_existed: bool = self.status_log_filepath.exists()
        self.status_log_filepath.parent.mkdir(parents=True, exist_ok=True)
        self.fieldnames: list[str] = [
            "timestamp",
            "signal",
            "frequency",
            "gain",
            "urms",
            "irms",
            "phase",
            "temperature",
        ]

        self.sonicamp: Optional[SonicAmpAgent] = None
        self.priority_counter: int = 5
        self.old_status: Optional[sp.Status] = None
        self.update_values_to_check: Dict[str, ttk.Variable] = {
            "frequency": self.frequency,
            "gain": self.gain,
            "temperature": self.temperature,
            "urms": self.urms,
            "irms": self.irms,
            "phase": self.phase,
            "signal": self.signal,
        }

        self.disconnectables: Set[Disconnectable] = set()
        self.connectables: Set[Connectable] = set()
        self.configurables: Set[Configurable] = set()
        self.updatables: Set[Updatable] = set()
        self.scriptables: Set[Scriptable] = set()
        self.feedbackables: Set[Feedbackable] = set()
        logger.debug("initialized Root")

    @property
    def resizer(self) -> Resizer:
        return self._resizer

    @property
    def width_layouts(self) -> Iterable[Layout]:
        return self._width_layouts

    @property
    def height_layouts(self) -> Iterable[Layout]:
        return self._height_layouts

    def bind_events(self) -> None:
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind(const.Events.RESIZING, self.on_resizing)
        self.bind(const.Events.SET_GAIN, self.on_gain_set)

    def on_resizing(self, event: Any, *args, **kwargs) -> None:
        return self.resizer.resize(event=event)

    def on_connect(self, event=None) -> None:
        logger.debug("Connection attempt")
        if not self.connect_to_amp():
            return
        self.status_engine()

    def connect_to_amp(self) -> bool:
        try:
            self.sonicamp: SonicAmpAgent = SonicAmpAgent(self.port.get())
            self.sonicamp.daemon = True
            self.sonicamp.start()
            self.sonicamp.resume()
            return True
        except Exception as e:
            logger.debug(f"Hello? {e}")
            return False

    def after_connect(self) -> None:
        for connectable in self.connectables:
            connectable.on_connect(
                Connectable.ConnectionData(
                    heading1="sonic",
                    heading2="catch",
                    subtitle="You are connected to",
                    firmware_info="SONICCATCH FIRMWARE",
                    tabs=self.frames_for_soniccatch,
                )
            )
        self.connected = True

    def status_engine(self) -> None:
        def is_connection_ready() -> None:
            if self.sonicamp.connection_established.is_set():
                self.after_connect()
                self.sonicamp.connection_established.clear()
            return self.sonicamp.connection.is_set()

        def check_output_queue() -> None:
            while self.sonicamp.output_queue.qsize():
                priority, command = self.sonicamp.output_queue.get()
                logger.debug(f"Command: {command}, Prio: {priority}")

                if command.type_ == "status":
                    if command.message == "-":
                        if self.old_status is None:
                            status: sp.Status = sp.Status().from_string(command.answer)
                        else:
                            status: sp.Status = copy.deepcopy(
                                self.old_status
                            ).update_status(command.answer)
                    else:
                        status: sp.Status = copy.deepcopy(self.old_status).from_sens(
                            command.answer
                        )
                    logger.debug(status)
                    self.serialize_data(status)
                    self.on_update(status)

                elif command.type_ == "feedback":
                    for child in self.feedbackables:
                        child.on_feedback(command.answer)

                self.check_output_queue(command)
                self.sonicamp.output_queue.task_done()
            self.sonicamp.add_job(
                Command(message="-", type_="status"), self.priority_counter
            )
            self.priority_counter += 1
            if self.old_status.signal:
                self.sonicamp.add_job(
                    Command(message="?sens", type_="status"), self.priority_counter
                )
                self.priority_counter += 1

        def check_exceptions_queue() -> None:
            if not self.sonicamp.exceptions_queue.empty():
                (
                    exception_type,
                    exception_value,
                    traceback,
                ) = self.sonicamp.exceptions_queue.get()

                logger.warning(f"Got exception {exception_type}")
                logger.warning(f"Got exception value {exception_value}")

                if issubclass(exception_type, sp.serial.SerialException):
                    self.after_cancel(self.status_engine_after_id)
                    self.event_generate(const.Events.DISCONNECTED)
                    return

                self.sonicamp.exceptions_queue.task_done()

        self.status_engine_after_id = self.after(100, self.status_engine)
        if self.sonicamp is None or not is_connection_ready():
            return
        check_output_queue()
        check_exceptions_queue()

    def serialize_data(self, status: sp.Status) -> None:
        with self.status_log_filepath.open(mode="a", newline="") as file:
            writer = csv.DictWriter(
                file, fieldnames=self.fieldnames, extrasaction="ignore"
            )
            if not self.status_log_filepath_existed:
                writer.writeheader()
                self.status_log_filepath_existed = True
            writer.writerow(status.dump())

    def check_output_queue(self, command: Command) -> None:
        pass

    def stop_status_engine(self) -> None:
        if self.sonicamp is not None:
            self.sonicamp.shutdown()
            self.sonicamp = None

    def on_update(self, status: sp.Status, *args, **kwargs) -> None:
        if self.old_status is None:
            for attribute, tk_var in self.update_values_to_check.items():
                new_value = getattr(status, attribute)
                tk_var.set(new_value)
                logger.debug(f"Updating attribute: {attribute}, {tk_var.get()}")
            self.old_status = status
            return

        for attribute, tk_var in self.update_values_to_check.items():
            old_value = getattr(self.old_status, attribute)
            new_value = getattr(status, attribute)
            if old_value != new_value:
                tk_var.set(new_value)
                logger.debug(f"Updating attribute: {attribute}, {tk_var.get()}")

        self.old_status = status

    def on_frequency_change(self, event: Any = None, *args, **kwargs) -> None:
        self.frequency.set(self.frequency.get() / 1000)
        self.frequency_text.set(f"Freq.: {self.frequency.get()} kHz")
        for child in self.updatables:
            child.on_frequency_change()

    def on_gain_change(self, event: Any = None, *args, **kwargs) -> None:
        self.gain_text.set(f"Gain: {self.gain.get()} %")
        for child in self.updatables:
            child.on_gain_change()

    def on_temperature_change(self, event: Any = None, *args, **kwargs) -> None:
        self.temperature_text.set(f"Temp.: {self.temperature.get()} °C")
        for child in self.updatables:
            child.on_temperature_change()

    def on_urms_change(self, event: Any = None, *args, **kwargs) -> None:
        self.urms_text.set(f"Urms: {self.urms.get()} mV")
        for child in self.updatables:
            child.on_urms_change()

    def on_irms_change(self, event: Any = None, *args, **kwargs) -> None:
        self.irms_text.set(f"Irms: {self.irms.get()} mA")
        for child in self.updatables:
            child.on_irms_change()

    def on_phase_change(self, event: Any = None, *args, **kwargs) -> None:
        self.phase_text.set(f"Phase: {self.phase.get()} °")

    def on_mode_change(self, event: Any = None, *args, **kwargs) -> None:
        pass

    def on_signal_change(self, event: Any = None, *args, **kwargs) -> None:
        for child in self.updatables:
            child.on_signal_change()

    def on_frequency_set(self) -> None:
        self.sonicamp.input_queue.put(Command(f"!f={self._freq.get()}"))

    def on_gain_set(self, event: Any = None, *args, **kwargs) -> None:
        logger.debug(f"Event triggered by {event.widget}, {event}")
        self.sonicamp.add_job(Command(f"!g={self._gain.get()}", type_="feedback"), 0)

    def on_closing(self) -> None:
        self.sonicamp.shutdown() if self.sonicamp else None
        self.destroy()
