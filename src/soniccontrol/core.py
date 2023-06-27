from __future__ import annotations

import time
import os
import platform
import datetime
import traceback
import csv
import json
import logging
import tkinter as tk
import tkinter.ttk as ttk
import ttkbootstrap as ttkb
import serial
import sonicpackage as sp

from dataclasses import dataclass, field
from PIL.ImageTk import PhotoImage
from tkinter import font
from tkinter import messagebox
from tkinter import TclError

from sonicpackage import (
    SonicInterface,
    SonicThread,
    Status,
    Command,
    SerialConnection,
    SonicAmp,
    SonicCatchOld,
    SonicCatchAncient,
    SonicWipe40KHZ,
    SonicWipeOld,
    SonicWipeAncient,
    SonicCatch,
    SonicWipe,
    DeviceNotImplementedError,
)

import soniccontrol.constants as const

from soniccontrol.statusframe import (
    StatusFrameCatch,
    StatusFrame40KHZ,
    StatusFrameWipe,
    StatusFrameWipeOld,
    StatusFrame,
)

from soniccontrol.serialmonitor import (
    SerialMonitor,
    SerialMonitor40KHZ,
    SerialMonitorCatch,
    SerialMonitorWipe,
)

from soniccontrol.sonicmeasure import SonicMeasureWindow
from soniccontrol.notebook import ScNotebook
from soniccontrol.helpers import logger


