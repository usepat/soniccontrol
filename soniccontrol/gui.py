import datetime
import enum
from functools import cache
import logging
import re
import tkinter as tk
from tkinter import filedialog, messagebox
import tkinter.ttk as ttk
from matplotlib import style
from matplotlib.figure import Figure
from  matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import ttkbootstrap as ttkb
from ttkbootstrap.tooltip import ToolTip
from typing import Union
from abc import ABC, abstractmethod
import time
import csv
import subprocess
import os
from sonicpackage import Command, SerialConnection, Status, SonicCatch#, SonicCatchOld
from sonicpackage.amp_tools import serial
from .helpers import logger, status_logger



class ScriptCommand(enum.Enum):
    
    SET_FRQ: str = "frequency XXXXXXXX\n"
    SET_GAIN: str = "gain XXX\n"
    SET_KHZ: str = "setkHz\n"
    SET_MHZ: str = "setMHz\n"
    SET_SIGNAL_ON: str = "on\n"
    SET_SIGNAL_OFF: str = "off\n"
    SET_AUTO: str = "autotune\n"
    SET_HOLD: str = "hold X\n"
    STARTLOOP: str = "startloop X\n"
    ENDLOOP: str = "endloop\n"
    SET_RAMP: str = "ramp XXXXXXX,XXXXXXX,XXXX,XX\n"
    # SET_WIPE: str = ""
    # SET_PROT: str = ""
    # SET_PROT_RANGE: str = ""
    # SET_PROT_STEP: str =""
    # SET_PROT_TIME_ON: str =""
    # SET_PROT_TIME_OFF: str =""
    # SET_PROT_FRQ1: str = ""
    # SET_PROT_FRQ2: str = ""
    # SET_PROT_FRQ3: str = ""
    # SET_TUNING_STEP: str = ""
    # SET_TUNING_PAUSE: str = ""
    # SET_SCANNING_STEP: str = ""
    # SET_FLOW: str = ""
    # SET_CURRENT1: str = ""
    # SET_CURRENT2: str = ""
    # SET_SERIAL: str = ""



class HomeTabCatch(ttk.Frame):
    
    @property
    def root(self) -> tk.Tk:
        return self._root
    
    def __init__(self, parent: ttk.Notebook, root: tk.Tk, name: str, *args, **kwargs) -> None:
        """
        The Hometab is a child tab of the Notebook menu and is resonsible
        for handling and updating its children
        
        The frame is, again, splittet up into two main frames that organize
        its children
        
        """
        super().__init__(parent, name=name, *args, **kwargs)
        self._root: tk.Tk = root
        
        self.config(height=200, width=200)
        
        # Here follows the code regarding the TOPFRAME
        self.topframe: ttk.Labelframe = ttk.Labelframe(self, text="Manual control")
        self.control_frame: ttk.Frame = ttk.Frame(self.topframe)
        
        # Frq frame
        self.frq_frame: ttk.Label = ttk.Label(self.control_frame)
        self.frq_spinbox: ttk.Spinbox = ttk.Spinbox(
            self.frq_frame,
            from_=600000,
            increment=100,
            to=6000000,
            textvariable=self.root.frq, 
            width=16,
            style='dark.TSpinbox',
            command=self.set_frq)
        ToolTip(self.frq_spinbox, text="Configure the frequency of your device")
        
        self.scroll_digit: ttk.Spinbox = ttk.Spinbox(
            self.frq_frame,
            from_=1,
            increment=1,
            to=6,
            validate=None,
            width=5,
            style='secondary.TSpinbox',
            command=self.set_scrolldigit)
        ToolTip(self.scroll_digit, text="Set the digit you want to scroll in the Frequency field")
        
        # Gain Frame
        self.gain_frame: ttk.Frame = ttk.Frame(self.control_frame)
        self.gain_spinbox: ttk.Spinbox = ttk.Spinbox(
            self.gain_frame,
            from_=0,
            increment=10,
            to=150,
            textvariable=self.root.gain,
            width=5,
            style='dark.TSpinbox',
            command=self.set_gain)
        ToolTip(self.gain_frame, text="Configure the gain for your device")
        
        self.gain_scale: ttk.Scale = ttk.Scale(
            self.gain_frame,
            from_=0,
            to=150,
            name='gainscale',
            length=180,
            orient=tk.HORIZONTAL,
            style="primary.TScale",
            variable=self.root.gain,)
            #command=lambda: self.root.serial.sc_sendget(Command.SET_GAIN + int(self.root.gain.get()), self.root.thread))
        
        # kHz MHz Frame
        self.frq_rng_frame: ttk.Label = ttk.Label(self.control_frame)
        self.khz_button: ttkb.Radiobutton = ttkb.Radiobutton(
            self.frq_rng_frame,
            text='KHz',
            value='khz',
            variable=self.root.frq_range,
            bootstyle='dark-outline-toolbutton',
            width=12,
            command=lambda: self.insert_feed(self.root.serial.sc_sendget(Command.SET_KHZ, self.root.thread)))
        
        self.mhz_button: ttkb.Radiobutton = ttkb.Radiobutton(
            self.frq_rng_frame,
            text='MHz',
            value='mhz',
            variable=self.root.frq_range,
            bootstyle='dark-outline-toolbutton',
            width=12,
            command=lambda: self.insert_feed(self.root.serial.sc_sendget(Command.SET_MHZ, self.root.thread))) 
        
        # Other children of the control frame
        self.set_val_btn: ttk.Button = ttk.Button(
            self.control_frame,
            text='Set Frequency and Gain',
            command=self.set_val,
            bootstyle='dark.TButton',)
        
        self.sonic_measure_frame: ttk.Frame = ttk.Frame(self.topframe)
        self.sonic_measure_button: ttk.Button = ttk.Button(
            self.sonic_measure_frame,
            text='Sonic measure',
            style='dark.TButton',
            image=self.root.graph_img,
            compound=tk.TOP,
            command=self.publish_sonicmeasure)
        
        self.serial_monitor_btn: ttk.Button = ttk.Button(
            self.sonic_measure_frame,
            text='Serial Monitor',
            style='secondary.TButton',
            width=12,
            command=self.root.publish_serial_monitor,)
        
        self.us_control_frame: ttk.Frame = ttk.Frame(self)
        self.us_on_button: ttk.Button = ttk.Button(
            self.us_control_frame,
            text='ON',
            style='success.TButton',
            width=10,
            command=lambda: self.insert_feed(self.root.serial.sc_sendget(Command.SET_SIGNAL_ON, self.root.thread)))
        ToolTip(self.us_on_button, text="Turn the ultrasound signal on")
        
        self.us_off_button: object = ttk.Button(
            self.us_control_frame,
            text='OFF',
            style='danger.TButton',
            width=10,
            command=lambda: self.insert_feed(self.root.serial.sc_sendget(Command.SET_SIGNAL_OFF, self.root.thread)))
        ToolTip(self.us_off_button, text="Turn the ultrasound signal off")
        
        self.botframe: ttk.Frame = ttk.Frame(self)
        
        # Feedback Frame
        self.output_frame: ttk.Frame = ttk.LabelFrame(self.botframe, text='Feedback')
        container: ttk.Frame = ttk.Frame(self.output_frame)
        self.canvas: tk.Canvas = tk.Canvas(container)
        scrollbar: ttk.Scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollable_frame: ttk.Frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda x: self.canvas.configure(scrollregion=self.canvas.bbox(tk.ALL)))
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor=tk.NW)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        container.pack(anchor=tk.N, expand=True, fill=tk.BOTH, padx=5, pady=5, side=tk.TOP)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        logger.info("HometabCatch\tInitialized")
        
    def insert_feed(self, text: Union[str, list]) -> None:
        """Function that inserts a string or a list into the feedback frame

        Args:
            text (Union[str, list]): The text, that should be inserted
        """
        if text is list:
            text = ' '.join(text)
        
        ttk.Label(self.scrollable_frame, text=text, font=("Consolas", 10)).pack(fill=tk.X, side=tk.TOP, anchor=tk.W)
        self.canvas.update()
        self.canvas.yview_moveto(1)
        
    def set_val(self) -> None:
        """Function that will be called after pressing the <Set Frequency and Gain> Button
        It firstly checks if the values are supported under the current relay setting
        """
        frq: int = self.root.frq.get()
        gain: int = self.root.gain.get()
        
        logger.info(f"HometabCatch\tsetting frequency and gain\t{frq = }\t{gain = }")
        
        if self.check_range(frq):
            self.insert_feed(self.root.serial.sc_sendget(Command.SET_GAIN + gain, self.root.thread))
            self.insert_feed(self.root.serial.sc_sendget(Command.SET_FRQ + frq, self.root.thread))
        
        else:
            messagebox.showwarning("Wrong Frequency Value", "This frequency cannot be setted under the current frequency range mode. Please use the spinbox once again")

    def set_frq(self) -> None:
        """Sets the frequency"""
        frq: int = self.root.frq.get()
        
        if self.check_range(frq):
            self.root.serial.sc_sendget(Command.SET_FRQ + frq, self.root.thread)
        
        else:
            messagebox.showwarning("Wrong Frequency Value", "This frequency cannot be setted under the current frequency range mode. Please use the spinbox once again")
    
    def set_gain(self) -> None:
        self.insert_feed(self.root.serial.sc_sendget(Command.SET_GAIN + int(self.root.gain.get()), self.root.thread))
    
    def check_range(self, frq: int) -> bool:
        """Checks the current setting of the relay on the sonicamp and 
        returns true if the passed frequency is being supported under the
        current relay setting.

        Args:
            frq (int): The to be checked frequency

        Returns:
            bool: Result if that frequency is possible to set or not
        """
        if self.root.frq_range.get() == "khz" and (frq > 1200000 or frq < 50000):
            return False
        
        elif self.root.frq_range.get() == "mhz" and frq < 60000:
            return False
        
        return True
    
    def attach_data(self) -> None:
        """Attaches new data to the hometab"""
        logger.info("HometabCatch\tAttaching data")
        
        if self.root.frq_range.get() == "khz":
            self.frq_spinbox.config(
                from_=50000,
                to=1200000,)
            self.gain_scale.config(state=tk.DISABLED)
            self.gain_spinbox.config(state=tk.DISABLED)
        
        else:
            self.frq_spinbox.config(
                from_=600000,
                to=6000000,)
            self.gain_scale.config(state=tk.NORMAL)
            self.gain_spinbox.config(state=tk.NORMAL)
            
    def publish_sonicmeasure(self) -> None:
        self.sonicmeasure: SonicMeasure = SonicMeasure(self.root)
        
    def publish(self) -> None:
        """ Function to build children of this frame """
        logger.info("Publishing hometab")
        self.frq_spinbox.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.scroll_digit.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)
        
        self.gain_spinbox.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.gain_scale.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)
        
        self.khz_button.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.mhz_button.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)
        
        self.frq_frame.pack(side=tk.TOP, expand=True, fill=tk.X)
        self.gain_frame.pack(side=tk.TOP, expand=True, fill=tk.X)
        self.frq_rng_frame.pack(side=tk.TOP, expand=True, fill=tk.X)
        self.set_val_btn.pack(side=tk.TOP, expand=True, fill=tk.X, padx=10, pady=10)
        self.sonic_measure_button.pack(side=tk.TOP, padx=10, pady=10)
        self.serial_monitor_btn.pack(side=tk.TOP, padx=10, pady=5, expand=True, fill=tk.BOTH)
        
        self.control_frame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.sonic_measure_frame.grid(row=0, column=1, padx=20, pady=20, sticky=tk.NSEW)

        self.us_on_button.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.us_off_button.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)

        self.topframe.pack(side=tk.TOP, padx=10, pady=10)
        
        self.us_control_frame.pack(side=tk.TOP, padx=10, pady=10)

        self.output_frame.pack(anchor=tk.N, side=tk.TOP, padx=10, pady=10, expand=True, fill=tk.BOTH)
        self.botframe.pack(side=tk.TOP)        
            
    def set_scrolldigit(self) -> None:
        """ Function regarding the scroll digit combobox """
        self.frq_spinbox.config(
            increment = str(10 ** (int(self.scroll_digit.get())-1)))




