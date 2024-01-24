from soniccontrol import soniccontrol_logger
from soniccontrol.amp import SonicAmp
from soniccontrol.core.window import MainPresenter
from soniccontrol.core.windowview import MainView


def main() -> None:
    sonicamp: SonicAmp = SonicAmp()
    view: MainView = MainView()
    presenter: MainPresenter = MainPresenter(view, sonicamp)
    presenter.start()


main()
