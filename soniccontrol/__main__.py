from soniccontrol.tkintergui.views.core.cli_connection_window import CliConnectionWindow
from soniccontrol.tkintergui.views.core.connection_window import ConnectionWindow
from soniccontrol.utils.system import PLATFORM, System
from soniccontrol import soniccontrol_logger as logger

from async_tkinter_loop import async_mainloop
from ttkbootstrap.utility import enable_high_dpi_awareness


def main_refactored() -> None:
    mainwindow = ConnectionWindow()
    if PLATFORM != System.WINDOWS:
        logger.info("Enabling high dpi awareness for DARWIN/ LINUX")
        enable_high_dpi_awareness(mainwindow.view)
    async_mainloop(mainwindow.view)


def main_cli():
    mainwindow = CliConnectionWindow()
    if PLATFORM != System.WINDOWS:
        logger.info("Enabling high dpi awareness for DARWIN/ LINUX")
        enable_high_dpi_awareness(mainwindow.view)
    async_mainloop(mainwindow.view)


if __name__ == "__main__":
    main_cli()
