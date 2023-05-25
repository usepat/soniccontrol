from __future__ import annotations

import subprocess
import os
import typing
import threading
import tkinter as tk
import tkinter.ttk as ttk
import ttkbootstrap as ttkb

from tkinter import filedialog
from tkinter import messagebox

from soniccontrol.helpers import ToolTip, logger
from sonicpackage import Command
import sonicpackage as sp

if typing.TYPE_CHECKING:
    from soniccontrol.core import Root
    from soniccontrol.notebook import ScNotebook


class ConnectionTab(ttk.Frame):
    @property
    def root(self) -> Root:
        return self._root

    def __init__(self, parent: ScNotebook, root: Root, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self._root: Root = root

        self.hex_file_path: tk.StringVar = tk.StringVar()
        # self.transducer_active: tk.StringVar = tk.StringVar()
        self.transducer_active = tk.StringVar()

        self.topframe: ttk.Frame = ttk.Frame(self, padding=(10, 10, 10, 10))
        self.botframe: ttk.Frame = ttk.Frame(self)

        self._initialize_topframe()
        self._initialize_botframe()

        logger.debug("Initialized Connectiontab")

    def _initialize_topframe(self) -> None:
        self._initialize_heading()
        self._initialize_control_frame()

        self.flash_progressbar: ttk.Progressbar = ttk.Progressbar(
            self.topframe,
            mode="indeterminate",
            orient=tk.HORIZONTAL,
        )

    def _initialize_botframe(self) -> None:
        self._initialize_firmware_info()
        self._initialize_transducer_menue()

        self.serial_monitor_btn: ttk.Button = ttk.Button(
            self.botframe,
            text="Serial Monitor",
            style="secondary.TButton",
            width=12,
            state=tk.DISABLED,
            command=self.root.publish_serial_monitor,
        )

    def _initialize_heading(self) -> None:
        self.heading_frame: ttk.Frame = ttk.Frame(self.topframe)
        self.subtitle: ttk.Label = ttk.Label(self.heading_frame, padding=(0, 10, 0, 0))
        self.heading1: ttk.Label = ttk.Label(
            self.heading_frame,
            padding=(10, 0, 2, 10),
            font=self.root.qtype30,
            borderwidth=-2,
        )
        self.heading2: ttk.Label = ttk.Label(
            self.heading_frame,
            padding=(2, 0, 0, 10),
            font=self.root.qtype30b,
            borderwidth=-2,
        )

    def _initialize_control_frame(self) -> None:
        self.control_frame: ttk.Frame = ttk.Frame(self.topframe)
        self.connect_button: ttk.Button = ttkb.Button(
            self.control_frame, width=10, style="success.TButton"
        )
        self.ports_menue: ttk.Combobox = ttk.Combobox(
            master=self.control_frame,
            textvariable=self.root.port,
            width=7,
            style="dark.TCombobox",
            state=tk.READABLE,
        )
        ToolTip(
            self.ports_menue,
            text="Choose the serial communication address of you SonicAmp",
        )
        self.refresh_button: ttk.Button = ttkb.Button(
            self.control_frame,
            bootstyle="secondary-outline",
            image=self.root.REFRESH_IMG,
            command=self.refresh,
        )

    def _initialize_firmware_info(self) -> None:
        self.firmware_frame: ttk.Labelframe = ttk.Labelframe(
            self.botframe,
            text="Firmware",
        )
        self.firmware_label: ttk.Label = ttk.Label(
            self.firmware_frame, justify=tk.CENTER, style="dark.TLabel"
        )

    def _initialize_transducer_menue(self) -> None:
        if not self.root.config_file:
            return

        if self.root.config_file.modes:
            self.mode_frame: ttk.Frame = ttk.Frame(self.botframe)
            self.modes_menue: ttk.Combobox = ttk.Combobox(
                master=self.mode_frame,
                textvariable=self.root.current_mode,
                width=20,
                style="dark.TCombobox",
                state=tk.READABLE,
            )
            self.mode_button: ttk.Button = ttkb.Button(
                self.mode_frame,
                bootstyle="secondary-outline",
                command=self.set_mode,
                text="Set Mode",
            )
        if not self.root.config_file.transducer:
            return

        self.transducer_frame: ttk.Frame = ttk.Frame(self.botframe)
        self.transducer_menuebutton: ttkb.Menubutton = ttkb.Menubutton(
            self.transducer_frame,
            compound=tk.CENTER,
            style=ttkb.DARK,
            text="Pick Transducer",
            state=tk.DISABLED,
        )
        self._update_transducer_menue()
        self.transducer_preview: ttk.LabelFrame = ttk.LabelFrame(
            self.botframe,
            text="Currently configured transducer",
            style="secondary.TLabelframe",
            padding=(5, 5, 5, 5),
        )
        self.transducer_preview_label: ttk.Label = ttk.Label(
            self.transducer_preview, text=""
        )

    def set_mode(self) -> None:
        logger.info(
            f"Setting mode {self.root.custom_modes.get(self.root.current_mode.get())}"
        )
        self.root.sonicamp.set_mode(
            self.root.custom_modes.get(self.root.current_mode.get())
        )

    def set_atf(self) -> str:
        def configure_trd():
            logger.debug(f"Configuring transducer {self.transducer_active.get()}")
            current_transducer: dict = self.root.config_file.transducer.get(
                self.transducer_active.get()
            )
            self.root.sonicamp.set_threshold_freq(
                current_transducer.get("threshold_freq")
            )
            self.root.serial.send_and_get(
                Command.SET_PROT_FREQ1 + current_transducer.get("atf1")
            )
            self.root.serial.send_and_get(
                Command.SET_PROT_FREQ2 + current_transducer.get("atf2")
            )
            self.root.serial.send_and_get(
                Command.SET_PROT_FREQ3 + current_transducer.get("atf3")
            )
            logger.debug("sending att and atk commands")
            self.root.serial.send_and_get(
                Command.SET_ATT1 + current_transducer.get("att1")
            )
            self.root.serial.send_and_get(
                Command.SET_ATT2 + current_transducer.get("att2")
            )
            self.root.serial.send_and_get(
                Command.SET_ATK1 + current_transducer.get("atk1")
            )
            self.root.serial.send_and_get(
                Command.SET_ATK2 + current_transducer.get("atk2")
            )
            self.root.serial.send_and_get(
                Command.SET_ATK3 + current_transducer.get("atk3")
            )

            if self.root.config_file.transducer.get("commands"):
                for command in self.root.config_file.transducer.get("commands"):
                    self.root.serial.send_and_get(command)

            self.transducer_preview_label["text"] = self.config_file_str()

        threading.Thread(target=configure_trd, daemon=False).start()

    def config_file_str(self) -> str:
        transducer_data: dict = self.root.config_file.transducer.get(
            self.transducer_active.get()
        )
        logger.debug(f"Looking for data for transducer {transducer_data}")
        if not transducer_data:
            return

        string: str = ""
        for item in transducer_data:
            if (
                item == "atf1"
                or item == "atf2"
                or item == "atf3"
                or item == "threshold_freq"
            ):
                continue
            string += (
                item
                + ":\t"
                + str(
                    self.root.config_file.transducer[self.transducer_active.get()][item]
                )
                + "\n"
            )
        return string

    def _update_transducer_menue(self) -> None:
        if not self.root.config_file:
            return

        if self.root.config_file.modes:
            self.modes_menue.config(
                values=list(self.root.custom_modes.keys()),
            )

        if not self.root.config_file.transducer:
            return
        transducer_menue: tk.Menu = tk.Menu(self.transducer_menuebutton, tearoff=0)

        for trd in self.root.config_file.transducer.keys():
            logger.info(f"Adding transducer value {trd}")
            transducer_menue.add_radiobutton(
                label=trd,
                value=trd,
                variable=self.transducer_active,
                command=self.set_atf,
            )
        self.transducer_menuebutton["menu"] = transducer_menue

    def attach_data(self, rescue: bool = False) -> None:
        self._update_transducer_menue()

        if self.flash_progressbar.winfo_exists():
            self.flash_progressbar.stop()
            self.flash_progressbar.pack_forget()

        for child in self.control_frame.winfo_children():
            child.config(state=tk.NORMAL)

        if rescue:
            self.subtitle["text"] = "Rescue serial monitor connection"
            self.heading1["text"] = "Serial"
            self.heading2["text"] = "Monitor"
        else:
            self.subtitle["text"] = "You are connected to"
            self.heading1["text"] = self.root.sonicamp.type_[:5]
            self.heading2["text"] = self.root.sonicamp.type_[5:]

            fwmsg: Union[str, list] = self.root.sonicamp.firmware_msg
            self.firmware_label["text"] = fwmsg

        self.connect_button.config(
            bootstyle="danger",
            text="Disconnect",
            command=self.disconnect,
        )

        self.ports_menue.config(state=tk.DISABLED)
        self.refresh_button.config(state=tk.DISABLED)
        self.serial_monitor_btn.config(state=tk.NORMAL)

        if not self.root.config_file:
            return
        if not self.root.config_file.transducer:
            return
        self.transducer_menuebutton.config(state=tk.NORMAL)
        self.transducer_preview_label["text"] = self.config_file_str()

    def flash_mode(self) -> None:
        self.subtitle["text"] = "Your device is currently updating"
        self.heading1["text"] = "updating"
        self.heading2["text"] = "device"

        self.flash_progressbar.pack()
        self.flash_progressbar.start()

        for child in self.control_frame.winfo_children():
            child.config(state=tk.DISABLED)

    def abolish_data(self) -> None:
        self.subtitle["text"] = "Please connect to a SonicAmp system"
        self.heading1["text"] = "not"
        self.heading2["text"] = "connected"

        self.connect_button.config(
            bootstyle="success",
            text="Connect",
            command=self.root.__reinit__,
        )

        self.ports_menue.config(
            textvariable=self.root.port,
            values=self.root.serial.device_list,
            state=tk.NORMAL,
        )

        self.serial_monitor_btn.config(state=tk.DISABLED)
        self.refresh_button.config(state=tk.NORMAL)
        self.firmware_label["text"] = ""

        if self.root.config_file and self.root.config_file.transducer:
            self.transducer_menuebutton.config(state=tk.DISABLED)
            self.transducer_menuebutton["text"] = "Pick Transducer"
            self.transducer_preview_label["text"] = ""

        self.root.abolish_data()

    def refresh(self) -> None:
        self.ports_menue["values"] = self.root.serial.get_ports()

    def disconnect(self) -> None:
        if not self.root.thread.paused.is_set():
            self.root.thread.pause()

        self.abolish_data()
        self.root.serial.disconnect()
        self.root.publish_disconnected()
        logger.info("Disconnecting device")

    def publish(self) -> None:
        for child in self.children.values():
            child.pack()

        self.subtitle.grid(row=0, column=0, columnspan=2, sticky=tk.S)
        self.heading1.grid(row=1, column=0, columnspan=1, sticky=tk.E)
        self.heading2.grid(row=1, column=1, columnspan=1, sticky=tk.W)
        self.heading_frame.pack(padx=10, pady=10, expand=True)

        self.ports_menue.grid(
            row=0, column=0, columnspan=2, pady=10, padx=5, sticky=tk.NSEW
        )
        self.connect_button.grid(
            row=0, column=2, columnspan=1, pady=10, padx=5, sticky=tk.NSEW
        )
        self.refresh_button.grid(
            row=0, column=3, columnspan=1, pady=10, padx=5, sticky=tk.NSEW
        )
        self.control_frame.pack(padx=10, pady=10, expand=True)

        self.firmware_label.pack()
        self.serial_monitor_btn.grid(row=1, column=0, padx=10, pady=10)

        if self.root.config_file and self.root.config_file.modes:
            self.modes_menue.grid(row=0, column=0, padx=10, pady=10)
            self.mode_button.grid(row=0, column=1, padx=10, pady=10)
            self.mode_frame.grid(row=1, column=1, padx=10, pady=10)

        if self.root.config_file and self.root.config_file.transducer:
            self.transducer_menuebutton.pack()
            self.transducer_frame.grid(row=1, column=1, padx=10, pady=10)
            self.transducer_preview.grid(
                row=2, column=0, columnspan=2, padx=10, pady=10, sticky=tk.NSEW
            )

            self.transducer_preview_label.pack()

        # if self.root.config_data["hexflash"]:
        #     self.file_entry.pack(padx=10, pady=10, side=tk.TOP)
        #     self.upload_button.pack(padx=10, pady=10, side=tk.TOP)
        #     self.flash_frame.grid(row=0, column=1, padx=10, pady=10)
        #     self.firmware_frame.grid(row=0, column=0, columnspan=1, padx=10, pady=10)
        self.firmware_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10)


if __name__ == "__main__":
    pass
