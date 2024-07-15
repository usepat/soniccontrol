import attrs
import ttkbootstrap as ttk

from soniccontrol.tkintergui.vars.stringvar import StringVar


@attrs.frozen
class ConnectionModel:
    connection_state: ttk.StringVar = attrs.field(factory=ttk.StringVar)
    connection_port: ttk.StringVar = attrs.field(factory=ttk.StringVar)
    connection_subtitle: ttk.StringVar = attrs.field(factory=ttk.StringVar)
    connection_heading: ttk.StringVar = attrs.field(factory=ttk.StringVar)
    connection_heading2: ttk.StringVar = attrs.field(factory=ttk.StringVar)


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
    signal_text: ttk.StringVar = attrs.field(factory=ttk.StringVar)
    wipe_mode: ttk.BooleanVar = attrs.field(factory=ttk.BooleanVar)
    relay_mode: ttk.StringVar = attrs.field(factory=ttk.StringVar)


@attrs.frozen
class Filepaths:
    firmware_flash: ttk.StringVar = attrs.field(factory=ttk.StringVar)
    sonicmeasure_log: ttk.StringVar = attrs.field(factory=ttk.StringVar)
    scripting_log: ttk.StringVar = attrs.field(factory=ttk.StringVar)
    status_log: ttk.StringVar = attrs.field(factory=ttk.StringVar)


@attrs.frozen
class UserSettableVars:
    freq: ttk.IntVar = attrs.field(factory=ttk.IntVar)
    gain: ttk.IntVar = attrs.field(factory=ttk.IntVar)
    wipe: ttk.IntVar = attrs.field(factory=ttk.IntVar)
    relay_mode: ttk.StringVar = attrs.field(factory=ttk.StringVar)


@attrs.frozen
class DeviceModel:
    app_task: StringVar = attrs.field(factory=StringVar)
    scripting_task: StringVar = attrs.field(factory=StringVar)
    status_model: StatusVars = attrs.field(factory=StatusVars)
    atf_model: ATFVars = attrs.field(factory=ATFVars)
    connection_model: ConnectionModel = attrs.field(factory=ConnectionModel)
    filepath_model: Filepaths = attrs.field(factory=Filepaths)
    user_settable_model: UserSettableVars = attrs.field(factory=UserSettableVars)
