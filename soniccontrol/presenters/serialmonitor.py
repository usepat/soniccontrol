from soniccontrol.amp import SonicAmp
from soniccontrol.core.windowview import MainView
from soniccontrol.interfaces.presenter import Presenter
from soniccontrol.views.serialmonitorview import SerialMonitorView


class SerialMonitorPresenter(Presenter):
    def __init__(self, master: MainView, sonicamp: SonicAmp):
        super().__init__(master, sonicamp)
        print("lmao serialmonitor")

    @property
    def view(self) -> SerialMonitorView:
        return self.master.views.serialmonitor

    def bind_view(self) -> None:
        ...
