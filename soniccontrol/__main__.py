from soniccontrol.amp import SonicAmp
from soniccontrol.core.window import MainPresenter
from soniccontrol.core.windowview import MainView

import soniccontrol


def main() -> None:
    sonicamp: SonicAmp = SonicAmp()
    view: MainView = MainView()
    presenter: MainPresenter = MainPresenter(view, sonicamp)
    presenter.start()


if __name__ == "__main__":
    main()
