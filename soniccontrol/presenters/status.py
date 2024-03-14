from os import terminal_size

from soniccontrol.amp import SonicAmp
from soniccontrol.core.windowview import MainView
from soniccontrol.interfaces.presenter import Presenter
from soniccontrol.utils import constants
from soniccontrol.views.statusview import StatusBarView


class StatusBarPresenter(Presenter):
    def __init__(self, master: MainView, sonicamp: SonicAmp):
        super().__init__(master, sonicamp)
        print("lmao statusbar")
        self.bind_view()

    @property
    def view(self) -> StatusBarView:
        return self.master.views.statusbar

    def bind_view(self) -> None:
        self.view._program_state_label.configure(
            textvariable=self.master.misc_vars.program_state
        )
        self.view._freq_label.configure(
            textvariable=self.master.status_vars.freq_khz_text
        )
        self.view._gain_label.configure(textvariable=self.master.status_vars.gain_text)
        self.view._temperature_label.configure(
            textvariable=self.master.status_vars.temp_text
        )
        self.view._mode_label.configure(textvariable=self.master.status_vars.relay_mode)
        self.view._urms_label.configure(textvariable=self.master.status_vars.urms_text)
        self.view._irms_label.configure(textvariable=self.master.status_vars.irms_text)
        self.view._phase_label.configure(
            textvariable=self.master.status_vars.phase_text
        )
        self.master.status_vars.freq_khz_text.set("Freq: 10000 khz")
        self.master.misc_vars.program_state.set("Disconnected")

        self.master.bind_all(
            constants.events.DISCONNECTED_EVENT, self.view.on_disconnected, add=True
        )


class StatusPresenter(Presenter):
    def __init__(self, master: MainView, sonicamp: SonicAmp):
        super().__init__(master, sonicamp)
        print("lmao statusbar")
