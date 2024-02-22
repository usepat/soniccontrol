import soniccontrol
from soniccontrol.core.windowview import MainView

# VIEW TESTING SCRIPT
# This script it used to view the gui without any communication or presenter logic
# The GUI should appear with every view defaulting to its appearance. Using this script
# one can inspect the GUI and change appearences without needing to connect to a SonicAmp
# TODO: Make sure that the script works with async tkinter also


class SonicAmp:
    def __init__(self) -> None:
        pass


class MainPresenter:
    def __init__(self, view: MainView, sonicamp: SonicAmp) -> None:
        self._view = view

    def start(self) -> None:
        self._view.mainloop()


def test_gui() -> None:
    sonicamp: SonicAmp = SonicAmp()
    view: MainView = MainView()
    presenter: MainPresenter = MainPresenter(view, sonicamp)
    presenter.start()
