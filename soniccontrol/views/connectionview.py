from typing import Tuple

import ttkbootstrap as ttk
from soniccontrol.interfaces.layouts import Layout
from soniccontrol.utils import ImageLoader, constants
from ttkbootstrap.scrolled import ScrolledFrame

from soniccontrol import soniccontrol_logger as logger


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
            self._heading_frame,
            text=constants.ui.PLEASE_CONNECT_LABEL,
            anchor=ttk.CENTER,
        )
        self._heading_part_one: ttk.Label = ttk.Label(
            self._heading_frame,
            text=constants.ui.NOT_LABEL,
            font=("QTypeOT", 24),
            justify=ttk.CENTER,
            anchor=ttk.CENTER,
        )
        self._heading_part_two: ttk.Label = ttk.Label(
            self._heading_frame,
            text=constants.ui.CONNECTED_LABEL,
            font=("QTypeOT", 24),
            justify=ttk.CENTER,
            anchor=ttk.CENTER,
        )

        self._firmware_info_frame: ttk.Labelframe = ttk.Labelframe(
            self._body_frame, text=constants.ui.FIRMWARE_LABEL, style=ttk.DARK
        )
        self._firmware_info_label: ttk.Label = ttk.Label(
            self._firmware_info_frame,
            style=ttk.DARK,
            justify=ttk.CENTER,
            text="THIS IS A FIRMWARE LABEL TEST LABELL, REMOVE THIS TODO:\n usepat LABEL\n sonicamp: SONICAMP\n Version: 1.0.0\n",
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

        self._navigation_frame.pack(fill=ttk.X, pady=10, padx=7)
        self._ports_menue.pack(side=ttk.LEFT, expand=True, fill=ttk.X, padx=3)
        self._refresh_button.pack(side=ttk.LEFT, padx=3)
        self._connect_button.pack(side=ttk.LEFT, padx=3)

        self._body_frame.pack(fill=ttk.BOTH, expand=True)
        self._heading_frame.columnconfigure(0, weight=1)
        self._heading_frame.columnconfigure(1, weight=1)
        self._heading_frame.columnconfigure(2, weight=1)
        self._heading_frame.columnconfigure(3, weight=1)
        self._heading_frame.rowconfigure(0, weight=1)
        self._heading_frame.rowconfigure(1, weight=1)
        self._heading_frame.rowconfigure(2, weight=2)
        self._heading_frame.rowconfigure(3, weight=1)
        self._heading_frame.pack(fill=ttk.BOTH, expand=True, pady=10, padx=10)
        self._subtitle.grid(row=1, column=1, columnspan=2, sticky=ttk.EW)
        self._heading_part_one.grid(row=2, column=1, sticky=ttk.E)
        self._heading_part_two.grid(row=2, column=2, sticky=ttk.W)

        self._firmware_info_frame.pack(expand=True, pady=10, padx=10, anchor=ttk.CENTER)
        self._firmware_info_label.pack(fill=ttk.BOTH, expand=True, anchor=ttk.CENTER)

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
