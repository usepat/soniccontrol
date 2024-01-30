from typing import Tuple

import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame

from soniccontrol import soniccontrol_logger as logger
from soniccontrol.interfaces.layouts import Layout
from soniccontrol.utils import ImageLoader, constants


class ConnectionView(ttk.Frame):
    def __init__(
        self, master: ttk.tk.Widget | ttk.tk.Misc | None, *args, **kwargs
    ) -> None:
        super().__init__(master, *args, **kwargs)

        self._main_frame: ttk.Frame = ttk.Frame(self)
        self._navigation_frame: ttk.Frame = ttk.Frame(self._main_frame)
        self._refresh_button: ttk.Button = ttk.Button(
            self._navigation_frame,
            image=ImageLoader.load_image(constants.images.REFRESH_ICON_GREY, (13, 13)),
            style="secondary-outline",
            compound=ttk.RIGHT,
        )
        self._ports_menue: ttk.Combobox = ttk.Combobox(
            self._navigation_frame,
            style=ttk.DARK,
            state=ttk.READONLY,
        )
        self._connect_button: ttk.Button = ttk.Button(
            self._navigation_frame,
            style=ttk.SUCCESS,
            text=constants.ui.CONNECT_LABEL,
        )
        self._body_frame: ScrolledFrame = ScrolledFrame(self._main_frame)
        self._heading_frame: ttk.Frame = ttk.Frame(self._body_frame)
        self._subtitle: ttk.Label = ttk.Label(
            self._heading_frame, text=constants.ui.PLEASE_CONNECT_LABEL
        )
        self._heading_one: ttk.Label = ttk.Label(
            self._heading_frame, text=constants.ui.NOT_LABEL
        )
        self._heading_two: ttk.Label = ttk.Label(
            self._heading_frame, text=constants.ui.CONNECTED_LABEL
        )

        self._firmware_info_frame: ttk.Labelframe = ttk.Labelframe(
            self._body_frame, text=constants.ui.FIRMWARE_LABEL, style=ttk.DARK
        )
        self._firmware_info_label: ttk.Label = ttk.Label(
            self._firmware_info_frame, style=ttk.DARK, justify=ttk.CENTER
        )
        self._init_publish()

    @property
    def image(self) -> ttk.ImageTk.PhotoImage:
        return ImageLoader.load_image(constants.images.CONNECTION_ICON_BLACK, (25, 25))

    @property
    def tab_title(self) -> str:
        return constants.ui.CONNECTION_LABEL

    @property
    def layouts(self) -> set[Layout]:
        ...

    def _init_publish(self) -> None:
        self._main_frame.pack(fill=ttk.BOTH, expand=True)

        self._navigation_frame.columnconfigure(0, weight=5)
        self._navigation_frame.columnconfigure(1, weight=1)
        self._navigation_frame.columnconfigure(2, weight=3)
        self._navigation_frame.pack(fill=ttk.X)
        self._ports_menue.grid(row=0, column=0, sticky=ttk.EW)
        self._refresh_button.grid(row=0, column=1)
        self._connect_button.grid(row=0, column=2, sticky=ttk.EW)

        self._body_frame.pack(fill=ttk.BOTH, expand=True)
        self._heading_frame.columnconfigure(0, weight=1)
        self._heading_frame.columnconfigure(1, weight=1)
        self._heading_frame.rowconfigure(0, weight=1)
        self._heading_frame.rowconfigure(1, weight=2)
        self._heading_frame.pack(fill=ttk.BOTH, expand=True)
        self._subtitle.grid(row=0, column=0, columnspan=2, sticky=ttk.NSEW)
        self._heading_one.grid(row=1, column=0, sticky=ttk.NSEW)
        self._heading_two.grid(row=1, column=1, sticky=ttk.NSEW)

        self._firmware_info_frame.pack(fill=ttk.BOTH, expand=True)
        self._firmware_info_label.pack(fill=ttk.BOTH, expand=True)

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
