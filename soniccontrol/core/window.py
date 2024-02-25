import sys
from typing import Any, Callable, Literal, TypedDict, get_type_hints

import attrs
import ttkbootstrap as ttk
from async_tkinter_loop import async_mainloop
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
from ttkbootstrap.utility import enable_high_dpi_awareness


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
            enable_high_dpi_awareness(self)
        self.master.mainloop()
        # async_mainloop(self._view)


print(sys.platform)
