from soniccontrol.core.soniccontroller import SonicController
from soniccontrol.tkintergui.mainview import MainView
from soniccontrol.tkintergui.models import DeviceModel


def main() -> None:
    view: MainView = MainView()
    model: DeviceModel = DeviceModel()
    controller: SonicController = SonicController(view, model)
    controller.start()


if __name__ == "__main__":
    main()
