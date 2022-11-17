from __future__ import annotations

import subprocess
import os
import tkinter as tk
import tkinter.ttk as ttk
import ttkbootstrap as ttkb

from typing import Union, TYPE_CHECKING
from tkinter import filedialog
from tkinter import messagebox
# from ttkbootstrap.tooltip import ToolTip

from soniccontrol.helpers import ToolTip

if TYPE_CHECKING:
    from soniccontrol.core import Root
    from soniccontrol._notebook import ScNotebook


class ConnectionTab(ttk.Frame):
    
    @property
    def root(self) -> Root:
        return self._root
        
    def __init__(self, parent: ScNotebook, root: Root, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        
        self._root: Root = root
        
        self.hex_file_path: tk.StringVar = tk.StringVar()
        self.transducer_active: tk.StringVar = tk.StringVar()
        
        self.topframe: ttk.Frame = ttk.Frame(self, padding=(10, 10, 10, 10))
        self.botframe: ttk.Frame = ttk.Frame(self)
        
        self._initialize_topframe()
        self._initialize_botframe()
    
    def _initialize_topframe(self) -> None:
        self._initialize_heading()
        self._initialize_control_frame()
    
    def _initialize_botframe(self) -> None:
        self._initialize_firmware_info()
        self._initialize_flash_frame()
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
            padding=(10, 0, 0, 10),
            font=self.root.qtype30,
            borderwidth=-2,
        )

        self.heading2: ttk.Label = ttk.Label(
            self.heading_frame,
            padding=(0, 0, 5, 10),
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

    def _initialize_flash_frame(self) -> None:
        self.flash_frame = ttk.Labelframe(
            self.botframe,
            height=250,
            text="Update Firmware",
            width=200,
            padding=(0, 12, 0, 12),
        )

        self.file_entry = ttk.Button(
            self.flash_frame,
            text="Specify path for Firmware file",
            width=20,
            style="dark.TButton",
            command=self.hex_file_path_handler,
        )

        self.upload_button = ttk.Button(
            self.flash_frame,
            style="dark.TButton",
            width=20,
            text="Upload Firmware",
            command=self.upload_file,
        )
        
    def _initialize_transducer_menue(self) -> None:
        
        transducer_names: list = list(self.root.transducer.keys())
        
        self.transducer_frame: ttk.Frame = ttk.Frame(self.botframe)
        self.transducer_menuebutton: ttkb.Menubutton = ttkb.Menubutton(
            self.transducer_frame,
            compound=tk.CENTER,
            style=ttkb.DARK,
            text="Pick Transducer",
            state=tk.DISABLED,
        )
        
        transducer_menue: tk.Menu = tk.Menu(self.transducer_menuebutton, tearoff=0)
        
        for name in transducer_names:
            transducer_menue.add_radiobutton(
                label=name,
                value=name,
                variable=self.transducer_active,
                command=lambda: self.root.set_atf(self.transducer_active.get()),
            )

        self.transducer_menuebutton["menu"] = transducer_menue
        
        self.transducer_preview: ttk.LabelFrame = ttk.LabelFrame(
            self.botframe,
            text='Currently configured transducer',
            style='secondary.TLabelframe',
            padding=(5,5,5,5)
        )
        self.transducer_preview_label: ttk.Label = ttk.Label(
            self.transducer_preview,
            text=''
        )
        
    def config_file_str(self) -> str:
        string: str = ""
        
        for item in self.root.transducer[self.transducer_active.get()]:
            if not (item == "atf1" or  item == "atf2" or item == "atf3"):
                string += item + ":\t" + str(self.root.transducer[self.transducer_active.get()][item]) + "\n"
                print(string)
        
        return string
        
    def _update_transducer_menue(self) -> None:
        self.root.config_file_algorithm()

        transducer_names: list = list(self.root.transducer.keys())
        transducer_menue: tk.Menu = tk.Menu(self.transducer_menuebutton, tearoff=0)

        for name in transducer_names:
            transducer_menue.add_radiobutton(
                label=name,
                value=name,
                variable=self.transducer_active,
                command=lambda: self.root.set_atf(self.transducer_active.get()),
            )

        self.transducer_menuebutton["menu"] = transducer_menue


    def attach_data(self) -> None:
        """
        Attaches data to the connectiontab
        """
        self._update_transducer_menue()
        
        self.subtitle["text"] = "You are connected to"
        self.heading1["text"] = self.root.sonicamp.type_[:5]
        self.heading2["text"] = self.root.sonicamp.type_[5:]

        self.connect_button.config(
            bootstyle="danger",
            text="Disconnect",
            command=self.disconnect,
        )
        
        fwmsg: Union[str, list] = self.root.sonicamp.firmware_msg

        self.ports_menue.config(state=tk.DISABLED)
        self.refresh_button.config(state=tk.DISABLED)
        self.serial_monitor_btn.config(state=tk.NORMAL)
        self.transducer_menuebutton.config(state=tk.NORMAL)
        self.firmware_label["text"] = fwmsg

        for child in self.flash_frame.children.values():
            child.configure(state=tk.NORMAL)
            
    def abolish_data(self) -> None:
        """
        Abolishes data from the connectiontab
        """
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
        self.transducer_menuebutton.config(state=tk.DISABLED)
        self.refresh_button.config(state=tk.NORMAL)
        self.firmware_label["text"] = ""
        self.transducer_menuebutton['text'] = 'Pick Transducer'
        self.transducer_preview_label['text'] = ''

        for child in self.flash_frame.children.values():
            child.configure(state=tk.DISABLED)

        self.root.sonicamp = None
    
    def open_last_resort_connection(self) -> None:
        self.subtitle["text"] = "Rescue serial monitor connection"
        self.heading1["text"] = "Serial"
        self.heading2["text"] = "Monitor"
        self.serial_monitor_btn.config(
            state=tk.NORMAL
        )
        self.connect_button.config(
            bootstyle="danger",
            text="Disconnect",
            command=self.disconnect
        )
        
    def refresh(self) -> None:
        """
        Refreshes the potential ports
        """
        self.ports_menue["values"] = self.root.serial.get_ports()
        
    def disconnect(self) -> None:
        """
        Disconnects the soniccontrol with the current connection
        """
        if not self.root.thread.paused:
            self.root.thread.pause()

        self.abolish_data()
        self.root.serial.disconnect()
        self.root.publish_disconnected()
        
    def hex_file_path_handler(self):
        """Gets the file of a potential hex firmware file, and checks if it's even a hex file"""
        self.hex_file_path = filedialog.askopenfilename(
            defaultextension=".hex", filetypes=(("HEX File", "*.hex"),)
        )

        if self.hex_file_path[-4:] == ".hex":
            self.file_entry.config(
                style="success.TButton", text="File specified and validated"
            )

        else:
            messagebox.showerror(
                "Wrong File",
                'The specified file is not a validated firmware file. Please try again with a file that ends with the format ".hex"',
            )
            self.file_entry.config(
                style="danger.TButton", text="File is not a firmware file"
            )

    def upload_file(self):
        """Upploads the hex file to the hardware via AVRDUDE"""
        if self.root.serial.is_connected:

            if self.hex_file_path:
                port = self.root.serial.port
                self.root.serial.disconnect()
                cur_dir = os.getcwd()
                print(cur_dir)
                # self.firmware_progress_text.pack(padx=10, pady=10)

                try:
                    command = f'"{cur_dir}/avrdude/avrdude.exe" -v -patmega328p -carduino -P{port} -b115200 -D -Uflash:w:"{self.hex_file_path}":i'
                    msgbox = messagebox.showwarning(
                        "Process about to start",
                        "The program is about to flash a new firmware on your device, please do NOT disconnect or turn off your device during that process",
                    )

                    if msgbox:
                        subprocess.run(command, shell=True)
                        self.file_entry.configure(
                            style="dark.TButton",
                            text="Specify the path for the Firmware file",
                        )
                        # self.firmware_progress_text.pack_forget()
                        self.connectPort(port)
                    else:
                        messagebox.showerror("Error", "Cancled the update")

                except WindowsError:
                    messagebox.showerror(
                        "Error",
                        "Something went wrong, please try again. Maybe restart the device and the program",
                    )

            else:
                messagebox.showerror(
                    "Couldn't find file",
                    "Please specify the path to the firmware file, before flashing your SonicAmp",
                )
        else:
            messagebox.showerror(
                "Error",
                "No connection is established, please recheck all connections and try to reconnect in the Connection Tab. Make sure the instrument is in Serial Mode.",
            )
    
    def publish(self) -> None:
        """
        Method to publish the children of the Connection Tab
        and for that itself too
        """
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
        
        if len(self.root.transducer) > 1:
            self.transducer_menuebutton.pack()
            self.transducer_frame.grid(row=1, column=1, padx=10, pady=10)

            self.transducer_preview.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky=tk.NSEW)
            self.transducer_preview_label.pack()

        # if self.root.config_data["hexflash"]:
        #     self.file_entry.pack(padx=10, pady=10, side=tk.TOP)
        #     self.upload_button.pack(padx=10, pady=10, side=tk.TOP)
        #     self.flash_frame.grid(row=0, column=1, padx=10, pady=10)
        #     self.firmware_frame.grid(row=0, column=0, columnspan=1, padx=10, pady=10) 
        
        self.firmware_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
            
