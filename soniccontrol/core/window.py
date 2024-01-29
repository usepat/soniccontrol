import sys

from async_tkinter_loop import async_mainloop
from soniccontrol.amp import SonicAmp
from soniccontrol.core import core_logger as logger
from soniccontrol.core.windowview import MainView
from ttkbootstrap.utility import enable_high_dpi_awareness


class MainPresenter:
    def __init__(self, view: MainView, sonicamp: SonicAmp) -> None:
        self._sonicamp: SonicAmp = sonicamp
        self._view: MainView = view

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
            enable_high_dpi_awareness(self, 1.8)
        self._view.mainloop()
        # async_mainloop(self._view)


print(sys.platform)
