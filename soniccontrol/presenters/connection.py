import ttkbootstrap as ttk
from icecream import ic
from soniccontrol.amp import SonicAmp
from soniccontrol.core.windowview import MainView
from soniccontrol.interfaces.presenter import Presenter
from soniccontrol.utils import constants
from soniccontrol.views.connectionview import ConnectionView


class ConnectionPresenter(Presenter):
    def __init__(self, master: MainView, sonicamp: SonicAmp):
        super().__init__(master, sonicamp)
        print("lmao connection")
        self.bind_view()

    @property
    def view(self) -> ConnectionView:
        return self.master.views.connection

    def bind_view(self) -> None:
        self.master.bind_all(
            constants.events.CONNECTION_ATTEMPT_EVENT,
            self.on_connection_attempt,
            add=True,
        )
        self.view.bind_all(
            constants.events.CONNECTION_ATTEMPT_EVENT,
            self.view.on_connection_attempt,
            add=True,
        )
        self.master.bind_all(
            constants.events.DISCONNECTED_EVENT, self.on_disconnect, add=True
        )
        self.view.bind_all(
            constants.events.DISCONNECTED_EVENT, self.view.on_disconnect, add=True
        )

        self.view._subtitle.configure(
            textvariable=self.master.misc_vars.connection_subtitle
        )
        self.view._heading_part_one.configure(
            textvariable=self.master.misc_vars.device_heading1
        )
        self.view._heading_part_two.configure(
            textvariable=self.master.misc_vars.device_heading2
        )

    def on_connection_attempt(self, event: ttk.tk.Event, *args, **kwargs) -> None:
        ic("on connection attempt lmao")
        self.master.misc_vars.connection_subtitle.set("This might take a moment")
        self.master.misc_vars.device_heading1.set("connecting")
        self.master.misc_vars.device_heading2.set("")
        self.master.misc_vars.device_heading1.animate_dots(self.view)

    def on_connect(self, event: ttk.tk.Event, *args, **kwargs) -> None:
        pass

    def on_disconnect(self, event: ttk.tk.Event, *args, **kwargs) -> None:
        ic("disconnecting lmao")
        self.master.misc_vars.connection_subtitle.set(constants.ui.PLEASE_CONNECT_LABEL)
        self.master.misc_vars.device_heading1.stop_animation()
        self.master.misc_vars.device_heading1.set("not")
        self.master.misc_vars.device_heading2.set("connected")
