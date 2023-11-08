import tkinter as tk
from typing import Optional
import logging
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame
import serial.tools.list_ports as list_ports
from PIL.ImageTk import PhotoImage
from async_tkinter_loop import async_handler
import soniccontrol.constants as const
from soniccontrol.core.interfaces import (
    RootChild,
    Disconnectable,
    Connectable,
    Flashable,
    Root,
    RootStringVar,
    WidthLayout,
)

logger = logging.getLogger(__name__)


class ConnectionFrame(RootChild, Disconnectable, Connectable, Flashable):
    def __init__(
        self,
        master: Root,
        tab_title: str = "Connection",
        image: Optional[PhotoImage] = None,
        *args,
        **kwargs
    ) -> None:
        super().__init__(master, tab_title=tab_title, image=image, *args, **kwargs)
        self.set_layouts(
            [
                WidthLayout(min_size=350, command=self.set_large_layout),
                WidthLayout(min_size=310, command=self.set_small_layout),
            ]
        )

        self.heading1_var: RootStringVar = RootStringVar(self, value="not")
        self.heading2_var: RootStringVar = RootStringVar(self, value="connected")
        self.subtitle_var: RootStringVar = RootStringVar(
            self, value="Please connect to a SonicAmp device"
        )

        self.main_frame: ScrolledFrame = ScrolledFrame(
            self, autohide=True, padding=(10, 10, 10, 10)
        )
        self.heading_frame: ttk.Frame = ttk.Frame(self.main_frame)
        self.subtitle_label: ttk.Label = ttk.Label(
            self.heading_frame, padding=(0, 10, 0, 0), textvariable=self.subtitle_var
        )
        self.heading1_label: ttk.Label = ttk.Label(
            self.heading_frame,
            padding=(10, 0, 2, 10),
            font=("QTypeOT-CondLight", 30),
            textvariable=self.heading1_var,
            justify=ttk.CENTER,
            anchor=ttk.CENTER,
            borderwidth=-2,
        )
        self.heading2_label: ttk.Label = ttk.Label(
            self.heading_frame,
            padding=(2, 0, 0, 10),
            font=("QTypeOT-CondBook", 30),
            textvariable=self.heading2_var,
            justify=ttk.CENTER,
            anchor=ttk.CENTER,
            borderwidth=-2,
        )
        self.firmware_frame: ttk.Frame = ttk.Frame(self.heading_frame)
        self.firmware_label_frame: ttk.Labelframe = ttk.Labelframe(
            self.firmware_frame,
            text="Firmware",
        )
        self.firmware_label: ttk.Label = ttk.Label(
            self.firmware_label_frame,
            justify=ttk.CENTER,
            bootstyle=ttk.DARK,
        )

        self.control_frame: ttk.Frame = ttk.Frame(self.main_frame)
        self.connect_button: ttk.Button = ttk.Button(
            self.control_frame,
            width=10,
            style=ttk.SUCCESS,
            command=self.on_connection_attempt,
        )
        self.port_frame: ttk.Frame = ttk.Frame(self.control_frame)
        self.ports_menue: ttk.Combobox = ttk.Combobox(
            master=self.port_frame,
            textvariable=self.root.port,
            values=[port.device for port in list_ports.comports()],
            width=15,
            style="dark.TCombobox",
            state=tk.READABLE,
        )
        self.refresh_button: ttk.Button = ttk.Button(
            self.port_frame,
            bootstyle="secondary-outline",
            image=self.root.restart_image,
            command=lambda: self.ports_menue.configure(
                values=[port.device for port in list_ports.comports()]
            ),
        )

        self.bind_events()
        self.publish()

    def show_firmware(self, event=None) -> None:
        print("showing firmware....")
        self.firmware_label_frame.pack(padx=5, pady=5)
        for child in self.heading_frame.children.values():
            child.bind("<Button-1>", self.hide_firmware)

    def hide_firmware(self, event=None) -> None:
        print("hiding firmware....")
        self.firmware_label_frame.pack_forget()
        for child in self.heading_frame.children.values():
            child.bind("<Button-1>", self.show_firmware)

    def mark_heading_frame(self, event=None) -> None:
        self.heading_frame.configure(bootstyle=ttk.SECONDARY)
        self.subtitle_label.configure(bootstyle="inverse-secondary")
        self.heading1_label.configure(bootstyle="inverse-secondary")
        self.heading2_label.configure(bootstyle="inverse-secondary")
        self.firmware_label_frame.configure(bootstyle=ttk.SECONDARY)
        # self.firmware_label.configure(bootstyle="inverse-secondary")

    def unmark_heading_frame(self, event=None) -> None:
        self.heading_frame.configure(bootstyle=ttk.DEFAULT)
        for child in self.heading_frame.children.values():
            child.configure(bootstyle=ttk.DEFAULT)

    def set_small_layout(self, *args, **kwargs) -> None:
        self.set_small_width_heading()
        self.set_small_width_control_frame()

    def set_large_layout(self, *args, **kwargs) -> None:
        self.set_large_width_heading()
        self.set_large_width_control_frame()

    def set_small_width_heading(self) -> None:
        for child in self.heading_frame.children.values():
            child.grid_forget()
        self.subtitle_label.pack(fill=ttk.X, anchor=ttk.CENTER)
        self.heading1_label.pack(fill=ttk.X, anchor=ttk.CENTER)
        self.heading2_label.pack(fill=ttk.X, anchor=ttk.CENTER)
        self.firmware_frame.pack(anchor=ttk.CENTER, padx=5, pady=5)

    def set_large_width_heading(self) -> None:
        for child in self.heading_frame.children.values():
            child.pack_forget()
        self.subtitle_label.grid(row=0, column=0, columnspan=2, sticky=tk.S)
        self.heading1_label.grid(row=1, column=0, columnspan=1, sticky=tk.E)
        self.heading2_label.grid(row=1, column=1, columnspan=1, sticky=tk.W)
        self.firmware_frame.grid(
            row=2, column=0, columnspan=2, sticky=tk.N, padx=5, pady=5
        )

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

    def change_heading(
        self, title_part1: str, title_part2: str, subtitle: str, **kwargs
    ) -> None:
        self.subtitle_var.set(subtitle)
        self.heading1_var.set(title_part1)
        self.heading2_var.set(title_part2)

    def change_button_to(
        self, connected: bool = False, disconnected: bool = False, **kwargs
    ) -> None:
        if not connected ^ disconnected:
            return
        self.connect_button.configure(
            state=ttk.NORMAL,
            bootstyle=ttk.DANGER if disconnected else ttk.SUCCESS,
            text="Disconnect" if disconnected else "Connect",
            command=lambda: self.event_generate(const.Events.DISCONNECTED)
            if disconnected
            else self.on_connection_attempt(),
        )

    def enable_firmware_info(self) -> None:
        self.heading_frame.bind("<Button-1>", self.show_firmware)
        for child in self.heading_frame.children.values():
            child.bind("<Button-1>", self.show_firmware)
        self.heading_frame.bind("<Enter>", self.mark_heading_frame)
        self.heading_frame.bind("<Leave>", self.unmark_heading_frame)
        self.firmware_label.configure(text=self.root.sonicamp.info.firmware_info)

    def disable_firmware_info(self) -> None:
        self.heading_frame.unbind("<Button-1>")
        for child in self.heading_frame.children.values():
            child.unbind("<Button-1>")
        self.heading_frame.unbind("<Enter>")
        self.heading_frame.unbind("<Leave>")
        self.firmware_label.configure(text="")

    @async_handler
    async def on_connection_attempt(self) -> None:
        logger.debug("Connection attempt connectionframe...")
        self.change_heading(title_part1="Connecting", title_part2="", subtitle="")
        self.heading2_var.animate_dots()
        for child in self.port_frame.winfo_children():
            child.configure(state=ttk.DISABLED)
        self.connect_button.configure(
            text="Cancel",
            bootstyle=ttk.DANGER,
            command=lambda: self.event_generate(const.Events.DISCONNECTED),
        )
        self.update()
        self.root.on_connection_attempt()

    def on_connect(self, connection_data: Connectable.ConnectionData) -> None:
        self.heading2_var.stop_animation_of_dots()
        self.change_heading(
            title_part1=connection_data.heading1,
            title_part2=connection_data.heading2,
            subtitle=connection_data.subtitle,
        )
        self.change_button_to(disconnected=True)
        self.ports_menue.config(state=tk.DISABLED)
        self.refresh_button.config(state=tk.DISABLED)
        self.enable_firmware_info()

    def on_refresh(self) -> None:
        pass

    def on_disconnect(self, event) -> None:
        self.heading2_var.is_dot_animation_running = False
        self.change_heading(
            title_part1="not",
            title_part2="connected",
            subtitle="Please connect to a SonicAmp system",
        )
        self.firmware_label["text"] = ""
        self.change_button_to(connected=True)
        self.ports_menue["state"] = ttk.NORMAL
        self.refresh_button["state"] = ttk.NORMAL
        self.event_generate(const.Events.PORT_REFRESH)
        self.disable_firmware_info()

    def on_validation(self) -> None:
        self.change_heading(
            title_part1="Validating Firmware File", title_part2="", subtitle=""
        )
        self.heading2.animate_dots()

    def on_firmware_upload(self) -> None:
        self.change_heading(
            title_part1="Uploading Firmware",
            title_part2="",
            subtitle="This might take a while. Make sure the device stays on and connected.",
        )

    def on_validation_success(self) -> None:
        self.change_heading(
            title_part1="Validation successfull", title_part2="", subtitle=""
        )

    def publish(self) -> None:
        self.main_frame.pack(expand=True, fill=ttk.BOTH)
        self.heading_frame.pack(ipadx=10, ipady=10)
        self.control_frame.pack(padx=10, pady=10)
        self.refresh_button.grid(row=0, column=0, pady=5)
        self.ports_menue.grid(row=0, column=1, padx=5, pady=5, sticky=ttk.NSEW)
        self.firmware_label.pack(expand=True, fill=ttk.BOTH, padx=10, pady=10)
