from os import terminal_size

from soniccontrol.amp import SonicAmp
from soniccontrol.core.windowview import MainView
from soniccontrol.interfaces.presenter import Presenter
from soniccontrol.utils import constants
from soniccontrol.views.statusview import StatusBarView, StatusView


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

        self.master.bind_all(
            constants.events.CONNECTED_EVENT, self.view.on_connected, add=True
        )
        self.master.bind_all(
            constants.events.DISCONNECTED_EVENT, self.view.on_disconnected, add=True
        )
        self.master.bind_all(
            constants.events.SCRIPT_START_EVENT, self.view.on_script_start, add=True
        )
        self.master.bind_all(
            constants.events.SCRIPT_STOP_EVENT, self.view.on_idle, add=True
        )
        self.master.bind_all(
            constants.events.AUTO_MODE_EVENT, self.view.on_auto_mode, add=True
        )
        self.master.bind_all(
            constants.events.SIGNAL_OFF, self.view.on_signal_off, add=True
        )
        self.master.bind_all(
            constants.events.SIGNAL_ON, self.view.on_signal_on, add=True
        )


class StatusPresenter(Presenter):
    def __init__(self, master: MainView, sonicamp: SonicAmp):
        super().__init__(master, sonicamp)
        print("Initialized StatusViewPresenter")
        self.bind_view()

    @property
    def view(self) -> StatusView:
        return self.master._status_frame

    def bind_view(self) -> None:
        self.view._urms_label.configure(textvariable=self.master.status_vars.urms_text)
        self.view._irms_label.configure(textvariable=self.master.status_vars.irms_text)
        self.view._phase_label.configure(
            textvariable=self.master.status_vars.phase_text
        )
        self.view._connection_label.configure(
            textvariable=self.master.misc_vars.connection_state
        )
        self.view._signal_label.configure(
            textvariable=self.master.status_vars.signal_text
        )

        self.master.bind_all(
            constants.events.SIGNAL_ON, self.view.on_signal_on, add=True
        )
        self.master.bind_all(
            constants.events.SIGNAL_OFF, self.view.on_signal_off, add=True
        )
        self.master.bind_all(
            constants.events.CONNECTED_EVENT, self.view.on_connect, add=True
        )
        self.master.bind_all(
            constants.events.DISCONNECTED_EVENT, self.view.on_disconnect
        )
