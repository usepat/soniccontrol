from typing import TypedDict

import ttkbootstrap as ttk
from PIL import Image, ImageTk

from soniccontrol import const
from soniccontrol import soniccontrol_logger as logger
from soniccontrol.components.notebook import Notebook
from soniccontrol.interfaces.layouts import Layout
from soniccontrol.utils import ImageLoader
from soniccontrol.views.connectionview import ConnectionView
from soniccontrol.views.homeview import HomeView
from soniccontrol.views.infoview import InfoView
from soniccontrol.views.scriptingview import ScriptingView
from soniccontrol.views.serialmonitorview import SerialMonitorView
from soniccontrol.views.settingsview import SettingsView
from soniccontrol.views.sonicmeasureview import SonicMeasureView
from soniccontrol.views.statusview import StatusBarView, StatusView


class SonicControlViewsDict(TypedDict):
    home: HomeView
    scripting: ScriptingView
    connection: ConnectionView
    settings: SettingsView
    info: InfoView
    sonicmeasure: SonicMeasureView
    serialmonitor: SerialMonitorView
    statusview: StatusView


class MiscVarsDict(TypedDict):
    program_state: ttk.StringVar
    connection_port: ttk.StringVar
    device_heading1: ttk.StringVar
    device_heading2: ttk.StringVar
    subtitle: ttk.StringVar


class FilepathDict(TypedDict):
    firmware_flash: ttk.StringVar
    sonicmeasure_log: ttk.StringVar
    status_log: ttk.StringVar


class UserSettableVarsDict(TypedDict):
    freq: ttk.IntVar
    gain: ttk.IntVar
    wipe: ttk.IntVar


class ATFVarsDict(TypedDict):
    atf_config_name: ttk.StringVar
    atf1: ttk.IntVar
    atk1: ttk.DoubleVar
    atf2: ttk.IntVar
    atk2: ttk.DoubleVar
    atf3: ttk.IntVar
    atk3: ttk.DoubleVar
    att1: ttk.DoubleVar


class StatusVarsDict(TypedDict):
    freq_khz: ttk.DoubleVar
    freq_khz_text: ttk.StringVar
    gain: ttk.IntVar
    gain_text: ttk.StringVar
    temp: ttk.DoubleVar
    temp_text: ttk.StringVar
    urms: ttk.DoubleVar
    urms_text: ttk.StringVar
    irms: ttk.DoubleVar
    irms_text: ttk.StringVar
    phase: ttk.DoubleVar
    phase_text: ttk.StringVar
    signal: ttk.BooleanVar
    wipe_mode: ttk.BooleanVar
    relay_mode: ttk.StringVar


# TODO: look how to abstract the class, so that the images are stored in one place and referenced in the children views


class MainView(ttk.Window):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.wm_title(const.ui.IDLE_TITLE)
        ttk.Style(const.ui.THEME)
        ImageLoader(self)

        # font = ttk.font.Font(
        #     name="QTypeCondExtraLight",
        #     font=const.fonts.QTYPE_OT_COND_EXTRALIGHT_PATH,
        #     size=10,
        # )
        # self.default_font = ttk.font.nametofont("TkDefaultFont")
        # self.default_font.configure(family="QTypeOT", size=10)

        # Utililty tkinter variables
        self._misc_vars: MiscVarsDict = {
            "connection_port": ttk.StringVar(),
            "device_heading1": ttk.StringVar(value="sonic"),
            "device_heading2": ttk.StringVar(),
            "program_state": ttk.StringVar(),
            "subtitle": ttk.StringVar(),
        }

        # Filepath tkinter variables
        self._filepath_vars: FilepathDict = {
            "firmware_flash": ttk.StringVar(),
            "sonicmeasure_log": ttk.StringVar(),
            "status_log": ttk.StringVar(),
        }

        # Setter tkinter variables
        self._user_setter_vars: UserSettableVarsDict = {
            "freq": ttk.IntVar(),
            "gain": ttk.IntVar(),
            "wipe": ttk.IntVar(),
        }

        # ATF tkinter variables
        self._atf_vars: ATFVarsDict = {
            "atf_config_name": ttk.StringVar(),
            "atf1": ttk.IntVar(),
            "atf2": ttk.IntVar(),
            "atf3": ttk.IntVar(),
            "atk1": ttk.DoubleVar(),
            "atk2": ttk.DoubleVar(),
            "atk3": ttk.DoubleVar(),
            "att1": ttk.DoubleVar(),
        }

        # Status tkinter variables
        self._status_vars: StatusVarsDict = {
            "freq_khz": ttk.DoubleVar(),
            "freq_khz_text": ttk.StringVar(),
            "gain": ttk.IntVar(),
            "gain_text": ttk.StringVar(),
            "irms": ttk.DoubleVar(),
            "irms_text": ttk.StringVar(),
            "phase": ttk.DoubleVar(),
            "phase_text": ttk.StringVar(),
            "urms": ttk.DoubleVar(),
            "urms_text": ttk.StringVar(),
            "temp": ttk.DoubleVar(),
            "temp_text": ttk.StringVar(),
            "signal": ttk.BooleanVar(),
            "relay_mode": ttk.StringVar(),
            "wipe_mode": ttk.BooleanVar(),
        }

        # tkinter components
        self._main_frame: ttk.Panedwindow = ttk.Panedwindow(self, orient=ttk.HORIZONTAL)
        self._left_notebook: Notebook = Notebook(self)
        self._right_notebook: Notebook = Notebook(self)
        self._status_bar: StatusBarView = StatusBarView(self, style=ttk.DARK)

        self._views: SonicControlViewsDict = {
            "home": HomeView(self),
            "connection": ConnectionView(self),
            "scripting": ScriptingView(self),
            "settings": SettingsView(self),
            "serialmonitor": SerialMonitorView(self),
            "info": InfoView(self),
            "sonicmeasure": SonicMeasureView(self),
            "statusview": StatusView(self),
        }

        self._init_publish()

    @property
    def layouts(self) -> set[Layout]:
        ...

    @property
    def views(self) -> SonicControlViewsDict:
        return self._views

    @property
    def status_vars(self) -> StatusVarsDict:
        return self._status_vars

    @property
    def atf_vars(self) -> ATFVarsDict:
        return self._atf_vars

    @property
    def user_setter_vars(self) -> UserSettableVarsDict:
        return self._user_setter_vars

    @property
    def filepath_vars(self) -> FilepathDict:
        return self._filepath_vars

    def publish(self) -> None:
        ...

    def _init_publish(self) -> None:
        self._main_frame.pack(expand=True, fill=ttk.BOTH)
        self._status_bar.pack(fill=ttk.X)
        self._main_frame.add(self._left_notebook, weight=1)
        self._left_notebook.add_tabs(
            [
                self.views["home"],
                self.views["scripting"],
                self.views["sonicmeasure"],
                self.views["serialmonitor"],
                self.views["connection"],
            ],
            show_titles=True,
            show_images=True,
        )

    def set_large_width_layout(self) -> None:
        ...

    def set_small_width_layout(self) -> None:
        ...

    def on_disconnect(self) -> None:
        ...

    def on_firmware_flash(self) -> None:
        ...
