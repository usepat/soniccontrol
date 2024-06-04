from soniccontrol.core.soniccontroller import SonicController
from soniccontrol.tkintergui.mainview import MainView
from soniccontrol.tkintergui.mainwindow import MainWindow
from soniccontrol.tkintergui.models import DeviceModel
from soniccontrol.utils.system import PLATFORM, System
from soniccontrol import soniccontrol_logger as logger

from async_tkinter_loop import async_mainloop
from ttkbootstrap.utility import enable_high_dpi_awareness

def main() -> None:
    view: MainView = MainView()
    model: DeviceModel = DeviceModel()
    controller: SonicController = SonicController(view, model)
    controller.start()


def main_refactored() -> None:
    mainwindow = MainWindow()
    if PLATFORM != System.WINDOWS:
        logger.info("Enabling high dpi awareness for DARWIN/ LINUX")
        enable_high_dpi_awareness(mainwindow.view)
    async_mainloop(mainwindow.view)


if __name__ == "__main__":
    main_refactored()