class HomeTabWipe(ttk.Frame):
    
    @property
    def root(self) -> tk.Tk:
        return self._root
    
    def __init__(self, parent: ttk.Notebook, root: tk.Tk, name: str, *args, **kwargs) -> None:
        """
        The Hometab is a child tab of the Notebook menu and is resonsible
        for handling and updating its children
        
        The frame is, again, splittet up into two main frames that organize
        its children
        """
        super().__init__(parent, name=name, *args, **kwargs)
        self._root: tk.Tk = root
        
        self.config(height=200, width=200)
        
        self.wipe_var: tk.IntVar = tk.IntVar(value=5)
        self.wipe_mode: tk.BooleanVar = tk.BooleanVar(value=True)
        
        # Here follows the code regarding the TOPFRAME
        self.topframe: ttk.Frame = ttk.Frame(self)
        self.frq_control_frame: ttk.LabelFrame = ttk.LabelFrame(self.topframe, text='Set up frequency') 
        
        # Frq frame
        self.frq_frame: ttk.Label = ttk.Label(self.frq_control_frame)
        self.frq_spinbox: ttk.Spinbox = ttk.Spinbox(
            self.frq_frame,
            from_=50000,
            increment=100,
            to=1200000,
            textvariable=self.root.frq, 
            width=8,
            style='dark.TSpinbox',
            command=self.set_frq)
        ToolTip(self.frq_spinbox, text="Configure the frequency of your device")
        
        self.scroll_digit: ttk.Spinbox = ttk.Spinbox(
            self.frq_frame,
            from_=1,
            increment=1,
            to=6,
            validate=None,
            width=5,
            style='secondary.TSpinbox',
            command=self.set_scrolldigit)
        ToolTip(self.scroll_digit, text="Set the digit you want to scroll in the frequency field")
        
        self.set_val_btn: ttk.Button = ttk.Button(
            self.frq_control_frame,
            text='Set Frequency',
            bootstyle='dark.TButton',
            command=lambda: self.insert_feed(self.root.serial.sc_sendget(Command.SET_FRQ + self.root.frq.get(), self.root.thread)))
        
        self.us_on_button: ttk.Button = ttk.Button(
            self.frq_control_frame,
            text='ON',
            style='success.TButton',
            width=10,
            command=lambda: self.insert_feed(self.root.serial.sc_sendget(Command.SET_SIGNAL_ON, self.root.thread)))
        ToolTip(self.us_on_button, text="Turn the ultrasound signal on")
        
        self.wipe_frame: ttk.LabelFrame = ttk.LabelFrame(self.topframe, text='Set up wiping')
        self.wipe_spinbox: ttk.Spinbox = ttk.Spinbox(
            self.wipe_frame,
            from_=1,
            increment=5,
            to=100,
            textvariable=self.wipe_var, 
            width=16,
            style='dark.TSpinbox',)
        ToolTip(self.wipe_spinbox, text="Set up wipe cycles")
        
        self.wipe_mode_frame: ttk.Label = ttk.Label(self.wipe_frame)
        self.def_wipe_button: ttkb.Radiobutton = ttkb.Radiobutton(
            self.wipe_mode_frame,
            text='Definite',
            value=True,
            variable=self.wipe_mode,
            bootstyle='dark-outline-toolbutton',
            width=6,
            command=self.handle_wipe_mode)
        
        self.inf_wipe_button: ttkb.Radiobutton = ttkb.Radiobutton(
            self.wipe_mode_frame,
            text='Infinite',
            value=False,
            variable=self.wipe_mode,
            bootstyle='dark-outline-toolbutton',
            width=6,
            command=self.handle_wipe_mode)
        
        # self.protocol_menu: ttk.Button = ttk.Button(
        #     self.wipe_frame)
        self.start_wipe_button: ttk.Button = ttk.Button(
            self.wipe_frame,
            text='WIPE',
            style='primary.TButton',
            command=self.start_wiping)
        
        self.us_off_button: object = ttk.Button(
            self.topframe,
            text='OFF',
            style='danger.TButton',
            width=10,
            command=self.set_signal_off)
        ToolTip(self.us_on_button, text="Turn the ultrasound signal off")
        
        self.botframe: ttk.Frame = ttk.Frame(self)
        
        # Feedback Frame
        self.output_frame: ttk.Frame = ttk.LabelFrame(self.botframe, text='Feedback')
        container: ttk.Frame = ttk.Frame(self.output_frame)
        self.canvas: tk.Canvas = tk.Canvas(container)
        scrollbar: ttk.Scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollable_frame: ttk.Frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda x: self.canvas.configure(scrollregion=self.canvas.bbox(tk.ALL)))
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor=tk.NW)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        container.pack(anchor=tk.N, expand=True, fill=tk.BOTH, padx=5, pady=5, side=tk.TOP)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        logger.info("HometabWipe\tinitialized")
        
    def insert_feed(self, text: Union[str, list]) -> None:
        """Function that inserts a list or a string into the feedback frame

        Args:
            text (Union[str, list]): Data that should be inserted
        """
        if text is list:
            text = ' '.join(text)
        
        ttk.Label(self.scrollable_frame, text=text, font=("Consolas", 10)).pack(fill=tk.X, side=tk.TOP, anchor=tk.W)
        self.canvas.update()
        self.canvas.yview_moveto(1)
        
    def set_frq(self) -> None:
        """Sets the frequency of the sonicamp"""
        self.root.serial.sc_sendget(Command.SET_FRQ + self.root.frq.get(), self.root.thread)
    
    def set_signal_off(self) -> None:
        self.root.wipe_mode.set(0)
        self.root.status_frame_wipe.wipe_progressbar.stop()
        self.insert_feed(self.root.serial.sc_sendget(Command.SET_SIGNAL_OFF, self.root.thread))
    
    def handle_wipe_mode(self) -> None:
        # In case its set to definite
        if self.wipe_mode.get():
            self.wipe_spinbox.config(state=tk.NORMAL)
        
        else:
            self.wipe_spinbox.config(state=tk.DISABLED)
    
    def start_wiping(self) -> None:
        # In case its set to definite
        wipe_runs: int = self.wipe_mode.get()
        
        if wipe_runs:
            self.insert_feed(self.root.serial.sc_sendget(Command.SET_WIPE_DEF + self.wipe_var.get(), self.root.thread))
        
        else:
            self.insert_feed(self.root.serial.sc_sendget(Command.SET_WIPE_INF, self.root.thread))
        
        logger.info(f"HometabWipe\tStarting wipe with definite cycles set to\t{wipe_runs = }")
        self.root.status_frame_wipe.wipe_progressbar.start()
        self.root.wipe_mode.set(1)
            
    def attach_data(self) -> None:
        """Attaches data to the hometab"""
        logger.info("HometabWipe\tAttaching data")
        self.frq_spinbox.config(
            from_=50000,
            to=1200000)
        
    def publish(self) -> None:
        """ Function to build children of this frame """
        logger.info("HometabWipe\tPublishing")
        self.frq_spinbox.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.scroll_digit.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)        
        self.frq_frame.pack(side=tk.TOP, expand=True, fill=tk.X)
        self.set_val_btn.pack(side=tk.TOP, expand=True, fill=tk.X, padx=10, pady=10)
        self.us_on_button.pack(side=tk.TOP, expand=True, fill=tk.X, padx=10, pady=10)
        
        self.wipe_spinbox.pack(side=tk.TOP, expand=True, padx=10, pady=10, fill=tk.X)
        self.inf_wipe_button.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.def_wipe_button.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)
        self.wipe_mode_frame.pack(side=tk.TOP, expand=True, fill=tk.X)
        self.start_wipe_button.pack(side=tk.TOP, expand=True, padx=10, pady=10, fill=tk.X)
        
        self.wipe_frame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.frq_control_frame.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)
        
        self.us_off_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky=tk.NSEW)
        
        self.topframe.pack(side=tk.TOP, padx=20, pady=20)
        
        self.output_frame.pack(anchor=tk.N, side=tk.TOP, padx=10, pady=10, expand=True, fill=tk.BOTH)
        self.botframe.pack(side=tk.TOP)        
            
    def set_scrolldigit(self) -> None:
        """ Function regarding the scroll digit combobox """
        self.frq_spinbox.config(
            increment = str(10 ** (int(self.scroll_digit.get())-1)))
        


