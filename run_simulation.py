from soniccontrol.tkintergui.views.core.cli_connection_window import CliConnectionWindow
from soniccontrol.utils.system import PLATFORM, System
from soniccontrol import soniccontrol_logger as logger

from async_tkinter_loop import async_mainloop
from ttkbootstrap.utility import enable_high_dpi_awareness


def main_cli():
    main_window = CliConnectionWindow()
    if PLATFORM != System.WINDOWS:
        logger.info("Enabling high dpi awareness for DARWIN/ LINUX")
        enable_high_dpi_awareness(main_window.view)
    async_mainloop(main_window.view)

if __name__ == "__main__":
    main_cli()