class Root(tk.Tk):
    MAX_WIDTH = 1600
    MAX_HEIGHT = 1600
    MIN_HEIGHT = 300
    MIN_WIDTH = 300
    TITLE: str = "SonicControl"
    THEME: str = "sandstone"
    LOGGER_LEVEL: int = logging.DEBUG

    @property
    def serial(self) -> SerialConnection:
        return self._serial

    @property
    def amp_controller(self) -> SonicInterface:
        return self._amp_controller

    @property
    def sonicamp(self) -> SonicAmp:
        return self._sonicamp

    @property
    def thread(self) -> SonicThread:
        return self._thread

    def __init__(self, *args, **kwargs) -> None:
        super().__init__()

        self._amp_controller: SonicInterface
        self._sonicamp: SonicAmp
        self._thread: SonicThread
        self._serial: SerialConnection = SerialConnection()

        # deprecated
        self.custom_modes: dict[str, sp.Mode] = {}
        self.current_mode = tk.StringVar()
        self.serial_monitor_published: bool = True

        self.port: tk.StringVar = tk.StringVar()
        self.config_file: ConfigData = ConfigData().read_json()

        self.wm_title(Root.TITLE)
        ttkb.Style(theme=Root.THEME)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        if platform.system() == "Windows":
            self.iconbitmap("src//soniccontrol//pictures//welle.ico")

        # default font in GUI and custom Fonts
        default_font: font.Font = font.nametofont("TkDefaultFont")
        default_font.configure(family="Arial", size=12)
        self.option_add("*Font", default_font)
        self.arial12: font.Font = font.Font(
            family="Arial", size=12, weight=tk.font.BOLD
        )
        self.qtype12: font.Font = font.Font(
            family="QTypeOT-CondMedium", size=12, weight=tk.font.BOLD
        )
        self.qtype30: font.Font = font.Font(family="QTypeOT-CondLight", size=30)
        self.qtype30b: font.Font = font.Font(
            family="QTypeOT-CondBook", size=30, weight=tk.font.BOLD
        )

        # Defining images
        self.REFRESH_IMG: PhotoImage = PhotoImage(const.REFRESH_RAW_IMG)
        self.HOME_IMG: PhotoImage = PhotoImage(const.HOME_RAW_IMG)
        self.SCRIPT_IMG: PhotoImage = PhotoImage(const.SCRIPT_RAW_IMG)
        self.CONNECTION_IMG: PhotoImage = PhotoImage(const.CONNECTION_RAW_IMG)
        self.INFO_IMG: PhotoImage = PhotoImage(const.INFO_RAW_IMG)
        self.PLAY_IMG: PhotoImage = PhotoImage(const.PLAY_RAW_IMG)
        self.PAUSE_IMG: PhotoImage = PhotoImage(const.PAUSE_RAW_IMG)
        self.WAVE_IMG: PhotoImage = PhotoImage(const.WAVE_RAW_IMG)
        self.GRAPH_IMG: PhotoImage = PhotoImage(const.GRAPH_RAW_IMG)
        self.LED_GREEN_IMG: PhotoImage = PhotoImage(const.LED_GREEN_RAW_IMG)
        self.LED_RED_IMG: PhotoImage = PhotoImage(const.LED_RED_RAW_IMG)

        # Configuring and starting the Thread
        self._thread: SonicThread = SonicAgent(self)
        self._thread.daemon = True
        self._thread.start()
        self._thread.pause()

        # Starting the main graphical parts of the GUI
        self.mainframe: ttk.Frame = ttkb.Frame(self, bootstyle="success")
        self.notebook: ScNotebook = ScNotebook(self.mainframe, self)
        self.status_frame: ttk.Frame = ttk.Frame(self.mainframe)
        self.sonicmeasure: SonicMeasureWindow = SonicMeasureWindow(self)
        self.serial_monitor: ttk.Frame = ttk.Frame(self.mainframe)

        logger.debug("Initialized Root")
        self.__reinit__(True)

    def __reinit__(self, first_start: bool = False) -> None:
        if first_start:
            self.publish_disconnected()
            return

        rescue_me: bool = False
        exception: bool = True

        try:
            self.decide_action()

        except serial.SerialException as se:
            logger.debug(traceback.format_exc())
            logger.warning(se)
            messagebox.showerror("Connection Error", se)

        except AssertionError as ass_e:
            logger.debug(traceback.format_exc())
            logger.warning(ass_e)
            rescue_me: bool = messagebox.askyesno(
                "Data Error", f"{ass_e}\nDo you want to go into rescue mode?"
            )

        except MemoryError as mem_e:
            logger.debug(traceback.format_exc())
            logger.warning(mem_e)
            rescue_me: bool = messagebox.askyesno(
                "Memory Error", f"{mem_e}Do you want to go into rescue mode?"
            )
            messagebox.showerror()

        except AttributeError as attr_e:
            logger.debug(traceback.format_exc())
            logger.warning(attr_e)
            rescue_me: bool = messagebox.askyesno(
                "Data Error", f"{attr_e}\nDo you want to go into rescue mode?"
            )

        except DeviceNotImplementedError as nie:
            logger.debug(traceback.format_exc())
            logger.warning(nie)
            rescue_me: bool = messagebox.askyesno(
                "Data Error", f"{nie}\nDo you want to go into rescue mode?"
            )

        except TypeError as te:
            logger.debug(traceback.format_exc())
            logger.warning(te)
            rescue_me: bool = messagebox.askyesno(
                "Data Error", f"{te}\nDo you want to go into rescue mode?"
            )

        except Exception as e:
            logger.debug(traceback.format_exc())
            logger.warning(e)
            messagebox.showerror("Error", e)

        except TclError as tcle:
            logger.debug(traceback.format_exc())
            logger.warning(tcle)
            messagebox.showerror("Tkinter Error", tcle)

        else:
            exception: bool = False

            self._initialize_data()
            if isinstance(self.sonicamp, SonicWipe40KHZ):
                return

            self.engine()
            self._thread.resume() if self.thread.paused.is_set() else None

        finally:
            if rescue_me and exception:
                self.publish_rescue_mode()
            elif not rescue_me and exception:
                self.publish_disconnected()

    def decide_action(self) -> None:
        self._amp_controller: SonicInterface = SonicInterface(
            port=self.port.get(), logger_level=self.LOGGER_LEVEL, thread=self.thread
        )
        self._sonicamp: SonicAmp = self.amp_controller.sonicamp
        self._serial: SerialConnection = self.amp_controller.serial

        logger.info("Succesfully connected and built sonicamp")
        logger.info(f"{self.sonicamp}")

        if isinstance(self.sonicamp, SonicCatchOld) or isinstance(
            self.sonicamp, SonicCatchAncient
        ):
            self.publish_for_old_catch()

        elif isinstance(self.sonicamp, SonicWipeOld) or isinstance(
            self.sonicamp, SonicWipeAncient
        ):
            self.publish_for_old_wipe()

        elif isinstance(self.sonicamp, SonicWipe40KHZ):
            self.publish_for_wipe40khz()

        elif isinstance(self.sonicamp, SonicCatch):
            self.publish_for_catch()

        elif isinstance(self.sonicamp, SonicWipe):
            self.publish_for_wipe()

        else:
            raise Exception("Do not know which device it is!")

    def _initialize_data(self) -> None:
        self.config_file: ConfigData = ConfigData().read_json()
        logger.debug(f"read config file: {self.config_file}")
        if not self.config_file:
            self.attach_data()
            return
        if not self.config_file.modes:
            self.attach_data()
            return

        for mode in self.sonicamp._supported_modes:
            self.custom_modes.update({str(mode): mode})
        for key, mode in self.config_file.modes.items():
            logger.info(f"adding mode {mode}")
            mode = self.sonicamp.define_new_mode(
                mode.get("freq_begin"),
                mode.get("freq_end"),
                mode.get("gain_begin"),
                mode.get("gain_end"),
            )
            self.custom_modes.update({str(mode): mode})
        self.attach_data()

    def engine(self) -> None:
        try:
            while self.thread.queue.qsize():
                status: Status = self.thread.queue.get(0)
                self.sonicamp._status = status
                logger.info(f"New status = {status}")
                self.amp_controller.register_data()
                self.update_idletasks()
                self.attach_data()
        except AttributeError as ae:
            print(ae.with_traceback())
            logger.warning("Could not find status because sonicamp is none")

        self.after(100, self.engine)

    def attach_data(self) -> None:
        self.config_file: ConfigData = ConfigData().read_json()
        self.notebook.attach_data()
        self.status_frame.attach_data()

    def abolish_data(self) -> None:
        self._sonicamp = None
        self._amp_controller = None
        self.notebook.abolish_data()

    def publish_rescue_mode(self) -> None:
        self._serial: SerialConnection = SerialConnection().connect(self.port.get())
        self.serial_monitor: SerialMonitor = SerialMonitor(self)
        self.notebook.publish_rescue_mode()

    def publish_disconnected(self) -> None:
        self.serial.disconnect()
        self.notebook.publish_disconnected()
        self.status_frame.destroy()
        self.mainframe.pack(side=tk.TOP, fill=tk.BOTH)
        self.notebook.pack(side=tk.TOP, fill=tk.BOTH)

        if self.winfo_width() == Root.MAX_WIDTH:
            self._adjust_dimensions()

        if tk.Toplevel.winfo_exists(self.sonicmeasure):
            self.sonicmeasure.destroy()

        self.thread.pause() if not self.thread.paused.is_set() else None

    def publish_for_old_catch(self) -> None:
        self._pre_publish()
        self.serial_monitor: SerialMonitor = SerialMonitorCatch(self)
        self.status_frame: StatusFrame = StatusFrameCatch(self.mainframe, self)
        self.attach_data()
        self.notebook.publish_for_old_catch()
        self._after_publish()

    def publish_for_old_wipe(self) -> None:
        self._pre_publish()
        self.serial_monitor: SerialMonitor = SerialMonitorWipe(self)
        self.status_frame: StatusFrame = StatusFrameWipeOld(self.mainframe, self)
        self.attach_data()
        self.notebook.publish_for_old_wipe()
        self._after_publish()

    def publish_for_wipe40khz(self) -> None:
        self.thread.pause() if not self.thread.paused.is_set() else None
        self._pre_publish()
        self.serial_monitor: SerialMonitor = SerialMonitor40KHZ(self)
        self.status_frame: StatusFrame = StatusFrame40KHZ(self.mainframe, self)
        self.notebook.publish_for_wipe40khz()
        self.status_frame.connection_on()
        self._after_publish()

    def publish_for_wipe(self) -> None:
        self._pre_publish()
        self.serial_monitor: SerialMonitor = SerialMonitorWipe(self)
        self.status_frame: StatusFrame = StatusFrameWipe(self.mainframe, self)
        self.attach_data()
        self.notebook.publish_for_wipe()
        self._after_publish()

    def publish_for_catch(self) -> None:
        self.publish_for_old_catch()

    def publish_sonicmeasure(self) -> None:
        self.sonicmeasure: SonicMeasureWindow = SonicMeasureWindow(self)
        self.notebook.hometab.sonic_measure_button.config(state=tk.DISABLED)

    # def publish_serial_monitor(self) -> None:
    #     if not self._is_wided():
    #         return
    #     self.serial_monitor.pack(
    #         anchor=tk.E, side=tk.RIGHT, padx=5, pady=5, expand=True, fill=tk.BOTH
    #     )

    def publish_serial_monitor(self) -> None:
        if self.serial_monitor_published:
            self.serial_monitor.focus_force()
            return
        self.serial_monitor = SerialMonitor(self)
        self.serial_monitor_published = True

    def unpublish_serial_monitor(self) -> None:
        self.serial_monitor.destroy()
        self.serial_monitor_published = False

    def _is_wided(self) -> bool:
        if self.winfo_width() == Root.MIN_WIDTH:
            self.geometry(f"{Root.MAX_WIDTH}x{Root.MIN_HEIGHT}")
            return True

        else:
            self.geometry(f"{Root.MIN_WIDTH}x{Root.MIN_HEIGHT}")
            return False

    def _pre_publish(self) -> None:
        self.serial_monitor.destroy()
        self.status_frame.destroy()

    def _after_publish(self) -> None:
        self.status_frame.publish()
        self.mainframe.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self.notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.status_frame.pack(side=tk.TOP, fill=tk.X)

    def on_closing(self) -> None:
        from soniccontrol.scriptingtab import ScriptingTab

        if self.sonicamp is None:
            self.destroy()
            return

        if (
            isinstance(self.notebook.scriptingtab, ScriptingTab)
            and self.notebook.scriptingtab.sequence is not None
        ):
            logger.info("ending sequence")
            self.notebook.scriptingtab.end_sequence()

        if tk.Toplevel.winfo_exists(self.sonicmeasure):
            self.sonicmeasure.on_closing()

        self.thread.pause() if not self.thread.paused else None
        self.thread.stop()
        self.thread.join()

        self.destroy()