class ScriptingTab(ttk.Frame):
    """ Scripting tab of the GUI"""
    
    @property
    def root(self) -> tk.Tk:
        return self._root
    
    @property
    def serial(self) -> SerialConnection:
        return self._serial
    
    def __init__(self, parent: ttk.Notebook, root: tk.Tk, *args, **kwargs) -> None:
        """ Declare all children """
        super().__init__(parent, *args, **kwargs)
        
        self._root = root
        self._serial: SerialConnection = root.serial
        self.script_filepath: str
        self.save_filename: str
        self.logfilename: str
        self.logfilepath: str
        self.current_task: tk.StringVar = tk.StringVar(value='Idle')
        self.status: Status
        self.previous_task: str = "Idle"
        
        self._filetypes: list[tuple] = [('Text', '*.txt'),('All files', '*'),]
        
        self.logger: logging.Logger
        
        self.config(height=200, width=200)
        
        self.button_frame: ttk.Frame = ttk.Frame(self)
        self.start_script_btn = ttk.Button(
            self.button_frame,
            text='Run',
            style='success.TButton',
            width=11,
            image=self.root.play_img,
            compound=tk.RIGHT,
            command=self.read_file,)
        
        self.load_script_btn: ttk.Button = ttk.Button(
            self.button_frame,
            text='Open script file',
            style='dark.TButton',
            width=15,
            command=self.load_file,)
        
        self.save_script_btn: ttk.Button = ttk.Button(
            self.button_frame,
            text='Save script file',
            style='dark.TButton',
            width=15,
            command=self.save_file,)
        
        # self.save_log_btn: ttk.Button = ttk.Button(
        #     self.button_frame,
        #     text='Specify logfile path',
        #     style='dark.TButton',
        #     width=15,
        #     command=self.open_logfile)
        
        self.script_guide_btn = ttk.Button(
            self.button_frame,
            text='Function Helper',
            style='info.TButton',
            width=15,
            command=lambda: ScriptingGuide(self.root, self.scripttext))
        ToolTip(self.script_guide_btn, text="Help regarding the scripting commands")
        
        self.scripting_frame: ttk.Labelframe = ttk.Labelframe(
            self,
            text="Script Editor",
            style="dark.TLabelframe",
            padding=(5,5,5,5),)
        
        self.scripttext: tk.Text = tk.Text(
            self.scripting_frame,
            autoseparators=False,
            background='white',
            setgrid=False,
            width=35,
            padx=5,
            pady=5,
            font=("Consolas", 12))
        
        self.scrollbar: ttk.Scrollbar = ttk.Scrollbar(
            self.scripting_frame,
            orient='vertical',
            command=self.scripttext.yview)  
        
        # self.show_log_console: ttk.Button = ttk.Button(
        #     self.scripting_frame,
        #     text='Show log console',
        #     style="secondary.TButton",
        #     command=self.show_console)
        
        self.cur_task_label = ttk.Label(
           self.scripting_frame,
           justify=tk.CENTER,
           anchor=tk.CENTER,
           style="dark.TLabel",
           textvariable=self.current_task)
        
        self.sequence_status: ttk.Progressbar = ttk.Progressbar(
            self.scripting_frame,
            length=160,
            mode="indeterminate",
            orient=tk.HORIZONTAL,
            style="dark.TProgressbar",)
        
        self._sequence_dir: str = 'ScriptingSequence'
        self.fieldnames: list = ['timestamp','frequency', 'urms', 'irms', 'phase']
        
        if not os.path.exists(self._sequence_dir):
            logger.info(f"ScriptingTab\tno sequence directory\tcreating folder")
            os.mkdir(self._sequence_dir)
        
        logger.info("ScriptingTab\tInitialized")

    def publish(self):
        # Button Frame
        logger.info("Scriptingtab\tPublishing")
        self.button_frame.pack(anchor=tk.N, side=tk.LEFT, padx=5, pady=5)
        
        for child in self.button_frame.winfo_children():
            child.pack(side=tk.TOP, padx=5, pady=5)

        #Scripting Frame
        self.scripting_frame.pack(anchor=tk.N ,side=tk.RIGHT ,padx=5, pady=5, expand=True, fill=tk.X)
        self.scripttext.grid(row=0, column=0, columnspan=2)
        # self.show_log_console.grid(row=1, column=0, padx=5, pady=5)
        self.cur_task_label.grid(row=1, column=0, padx=0, pady=5, sticky=tk.EW, columnspan=2)
        self.sequence_status.grid(row=2, column=0, padx=0, pady=5, sticky=tk.EW, columnspan=2)
    
    def show_console(self):
        pass
    
    def load_file(self) -> None:
        self.script_filepath = filedialog.askopenfilename(defaultextension='.txt', filetypes=self._filetypes)
        
        with open(self.script_filepath, 'r') as f:
            self.scripttext.delete(0, tk.END)
            self.scripttext.insert(tk.INSERT, f.read())
        
        logger.info("Loaded file")
    
    def save_file(self) -> None:
        self.save_filename = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=self._filetypes)
        
        with open(self.save_filename, 'w') as f:
            f.write(self.scripttext.get(0, tk.END))
    
    def open_logfile(self) -> None:
        self.logfilepath = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=self._filetypes)
    
    def close_file(self) -> None:
        """Function that closes the scripting sequence"""
        self.run: bool = False
        
        logger.info("Scriptingtab\tSequence ended\t")
        
        self.start_script_btn.configure(
            text='Run',
            style='success.TButton',
            image=self.root.play_img,
            command=self.read_file)
        
        self.scripttext.tag_delete("currentLine", 1.0, tk.END)
        self.sequence_status.stop()
        self.current_task.set("Idle")
        self.previous_task = "Idle"
        self.root.notebook.enable_children()
        self.scripttext.config(state=tk.NORMAL)
        self.load_script_btn.config(state=tk.NORMAL)
        self.save_script_btn.config(state=tk.NORMAL)
        # self.save_log_btn.config(state=tk.NORMAL)
        self.script_guide_btn.config(state=tk.NORMAL)
        self.sequence_status.config(text=None)
        
        self.serial.send_and_get(Command.SET_SIGNAL_OFF)
        
        self.root.attach_data()
        self.root.thread.resume()
    
    def read_file(self) -> None:
        """Starts the scripting sequence"""
        self.run: bool = True
    
        self.logger: logging.Logger = logging.getLogger("Scripting")
        self.formatter: logging.Formatter = logging.Formatter('%(asctime)s\t%(message)s')
        self.file_handler: logging.FileHandler = logging.FileHandler(f'{self._sequence_dir}//{datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")}_sequence.csv')
        self.logger.setLevel(logging.DEBUG)
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)
        
        self.root.thread.pause()
        
        self.start_script_btn.configure(
            text='Stop',
            style='danger.TButton',
            image=self.root.pause_img,
            command=self.close_file)
        
        self.sequence_status.start()
        self.root.notebook.disable_children(self)
        self.scripttext.config(state=tk.DISABLED)
        self.load_script_btn.config(state=tk.DISABLED)
        self.save_script_btn.config(state=tk.DISABLED)
        self.script_guide_btn.config(state=tk.DISABLED)
        
        self.serial.send_and_get(Command.SET_SIGNAL_ON)
        
        self.status_handler()
        self.start_sequence()
        
    def set_run(self, state: bool) -> None:
        """The sequence checks the run flag constantly, so this function
        acts as a setter of that variable

        Args:
            state (bool): The to be setted state
        """
        self.run: bool = state
    
    def highlight_line(self, current_line: int) -> None:
        """Function that highlights the current line of the sequence in the script editor
        The argument current_line

        Args:
            current_line (int): current line in the script, that need to be highlighted
        """
        current_line += 1
        self.scripttext.tag_remove('currentLine', 1.0, "end")
        self.scripttext.tag_add('currentLine', f"{current_line}.0", f"{current_line}.end")
        self.scripttext.tag_configure('currentLine', background="#3e3f3a", foreground="#dfd7ca")
    
    def start_sequence(self) -> None:
        """
        Starts the scripting sequence:
        """
        self.commands: list[str] = []
        self.args_: list[str] = []
        self.loops: list[list[int]] = [[]]
        self.loop_index: int = 0
        
        logger.info(f"Scriptingtab\tstarting Sequence")
        
        # Try to parse the string from the textfield and get the data into ordered arrays
        # If it fails, the formatting supposedely is false, so an error is shown
        try:
            self.parse_commands(self.scripttext.get(1.0, tk.END))
        
        except Exception as e:
            print(e)
            messagebox.showerror("Error in formatting", "It seems you've given commands or arguments in the wrong format")
            self.run: bool = False
        
        line: int = 0
        while line < len(self.commands) and self.run:
            self.highlight_line(line)
            
            if self.commands[line] == 'startloop':
                
                logger.info(f"Scriptingtab\tfound startloop at\t{line}")
                if self.loops[line][1] and isinstance(self.loops[line][1], int):
                    logger.info(f"Scriptingtab\tStarting loop\tQuantifier of loop now {self.loops[line][1] = }")
                    self.loops[line][1] -= 1
                    line += 1
                
                elif self.loops[line][1] == 'inf':
                    logger.info(f"Scriptingtab\tDetected infinite loop\tgoing to the next line")
                    line += 1
                
                else:
                    logger.info(f"Scriptingtab\tQuantifier is zero, going to index of first command after endloop\t {self.loops[line][2] = }")
                    line: int = self.loops[line][2] + 1
            
            elif self.commands[line] == 'endloop':
                
                logger.info(f"ScriptingTab\tDetected endloop at\t{line}")
                for loop in self.loops:
                    if loop and loop[2] == line:
                        
                        for j in range(loop[0]+1, loop[2]):
                            logger.info(f"Scriptingtab\tNow checking if nested loops should be reseted")
                            if self.loops[j]:
                                logger.info(f"ScriptingTab\tFound loop to be reseted\t {self.loops[j] = }")
                                self.loops[j][1] = self.args_[j][0]
                        
                        line: int = loop[0]
                        
            else:
                logger.info(f"Scriptingtab\tExecuting command at\t{line = }")
                self.exec_command(line)
                line += 1

        # So that the close_file function doesn't get called two times
        if not self.run:
            return
        else:
            self.close_file()

    
    def status_handler(self) -> None:
        """Update the Root Window at the status frame to display the current data from the sequence"""
        try:
            self.status: Status = self.root.sonicamp.get_status()
            logger.info(f"Scriptingtab\tGot status with data\t{self.status = }")
            status_logger.info(f"{self.status.frequency}\t{self.status.gain}\t{self.status.signal}") 
        
        except ValueError:
            pass
        
        if self.root.sonicamp.type_ == 'soniccatch':
            self.root.status_frame_catch.gain_meter["amountused"] = self.status.gain
            self.root.status_frame_catch.frq_meter["amountused"] = self.status.frequency / 1000

            if self.status.signal:
                self.root.status_frame_catch.sig_status_label["text"] = "Signal ON"
                self.root.status_frame_catch.sig_status_label["image"] = self.root.led_green_img
            else:
                self.root.status_frame_catch.sig_status_label["text"] = "Signal OFF"
                self.root.status_frame_catch.sig_status_label["image"] = self.root.led_red_img
        
        elif self.root.sonicamp.type_ == 'sonicwipe':
            self.root.status_frame_wipe.frq_meter["amountused"] = self.status.frequency / 1000

            if self.status.signal:
                self.root.status_frame_wipe.sig_status_label["text"] = "Signal ON"
                self.root.status_frame_wipe.sig_status_label["image"] = self.root.led_green_img
            else:
                self.root.status_frame_wipe.sig_status_label["text"] = "Signal OFF"
                self.root.status_frame_wipe.sig_status_label["image"] = self.root.led_red_img

        self.root.update()

    def exec_command(self, counter: int) -> None:
        """This function manages the execution of functions
        and manages the visualization of the execution

        Args:
            counter (int): The index of the line
        """
        self.highlight_line(counter)

        # For the visual feedback of the sequence
        self.current_task.set(f"{self.commands[counter]} {str(self.args_[counter])}")
        if counter > 0:
            self.previous_task: str = f"{self.commands[counter-1]} {self.args_[counter-1]}"

        # Just for managing purposes
        if len(self.args_[counter]) == 1:
            argument: int = self.args_[counter][0]
        else:
            argument: list = self.args_[counter]

        if self.run:
            
            logger.info(f"Scriptingtab\tExecuting command\t{self.commands[counter] = }")
                        
            if self.commands[counter] == "frequency":
                self.check_relay(frq=argument)
                self.serial.send_and_get(Command.SET_FRQ + argument)
            
            elif self.commands[counter] == "gain":
                self.check_relay(gain=argument)
                self.serial.send_and_get(Command.SET_GAIN + argument)
            
            elif self.commands[counter] == "ramp":
                self.start_ramp(argument)
            
            elif self.commands[counter] == "hold":
                self.hold(argument)
            
            elif self.commands[counter] == "on":
                self.serial.send_and_get(Command.SET_SIGNAL_ON)
            
            elif self.commands[counter] == "off":
                self.serial.send_and_get(Command.SET_SIGNAL_OFF)

            elif self.commands[counter] == "autotune":
                self.serial.send_and_get(Command.SET_AUTO)
                
            else:
                messagebox.showerror("Wrong command", f"the command {self.commands[counter]} is not known, please use the correct commands in the correct syntax")
                self.run: bool = False
        
        self.status_handler()
        self.logger.info(f"{str(self.commands[counter])}\t{str(argument)}\t{self.status.frequency}\t{self.status.gain}")
    
    def hold(self, args_: Union[list, int]) -> None:
        """Holds the time during sequence, that was passed as an argument
        The user has the ability to control in which time unit the delay should
        be executed. More concretly:
            trailing 's' -> seconds
            trailing 'ms' -> milliseconds

        Args:
            args_ (list[Union[str, int]]): _description_
        """
        now: datetime.datetime = datetime.datetime.now()
        # Let us find out, what unit the delay should be in
        if isinstance(args_, int):
            logger.info(f"Scriptingtab\tNo unit given\tusing seconds")
            target: datetime.datetime = now + datetime.timedelta(seconds=args_)
        
        elif (len(args_) > 1 and args_[1] == 's') or (len(args_) == 1):
            logger.info(f"Scriptingtab\tunit given\t{args_[1] = }\tusing seconds")
            target: datetime.datetime = now + datetime.timedelta(seconds=args_[0])
        
        elif len(args_) > 1 and args_[1] == 'ms':
            logger.info(f"Scriptingtab\tunit given\t{args_[1] = }\tusing milliseconds")
            target: datetime.datetime = now + datetime.timedelta(milliseconds=args_[0])
        
        else:
            logger.info(f"Scriptingtab\tno unit given\tusing seconds (else condition)")
            target: datetime.datetime = now + datetime.timedelta(seconds=args_[0])
        
        # The actual execute of the delay
        while now < target and self.run:
            time.sleep(0.02)
            now = datetime.datetime.now()
            self.root.update()
                
    def check_relay(self, frq: int = 0, gain: int = 0) -> None:
        """Function that checks the current relay setting in a soniccatch and changes
        the relay accordingly, so that the frequency set would be possible

        Args:
            frq (int):  The frequency that should be set
            gain (int): The gain that should be setted, if needed
        """
        running_soniccatch: bool = self.run and (isinstance(self.root.sonicamp, SonicCatch))# or isinstance(self.root.sonicamp, SonicCatchOld))
                
        if (running_soniccatch and frq >= 1000000 and self.status.frequency < 1000000) or (running_soniccatch and gain and self.status.frequency >= 1000000):
            logger.info(f"Scriptingtab\tChecking relay\tSetting to MHz")
            self.serial.send_and_get(Command.SET_MHZ)
            self.serial.send_and_get(Command.SET_SIGNAL_ON)
    
        elif running_soniccatch and  frq < 1000000 and self.status.frequency >= 1000000:
            logger.info(f"Scriptingtab\tChecking relay\tSetting to kHz")
            self.serial.send_and_get(Command.SET_KHZ)
            self.serial.send_and_get(Command.SET_SIGNAL_ON)
        
        elif running_soniccatch and gain and self.status.frequency < 1000000:
            self.close_file()
            messagebox.showerror("Semantic error", "Gain setting is not supported for frequencies under 1MHz. Please make sure that the frequency is over 1MHz when setting the gain")       
    
    def start_ramp(self, args_: list) -> None:
        """Starts the ramp process, and ramps up the frequency from a
        start value to a stop value. The resolution (step size) is also given
        from the passed argument. Additionally, a delay and the unit of that
        delay are also passed down.

        Args:
            args_ (list): [start, stop, step, delay, unit]
            example:
            [1200000, 1900000, 10000, 100, 'ms']
        """
        logger.info("Scriptingtb\tstarting ramp")
        
        # declaring variables for easier use
        start: int = args_[0]
        stop: int = args_[1]
        step: int = args_[2]
        delay: int = args_[3]
        
        # Constructing an argument for the delay
        if len(args_) > 4:
            hold_argument: list = [delay, args_[4]]
        else: 
            hold_argument: list = [delay]
        
        # in case the ramp should be decreasing
        if start > stop:
            frq_list: list[int] = list(range(stop, start+step, step))
            frq_list.sort(reverse=True)
        else:
            frq_list: list[int] = list(range(start, stop+step, step))

        # The core of the ramp function
        for frq in frq_list:
            if self.run:
                self.current_task.set(f"Ramp is @ {frq/1000}kHz")
                
                self.check_relay(frq)
                self.serial.send_and_get(Command.SET_FRQ + frq)
                self.status_handler()
                
                self.logger.info(f"ramp\t{start},{stop},{step}\t{self.status.frequency}\t{self.status.gain}")

                self.hold(hold_argument)
            else:
                break
    
    def parse_commands(self, text: str) -> None:
        """Parse a string and split it into data parts
        Conretely into:
            self.commands -> a list of strings indicating which action to execute
            self.args_ -> a list of numbers and values for the commands
            self.loops -> data about index of loops, index of the end of loops and arguments
            
        Every list has the same length, indicating the line numbers

        Args:
            text (str): a str of text 
        """
        logger.info("Scriptingtab\tParsing commands")
        
        # The string becomes a list of strings, in which each item resembles a line
        line_list: list[str] = text.rstrip().splitlines()

        for line in line_list:
            # Clean the line and split it where a white-space is
            line: list = line.rstrip().split(' ')
            
            # Go through each word or number item of that line
            for i, part in enumerate(line):
                part = part.rstrip()                    # Clean the part from leading and trailing white-spaces
                
                # If the part is numeric, it should be resembled as an integer, not a string
                if part.isnumeric():
                    line[i] = int(part)
                
                # If part has no length, it's essentially a empty part, we don't need that
                elif not len(part):
                    line.pop(i)
                
                # In case it's a delay that shows in which time unit it should be executet
                elif part[-2:] == 'ms' and part[0].isdigit():
                    line[i] = int(part[:-2])
                    line.append(part[-2:])
                
                elif part[-1:] == 's' and part[-2:] != 'ms' and part[0].isdigit():
                    line[i] = int(part[:-1])
                    line.append(part[-1:])
            
            self.commands.append(line[0])
            self.args_.append(line[1:])
        
        # We go through each command to look for loops
        for i, command in enumerate(self.commands):
        
            if command == "startloop":
                if self.args_[i] == 'inf':
                    loopdata: list = [i, 'inf']
                else:    
                    loopdata: list = [i, self.args_[i][0]]
                self.loops.insert(i, loopdata)
            
            elif command == "endloop":
                self.loops.insert(i, [])
                for loop in reversed(self.loops):
                
                    if len(loop) == 2:
                        loop.insert(2, i)
                        break
            
            else:
                self.loops.insert(i, [])
        
        logger.info(f"Scriptingtab\tAfter parsing\t{self.commands = }\t{self.args_ = }\t{self.loops = }")
    
    def attach_data(self) -> None:
        pass
    


