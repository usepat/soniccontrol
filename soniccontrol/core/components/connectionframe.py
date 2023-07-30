import logging
from typing import Dict, Iterable
import tkinter as tk
import ttkbootstrap as ttk
import PIL
import soniccontrol.constants as const

from PIL.ImageTk import PhotoImage
from soniccontrol.interfaces import (
    RootChild,
    WidthLayout,
    Disconnectable,
    Connectable,
    Layout
)

logger = logging.getLogger(__name__)


class ConnectionFrame(RootChild, Disconnectable, Connectable):
    def __init__(
        self, parent_frame: ttk.Frame, tab_title: str, image: PIL.Image, *args, **kwargs
    ):
        super().__init__(parent_frame, tab_title, image, *args, **kwargs)
        self._width_layouts: Iterable[Layout] = (
            WidthLayout(
                min_width=100,
                command=self.set_small_layout
            ),
            WidthLayout(
                min_width=300,
                command=self.set_large_layout
            )
        )
        
        ### tkinter variables
        self.port: tk.StringVar = tk.StringVar()
        self.refresh_image: PhotoImage = PhotoImage(const.REFRESH_RAW_IMG)

        ### TOPFRAME
        self.topframe: ttk.Frame = ttk.Frame(self, padding=(10, 10, 10, 10))
        ### HEADING
        self.heading_frame: ttk.Frame = ttk.Frame(self.topframe)
        self.subtitle: ttk.Label = ttk.Label(self.heading_frame, padding=(0, 10, 0, 0))
        self.heading1: ttk.Label = ttk.Label(
            self.heading_frame,
            padding=(10, 0, 2, 10),
            font=("QTypeOT-CondBook", 30),
            justify=ttk.CENTER,
            anchor=ttk.CENTER,
            borderwidth=-2,
        )
        self.heading2: ttk.Label = ttk.Label(
            self.heading_frame,
            padding=(2, 0, 0, 10),
            font=("QTypeOT-CondBook", 30),
            justify=tk.CENTER,
            anchor=ttk.CENTER,
            borderwidth=-2,
        )
        self.firmware_frame: ttk.Labelframe = ttk.Labelframe(
            self.heading_frame,
            text="Firmware",
        )
        self.firmware_label: ttk.Label = ttk.Label(
            self.firmware_frame, justify=tk.CENTER, style="dark.TLabel"
        )
        ### PORTSMENUE
        self.control_frame: ttk.Frame = ttk.Frame(self.topframe)
        self.connect_button: ttk.Button = ttk.Button(
            self.control_frame,
            width=10,
            style="success.TButton",
            command=lambda: self.event_generate(const.Events.CONNECTION_ATTEMPT),
        )
        self.port_frame: ttk.Frame = ttk.Frame(self.control_frame)
        self.ports_menue: ttk.Combobox = ttk.Combobox(
            master=self.port_frame,
            textvariable=self.port,
            width=7,
            style="dark.TCombobox",
            state=tk.READABLE,
        )
        self.refresh_button: ttk.Button = ttk.Button(
            self.port_frame,
            bootstyle="secondary-outline",
            image=self.refresh_image,
            command=lambda: self.event_generate(const.Events.PORT_REFRESH),
        )
        ### OTHER
        self.flash_progressbar: ttk.Progressbar = ttk.Progressbar(
            self.topframe,
            mode="indeterminate",
            orient=tk.HORIZONTAL,
        )

        self.botframe: ttk.Frame = ttk.Frame(self)
        self.bind_events()
        self.publish()
        logger.debug('ConnectionFrame initialized')
    
    def bind_events(self) -> None:
        super().bind_events()

    def show_firmware(self, event=None) -> None:
        print("showing firmware....")

    def mark_heading_frame(self, event=None) -> None:
        self.heading_frame.configure(bootstyle=ttk.SECONDARY)
        self.subtitle.configure(bootstyle="inverse-secondary")
        self.heading1.configure(bootstyle="inverse-secondary")
        self.heading2.configure(bootstyle="inverse-secondary")
        self.firmware_frame.configure(bootstyle=ttk.SECONDARY)
        self.firmware_label.configure(bootstyle="inverse-secondary")

    def unmark_heading_frame(self, event=None) -> None:
        self.heading_frame.configure(bootstyle=ttk.DEFAULT)
        for child in self.heading_frame.children.values():
            child.configure(bootstyle=ttk.DEFAULT)
            
    def set_small_layout(self) -> None:
        logger.debug('setting small layout')
        self.set_small_width_heading()
        self.set_small_width_control_frame()
    
    def set_large_layout(self) -> None:
        logger.debug('setting large layout')
        self.set_large_width_heading()
        self.set_large_width_control_frame()

    def set_small_width_heading(self) -> None:
        for child in self.heading_frame.children.values():
            child.grid_forget()
        self.subtitle.pack(fill=ttk.X, anchor=ttk.CENTER)
        self.heading1.pack(fill=ttk.X, anchor=ttk.CENTER)
        self.heading2.pack(fill=ttk.X, anchor=ttk.CENTER)

    def set_large_width_heading(self) -> None:
        for child in self.heading_frame.children.values():
            child.pack_forget()
        self.subtitle.grid(row=0, column=0, columnspan=2, sticky=tk.S)
        self.heading1.grid(row=1, column=0, columnspan=1, sticky=tk.E)
        self.heading2.grid(row=1, column=1, columnspan=1, sticky=tk.W)

    def set_small_width_control_frame(self) -> None:
        for child in self.control_frame.children.values():
            child.grid_forget()
        self.port_frame.pack(fill=ttk.X)
        self.connect_button.pack(fill=ttk.X)

    def set_large_width_control_frame(self) -> None:
        for child in self.control_frame.children.values():
            child.pack_forget()
        self.port_frame.grid(row=0, column=0)
        self.connect_button.grid(row=0, column=1)

    def change_heading(self, title_part1: str, title_part2: str, subtitle: str, **kwargs) -> None:
        self.subtitle["text"] = subtitle
        self.heading1["text"] = title_part1
        self.heading2["text"] = title_part2

    def change_button_to(self, connected: bool = False, disconnected: bool = False, **kwargs) -> None:
        if not connected ^ disconnected:
            return
        self.connect_button.configure(
            bootstyle=ttk.DANGER if disconnected else ttk.SUCCESS,
            text="Disconnect" if disconnected else "Connect",
            command=lambda: self.event_generate(
                const.Events.CONNECTED if disconnected else const.Events.CONNECTION_ATTEMPT
            ),
        )
        
    def enable_firmware_info(self) -> None:
        self.heading_frame.bind("<Button-1>", self.show_firmware)
        for child in self.heading_frame.children.values():
            child.bind("<Button-1>", self.show_firmware)
        self.heading_frame.bind("<Enter>", self.mark_heading_frame)
        self.heading_frame.bind("<Leave>", self.unmark_heading_frame)
        
    def disable_firmware_info(self) -> None:
        self.heading_frame.unbind("<Button-1>")
        for child in self.heading_frame.children.values():
            child.unbind("<Button-1>")
        self.heading_frame.unbind("<Enter>")
        self.heading_frame.unbind("<Leave>")

    def on_connect(self) -> None:
        # self.change_heading(**connection_dict)
        self.change_button_to(disconnected=True)
        self.ports_menue.config(state=tk.DISABLED)
        self.refresh_button.config(state=tk.DISABLED)
        self.enable_firmware_info()
        logger.debug('Connectionframe shows itself connected')
    
    def on_refresh(self) -> None:
        pass

    def on_disconnect(self, event) -> None:
        self.change_heading(title_part1='not', title_part2='connected', subtitle="Please connect to a SonicAmp system")
        self.firmware_label["text"] = ""
        self.change_button_to(connected=True)
        self.ports_menue['state'] = ttk.NORMAL
        self.refresh_button['state'] = ttk.NORMAL
        self.event_generate(const.Events.PORT_REFRESH)
        self.disable_firmware_info()
        logger.debug('Connectionframe shows itself disconnected')
        
    def publish(self) -> None:
        self.topframe.pack(expand=True, fill=ttk.BOTH)
        self.heading_frame.pack(ipadx=10, ipady=10)
        self.control_frame.pack(padx=10, pady=10)
        self.refresh_button.grid(row=0, column=0, pady=5)
        self.ports_menue.grid(row=0, column=1, padx=5, pady=5, sticky=ttk.NSEW)