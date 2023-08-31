from typing import Any, Optional, Iterable, Set, Dict
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox
import abc
import platform
import sys
import subprocess
import csv
import logging
import pathlib
import soniccontrol.constants as const
import copy
import threading
from soniccontrol.sonicamp import SonicAmpAgent, Command
from soniccontrol.interfaces import (
    Resizable,
    Updatable,
    Disconnectable,
    Configurable,
    Connectable,
    Scriptable,
    Flashable,
    Feedbackable,
    Resizer,
    Layout,
)
from soniccontrol.interfaces.tkinter_vars import RootStringVar
import sonicpackage as sp

logger = logging.getLogger(__name__)


class Root(tk.Tk, Resizable, Updatable):
    def __init__(self) -> None:
        super().__init__()
        self._width_layouts: Optional[Iterable[Layout]] = None
        self._height_layouts: Optional[Iterable[Layout]] = None
        self._resizer: Resizer = Resizer(self)

        # miscellous global vars
        self.byte_encoding: str = (
            "utf-8" if platform.system() != "Windows" else "windows-1252"
        )
        self.firmware_flash_file: Optional[pathlib.Path] = None
        self.validation_successfull: threading.Event = threading.Event()
        self.flashing_successfull: threading.Event = threading.Event()

        # (global set) tkinter variables
        self._freq: ttk.IntVar = ttk.IntVar()
        self._gain: ttk.IntVar = ttk.IntVar()
        self._wipe_inf_or_def: ttk.BooleanVar = ttk.BooleanVar()
        self._wipe_cycles: ttk.IntVar = ttk.IntVar()

        self.atf_configuration_name: ttk.StringVar = ttk.StringVar(value="None")
        self._atf1: ttk.IntVar = ttk.IntVar(value=0)
        self._atk1: ttk.DoubleVar = ttk.DoubleVar(value=0)

        self._atf2: ttk.IntVar = ttk.IntVar(value=0)
        self._atk2: ttk.DoubleVar = ttk.DoubleVar(value=0)

        self._atf3: ttk.IntVar = ttk.IntVar(value=0)
        self._atk3: ttk.DoubleVar = ttk.DoubleVar(value=0)
        self._att1: ttk.DoubleVar = ttk.DoubleVar(value=0)

        self.connected: bool = True
        # (glabal read) tkinter variables
        self.frequency: ttk.DoubleVar = ttk.DoubleVar(value=1000)
        self.frequency_text: ttk.StringVar = ttk.StringVar()
        self.frequency.trace(ttk.W, self.on_frequency_change)

        self.gain: ttk.IntVar = ttk.IntVar(value=100)
        self.gain_text: ttk.StringVar = ttk.StringVar()
        self.gain.trace(ttk.W, self.on_gain_change)

        self.temperature: ttk.DoubleVar = ttk.DoubleVar(value=23.5)
        self.temperature_text: ttk.StringVar = ttk.StringVar()
        self.temperature.trace(ttk.W, self.on_temperature_change)

        self.urms: ttk.IntVar = ttk.IntVar(value=1003)
        self.urms_text: ttk.StringVar = ttk.StringVar()
        self.urms.trace(ttk.W, self.on_urms_change)

        self.irms: ttk.IntVar = ttk.IntVar(value=134)
        self.irms_text: ttk.StringVar = ttk.StringVar()
        self.irms.trace(ttk.W, self.on_irms_change)

        self.phase: ttk.IntVar = ttk.IntVar(value=75)
        self.phase_text: ttk.StringVar = ttk.StringVar()
        self.phase.trace(ttk.W, self.on_phase_change)

        self.signal: ttk.BooleanVar = ttk.BooleanVar(value=False)
        self.signal.trace(ttk.W, self.on_signal_change)

        self.wipe_mode: ttk.BooleanVar = ttk.BooleanVar(value=False)
        self.wipe_mode.trace(ttk.W, self.on_wipe_mode_change)

        self.mode: ttk.StringVar = ttk.StringVar(value="Catch")
        self.soniccontrol_state: RootStringVar = RootStringVar(
            value="Manual", master=self
        )
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

        self.sonicmeasure_log_var: ttk.StringVar = ttk.StringVar(
            value="logs//sonicmeasure.csv"
        )
        self.sonicmeasure_log_var.trace_add("write", self.sonicmeasure_log_changed)
        self.sonicmeasure_log: pathlib.Path = pathlib.Path(
            self.sonicmeasure_log_var.get()
        )
        self.sonicmeasure_running: threading.Event = threading.Event()

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
            "wipe_mode": self.wipe_mode,
        }

        self.disconnectables: Set[Disconnectable] = set()
        self.connectables: Set[Connectable] = set()
        self.configurables: Set[Configurable] = set()
        self.updatables: Set[Updatable] = set()
        self.scriptables: Set[Scriptable] = set()
        self.feedbackables: Set[Feedbackable] = set()
        self.flashables: Set[Flashable] = set()
        logger.debug("initialized Root")

    @property
    def resizer(self) -> Resizer:
        return self._resizer

    @property
    def width_layouts(self) -> Optional[Iterable[Layout]]:
        return self._width_layouts

    @property
    def height_layouts(self) -> Optional[Iterable[Layout]]:
        return self._height_layouts

    def bind_events(self) -> None:
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind(const.Events.RESIZING, self.on_resizing)
        self.bind(const.Events.SET_GAIN, self.on_gain_set)
        self.bind(const.Events.FIRMWARE_FLASH, self.on_firmware_flash)

    def on_resizing(self, event: Any, *args, **kwargs) -> None:
        return self.resizer.resize(event=event)

    def sonicmeasure_log_changed(self, event: Any = None, *args, **kwargs) -> None:
        self.sonicmeasure_log = pathlib.Path(self.sonicmeasure_log_var.get())

        if not self.sonicmeasure_log.exists():
            self.sonicmeasure_log.parent.mkdir(parents=True, exist_ok=True)

    def on_firmware_flash(self, *args, **kwargs) -> None:
        self.event_generate(const.Events.DISCONNECTED)

        for flashable in self.flashables:
            flashable.on_validation()

        self.validation_thread: threading.Thread = threading.Thread(
            target=self.validate_flash_file_thread,
            args=(
                self.port.get(),
                self.firmware_flash_file,
            ),
            daemon=True,
        )
        self.validation_thread.start()
        self.check_firware_validation()

    def check_firware_validation(self) -> None:
        if self.validation_thread.is_alive():
            self.after(100, self.check_firware_validation)
            return
        if self.validation_successfull.is_set():
            for flashable in self.flashables:
                flashable.on_validation_success()
            self.upload_firmware()
            self.validation_successfull.clear()
        else:
            Messagebox.show_error(
                "AVRDUDE Test was not passed. The file seems to be invalid or corrupted",
                "Validation Error",
            )
            self.event_generate(const.Events.CONNECTION_ATTEMPT)

    def upload_firmware(self) -> None:
        for flashable in self.flashables:
            flashable.on_firmware_upload()

        self.flashing_thread: threading.Thread = threading.Thread(
            target=self.flashing_worker,
            args=(
                self.port.get(),
                self.firmware_flash_file,
            ),
            daemon=True,
        )
        self.flashing_thread.start()
        self.check_flashing_state()

    def check_flashing_state(self) -> None:
        if self.flashing_thread.is_alive():
            self.after(100, self.check_flashing_state)
            return
        if self.flashing_successfull.is_set():
            self.flashing_successfull.clear()
            self.event_generate(const.Events.CONNECTION_ATTEMPT)
        else:
            Messagebox.show_error(
                "AVRDUDE Upload was not passed. Something went wrong during the process.",
                "Firmware Flash Error",
            )
            self.event_generate(const.Events.DISCONNECTED)

    @staticmethod
    def flash_command(port: str, hex_file_path: str, test: bool = False) -> str:
        logger.info(f"Getting flash command for Platform {platform.system()}")

        if platform.system() == "Linux" and test:
            command = f'"avrdude/Linux/avrdude" -n -v -p atmega328p -c arduino -P {port} -b 115200 -D -U flash:w:"{hex_file_path}":i'
        elif platform.system() == "Linux" and not test:
            command = f'"avrdude/Linux/avrdude" -v -p atmega328p -c arduino -P {port} -b 115200 -D -U flash:w:"{hex_file_path}":i'

        if platform.system() == "Darwin" and test:
            command = f'"avrdude/Darwin/avrdude" -n -v -p atmega328p -c arduino -P {port} -b 115200 -D -U flash:w:"{hex_file_path}":i'
        elif platform.system() == "Darwin" and not test:
            command = f'"avrdude/Darwin/avrdude" -v -p atmega328p -c arduino -P {port} -b 115200 -D -U flash:w:"{hex_file_path}":i'

        elif platform.system() == "Windows" and test:
            command = f'"avrdude/Windows/avrdude.exe" -n -v -p atmega328p -c arduino -P {port} -b 115200 -D -U flash:w:"{hex_file_path}":i'
        elif platform.system() == "Windows" and not test:
            command = f'"avrdude/Windows/avrdude.exe" -v -p atmega328p -c arduino -P {port} -b 115200 -D -U flash:w:"{hex_file_path}":i'
        else:
            raise ValueError("Illegal values passed into flash_command method")
        return command

    def validate_flash_file_thread(self, flash_file: str, port: str) -> None:
        try:
            logger.debug(f"Validating firmware file")
            command: str = self.flash_command(flash_file, port, test=True)
            commandline_process: subprocess.Popen = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            command_result, _ = commandline_process.communicate()
            command_result = command_result.decode(self.byte_encoding)
            logger.debug(f"AVRDUDE Test log: {command_result}")

            if commandline_process.returncode > 0:
                logger.error("Errors occurred during the firmware flash")
                return
        except Exception as e:
            logger.error(sys.exc_info())
            return
        else:
            self.validation_successfull.set()

    def flashing_worker(self, flash_file: str, port: str) -> None:
        try:
            logger.debug(f"Uploading Firmware File...")
            command: str = self.flash_command(flash_file, port, test=False)
            commandline_process: subprocess.Popen = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            command_result, _ = commandline_process.communicate()
            command_result = command_result.decode(self.byte_encoding)
            logger.debug(f"AVRDUDE Test log: {command_result}")
        except Exception as e:
            logger.error(sys.exc_info())
            return
        else:
            self.flashing_successfull.set()

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
        pass

    def status_engine(self) -> None:
        def is_connection_ready() -> bool:
            if self.sonicamp.connection_established.is_set():
                self.sonicamp.connection_established.clear()
                self.after_connect()
                self.connected = True
            return self.sonicamp.connection.is_set()

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

        self.status_engine_after_id = self.after(300, self.status_engine)
        if self.sonicamp is None or not is_connection_ready():
            return
        self.check_output_queue()
        check_exceptions_queue()

    def update_sonicamp(self, priority: int = 5, mode: str = "status") -> None:
        if self.sonicmeasure_running.is_set():
            command = Command(message="?sens", type_="sonicmeasure")
            self.sonicamp.add_job(
                Command(message="?sens", type_="sonicmeasure"), priority
            )
            return
            # command.processed.wait()

        command = Command(message="-", type_="status")
        self.sonicamp.add_job(command, priority)
        # command.processed.wait()

        if self.old_status and self.old_status.signal:
            command = Command(message="?sens", type_="status")
            self.sonicamp.add_job(command, priority)
            # command.processed.wait()

    def check_output_queue(self) -> None:
        command: Optional[Command] = None
        while self.sonicamp.output_queue.qsize():
            priority, command = self.sonicamp.output_queue.get()
            logger.debug(f"Command: {command}, Prio: {priority}")

            if command.message in ("?atf1", "?atf2", "?atf3", "?att1"):
                self.check_atf_data(command)

            if command.message in ("?sens", "-"):
                if command.message == "-":
                    if self.old_status is None:
                        status: sp.Status = sp.Status().from_string(command.answer)
                    else:
                        status: sp.Status = copy.deepcopy(
                            self.old_status
                        ).update_status(command.answer)
                else:
                    if self.old_status is None:
                        status: sp.Status = sp.Status().from_sens(
                            command.answer, factorised=True
                        )
                    else:
                        status: sp.Status = copy.deepcopy(self.old_status).from_sens(
                            command.answer, factorised=True
                        )

                if command.type_ == "sonicmeasure":
                    self.react_on_sonicmeasure(status)
                logger.debug(status)
                self.serialize_data(status)
                self.on_update(status)

            elif command.type_ == "feedback":
                for child in self.feedbackables:
                    child.on_feedback(command.answer)

            elif command.type_ == "script":
                for child in self.scriptables:
                    child.on_feedback(command.answer)

            if command.callback is not None:
                command.callback(command.answer)

            self.sonicamp.output_queue.task_done()

        self.update_sonicamp(
            1 if command and command.type_ in ("sonicmeasure", "script") else 5,
            command.type_ if command is not None else "status",
        )

    def react_on_sonicmeasure(self, status: sp.Status) -> None:
        with self.sonicmeasure_log.open(mode="a", newline="") as file:
            writer = csv.DictWriter(
                file, fieldnames=self.fieldnames, extrasaction="ignore"
            )
            writer.writerow(status.dump())

    def check_atf_data(self, command: Command):
        if command.message == "?att1":
            self._att1.set(float(command.answer))
            logger.debug(f"att1: {command}, {float(command.answer)}")
            return

        atf: int = 0
        atk: int = 0
        lines = command.answer.splitlines()
        logger.debug(lines)

        atf, atk, *_ = lines

        if command.message == "?atf1":
            self._atf1.set(atf)
            self._atk1.set(atk)
        elif command.message == "?atf2":
            self._atf2.set(atf)
            self._atk2.set(atk)
        elif command.message == "?atf3":
            self._atf3.set(atf)
            self._atk3.set(atk)
        logger.debug(f"atf setting: {command}, {atf, atk}")

    def serialize_data(self, status: sp.Status) -> None:
        with self.status_log_filepath.open(mode="a", newline="") as file:
            writer = csv.DictWriter(
                file, fieldnames=self.fieldnames, extrasaction="ignore"
            )
            if not self.status_log_filepath_existed:
                writer.writeheader()
                self.status_log_filepath_existed = True
            writer.writerow(status.dump())

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

    def on_wipe_mode_change(self, event: Any = None, *args, **kwargs) -> None:
        if self.wipe_mode.get():
            self.soniccontrol_state.animate_dots(text="Auto")
        else:
            self.soniccontrol_state.stop_animation_of_dots()
            self.soniccontrol_state.set("Manual")
        for child in self.updatables:
            child.on_wipe_mode_change()

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