class ScriptingGuide(tk.Toplevel):
    
    def __init__(self, root: tk.Tk, scripttext: tk.Text, *args, **kwargs) -> None:
        super().__init__(root, *args, **kwargs)
        self.title('Function Helper')

        self.scripttext: tk.Text = scripttext
        
        # Headings
        self.heading_frame: ttk.Frame = ttk.Frame(self)
        self.heading_command = ttk.Label(
            self.heading_frame, 
            anchor=tk.W, 
            justify=tk.CENTER, 
            text='Command',
            width=15,
            style="dark.TLabel",
            font="QTypeOT-CondMedium 15 bold",)
        self.heading_command.grid(row=0, column=0, padx=5, pady=5, sticky=tk.NSEW)
        
        self.heading_arg = ttk.Label(
            self.heading_frame, 
            anchor=tk.W, 
            justify=tk.CENTER,
            width=15,
            style="info.TLabel",
            text='Arguments', 
            font="QTypeOT-CondMedium 15 bold",)
        self.heading_arg.grid(row=0, column=1, padx=5, pady=5, sticky=tk.NSEW)
        
        # self.heading_description = ttk.Label(
        #     self.heading_frame, 
        #     anchor=tk.W, 
        #     justify=tk.CENTER,
        #     width=15,
        #     style="primary.TLabel",
        #     text='Description',
        #     font="QTypeOT-CondMedium 15 bold",)
        # self.heading_description.grid(row=0, column=2, padx=5, pady=5, sticky=tk.NSEW)
        self.heading_frame.pack(side=tk.TOP, padx=5, pady=5, anchor=tk.W, expand=True, fill=tk.X)
        
        self.hold_btn: ScriptingGuideRow = ScriptingGuideRow(
            self,
            btn_text="hold",
            arg_text="[1-10000] in [seconds/ milliseconds] (depending on what you write e.g: 100ms, 5s, 123s)",
            desc_text=None,
            command=lambda: self.insert_command(ScriptCommand.SET_HOLD),)
        self.hold_btn.pack(side=tk.TOP, padx=5, pady=5, anchor=tk.W)
        ToolTip(self.hold_btn, text="Hold the last state for X seconds/ milliseconds, depending on what unit you have given")
        
        self.frq_btn: ScriptingGuideRow = ScriptingGuideRow(
            self,
            btn_text='frequency',
            arg_text='[50.000-6.000.000] in [Hz]',
            desc_text=None,
            command = lambda: self.insert_command(ScriptCommand.SET_FRQ))
        self.frq_btn.pack(side=tk.TOP, padx=5, pady=5, anchor=tk.W)
        ToolTip(self.frq_btn, text='Change to the indicated frequency in Hz')
        
        self.gain_btn: ScriptingGuideRow = ScriptingGuideRow(
            self,
            btn_text='gain',
            arg_text='[1-150] in [%]',
            desc_text=None,
            command = lambda: self.insert_command(ScriptCommand.SET_GAIN))
        ToolTip(self.gain_btn, text='Change to the selected gain in %')
        
        # self.khz_btn: ScriptingGuideRow = ScriptingGuideRow(
        #     self,
        #     btn_text='setkHz',
        #     arg_text=None,
        #     desc_text='Change to the kHz range amplifier',
        #     command = lambda: self.insert_command(ScriptCommand.SET_KHZ))
        # self.khz_btn.pack(side=tk.TOP, padx=5, pady=5, anchor=tk.W)
        
        # self.mhz_btn: ScriptingGuideRow = ScriptingGuideRow(
        #     self,
        #     btn_text='setMHz',
        #     arg_text=None,
        #     desc_text='Change to the MHz range amplifier',
        #     command = lambda: self.insert_command(ScriptCommand.SET_MHZ))
        # self.mhz_btn.pack(side=tk.TOP, padx=5, pady=5, anchor=tk.W)
        
        self.on_btn: ScriptingGuideRow = ScriptingGuideRow(
            self,
            btn_text='on',
            arg_text=None,
            desc_text=None,
            command = lambda: self.insert_command(ScriptCommand.SET_SIGNAL_ON))
        self.on_btn.pack(side=tk.TOP, padx=5, pady=5, anchor=tk.W)
        ToolTip(self.on_btn, text='Activate US emission')
        
        self.off_btn: ScriptingGuideRow = ScriptingGuideRow(
            self,
            btn_text='off',
            arg_text=None,
            desc_text=None,
            command = lambda: self.insert_command(ScriptCommand.SET_SIGNAL_OFF))
        self.off_btn.pack(side=tk.TOP, padx=5, pady=5, anchor=tk.W)
        ToolTip(self.off_btn, text='Deactivate US emission')
        
        self.startloop_btn: ScriptingGuideRow = ScriptingGuideRow(
            self,
            btn_text='startloop',
            arg_text='[2-10.000] as an [integer]',
            desc_text=None,
            command = lambda: self.insert_command(ScriptCommand.STARTLOOP))
        self.startloop_btn.pack(side=tk.TOP, padx=5, pady=5, anchor=tk.W)
        ToolTip(self.startloop_btn, text='Start a loop for X times')
        
        self.endloop_btn: ScriptingGuideRow = ScriptingGuideRow(
            self,
            btn_text='endloop',
            arg_text=None,
            desc_text=None,
            command = lambda: self.insert_command(ScriptCommand.ENDLOOP))
        self.endloop_btn.pack(side=tk.TOP, padx=5, pady=5, anchor=tk.W)
        ToolTip(self.endloop_btn, text='End the loop here')
        
        self.ramp_btn: ScriptingGuideRow = ScriptingGuideRow(
            self,
            btn_text='ramp',
            arg_text='<start f [Hz]> <stop f [Hz]> <step size [Hz]> <delay [ms / s]><unit of time> \nThe delay should be written like a hold (e.g: 100ms, 5s, 3s, 234ms)',
            desc_text=None,
            command = lambda: self.insert_command(ScriptCommand.SET_RAMP))
        self.ramp_btn.pack(side=tk.TOP, padx=5, pady=5, anchor=tk.W)
        ToolTip(self.ramp_btn, text='Create a frequency ramp with a start frequency, a stop frequency,\n a step size and a delay between steps')
                
        if root.sonicamp.type_ == 'soniccatch':
            self.gain_btn.pack(side=tk.TOP, padx=5, pady=5, anchor=tk.W)
        
        self.disclaimer_label: ttk.Label = ttk.Label(
            self, 
            text='To insert a function at the cursor position, click on the respective button', 
            font=('TkDefaultFont', 11, 'bold'))
        self.disclaimer_label.pack(side=tk.TOP, expand=True, fill=tk.X, padx=5, pady=5)
        
    def insert_command(self, command: ScriptCommand) -> None:
        self.scripttext.insert(self.scripttext.index(tk.INSERT), command.value)
        
        
        

