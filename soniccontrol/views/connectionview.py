from typing import Tuple

import ttkbootstrap as ttk
from soniccontrol.interfaces.layouts import Layout
from ttkbootstrap.scrolled import ScrolledFrame


class ConnectionView(ttk.Frame):
    def __init__(
        self, master: ttk.tk.Widget | ttk.tk.Misc | None, *args, **kwargs
    ) -> None:
        super().__init__(master, *args, **kwargs)

        self._main_frame: ScrolledFrame = ScrolledFrame(self)

    @property
    def image(self) -> ttk.tk.PhotoImage:
        ...

    @property
    def tab_title(self) -> str:
        ...

    @property
    def layouts(self) -> set[Layout]:
        ...

    def toggle_firmware(self) -> None:
        ...

    def toggle_heading_highlight(self) -> None:
        ...

    def set_small_width_heading(self) -> None:
        ...

    def set_large_width_heading(self) -> None:
        ...

    def set_small_width_control_frame(self) -> None:
        ...

    def set_large_width_control_frame(self) -> None:
        ...

    def set_heading(self, heading: Tuple[str, str] | str, subtitle: str) -> None:
        ...

    def change_button_to(
        self, connected: bool = False, disconnected: bool = False
    ) -> None:
        ...

    def enable_firmware_info(self) -> None:
        ...

    def disable_firmware_info(self) -> None:
        ...

    def on_connection_attempt(self) -> None:
        ...

    def on_connect(self) -> None:  # , event: ConnectionEvent) -> None:
        ...

    def on_disconnect(self) -> None:
        ...

    def publish(self) -> None:
        ...
