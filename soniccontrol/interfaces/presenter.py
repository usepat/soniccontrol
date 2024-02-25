import abc

from soniccontrol.amp import SonicAmp
from soniccontrol.core.windowview import MainView


class Presenter(abc.ABC):
    def __init__(self, master: MainView, sonicamp: SonicAmp):
        self._master = master
        self._sonicamp = sonicamp

    @property
    def master(self):
        return self._master

    @property
    def sonicamp(self):
        return self._sonicamp