class ScriptingGuideRow(ttk.Frame):
    
    def __init__(self, parent: ttk.Frame, btn_text: str, arg_text: str, desc_text: str, command,*args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        
        self.command_btn: ttk.Button = ttk.Button(
            self,
            width=15,
            style="dark.TButton",
            text=btn_text,
            command=command)
        self.command_btn.grid(row=0, column=0, padx=5, pady=5, sticky=tk.NSEW)
        
        if arg_text:
            # self.arg_entry: ttk.Entry = ttk.Entry(
            #     self,
            #     width=15,
            #     justify=tk.LEFT,
            #     style="info.TEntry",)
            # self.arg_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.NSEW)

            self.arg_label: ttk.Label = ttk.Label(
                self,
                style='inverse.info.TLabel',
                text=arg_text)
            self.arg_label.grid(row=0, column=2, padx=5, pady=5, sticky=tk.NSEW)  
        
        if desc_text:
            self.desc_label: ttk.Label = ttk.Label(
                self,
                text=desc_text,
                style='inverse.primary.TLabel')
            self.desc_label.grid(row=0, column=3, padx=5, pady=5, sticky=tk.NSEW)


class ConnectionTab(ttk.Frame):
    
    @property
    def root(self) -> tk.Tk:
        return self._root
    
    def __init__(self, parent: ttk.Notebook, root: tk.Tk, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self._root = root
        
        self.topframe: ttk.Frame = ttk.Frame(self, padding=(10, 10, 10, 10))
        self.heading_frame: ttk.Frame = ttk.Frame(self.topframe)
        
        self.subtitle: ttk.Label = ttk.Label(self.heading_frame, padding=(0, 10, 0, 0))
        
        self.heading1 = ttk.Label(
            self.heading_frame, 
            padding=(10,0,0,10),
            font = self.root.qtype30,
            borderwidth=-2)
        
        self.heading2 = ttk.Label(
            self.heading_frame,
            padding=(0,0,10,10),
            font = self.root.qtype30b,
            borderwidth=-2)
        
        self.control_frame = ttk.Frame(self.topframe)
        
        self.connect_button = ttkb.Button(
            self.control_frame, 
            width = 10,
            style="success.TButton")
        
        self.ports_menue = ttk.Combobox(
            master=self.control_frame,
            textvariable=self.root.port,
            values=None,
            width=7,
            style = "dark.TCombobox",
            state=tk.READABLE)
        ToolTip(self.ports_menue, text="Choose the serial communication address of you SonicAmp")
        
        self.refresh_button = ttkb.Button(
            self.control_frame, 
            bootstyle="secondary-outline",
            image=self.root.refresh_img, 
            command = self.refresh)
        
        self.botframe: ttk.Frame = ttk.Frame(self)

        self.firmware_frame: ttk.Labelframe = ttk.Labelframe(
            self.botframe,
            text='Firmware',)
        
        self.firmware_label: ttk.Label = ttk.Label(
            self.firmware_frame,
            justify=tk.CENTER,
            style='dark.TLabel')
        
        self.flash_frame = ttk.Labelframe(
            self.botframe, 
            height=250, 
            text='Update Firmware', 
            width=200,
            padding=(0, 12, 0, 12))
        
        self.file_entry = ttk.Button(
            self.flash_frame, 
            text="Specify path for Firmware file", 
            width=20, 
            style="dark.TButton",
            command=self.hex_file_path_handler)
        
        self.hex_file_path = tk.StringVar()
        
        self.upload_button = ttk.Button(
            self.flash_frame, 
            style='dark.TButton',
            width=20,
            text='Upload Firmware', 
            command=self.upload_file)
        
        self.serial_monitor_btn: ttk.Button = ttk.Button(
            self.botframe,
            text='Serial Monitor',
            style='secondary.TButton',
            width=12,
            command=self.root.publish_serial_monitor,)
        
        logger.info("Connectiontab\tInitialized children and object connectiontab")
    
    def attach_data(self) -> None:
        """Attaches data to the connectiontab"""
        logger.info("Connectiontab\tattaching data")
        self.subtitle["text"] = "You are connected to"
        self.heading1["text"] = self.root.sonicamp.type_[:5]
        self.heading2["text"] = self.root.sonicamp.type_[5:]
        
        self.connect_button.config(
            bootstyle="danger",
            text="Disconnect",
            command=self.disconnect,)
        
        self.ports_menue.config(state=tk.DISABLED)
        self.refresh_button.config(state=tk.DISABLED)
        self.firmware_label["text"] = self.root.sonicamp.firmware_msg #* Treeview for future ideas
        
        for child in self.flash_frame.children.values():
            child.configure(state=tk.NORMAL)
        
    def abolish_data(self) -> None:
        """Abolishes data from the connectiontab"""
        logger.info("Connectiontab\tabolishing data")
        self.subtitle["text"] = "Please connect to a SonicAmp system"
        self.heading1["text"] = "not"
        self.heading2["text"] = "connected"
        
        self.connect_button.config(
            bootstyle="success",
            text="Connect",
            command=self.root.__reinit__,)
        
        self.ports_menue.config(
            textvariable=self.root.port,
            values=self.root.serial.device_list,
            state=tk.NORMAL)
        
        self.refresh_button.config(state=tk.NORMAL)
        self.firmware_label["text"] = ""
        
        for child in self.flash_frame.children.values():
            child.configure(state=tk.DISABLED)
        self.root.sonicamp = None

    def refresh(self) -> None:
        """Refreshes the potential ports"""
        self.ports_menue['values'] = self.root.serial.get_ports()
    
    def disconnect(self) -> None:
        """Disconnects the soniccontrol with the current connection"""
        logger.info(f"Connectiontab\tDisconnecting")
        self.root.thread.pause()
        self.abolish_data()
        self.root.serial.disconnect()
        self.root.publish_disconnected()
    
    def publish(self) -> None:
        logger.info("Connectiontab\tPublishing connectiontab")
        
        for child in self.children.values():
            child.pack()
        
        self.subtitle.grid(row=0, column=0, columnspan=2, sticky=tk.S)
        self.heading1.grid(row=1, column=0, columnspan=1, sticky=tk.E)
        self.heading2.grid(row=1, column=1, columnspan=1, sticky=tk.W)
        self.heading_frame.pack(padx=10, pady=20, expand=True)

        self.ports_menue.grid(row=0, column=0, columnspan=2, pady=10, padx=5, sticky=tk.NSEW)        
        self.connect_button.grid(row=0, column=2,columnspan=1, pady=10, padx=5, sticky=tk.NSEW)
        self.refresh_button.grid(row=0, column=3 ,columnspan=1,  pady=10, padx=5, sticky=tk.NSEW)
        self.control_frame.pack(padx=10, pady=20, expand=True)
    
        self.firmware_frame.grid(row=0, column=0, padx=10, pady=10)
        self.firmware_label.pack()
        self.serial_monitor_btn.grid(row=1, column=0, padx=10, pady=10)
        # self.file_entry.pack(padx=10, pady=10, side=tk.TOP)
        # self.upload_button.pack(padx=10, pady=10, side=tk.TOP)
        # self.flash_frame.grid(row=0, column=1, padx=10, pady=10)
    
    def hex_file_path_handler(self):
        """Gets the file of a potential hex firmware file, and checks if it's even a hex file"""
        self.hex_file_path = filedialog.askopenfilename(defaultextension=".hex", filetypes=(("HEX File", "*.hex"),))
        
        if self.hex_file_path[-4:] == ".hex":
            self.file_entry.config(style="success.TButton", text="File specified and validated")
        
        else:
            messagebox.showerror("Wrong File", "The specified file is not a validated firmware file. Please try again with a file that ends with the format \".hex\"")
            self.file_entry.config(style="danger.TButton", text="File is not a firmware file")

    def upload_file(self):
        """Upploads the hex file to the hardware via AVRDUDE"""
        if self.root.serial.is_connected:
            
            if self.hex_file_path:
                port = self.ser.port
                self.ser.close()
                cur_dir = os.getcwd()
                # self.firmware_progress_text.pack(padx=10, pady=10)
                
                try:
                    command = f"\"{cur_dir}/avrdude/avrdude.exe\" -v -patmega328p -carduino -P{port} -b115200 -D -Uflash:w:\"{self.hex_file_path}\":i"
                    msgbox = messagebox.showwarning("Process about to start", "The program is about to flash a new firmware on your device, please do NOT disconnect or turn off your device during that process")
                    
                    if msgbox:
                        output = subprocess.run(command, shell=True)
                        self.file_entry.configure(style="dark.TButton", text="Specify the path for the Firmware file")
                        # self.firmware_progress_text.pack_forget()
                        self.connectPort(port)
                    else:
                        messagebox.showerror("Error", "Cancled the update")
                
                except WindowsError:
                    messagebox.showerror("Error", "Something went wrong, please try again. Maybe restart the device and the program")
            
            else:
                messagebox.showerror("Couldn't find file", "Please specify the path to the firmware file, before flashing your SonicAmp")
        else:
            messagebox.showerror("Error", "No connection is established, please recheck all connections and try to reconnect in the Connection Tab. Make sure the instrument is in Serial Mode.")



class InfoTab(ttk.Frame):
    
    INFOTEXT = (
        "Welcome to soniccontrol, a light-weight application to\n" 
        "control sonicamp systems over the serial interface. \n"
        "For help, click the \"Manual\" button below\n"
        "\n"
        "(c) usePAT G.m.b.H\n")
    
    @property
    def root(self) -> tk.Tk:
        return self._root
    
    def __init__(self, parent: ttk.Notebook, root: tk.Tk, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self._root = root
        self.soniccontrol_logo_frame: ttk.Frame = ttk.Frame(self)
        self.soniccontrol_logo1 = ttk.Label(
            self.soniccontrol_logo_frame,
            text = "sonic",
            padding=(10,0,0,10),
            font = "QTypeOT-CondLight 30",
            borderwidth=-2,)
        
        self.soniccontrol_logo2 = ttk.Label(
            self.soniccontrol_logo_frame,
            text = 'control',
            padding=(0,0,0,10),
            font = "QTypeOT-CondBook 30 bold",
            borderwidth=-2,)
        
        self.info_label = ttk.Label(self, text=InfoTab.INFOTEXT)
        
        self.controlframe = ttk.Frame(self)
        self.manual_btn = ttk.Button(
            self.controlframe,
            text='Help Manual',
            command=self.open_manual)
        
        # self.dev_btn = ttk.Button(
        #     self.controlframe,
        #     text='I\'m a developer...',
        #     command=self.root.publish_serial_monitor,
        #     style='outline.dark.TButton')
        
        self.version_label: ttk.Label = ttk.Label(
            self,
            text=self.root.VERSION,)
        
        logger.info("Infotab\tInitialized")
        
    def publish(self) -> None:
        """Publishes the object and children"""
        logger.info("Infotab\tpublishing infotab")
        self.soniccontrol_logo1.grid(row=0, column=0)
        self.soniccontrol_logo2.grid(row=0, column=1)
        self.soniccontrol_logo_frame.pack(padx=20, pady=20)
        self.info_label.pack()
        self.manual_btn.grid(row=0, column=0, padx=5, pady=10)
        # self.dev_btn.grid(row=0, column=1, padx=5, pady=10)
        self.controlframe.pack()
        
        self.version_label.pack(anchor=tk.S, side=tk.BOTTOM, padx=10, pady=10)
    
    def open_manual(self) -> None:
        """Opens the helppage manual with the default pdf viewer"""
        subprocess.Popen(['help_page.pdf'], shell=True)
    
    def attach_data(self) -> None:
        pass



class SonicMeasure(tk.Toplevel):
    
    @property
    def serial(self) -> SerialConnection:
        return self._serial
    
    def __init__(self, root: tk.Tk, *args, **kwargs) -> None:
        super().__init__(master=root, *args, **kwargs)
        # self._root: tk.Tk = root
        self._serial: SerialConnection = root.serial
        self.root: tk.Tk = root
        self._filetypes: list[tuple] = [('Text', '*.txt'),('All files', '*'),]
        
        self.title('SonicMeasure')
        
        self.start_frq: tk.IntVar = tk.IntVar(value=1900000)
        self.stop_frq: tk.IntVar = tk.IntVar(value=2100000)
        self.step_frq: tk.IntVar = tk.IntVar(value=100)
        
        self.start_gain: tk.IntVar = tk.IntVar(value=10)
        self.stop_gain: tk.IntVar = tk.IntVar(value=10)
        self.step_gain: tk.IntVar = tk.IntVar(value=0)
        
        # Figure Frame
        self.fig_frame: ttk.Frame = ttk.Frame(self)
        self.figure_canvas: MeasureCanvas = MeasureCanvas(self.fig_frame, self.start_frq.get(), self.stop_frq.get())
        self.toolbar = NavigationToolbar2Tk(self.figure_canvas, self.fig_frame)
        # Utility controls Frame
        self.control_frame: ttk.Frame = ttk.Frame(self)
        self.util_ctrl_frame: ttk.Frame = ttk.Frame(self.control_frame)
        self.start_btn: ttk.Button = ttk.Button(
            self.util_ctrl_frame,
            text="Start",
            style='success.TButton',
            image=root.play_img,
            compound=tk.RIGHT,
            command=self.start)
        
        self.save_btn: ttk.Button = ttk.Button(
            self.util_ctrl_frame,
            text="Save Plot",
            style="info.TButton",
            # image=self.root.save_img, #! Implement image
            # compound=tk.RIGHT,
            command=self.save)
        
        # Frquency Frame
        self.frq_frame: ttk.LabelFrame = ttk.LabelFrame(self.control_frame, text="Set up Frequency", style="secondary.TLabelframe")
        self.start_frq_label: ttk.Label = ttk.Label(self.frq_frame, text="Start frequency [Hz]")
        self.start_frq_entry: ttk.Entry = ttk.Entry(
            self.frq_frame,
            textvariable=self.start_frq,
            style="dark.TEntry",)
        
        self.stop_frq_label: ttk.Label = ttk.Label(self.frq_frame, text="Stop frequency [Hz]")
        self.stop_frq_entry: ttk.Entry = ttk.Entry(
            self.frq_frame,
            textvariable=self.stop_frq,
            style="dark.TEntry",)
        
        self.step_frq_label: ttk.Label = ttk.Label(self.frq_frame, text="Resolution [Hz]")
        self.step_frq_entry: ttk.Entry = ttk.Entry(
            self.frq_frame,
            textvariable=self.step_frq,
            style="dark.TEntry")
        
        # Gain Frame
        self.gain_frame: ttk.LabelFrame = ttk.LabelFrame(self.control_frame, text="Set up Gain", style="secondary.TLabelframe")
        self.start_gain_label: ttk.Label = ttk.Label(self.gain_frame, text="Start gain [%]")
        self.start_gain_entry: ttk.Entry = ttk.Entry(
            self.gain_frame,
            textvariable=self.start_gain,
            style="dark.TEntry",)
        
        self.stop_gain_label: ttk.Label = ttk.Label(self.gain_frame, text="Stop gain [%]")
        self.stop_gain_entry: ttk.Entry = ttk.Entry(
            self.gain_frame,
            textvariable=self.stop_gain,
            style="dark.TEntry",)
        
        self.step_gain_label: ttk.Label = ttk.Label(self.gain_frame, text="Resolution [%]")
        self.step_gain_entry: ttk.Entry = ttk.Entry(
            self.gain_frame,
            textvariable=self.step_gain,
            style="dark.TEntry")
        
        self._spectra_dir: str = 'SonicMeasure'
        self.fieldnames: list = ['timestamp','frequency', 'urms', 'irms', 'phase']
        
        if not os.path.exists(self._spectra_dir):
            os.mkdir(self._spectra_dir)
        
        self.publish()
        
    def on_closing(self) -> None:
        """Function that will be executed if window closes"""
        self.stop()
        self.destroy()
        
    def start(self) -> None:
        """WHat happens if the start button is being pressed"""
        logger.info(f"SonicMeasure\tstarting measure")
        
        self.run: bool = True
        # Change the appearence of the start button -> to a stop button
        self.start_btn.config(
            text='Stop',
            style='danger.TButton',
            image=self.root.pause_img,
            command=self.stop)
        
        self.save_btn.config(state=tk.DISABLED)
        
        for child in self.frq_frame.children.values():
            child.config(state=tk.DISABLED)
        
        timestamp: str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.spectra_file: str = f"sonicmeasure_{timestamp}.csv"
        self._create_csv()
        
        self.root.thread.pause()
        self.serial.send_and_get(Command.SET_MHZ)
        self.serial.send_and_get(Command.SET_SIGNAL_ON)
        self.serial.send_and_get(Command.SET_GAIN + self.start_gain.get())
        self.start_sequence()
        
    def stop(self) -> None:
        """Code tha will be executed if the Measure sequence is stopped"""
        self.start_btn.config(
            text='Run',
            style='success.TButton',
            image=self.root.play_img,
            command=self.start)
        self.save_btn.config(state=tk.NORMAL)
        
        for child in self.frq_frame.children.values():
            child.config(state=tk.NORMAL)
        
        self.serial.send_and_get(Command.SET_SIGNAL_OFF)
        
        # In case the thread was paused, resume. If statement to not resume the thread twice
        if self.root.thread.paused:
            self.root.thread.resume()
        
    def _create_csv(self) -> None:
        """Create a csv for the current measurement"""
        with open(f"{self._spectra_dir}//{self.spectra_file}", "a", newline='') as f:
            f.write(f"{datetime.datetime.now()}\ngain = {self.root.sonicamp.status.gain}\ndate[Y-m-d]\ntime[H:m:s.ms]\nurms[mV]\nirms[mA]\nphase[degree]\n\n")
            csv_writer: csv.DictWriter = csv.DictWriter(
                f, fieldnames=self.fieldnames)
            csv_writer.writeheader()
    
    def start_sequence(self) -> None:
        """Starts the sequence and the measurement"""
        start: int = self.start_frq.get()
        stop: int = self.stop_frq.get()
        step: int = self.step_frq.get()
        
        self.figure_canvas.update_axes(start, stop)
        
        self.frq_list: list = []
        self.urms_list: list = []
        self.irms_list: list = []
        self.phase_list: list = []
        
        if start < 600000 or stop < 600000:
            messagebox.showinfo("Not supported values", "Please make sure that your frequency values are between 600000Hz and 6000000Hz")
            self.stop()
        
        # In case start value is higher than stop value and the sequence should be run decreasingly
        elif start > stop:
            step = -abs(step)
                
        for frq in range(start, stop, step):
            
            try:
                data: dict = self.get_data(frq)
                self.protocol("WM_DELETE_WINDOW", self.on_closing)      # tkinter protocol function to -> What function should be called when event (Window closes) happens
                print(data)
                self.plot_data(data)
                self.register_data(data)
            
            # What should be done, if connection suddelny disappears
            except serial.SerialException:
                self.root.__reinit__()
                break
        
        self.stop()
    
    def plot_data(self, data: dict) -> None:
        """Append the data to the plotted list and update
        the plot accordingly 

        Args:
            data (dict): The data that needs to be plotted, specifically with the dict keys:
                -> "frequency" (int)    : the current frequency
                -> "urms" (int)         : the current Urms (Voltage)
                -> "irms" (int)         : the current Irms (Amperage)
                -> "phase" (int)        : the current phase (Degree)
        """
        logger.info(f"SonicMeasure\tPlotting data\t{data = }")
        
        self.frq_list.append(data["frequency"])
        self.urms_list.append(data["urms"])
        self.irms_list.append(data["irms"])
        self.phase_list.append(data["phase"])
        
        self.figure_canvas.plot_urms.set_data(self.frq_list, self.urms_list)
        self.figure_canvas.plot_irms.set_data(self.frq_list, self.irms_list)
        self.figure_canvas.plot_phase.set_data(self.frq_list, self.phase_list)
        
        self.figure_canvas.draw()
        
        self.figure_canvas.ax_urms.set_ylim(
            min(self.urms_list) - min(self.urms_list) * 0.4,
            max(self.urms_list) + max(self.urms_list) * 0.2,)
        self.figure_canvas.ax_irms.set_ylim(
            min(self.irms_list) - min(self.irms_list) * 0.4,
            max(self.irms_list) + max(self.irms_list) * 0.2,)
        self.figure_canvas.ax_phase.set_ylim(
            min(self.phase_list) - min(self.phase_list) * 0.4,
            max(self.phase_list) + max(self.phase_list) * 0.2,)
        
        self.figure_canvas.flush_events()
        self.root.update()
            
    def register_data(self, data: dict) -> None:
        """Register the measured data in a csv file"""
        logger.info(f"SonicMeasrue\tRegistering data in a csv file\t{data = }")
        
        with open(f"{self._spectra_dir}//{self.spectra_file}", "a", newline='') as f:
            csv_writer: csv.DictWriter = csv.DictWriter(
                f, fieldnames=self.fieldnames)
            print(data)
            csv_writer.writerow(data)
            
    def get_data(self, frq: int) -> dict:
        """Sets the passed freqeuency and gets the new data from the change
        of state

        Args:
            frq (int): The frequency to be setted

        Returns:
            dict: The data with URMS, IRMS and PHASE
        """     
        logger.info(f"SonicMeasrue\tGetting data for\t{frq = }")
        
        self.serial.send_and_get(Command.SET_FRQ + frq)
        data_list: list = self._get_sens()
        data_dict: dict = self._list_to_dict(data_list)

        logger.info(f"SonicMeasure\tGot data\t{data_dict = }")
        return data_dict
    
    def _list_to_dict(self, data_list: list) -> dict:
        """Converts a list from the SonSens Module through the command ?sens
        to a dictionary

        Args:
            data_list (list): The data in a list

        Returns:
            dict: The data in a dictionary with the following keywords:
        """
        data_dict: dict = {
            'timestamp': datetime.datetime.now(),
            'frequency': data_list[0],
            'urms': data_list[1],
            'irms': data_list[2],
            'phase': data_list[3],}
        
        return data_dict
    
    def _get_sens(self) -> list:
        """Gets the current sensor data via the ?sens command

        Returns:
            list: The from the sonicamp returned sensor data
        """
        data_str = self.serial.send_and_get(Command.GET_SENS)
        data_list: list = [int(data) for data in data_str.split(' ') if data != None or data != '']
        
        # if the data wasn't fetched correctly, repeat until it works
        if len(data_list) < 3:
            return self._get_sens()
        
        return data_list
    
    def save(self) -> None:
        pass
    
    def publish(self) -> None:
        self.fig_frame.pack(fill=tk.BOTH, expand=True)
        self.figure_canvas._tkcanvas.pack(fill=tk.BOTH, expand=True)
        self.control_frame.pack()
        
        self.util_ctrl_frame.grid(row=0, column=0, padx=5, pady=5)
        self.frq_frame.grid(row=0, column=1, padx=5, pady=5)
        self.gain_frame.grid(row=0, column=2, padx=5, pady=5)
        
        self.start_btn.pack(expand=True, fill=tk.BOTH, padx=3, pady=3)
        # self.save_btn.pack(expand=True, fill=tk.BOTH, padx=3, pady=3)
        
        # Frq Frame
        self.start_frq_label.grid(row=0, column=0, padx=3, pady=3)
        self.start_frq_entry.grid(row=0, column=1, padx=3, pady=3)
        
        self.stop_frq_label.grid(row=1, column=0, padx=3, pady=3)
        self.stop_frq_entry.grid(row=1, column=1, padx=3, pady=3)
        
        self.step_frq_label.grid(row=2, column=0, padx=3, pady=3)
        self.step_frq_entry.grid(row=2, column=1, padx=3, pady=3)
        
        # Gain Frame
        self.start_gain_label.grid(row=0, column=0, padx=3, pady=3)
        self.start_gain_entry.grid(row=0, column=1, padx=3, pady=3)
        
        # self.stop_gain_label.grid(row=1, column=0, padx=3, pady=3)
        # self.stop_gain_entry.grid(row=1, column=1, padx=3, pady=3)
        
        # self.step_gain_label.grid(row=2, column=0, padx=3, pady=3)
        # self.step_gain_entry.grid(row=2, column=1, padx=3, pady=3)
        
        
        
        
class MeasureCanvas(FigureCanvasTkAgg):
    
    def __init__(self, parent: ttk.Frame, start_frq: int, stop_frq: int) -> None:
        self.figure: Figure = Figure()
        style.use('seaborn')
        
        self.ax_urms = self.figure.add_subplot(111)
        self.figure.subplots_adjust(right=0.8)
        
        self.ax_irms = self.ax_urms.twinx()
        self.ax_phase = self.ax_urms.twinx()
        self.ax_phase.spines['right'].set_position(("axes", 1.15))

        self.plot_urms, = self.ax_urms.plot([], [], "bo-", label="U$_{RMS}$ / mV")
        self.plot_irms, = self.ax_irms.plot([], [], "ro-", label="I$_{RMS}$ / mA")
        self.plot_phase, = self.ax_phase.plot([], [], "go-", label="Phase / °")
        
        self.ax_urms.set_xlim(start_frq, stop_frq)
        self.ax_urms.set_xlabel("Frequency / Hz")
        self.ax_urms.set_ylabel("U$_{RMS}$ / mV")
        self.ax_irms.set_ylabel("I$_{RMS}$ / mA")
        self.ax_phase.set_ylabel("Phase / °")
        
        self.ax_urms.yaxis.label.set_color(self.plot_urms.get_color())
        self.ax_irms.yaxis.label.set_color(self.plot_irms.get_color())
        self.ax_phase.yaxis.label.set_color(self.plot_phase.get_color())
        
        self.ax_urms.legend(handles=[self.plot_urms, self.plot_irms, self.plot_phase])
        super().__init__(self.figure, parent)
    
    def update_axes(self, start_frq: int, stop_frq: int) -> None:
        self.ax_urms.set_xlim(start_frq, stop_frq)