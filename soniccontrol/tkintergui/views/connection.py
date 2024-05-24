from typing import Tuple

import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame

from soniccontrol import soniccontrol_logger as logger
from soniccontrol.interfaces.view import TabView
from soniccontrol.tkintergui.utils.constants import (events, fonts, sizes,
                                                     style, ui_labels)
from soniccontrol.tkintergui.utils.image_loader import ImageLoader
from soniccontrol.tkintergui.widgets.responsive_label import ResponsiveLabel
from soniccontrol.utils.files import images


class ConnectionView(TabView):
    def __init__(self, master: ttk.tk.Widget | ttk.Window, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)

    @property
    def image(self) -> ttk.ImageTk.PhotoImage:
        return ImageLoader.load_image(images.CONNECTION_ICON_BLACK, sizes.TAB_ICON_SIZE)

    @property
    def tab_title(self) -> str:
        return ui_labels.CONNECTION_LABEL

    def _initialize_children(self) -> None:
        self._main_frame: ttk.Frame = ttk.Frame(self)
        self._navigation_frame: ttk.Frame = ttk.Frame(self._main_frame)
        self._refresh_button: ttk.Button = ttk.Button(
            self._navigation_frame,
            image=ImageLoader.load_image(
                images.REFRESH_ICON_GREY, sizes.BUTTON_ICON_SIZE
            ),
            style=style.SECONDARY_OUTLINE,
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
            text=ui_labels.CONNECT_LABEL,
            command=lambda: self.event_generate(events.CONNECTION_ATTEMPT_EVENT),
        )
        self._body_frame: ScrolledFrame = ScrolledFrame(self._main_frame)
        self._heading_frame: ttk.Frame = ttk.Frame(self._body_frame)
        self._subtitle: ttk.Label = ttk.Label(
            self._heading_frame,
            text=ui_labels.PLEASE_CONNECT_LABEL,
            anchor=ttk.CENTER,
        )
        self._heading_part_one: ttk.Label = ttk.Label(
            self._heading_frame,
            text=ui_labels.NOT_LABEL,
            font=(fonts.QTYPE_OT_CONDLIGHT, fonts.HEADING_SIZE),
            justify=ttk.CENTER,
            anchor=ttk.CENTER,
        )
        self._heading_part_two: ttk.Label = ttk.Label(
            self._heading_frame,
            text=ui_labels.CONNECTED_LABEL,
            font=(fonts.QTYPE_OT, fonts.HEADING_SIZE),
            justify=ttk.CENTER,
            anchor=ttk.CENTER,
        )

        self._firmware_info_frame: ttk.Labelframe = ttk.Labelframe(
            self._body_frame, text=ui_labels.FIRMWARE_LABEL, style=ttk.DARK
        )
        self._firmware_info_label: ttk.Label = ResponsiveLabel(
            self._firmware_info_frame,
            style=ttk.DARK,
            justify=ttk.CENTER,
            wraplength=300,
            parent_reference=self,
            text="THIS IS A FIRMWARE LABEL TEST LABELL, REMOVE THIS TODO:\n usepat LABEL\n sonicamp: SONICAMP\n Version: 1.0.0\n",
        )

    def _initialize_publish(self) -> None:
        logger.info("Initializing Publish")
        self._main_frame.pack(fill=ttk.BOTH, expand=True)

        self._navigation_frame.pack(
            fill=ttk.X,
            pady=sizes.LARGE_PADDING,
            padx=sizes.LARGE_PART_PADDING,
        )
        self._ports_menue.pack(
            side=ttk.LEFT, expand=True, fill=ttk.X, padx=sizes.SMALL_PADDING
        )
        self._refresh_button.pack(side=ttk.LEFT, padx=sizes.SMALL_PADDING)
        self._connect_button.pack(side=ttk.LEFT, padx=sizes.SMALL_PADDING)

        self._body_frame.pack(fill=ttk.BOTH, expand=True)
        self._body_frame.rowconfigure(0, weight=sizes.DONT_EXPAND, minsize=40)
        self._body_frame.rowconfigure(1, weight=sizes.EXPAND)
        self._body_frame.columnconfigure(0, weight=sizes.EXPAND)

        self._heading_frame.columnconfigure(0, weight=sizes.EXPAND)
        self._heading_frame.columnconfigure(1, weight=sizes.EXPAND)
        self._heading_frame.columnconfigure(2, weight=sizes.EXPAND)
        self._heading_frame.columnconfigure(3, weight=sizes.EXPAND)
        self._heading_frame.rowconfigure(0, weight=sizes.EXPAND)
        self._heading_frame.rowconfigure(1, weight=sizes.EXPAND)
        self._heading_frame.rowconfigure(2, weight=2)
        self._heading_frame.rowconfigure(3, weight=sizes.EXPAND)
        # self._heading_frame.pack(
        #     fill=ttk.BOTH,
        #     expand=True,
        #     pady=constants.misc.LARGE_PADDING,
        #     padx=constants.misc.LARGE_PADDING,
        # )

        self._heading_frame.grid(
            row=0,
            column=0,
            sticky=ttk.EW,
            pady=sizes.LARGE_PADDING,
            padx=sizes.LARGE_PADDING,
        )
        self._subtitle.grid(row=1, column=1, columnspan=2, sticky=ttk.EW)
        self._heading_part_one.grid(row=2, column=1, sticky=ttk.E)
        self._heading_part_two.grid(row=2, column=2, sticky=ttk.W)
        # self._firmware_info_frame.pack(
        #     expand=True,
        #     pady=constants.misc.LARGE_PADDING,
        #     padx=constants.misc.LARGE_PADDING,
        #     anchor=ttk.CENTER,
        # )
        self._firmware_info_frame.grid(
            row=1,
            column=0,
            # sticky=ttk.NSEW,
            pady=sizes.LARGE_PADDING,
            padx=sizes.LARGE_PADDING,
        )
        self._firmware_info_label.pack(fill=ttk.BOTH, expand=True, anchor=ttk.CENTER)

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

    def on_connection_attempt(self, event: ttk.tk.Event) -> None:
        self._connect_button.configure(
            bootstyle=ttk.DANGER,
            text="Cancel",
            command=lambda: self.event_generate(events.DISCONNECTED_EVENT),
        )

    def on_connect(
        self, event: ttk.tk.Event
    ) -> None:  # , event: ConnectionEvent) -> None:
        self._firmware_info_frame.grid()

    def on_disconnect(self, event: ttk.tk.Event) -> None:
        self._connect_button.configure(
            bootstyle=ttk.SUCCESS,
            text="Connect",
            command=lambda: self.event_generate(events.CONNECTION_ATTEMPT_EVENT),
        )
        self._firmware_info_frame.grid_remove()

    def publish(self) -> None:
        ...
