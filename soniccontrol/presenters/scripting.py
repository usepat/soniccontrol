from soniccontrol.amp import SonicAmp
from soniccontrol.core.windowview import MainView
from soniccontrol.interfaces.presenter import Presenter


class ScriptPresenter(Presenter):
    def __init__(self, master: MainView, sonicamp: SonicAmp):
        super().__init__(master, sonicamp)
        print("lmao script")
