from __future__ import annotations

import tkinter as tk
import tkinter.ttk as ttk
import ttkbootstrap as ttkb

from typing import TYPE_CHECKING

from sonicpackage import SonicAmp
from soniccontrol.sonicamp import SerialConnection
from soniccontrol.helpers import logger

if TYPE_CHECKING:
    from soniccontrol.core import Root


class StatusFrame(ttk.Frame):
    """
    The parent object of Status Frames, here the main objects
    and methods are defined. So that the code stays DRY

    Inheritance:
        ttk (ttk.Frame): the frame object from tkinter the class
        inherets from
    """
    NOT_CONN_TXT: str = "not connected"
    CONN_TXT: str = "connected"
    ON_TXT: str = "Signal ON"
    OFF_TXT: str = "Signal OFF"

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
        
        self._is_on: bool = False
        self._is_connected: bool = False
        self._gain_using: int = 0
        self._frq_using: int = 0
        self._temp_using: int = 0
        self._urms_using: int = None
        self._irms_using: int = None
        self._phase_using: int = None

        self.meter_frame: ttk.Frame = ttk.Frame(self)
        self.overview_frame: ttk.Frame = ttk.Frame(self, style="secondary.TFrame")
        self.sonsens_frame: ttk.Frame = ttk.Frame(self)

        # Meter Frame
        self.frq_meter: ttkb.Meter = ttkb.Meter(
            self.meter_frame,
            bootstyle=ttkb.DARK,
            amounttotal=1200000 / 1000,
            amountused=self._frq_using,
            textright="kHz",
            subtext="Current Frequency",
            metersize=150,
        )

        self.gain_meter: ttkb.Meter = ttkb.Meter(
            self.meter_frame,
            bootstyle=ttkb.SUCCESS,
            amounttotal=150,
            amountused=self._gain_using,
            textright="%",
            subtext="Current Gain",
            metersize=150,
        )

        self.temp_meter: ttkb.Meter = ttkb.Meter(
            self.meter_frame,
            bootstyle=ttkb.WARNING,
            amounttotal=100,
            amountused=self._temp_using,
            textright="°C",
            subtext="Thermometer not found",
            metersize=150,
        )
        
        # SonSens Frame
        self.urms_label: ttk.Label = ttk.Label(
            self.sonsens_frame, 
            font=self.root.qtype12, 
            anchor=tk.CENTER,
            style='primary.TLabel',
            padding=(5, 0, 20, 0),
        )
        self.irms_label: ttk.Label = ttk.Label(
            self.sonsens_frame, 
            font=self.root.qtype12, 
            anchor=tk.CENTER,
            style='danger.TLabel',
            padding=(20, 0, 20, 0),
        )        
        self.phase_label: ttk.Label = ttk.Label(
            self.sonsens_frame, 
            font=self.root.qtype12, 
            anchor=tk.CENTER,
            style='success.TLabel',
            padding=(20, 0, 5, 0),
        )

        # Overview Frame
        self.con_status_label: ttkb.Label = ttkb.Label(
            self.overview_frame,
            font="QTypeOT-CondBook 15",
            padding=(5, 0, 5, 0),
            justify=tk.CENTER,
            anchor=tk.CENTER,
            compound=tk.LEFT,
            width=15,
            image=self.root.LED_RED_IMG,
            bootstyle="inverse-secondary",
            text=self.NOT_CONN_TXT,
        )

        self.sig_status_label: ttkb.Label = ttkb.Label(
            self.overview_frame,
            font="QTypeOT-CondBook 15",
            padding=(5, 0, 5, 0),
            justify=tk.CENTER,
            anchor=tk.CENTER,
            compound=tk.LEFT,
            width=10,
            image=self.root.LED_RED_IMG,
            bootstyle="inverse-secondary",
            text=self.OFF_TXT,
        )

        self.err_status_label: ttkb.Label = ttkb.Label(
            self.overview_frame,
            font="QTypeOT-CondBook 15",
            padding=(5, 5, 5, 5),
            justify=tk.CENTER,
            anchor=tk.CENTER,
            compound=tk.CENTER,
            relief=tk.RIDGE,
            width=10,
            text=None,
        )
        
    def signal_on(self) -> None:
        """
        Method that changes the appearance of the statusframe to
        indicate that the US output signal of the SonicAmp is on
        """
        if not self._is_on:
            
            self.sig_status_label["image"] = self.root.LED_GREEN_IMG
            self.sig_status_label["text"] = self.ON_TXT
            
            self._is_on: bool = True
        
    def signal_off(self) -> None:
        """
        Method that changes the appearance of the statusframe to
        indicate that the US output signal of the SonicAmp is off
        """ 
        if self._is_on:
            
            self.sig_status_label["image"] = self.root.LED_RED_IMG
            self.sig_status_label["text"] = self.OFF_TXT
            
            self._is_on: bool = False
            
    def connection_off(self) -> None:
        """
        Method that changes the appearance of the statusframe to
        indicate that the connection to the SonicAmp is not there
        """
        if self._is_connected:
            
            self.con_status_label["image"] = self.root.LED_RED_IMG
            self.con_status_label["text"] = self.NOT_CONN_TXT
            
            self._is_connected: bool = False
            
    def connection_on(self) -> None:
        """
        Method that changes the appearance of the statusframe to
        indicate that the connection to a SonicAmp is there
        """
        if not self._is_connected:
            
            self.con_status_label["image"] = self.root.LED_GREEN_IMG
            self.con_status_label["text"] = self.CONN_TXT
            
            self._is_connected: bool = True
        
    def show_error(self) -> None:
        """
        Method to show an internal error, that originates in the 
        SonicAmp
        """
        for child in self.overview_frame.children.values():
            child.grid_forget()

        self.overview_frame["style"] = "danger.TFrame"
        self.err_status_label["text"] = None  #!Here
        self.err_status_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.CENTER)
    
    def change_values(
        self, 
        frq: int = None, 
        gain: int = None, 
        temp: int = None, 
        urms: int = None, 
        irms: int = None, 
        phase: int = None
    ) -> None:
        """
        Method that changes the values of the meter frame so that the passed
        values are indicated. Only those values that, are passed are updated,
        and even then only if that value is not already shown

        Args:
            frq (int, optional): The frequency value to show. Defaults to None.
            gain (int, optional): The gain value to show. Defaults to None.
            temp (int, optional): The temp value to show. Defaults to None.
        """
        if isinstance(frq, int) and frq != self._frq_using:
            
            self.frq_meter["amountused"] = frq / 1000
            self._frq_using: int = frq
        
        if isinstance(gain, int) and gain != self._gain_using:
            
            self.gain_meter["amountused"] = gain
            self._gain_using: int = gain
        
        if isinstance(temp, int) and temp != self._temp_using:
            
            self.temp_meter["amountused"] = temp
            self._temp_using: int = temp
            
        if isinstance(urms, int) and urms != self._urms_using:
            
            self.urms_label["text"] = f"Urms: {urms}mV"
            self._urms_using: int = urms
        
        if isinstance(irms, int) and irms != self._irms_using:
            
            self.irms_label["text"] = f"Irms: {irms}mA"
            self._irms_using: int = irms
        
        if isinstance(phase, int) and phase != self._phase_using:
            
            self.phase_label["text"] = f"Phase: {phase}˚"
            self._phase_using: int = phase    

    def attach_data(self) -> None:
        """
        Method to attach new data to the object, so that the
        object adapts itself accordingly
        """
        self.change_values(
            frq=self.sonicamp.status.frequency,
            gain=self.sonicamp.status.gain,
            urms=self.sonicamp.status.urms,
            irms=self.sonicamp.status.irms,
            phase=self.sonicamp.status.phase,
        )

        self.connection_on()

        if self.root.sonicamp.status.signal:
            self.signal_on()

        else:
            self.signal_off()

    def abolish_data(self) -> None:
        """
        Function to repeal setted values
        """
        self.change_values(
            frq=0,
            gain=0,
            temp=0,
        )

        self.connection_off()
        self.signal_off()
        


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
            style="dark.TSeperator",
        )

        self.wipe_data_frame: ttk.Frame = ttk.Frame(self.meter_frame)
        self.wipe_progressbar: ttkb.Floodgauge = ttkb.Floodgauge(
            self.wipe_data_frame,
            bootstyle=ttkb.PRIMARY,
            text="Wiping state",
            mode=ttkb.INDETERMINATE,
            font="Arial 15 bold",
            orient=ttkb.VERTICAL,
        )

        self.protocol_status: ttk.Label = ttk.Label(
            self.wipe_data_frame,
            textvariable=self.root.protocol,
            style="primary.TLabel",
        )

    def publish(self) -> None:
        """Function to build the statusframe"""
        self.frq_meter.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.seperator.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)
        self.wipe_data_frame.grid(row=0, column=2, padx=5, pady=5, sticky=tk.NSEW)

        self.wipe_progressbar.pack(
            side=tk.TOP,
            padx=5,
            pady=5,
            ipadx=5,
            ipady=5,
        )
        self.protocol_status.pack(side=tk.TOP, padx=5, pady=5)

        self.con_status_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.sig_status_label.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)

        self.meter_frame.pack(
            side=tk.TOP, expand=True, fill=tk.BOTH, ipadx=10, ipady=10
        )
        self.overview_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=0, pady=0)
        self.pack()


class StatusFrameCatch(StatusFrame):
    def __init__(self, parent: ttk.Frame, root: Root, *args, **kwargs) -> None:
        super().__init__(parent, root, *args, **kwargs)

        self.frq_meter["amounttotal"] = 6000000 / 1000

    def publish(self) -> None:
        self.frq_meter.grid(row=0, column=0, padx=10, sticky=tk.NSEW)
        self.gain_meter.grid(row=0, column=1, padx=10, sticky=tk.NSEW)
        self.temp_meter.grid(row=0, column=2, padx=10, sticky=tk.NSEW)

        self.urms_label.grid(row=0, column=0, sticky=tk.NSEW)
        self.irms_label.grid(row=0, column=1, sticky=tk.NSEW)
        self.phase_label.grid(row=0, column=2, sticky=tk.NSEW)

        self.con_status_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.sig_status_label.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)

        self.meter_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self.sonsens_frame.pack(side=tk.TOP, expand=True, padx=5, pady=5, anchor=tk.CENTER)
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

        self.meter_frame.pack(
            side=tk.TOP, expand=True, fill=tk.BOTH, ipadx=10, ipady=10
        )
        self.overview_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=0, pady=0)
        self.pack()
        
    def attach_data(self) -> None:
        pass
