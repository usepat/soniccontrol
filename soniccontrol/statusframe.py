from __future__ import annotations

import tkinter as tk
import tkinter.ttk as ttk
import ttkbootstrap as ttkb

from typing import Union, TYPE_CHECKING

from sonicpackage import SonicAmp
from soniccontrol.sonicamp import SerialConnection
from soniccontrol.helpers import logger

if TYPE_CHECKING:
    from soniccontrol.core import Root




class StatusFrame(ttk.Frame):
    """The parent object of Status Frames, here the main objects 
    and methods are defined. So that the code stays DRY

    Inheritance:
        ttk (ttk.Frame): the frame object from tkinter the class 
        inherets from 
    """
    @property
    def root(self) -> Root:
        return self._root
    
    @property
    def serial(self) -> SerialConnection:
        return self._serial
    
    @property
    def sonicamp(self) -> SonicAmp:
        return self._sonicamp
    
    def __init__(self, parent: ttk.Frame, root: Root, *args, **kwargs) -> None:
        super().__init__(master=parent, *args, **kwargs)
        
        self._root: Root = root
        self._serial: SerialConnection = root.serial
        self._sonicamp: SonicAmp = root.sonicamp
        
        self.meter_frame: ttk.Frame = ttk.Frame(self)
        self.overview_frame: ttk.Frame = ttk.Frame(self, style="secondary.TFrame")
        
        self.frq_meter: ttkb.Meter = ttkb.Meter(
            self.meter_frame,
            bootstyle='dark',
            amounttotal=1200000 / 1000, 
            amountused=0,
            textright='kHz',
            subtext='Current Frequency',
            metersize=150)
        
        self.gain_meter: ttkb.Meter = ttkb.Meter(
            self.meter_frame,
            bootstyle='success',
            amounttotal=150,
            amountused=0,
            textright='%',
            subtext='Current Gain',
            metersize=150)
        
        self.temp_meter: ttkb.Meter = ttkb.Meter(
            self.meter_frame,
            bootstyle='warning',
            amounttotal=100,
            amountused=None,
            textright='°C',
            subtext='Thermometer not found',
            metersize=150)
        
        # Overview Frame
        self.con_status_label: ttkb.Label = ttkb.Label(
            self.overview_frame,
            font="QTypeOT-CondBook 15",
            padding=(5,0,5,0),
            justify=tk.CENTER,
            anchor=tk.CENTER,
            compound=tk.LEFT,
            width=15,
            image=self.root.led_red_img,
            bootstyle="inverse-secondary",
            text="not connected")
        
        self.sig_status_label: ttkb.Label = ttkb.Label(
            self.overview_frame,
            font="QTypeOT-CondBook 15",
            padding=(5,0,5,0),
            justify=tk.CENTER,
            anchor=tk.CENTER,
            compound=tk.LEFT,
            width=10,
            image=self.root.led_red_img,
            bootstyle="inverse-secondary",
            text="Signal OFF")
        
        self.err_status_label: ttkb.Label = ttkb.Label(
            self.overview_frame,
            font="QTypeOT-CondBook 15",
            padding=(5,5,5,5),
            justify=tk.CENTER,
            anchor=tk.CENTER,
            compound=tk.CENTER,
            relief=tk.RIDGE,
            width=10,
            text=None)
        
        logger.info(f"initialized statusframe")
        
    def attach_data(self) -> None:
        """Method to attach new data to the object, so that the 
        object adapts itself accordingly
        """
        self.frq_meter["amountused"] = self.sonicamp.status.frequency / 1000    
        self.gain_meter["amountused"] = self.root.sonicamp.status.gain
        # self.temp_meter["amountused"] = 36 #!Here
        
        self.con_status_label["image"] = self.root.led_green_img
        self.con_status_label["text"] = "connected"
        
        if self.root.sonicamp.status.signal:
            self.sig_status_label["text"] = "Signal ON"
            self.sig_status_label["image"] = self.root.led_green_img
        
        else:
            self.sig_status_label["text"] = "Signal OFF"
            self.sig_status_label["image"] = self.root.led_red_img     
            
    def abolish_data(self) -> None:
        """ Function to repeal setted values """
        self.frq_meter["amountused"] = 0
        self.gain_meter["amountused"] = 0
        self.temp_meter["amountused"] = 0
        
        self.con_status_label["image"] = self.root.led_red_img
        self.con_status_label["text"] = "Not Connected"
        
        self.sig_status_label["image"] = self.root.led_red_img
        self.sig_status_label["text"] = "Signal OFF"
        
    def show_error(self) -> None:
        """ Shows the errormessage in the overview frame"""
        for child in self.overview_frame.children.values():
            child.grid_forget()
        
        self.overview_frame["style"] = "danger.TFrame"
        self.err_status_label["text"] = None #!Here
        self.err_status_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.CENTER)
        
        


class StatusFrameWipe(StatusFrame):
    
    def __init__(self, parent: ttk.Frame, root: Root, *args, **kwargs) -> None:
        """
        Statusframe object, that is used in case the GUI is
        connected to a SonicWipe
        """
        super().__init__(parent, root, *args, **kwargs)
        
        self.seperator: ttk.Separator = ttk.Separator(
            self.meter_frame,
            orient=tk.VERTICAL,
            style="dark.TSeperator",)
        
        self.wipe_data_frame: ttk.Frame = ttk.Frame(self.meter_frame)
        self.wipe_progressbar: ttkb.Floodgauge = ttkb.Floodgauge(
            self.wipe_data_frame,
            bootstyle='primary',
            text='Wiping state',
            mode=ttkb.INDETERMINATE,
            font="Arial 15 bold",
            orient=ttkb.VERTICAL,)
        
        self.protocol_status: ttk.Label = ttk.Label(
            self.wipe_data_frame,
            textvariable=self.root.protocol,
            style="primary.TLabel",)
        
    def publish(self) -> None:
        """ Function to build the statusframe """
        self.frq_meter.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.seperator.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)
        self.wipe_data_frame.grid(row=0, column=2, padx=5, pady=5, sticky=tk.NSEW)
        
        self.wipe_progressbar.pack(side=tk.TOP, padx=5, pady=5, ipadx=5, ipady=5,)
        self.protocol_status.pack(side=tk.TOP, padx=5, pady=5)
        
        self.con_status_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.sig_status_label.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)
        
        self.meter_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH, ipadx=10, ipady=10)
        self.overview_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=0, pady=0)
        self.pack()



class StatusFrameCatch(StatusFrame):
    
    def __init__(self, parent: ttk.Frame, root: Root, *args, **kwargs) -> None:
        super().__init__(parent, root, *args, **kwargs)
        
        self.frq_meter["amounttotal"] = 6000000 / 1000
    
    def publish(self) -> None:
        self.frq_meter.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.gain_meter.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)
        self.temp_meter.grid(row=0, column=2, padx=10, pady=10, sticky=tk.NSEW)
        
        self.con_status_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.sig_status_label.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)
        
        self.meter_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH, ipadx=10, ipady=10)
        self.overview_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=0, pady=0)
        self.pack()
        
        
        
class StatusFrameDutyWipe(StatusFrame):
    
    def __init__(self, parent: ttk.Frame, root: Root, *args, **kwargs) -> None:
        super().__init__(parent, root, *args, **kwargs)
        
        self.gain_meter["amounttotal"] = 100
        
    def publish(self) -> None:
        self.gain_meter.pack()
        
        self.con_status_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.sig_status_label.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)
        
        self.meter_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH, ipadx=10, ipady=10)
        self.overview_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=0, pady=0)
        self.pack()
        
        