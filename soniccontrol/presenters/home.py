from typing import get_type_hints

from soniccontrol.amp import SonicAmp
from soniccontrol.core.windowview import MainView
from soniccontrol.interfaces.presenter import Presenter
from soniccontrol.interfaces.view import View
from soniccontrol.utils import constants
from soniccontrol.utils.debounce_job import DebounceJob
from soniccontrol.views.homeview import HomeView

from soniccontrol import soniccontrol_logger as logger


class HomePresenter(Presenter):
    def __init__(self, master: MainView, sonicamp: SonicAmp):
        super().__init__(master, sonicamp)
        print("lmao home")
        self.bind_view()

    @property
    def view(self) -> HomeView:
        return self.master.views.home

    def bind_view(self) -> None:
        self.view._freq_spinbox.configure(
            command=DebounceJob(
                self.set_frequency,
                self.view._freq_spinbox,
            ),
            from_=0,
            to=100,
            textvariable=self.master.user_setter_vars.freq,
        )
        self.view._gain_spinbox.configure(
            command=DebounceJob(
                self.set_gain,
                self.view._gain_spinbox,
            ),
            from_=0,
            to=100,
            textvariable=self.master.user_setter_vars.gain,
        )
        self.view._gain_scale.configure(
            command=DebounceJob(
                self.set_gain,
                self.view._gain_scale,
            ),
            from_=0,
            to=100,
            variable=self.master.user_setter_vars.gain,
        )

        self.view._wipe_mode_button.configure(
            variable=self.master.user_setter_vars.relay_mode,
            command=self.change_relay_mode,
        )
        self.view._catch_mode_button.configure(
            variable=self.master.user_setter_vars.relay_mode,
            command=self.change_relay_mode,
        )

        self.view._set_values_button.configure(command=self.set_parameters)
        self.view._us_on_button.configure(command=self.set_signal_on)
        self.view._us_off_button.configure(command=self.set_signal_off)
        self.view._us_auto_button.configure(command=self.set_signal_auto)

        self.master.bind_all(
            constants.events.AUTO_MODE_EVENT,
            self.view.disable_control_panel,
            add=True,
        )
        self.master.bind_all(
            constants.events.SIGNAL_OFF,
            self.view.enable_control_panel,
            add=True,
        )

    def set_parameters(self) -> None:
        self.set_frequency()
        if self.master.user_setter_vars.relay_mode.get() != constants.ui.WIPE_LABEL:
            self.set_gain()

    def set_frequency(self, *args, **kwargs) -> None:
        if self.view._freq_spinbox.get().isnumeric():
            self.set_parameter("freq", self.master.user_setter_vars.freq.get())

    def set_gain(self, *args, **kwargs) -> None:
        if self.view._gain_spinbox.get().isnumeric():
            self.set_parameter("gain", self.master.user_setter_vars.gain.get())

    def set_parameter(self, parameter, value) -> None:
        answer: str = f"{parameter}: {value}"
        self.view.on_feedback(answer)

    def set_signal_auto(self, *args, **kwargs) -> None:
        self.view.on_feedback("Signal AUTO")
        self.master.event_generate(constants.events.AUTO_MODE_EVENT)

    def set_signal_off(self, *args, **kwargs) -> None:
        self.view.on_feedback("Signal OFF")
        self.master.event_generate(constants.events.SIGNAL_OFF)

    def set_signal_on(self, *args, **kwargs) -> None:
        self.view.on_feedback("Signal ON")
        self.master.event_generate(constants.events.SIGNAL_ON)

    def change_relay_mode(self):
        self.view.on_feedback(
            self.master.user_setter_vars.relay_mode.get()
            # await self.sonicamp.change_relay_mode(
            #     self.master.user_setter_vars.relay_mode.get()
            # )
        )
        if self.master.user_setter_vars.relay_mode.get() == constants.ui.WIPE_LABEL:
            self.view.disable_gain()
        else:
            self.view.enable_gain()
