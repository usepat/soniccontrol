import sys
from typing import Any, Callable, Literal, TypedDict, get_type_hints

import attrs
import ttkbootstrap as ttk
from async_tkinter_loop import async_mainloop
from ttkbootstrap.utility import enable_high_dpi_awareness

from soniccontrol.amp import SonicAmp
from soniccontrol.core import core_logger as logger
from soniccontrol.core.windowview import MainView
from soniccontrol.interfaces.presenter import Presenter
from soniccontrol.presenters import (ConnectionPresenter, HomePresenter,
                                     InfoPresenter, ScriptPresenter,
                                     SerialMonitorPresenter, SettingsPresenter,
                                     SonicMeasurePresenter, StatusBarPresenter,
                                     StatusPresenter)
from soniccontrol.utils import constants
from soniccontrol.utils.debounce_job import DebounceJob
from soniccontrol.views.serialmonitorview import SerialMonitorView


@attrs.frozen
class Presenters:
    home: HomePresenter = attrs.field()
    scripting: ScriptPresenter = attrs.field()
    sonicmeasure: SonicMeasurePresenter = attrs.field()
    serialmonitor: SerialMonitorPresenter = attrs.field()
    connection: ConnectionPresenter = attrs.field()
    settings: SettingsPresenter = attrs.field()
    info: InfoPresenter = attrs.field()
    statusbar: StatusBarPresenter = attrs.field()
    status: StatusPresenter = attrs.field()


class MainPresenter(Presenter):
    def __init__(self, master: MainView, sonicamp: SonicAmp) -> None:
        super().__init__(master, sonicamp)
        self._presenters: Presenters = Presenters(
            **{
                key: presenter(master, sonicamp)
                for key, presenter in get_type_hints(Presenters).items()
            }
        )

        self.master.bind(constants.events.RESIZING_EVENT, self.master.resize, add=True)
        self.bind_variable_traces()

        self.master.bind_all(
            constants.events.DISCONNECTED_EVENT,
            lambda _: self.master.misc_vars.program_state.set("Disconnected"),
            add=True,
        )
        self.master.bind_all(
            constants.events.DISCONNECTED_EVENT,
            self.master.on_disconnect,
            add=True,
        )
        self.master.status_vars.freq_khz.set(1000)
        self.master.status_vars.gain.set(150)
        self.master.user_setter_vars.relay_mode.set("Catch")
        self.master.status_vars.temp.set(23.4577)
        self.master.status_vars.urms.set(1000.10)
        self.master.status_vars.irms.set(1000.20)
        self.master.status_vars.phase.set(1000.30)

    def bind_variable_traces(self) -> None:
        self.master.status_vars.freq_khz.trace_add(
            "write",
            lambda var, index, mode: self.master.status_vars.freq_khz_text.set(
                f"Freq: {self.master.status_vars.freq_khz.get()} kHz"
            ),
        )
        self.master.status_vars.gain.trace_add(
            "write",
            lambda var, index, mode: self.master.status_vars.gain_text.set(
                f"Gain: {self.master.status_vars.gain.get()} %"
            ),
        )
        self.master.user_setter_vars.relay_mode.trace_add(
            "write",
            lambda var, index, mode: self.master.status_vars.relay_mode.set(
                f"Mode: {self.master.user_setter_vars.relay_mode.get()}"
            ),
        )
        self.master.status_vars.temp.trace_add(
            "write",
            lambda var, index, mode: self.master.status_vars.temp_text.set(
                f"Temp: {self.master.status_vars.temp.get():.2f} °C"
            ),
        )
        self.master.status_vars.urms.trace_add(
            "write",
            lambda var, index, mode: self.master.status_vars.urms_text.set(
                f"Urms: {self.master.status_vars.urms.get():.2f} mV"
            ),
        )
        self.master.status_vars.irms.trace_add(
            "write",
            lambda var, index, mode: self.master.status_vars.irms_text.set(
                f"Irms: {self.master.status_vars.irms.get():.2f} mA"
            ),
        )
        self.master.status_vars.phase.trace_add(
            "write",
            lambda var, index, mode: self.master.status_vars.phase_text.set(
                f"Phase: {self.master.status_vars.phase.get():.2f} °"
            ),
        )
        self.master.status_vars.signal.trace_add(
            "write",
            lambda var, index, mode: self.master.status_vars.signal_text.set(
                f"Signal {'ON' if self.master.status_vars.signal.get() else 'OFF'}"
            ),
        )

    # def bind_presenters_views(self) -> bool:
    #     for presenter in self._presenters:
    #         if not presenter.bind_view():
    #             return False
    #     return True

    def bind_events(self) -> None:
        ...

    def handle_firmware_flash(self) -> None:
        ...

    def handle_disconnect(self) -> None:
        ...

    def handle_script_start(self) -> None:
        ...

    def handle_script_stop(self) -> None:
        ...

    def handle_closing(self) -> None:
        ...

    def handle_connection_attempt(self) -> None:
        ...

    def handle_status_update(self) -> None:
        ...

    def handle_connect(self) -> None:
        ...

    def start(self) -> None:
        if sys.platform != "win32":
            logger.info("Enabling high dpi awareness")
            enable_high_dpi_awareness(self)
        self.master.mainloop()
        # async_mainloop(self._view)


print(sys.platform)
