import abc
from typing import Any

import attrs
import ttkbootstrap as ttk
from soniccontrol.components.stringvar import StringVar
from soniccontrol.utils import ImageLoader


@attrs.frozen
class MiscVars:
    program_state: ttk.StringVar = attrs.field(factory=ttk.StringVar)
    connection_port: ttk.StringVar = attrs.field(factory=ttk.StringVar)
    connection_subtitle: ttk.StringVar = attrs.field(factory=ttk.StringVar)
    device_heading1: StringVar = attrs.field(factory=StringVar)
    device_heading2: StringVar = attrs.field(factory=StringVar)
    subtitle: ttk.StringVar = attrs.field(factory=ttk.StringVar)


@attrs.frozen
class Filepaths:
    firmware_flash: ttk.StringVar = attrs.field(factory=ttk.StringVar)
    sonicmeasure_log: ttk.StringVar = attrs.field(factory=ttk.StringVar)
    status_log: ttk.StringVar = attrs.field(factory=ttk.StringVar)


@attrs.frozen
class UserSettableVars:
    freq: ttk.IntVar = attrs.field(factory=ttk.IntVar)
    gain: ttk.IntVar = attrs.field(factory=ttk.IntVar)
    wipe: ttk.IntVar = attrs.field(factory=ttk.IntVar)
    relay_mode: ttk.StringVar = attrs.field(factory=ttk.StringVar)


@attrs.frozen
class ATFVars:
    atf_config_name: ttk.StringVar = attrs.field(factory=ttk.StringVar)
    submitting_progress: ttk.IntVar = attrs.field(factory=ttk.IntVar)
    atf1: ttk.IntVar = attrs.field(factory=ttk.IntVar)
    atk1: ttk.DoubleVar = attrs.field(factory=ttk.DoubleVar)
    atf2: ttk.IntVar = attrs.field(factory=ttk.IntVar)
    atk2: ttk.DoubleVar = attrs.field(factory=ttk.DoubleVar)
    atf3: ttk.IntVar = attrs.field(factory=ttk.IntVar)
    atk3: ttk.DoubleVar = attrs.field(factory=ttk.DoubleVar)
    att1: ttk.DoubleVar = attrs.field(factory=ttk.DoubleVar)


@attrs.frozen
class StatusVars:
    freq_khz: ttk.DoubleVar = attrs.field(factory=ttk.DoubleVar)
    freq_khz_text: ttk.StringVar = attrs.field(factory=ttk.StringVar)
    gain: ttk.IntVar = attrs.field(factory=ttk.IntVar)
    gain_text: ttk.StringVar = attrs.field(factory=ttk.StringVar)
    temp: ttk.DoubleVar = attrs.field(factory=ttk.DoubleVar)
    temp_text: ttk.StringVar = attrs.field(factory=ttk.StringVar)
    urms: ttk.DoubleVar = attrs.field(factory=ttk.DoubleVar)
    urms_text: ttk.StringVar = attrs.field(factory=ttk.StringVar)
    irms: ttk.DoubleVar = attrs.field(factory=ttk.DoubleVar)
    irms_text: ttk.StringVar = attrs.field(factory=ttk.StringVar)
    phase: ttk.DoubleVar = attrs.field(factory=ttk.DoubleVar)
    phase_text: ttk.StringVar = attrs.field(factory=ttk.StringVar)
    signal: ttk.BooleanVar = attrs.field(factory=ttk.BooleanVar)
    wipe_mode: ttk.BooleanVar = attrs.field(factory=ttk.BooleanVar)
    relay_mode: ttk.StringVar = attrs.field(factory=ttk.StringVar)


class Root(ttk.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ImageLoader(self)

        # tkinter variables
        self._misc_vars: MiscVars = MiscVars()
        self._filepath_vars: Filepaths = Filepaths()
        self._user_setter_vars: UserSettableVars = UserSettableVars()
        self._atf_vars: ATFVars = ATFVars()
        self._status_vars: StatusVars = StatusVars()

        self._initialize_children()
        self._initialize_publish()

    @property
    @abc.abstractmethod
    def views(self) -> Any:
        ...

    @property
    def misc_vars(self) -> MiscVars:
        return self._misc_vars

    @property
    def status_vars(self) -> StatusVars:
        return self._status_vars

    @property
    def atf_vars(self) -> ATFVars:
        return self._atf_vars

    @property
    def user_setter_vars(self) -> UserSettableVars:
        return self._user_setter_vars

    @property
    def filepath_vars(self) -> Filepaths:
        return self._filepath_vars

    @abc.abstractmethod
    def _initialize_children(self) -> None:
        ...

    @abc.abstractmethod
    def _initialize_publish(self) -> None:
        ...
