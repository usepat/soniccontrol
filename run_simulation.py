from soniccontrol.tkintergui.views.core.connection_window import ConnectionWindow
from soniccontrol.utils.system import PLATFORM, System
from soniccontrol import soniccontrol_logger as logger

from async_tkinter_loop import async_mainloop
from ttkbootstrap.utility import enable_high_dpi_awareness


def main() -> None:
    main_window = ConnectionWindow(show_simulation_button=True)
    if PLATFORM != System.WINDOWS:
        logger.info("Enabling high dpi awareness for DARWIN/ LINUX")
        enable_high_dpi_awareness(main_window.view)
    async_mainloop(main_window.view)


if __name__ == "__main__":
    main()