# class SizeNotifier:
#     def __init__(self) -> None:
#         self.root = root
#         self.size_dict = size_dict
#         self.current_min_size = None

#         self.window.update()

#         min_height = self.window.winfo_height()
#         min_width = list(self.size_dict)[0]
#         self.window.minsize(min_width, min_height)

#         self.root.bind("<Configure>", self.check_size)

#     def check_size(self, event):
#         width = event.width
#         checked_size = None

#         for min_size in self.size_dict:
#             delta = width - min_size
#             if delta >= 0:
#                 checked_size = min_size

#         if check_size != self.current_min_size:
#             self.current_min_size = checked_size
#             self.size_dict[self.current_min_size]()


@dataclass
class ConfigData(object):
    hexflash: bool = field(default=False)
    dev_mode: bool = field(default=False)
    transducer: dict = field(default_factory=dict)
    modes: dict = field(default_factory=dict)

    @classmethod
    def read_json(cls) -> ConfigData:
        if not os.path.isfile("config.json"):
            return None
        with open("config.json", "r") as file:
            data: dict = json.load(file)
            obj: ConfigData = cls()
            obj.hexflash = data.get("hexflash") if "hexflash" in data else None
            obj.dev_mode = data.get("dev_mode") if "dev_mode" in data else None
            obj.modes = data.get("modes") if "modes" in data else {}
            if data.get("transducer") == None:
                return obj

            obj.transducer: dict = data.get("transducer")
            return obj


class SonicAgent(SonicThread):
    @property
    def root(self):
        return self._root

    def __init__(self, root: Root) -> None:
        super().__init__()
        self._root: Root = root

    def worker(self) -> None:
        try:
            if self.root.serial.is_connected:
                status: Status = self.root.sonicamp.get_status()

                if not isinstance(status, bool) and status != self.root.sonicamp.status:
                    self.queue.put(status)

        except IndexError as ie:
            logger.warning(ie)
        except serial.SerialException as se:
            logger.warning(traceback.format_exc(se))
            self.root.__reinit__()
        except Exception as e:
            logger.warning(f"{e}")


if __name__ == "__main__":
    pass
