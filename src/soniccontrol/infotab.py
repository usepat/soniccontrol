from __future__ import annotations

import subprocess
import os
import tkinter as tk
import tkinter.ttk as ttk

from typing import TYPE_CHECKING
from tkinter import filedialog
from tkinter import messagebox

from sonicpackage import SerialConnection

import soniccontrol.constants as const
from soniccontrol.helpers import logger

if TYPE_CHECKING:
    from soniccontrol.core import Root
    from soniccontrol.notebook import ScNotebook


class InfoTab(ttk.Frame):
    """
    The InfoTab is the part of the ScNotebook and has the corresping
    information about the SonicControl. Not only does it provide the
    version of the application. It can be used for opening the help
    manual.

    Inheritance:
        ttk (tkinter.ttk.Frame): the basic Frame object
    """

    INFOTEXT = (
        "Welcome to soniccontrol, a light-weight application to\n"
        "control sonicamp systems over the serial interface. \n"
        'For help, click the "Manual" button below\n'
        "\n"
        "(c) usePAT G.m.b.H\n"
    )

    @property
    def root(self) -> Root:
        return self._root

    def __init__(self, parent: ScNotebook, root: Root, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self._root: Root = root

        self.soniccontrol_logo_frame: ttk.Frame = ttk.Frame(self)

        self.soniccontrol_logo1: ttk.Label = ttk.Label(
            self.soniccontrol_logo_frame,
            text="sonic",
            padding=(10, 0, 0, 10),
            font="QTypeOT-CondLight 30",
            borderwidth=-2,
        )

        self.soniccontrol_logo2: ttk.Label = ttk.Label(
            self.soniccontrol_logo_frame,
            text="control",
            padding=(0, 0, 0, 10),
            font="QTypeOT-CondBook 30 bold",
            borderwidth=-2,
        )

        self.info_label: ttk.Label = ttk.Label(self, text=InfoTab.INFOTEXT)
        self.controlframe: ttk.Frame = ttk.Frame(self)
        self.manual_btn: ttk.Button = ttk.Button(
            self.controlframe, text="Help Manual", command=self.open_manual
        )
        self.flash_button: ttk.Button = ttk.Button(
            self.controlframe, text="Update Firmware", command=lambda: HexFlashWindow(self.root)
        )
        self.version_label: ttk.Label = ttk.Label(
            self,
            text=f"Version: {const.VERSION}",
        )

        logger.debug("Initialized infotab")

    def publish(self) -> None:
        """
        Publishes the object and children
        """
        self.soniccontrol_logo1.grid(row=0, column=0)
        self.soniccontrol_logo2.grid(row=0, column=1)
        self.soniccontrol_logo_frame.pack(padx=20, pady=20)
        self.info_label.pack()
        self.manual_btn.grid(row=0, column=0, padx=5, pady=10)
        
        if self.root.config_file and self.root.config_file.hexflash:
            self.flash_button.grid(row=0, column=2, padx=5, pady=10)
        
        self.controlframe.pack()
        self.version_label.pack(anchor=tk.S, side=tk.BOTTOM, padx=10, pady=10)

    @staticmethod
    def open_manual() -> None:
        """
        Opens the helppage manual with the default pdf viewer
        """
        path: str = r'src\\soniccontrol\\resources\\help_page.pdf'
        subprocess.Popen([path], shell=True)

    def attach_data(self) -> None:
        pass
    

# TODO: Hexflash is not that supported, ISSUE 
class HexFlashWindow(tk.Toplevel):
    
    def __init__(self, root: Root, *args, **kwargs):
        super().__init__(master=root, *args, **kwargs)
        
        self.root: Root = root
        self.serial: SerialConnection = root.serial
        
        self.flash_frame = ttk.Labelframe(
            self,
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
        
        for child in self.winfo_children():
            child.pack(expand=True, fill=tk.BOTH, padx=10, pady=10, anchor=tk.CENTER)
            
            for grandchild in child.winfo_children():
                grandchild.pack(expand=True, fill=tk.BOTH, padx=10, pady=10, anchor=tk.CENTER)
        
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
            
    def upload_file(self) -> None:
        
        if self.serial.is_connected:
            
            if self.hex_file_path:
                port: str = self.serial.port
                current_dir: str = os.getcwd()
                
                self.root.notebook.connectiontab.disconnect()
                
                try:
                    command = f'"{current_dir}/src/avrdude/avrdude.exe" -v -patmega328p -carduino -P{port} -b115200 -D -Uflash:w:"{self.hex_file_path}":i'
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
                        
                        self.root.port.set(port)
                        self.root.__reinit__()
                        
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
                
            

    
if __name__ == "__main__":
    InfoTab.open_manual()