from __future__ import annotations

import subprocess
import os
import platform
import threading
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
            padding=(10, 0, 2, 10),
            font="QTypeOT-CondLight 30",
            borderwidth=-2,
        )

        self.soniccontrol_logo2: ttk.Label = ttk.Label(
            self.soniccontrol_logo_frame,
            text="control",
            padding=(2, 0, 0, 10),
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

        self._initialize_flash_frame()
        logger.debug("Initialized infotab")

    def _initialize_flash_frame(self) -> None:
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
            width=23,
            style="dark.TButton",
            command=self.hex_file_path_handler,
        )

        self.upload_button = ttk.Button(
            self.flash_frame,
            style="dark.TButton",
            width=23,
            text="Upload Firmware",
            state=tk.DISABLED,
            command=self.upload_file,
        )

    def publish(self) -> None:
        """
        Publishes the object and children
        """
        self.soniccontrol_logo1.grid(row=0, column=0)
        self.soniccontrol_logo2.grid(row=0, column=1)
        self.soniccontrol_logo_frame.pack(padx=20, pady=20)
        self.info_label.pack()
        self.manual_btn.grid(row=0, column=0, padx=5, pady=10)

        self.file_entry.pack(pady=10, padx=10)
        self.upload_button.pack(pady=10, padx=10)

        self.controlframe.pack()
        self.version_label.pack(anchor=tk.S, side=tk.BOTTOM, padx=10, pady=10)

        if not (self.root.config_file and self.root.config_file.hexflash):
            return

        self.flash_frame.pack()

    @staticmethod
    def open_manual() -> None:
        """
        Opens the helppage manual with the default pdf viewer
        """
        path: str = r'src\\soniccontrol\\resources\\help_page.pdf'
        subprocess.Popen([path], shell=True)

    def hex_file_path_handler(self):
        """Gets the file of a potential hex firmware file, and checks if it's even a hex file"""
        self.hex_file_path = filedialog.askopenfilename(defaultextension=".hex", filetypes=(("HEX File", "*.hex"),))
        if not self.hex_file_path: return

        self.file_entry.config(style="success.TButton", text="File specified and validated")
        self.upload_button.config(state=tk.NORMAL)

    def upload_file(self) -> None:
        self.root.notebook.connectiontab.flash_progressbar.start()
        thread = threading.Thread(target=self._upload_file)
        thread.start()
            
    def _upload_file(self) -> None:
        if not self.root.serial.is_connected:
            messagebox.showerror("Connection Error", "It appears, that your device is not connected. Please connect the device")
            return
        
        if not self.hex_file_path:
            messagebox.showerror("Filepath Error", "The file you have given is not valid, please try again")
            return

    
        port: str = self.root.serial.port        
        self.root.notebook.connectiontab.disconnect()
        
        try:
            if platform.system() == "Linux":
                command = f'"avrdude/Linux/avrdude" -v -p atmega328p -c arduino -P {port} -b 115200 -D -U flash:w:"{self.hex_file_path}":i'
            
            elif platform.system() == "Windows":
                command = f'"avrdude/Windows/avrdude.exe" -v -p atmega328p -c arduino -P {port} -b 115200 -D -U flash:w:"{self.hex_file_path}":i'
            
            else: 
                messagebox.showerror("Platform not supported", "Your system is not supported for this operation")
                self.connect_after_hexflash(port)
                return

            msgbox = messagebox.showwarning(
                "Process about to start",
                "The program is about to flash a new firmware on your device, please do NOT disconnect or turn off your device during that process",
            )
            
            if not msgbox:
                messagebox.showerror("Error", "Cancled the update")
                self.connect_after_hexflash(port)
                return
            
            self.root.notebook.connectiontab.flash_mode()

            subprocess.run(command, shell=True)
            self.file_entry.configure(
                style="dark.TButton",
                text="Specify the path for the Firmware file",
            )
            
            self.connect_after_hexflash(port)
                    
        except WindowsError:
            messagebox.showerror(
                "Error",
                "Something went wrong, please try again. Maybe restart the device and the program",
            )

    def connect_after_hexflash(self, port: str) -> None:
        self.root.port.set(port)
        self.root.__reinit__()

    def attach_data(self) -> None:
        if not (self.root.config_file and self.root.config_file.hexflash):
            return
        
        self.flash_frame.pack()
    

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
            state=tk.DISABLED,
            command=self.upload_file,
        )
        
        for child in self.winfo_children():
            child.pack(expand=True, fill=tk.BOTH, padx=10, pady=10, anchor=tk.CENTER)
            
            for grandchild in child.winfo_children():
                grandchild.pack(expand=True, fill=tk.BOTH, padx=10, pady=10, anchor=tk.CENTER)
        
    def hex_file_path_handler(self):
        """Gets the file of a potential hex firmware file, and checks if it's even a hex file"""
        self.hex_file_path = filedialog.askopenfilename(defaultextension=".hex", filetypes=(("HEX File", "*.hex"),))
        if not self.hex_file_path: return

        self.file_entry.config(style="success.TButton", text="File specified and validated")
        self.upload_button.config(state=tk.NORMAL)

            
    def upload_file(self) -> None:
        if not self.serial.is_connected:
            messagebox.showerror("Connection Error", "It appears, that your device is not connected. Please connect the device")
            return
        
        if not self.hex_file_path:
            messagebox.showerror("Filepath Error", "The file you have given is not valid, please try again")
            return

    
        port: str = self.serial.port        
        self.root.notebook.connectiontab.disconnect()
        
        try:
            print(platform.system())
            if platform.system() == "Linux":
                command = f'"avrdude/Linux/avrdude" -v -p atmega328p -c arduino -P {port} -b 115200 -D -U flash:w:"{self.hex_file_path}":i'
            elif platform.system() == "Windows":
                command = f'"avrdude/Windows/avrdude.exe" -v -p atmega328p -c arduino -P {port} -b 115200 -D -U flash:w:"{self.hex_file_path}":i'
            
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
                
                self.root.port.set(port)
                self.root.__reinit__()
                
            else:
                messagebox.showerror("Error", "Cancled the update")
        except WindowsError:
            messagebox.showerror(
                "Error",
                "Something went wrong, please try again. Maybe restart the device and the program",
            )
                
            

    
if __name__ == "__main__":
    InfoTab.open_manual()