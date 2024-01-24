import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame

import soniccontrol.utils.constants as const
from soniccontrol.components.spinbox import Spinbox
from soniccontrol.interfaces.layouts import Layout


class HomeView(ttk.Frame):
    def __init__(self, master: ttk.Window, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)
        self._master: ttk.Window = master

        self._main_frame: ScrolledFrame = ScrolledFrame(self, autohide=True)
        self._top_frame: ttk.Frame = ttk.Frame(self._main_frame)
        self._control_frame: ttk.Labelframe = ttk.Labelframe(
            self._top_frame, text=const.ui.HOME_CONTROL_LABEL
        )
        self._freq_spinbox: Spinbox = Spinbox(
            self._control_frame, placeholder=const.ui.FREQ_PLACEHOLDER, style=ttk.DARK
        )
        self._gain_control_frame: ttk.Frame = ttk.Frame(self._control_frame)
        self._gain_spinbox: Spinbox = Spinbox(
            self._control_frame, placeholder=const.ui.GAIN_PLACEHOLDER, style=ttk.DARK
        )
        self._gain_scale: ttk.Scale = ttk.Scale(
            self._gain_control_frame, orient=ttk.HORIZONTAL, style=ttk.SUCCESS
        )

    @property
    def image(self) -> ttk.PhotoImage:
        ...

    @property
    def tab_title(self) -> str:
        ...

    @property
    def layouts(self) -> set[Layout]:
        ...

    def publish(self) -> None:
        ...

    def set_small_width_layout(self) -> None:
        ...

    def set_large_widht_layout(self) -> None:
        ...

    def on_relay_mode_mhz(self) -> None:
        ...

    def on_relay_mode_khz(self) -> None:
        ...

    def on_feedback(self) -> None:
        ...

    def on_wipe_mode_toggle(self) -> None:
        ...

    def on_auto_mode_toggle(self) -> None:
        ...
