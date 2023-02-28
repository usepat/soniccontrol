from __future__ import annotations

import tkinter as tk
import tkinter.ttk as ttk
import ttkbootstrap as ttkb

from typing import TYPE_CHECKING, Optional, Union

from sonicpackage import SonicInterface, Status, SerialConnection, SonicAmp
from soniccontrol.helpers import logger
import soniccontrol.constants as const

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
        super().__init__(parent, *args, **kwargs)

        self._root: Root = root
        self._serial: SerialConnection = root.serial
        self._sonicamp: SonicAmp = root.sonicamp

        self._is_on: bool = False
        self._is_connected: bool = False
        self._gain_using: int = 0
        self._freq_using: int = 0
        self._temp_using: float = 0
        self._urms_using: Optional[int] = None
        self._irms_using: Optional[int] = None
        self._phase_using: Optional[int] = None

        self.meter_frame: ttk.Frame = ttk.Frame(self)
        self.overview_frame: ttk.Frame = ttk.Frame(self, style="secondary.TFrame")
        self.sonsens_frame: ttk.Frame = ttk.Frame(self)

        # Meter Frame
        self.freq_meter: ttkb.Meter = ttkb.Meter(
            self.meter_frame,
            bootstyle=ttkb.DARK,
            amounttotal=self.sonicamp.mode.freq_stop / const.DIVIDE_TO_KHZ,
            amountused=self._freq_using,
            textright="kHz",
            subtext="Current Frequency",
            metersize=150,
        )

        self.gain_meter: ttkb.Meter = ttkb.Meter(
            self.meter_frame,
            bootstyle=ttkb.SUCCESS,
            amounttotal=self.sonicamp.mode.gain_stop,
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

        logger.debug("Initialized statusframe")

    def signal_on(self) -> None:
        """
        Method that changes the appearance of the statusframe to
        indicate that the US output signal of the SonicAmp is on
        """
        if self._is_on:
            return

        self.sig_status_label["image"] = self.root.LED_GREEN_IMG
        self.sig_status_label["text"] = self.ON_TXT
        
        self._is_on = True
        
    def signal_off(self) -> None:
        """
        Method that changes the appearance of the statusframe to
        indicate that the US output signal of the SonicAmp is off
        """ 
        if not self._is_on:
            return

        self.sig_status_label["image"] = self.root.LED_RED_IMG
        self.sig_status_label["text"] = self.OFF_TXT

        self._is_on = False

    def connection_off(self) -> None:
        """
        Method that changes the appearance of the statusframe to
        indicate that the connection to the SonicAmp is not there
        """
        if not self._is_connected:
            return

        self.con_status_label["image"] = self.root.LED_RED_IMG
        self.con_status_label["text"] = self.NOT_CONN_TXT

        self._is_connected = False

    def connection_on(self) -> None:
        """
        Method that changes the appearance of the statusframe to
        indicate that the connection to a SonicAmp is there
        """
        if self._is_connected:
            return

        self.con_status_label["image"] = self.root.LED_GREEN_IMG
        self.con_status_label["text"] = self.CONN_TXT

        self._is_connected = True

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
    
    def change_values(self, status: Status) -> None:
        self.update_freq(status)
        self.update_gain(status)
        self.update_temp(status)
        self.update_urms(status)
        self.update_irms(status)
        self.update_phase(status)

    def attach_data(self) -> None:
        """
        Method to attach new data to the object, so that the
        object adapts itself accordingly
        """
        self.change_values(self.sonicamp.status)
        self.connection_on()
        self.signal_on() if self.root.sonicamp.status.signal else self.signal_off()

    def update_freq(self, status: Union[int, Status]) -> None:
        if not (isinstance(status.frequency, int) and status.frequency != self._freq_using):
            return

        self.freq_meter['amounttotal'] = self.sonicamp.mode.freq_stop / const.DIVIDE_TO_KHZ
        self.freq_meter['amountused'] = status.frequency / const.DIVIDE_TO_KHZ
        self._freq_using = status.frequency

    def update_gain(self, status: Status) -> None:
        if not (isinstance(status.gain, int) and status.gain != self._gain_using):
            return

        self.gain_meter['amounttotal'] = self.sonicamp.mode.freq_stop
        self.gain_meter['amountused'] = status.gain
        self._gain_using = status.gain

    def update_temp(self, status: Status) -> None:
        temp: float = (
            status.temperature 
            if (status.temperature is None or status.temperature > 0) 
            else status.temperature * -1
        )

        if not (
            isinstance(status.temperature, float) 
            and status.temperature != self._temp_using
        ):
            self.temp_meter['subtext'] = 'Thermometer not found'
            return

        if temp < 0:
            self.temp_meter['amounttotal'] = const.MAX_NEGATIVE_TEMP
            self.temp_meter['bootstyle'] = ttkb.INFO
            self.temp_meter['subtext'] = 'Negative Temperature'
        else:
            self.temp_meter['amounttotal'] = const.MAX_POSITIVE_TEMP
            self.temp_meter['bootstyle'] = ttkb.WARNING
            self.temp_meter['subtext'] = 'Positive Temperature'

        self.temp_meter['amountused'] = temp
        self._temp_using = temp

    def update_urms(self, status: Status) -> None:
        if not (isinstance(status.urms, int) and status.urms != self._urms_using):
            return

        self.urms_label['text'] = f'Urms: {status.urms}mV'
        self._urms_using: int = status.urms

    def update_irms(self, status: Status) -> None:
        if not (isinstance(status.irms, int) and status.irms != self._irms_using):
            return

        self.irms_label['text'] = f'Irms: {status.irms}mA'
        self._irms_using = status.irms

    def update_phase(self, status: Status) -> None:
        if not (isinstance(status.phase, int) and status.phase != self._phase_using):
            return

        self.phase_label['text'] = f'Phase: {status.phase}˚'
        self._phase_using = status.phase  

    def abolish_data(self) -> None:
        self.connection_off()
        self.signal_off()


class StatusFrameWipeOld(StatusFrame):
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
        self.freq_meter.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.seperator.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)
        self.wipe_data_frame.grid(row=0, column=2, padx=5, pady=5, sticky=tk.NSEW)

        self.wipe_progressbar.pack(
            side=tk.TOP,
            padx=5,
            pady=5,
            ipadx=5,
            ipady=5,
        )
        # self.protocol_status.pack(side=tk.TOP, padx=5, pady=5)

        self.con_status_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.sig_status_label.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)

        self.meter_frame.pack(
            side=tk.TOP, expand=True, fill=tk.BOTH, ipadx=10, ipady=10
        )
        self.overview_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=0, pady=0)
        self.pack()


class StatusFrameWipe(StatusFrame):

    def __init__(self, parent: ttk.Frame, root: Root, *args, **kwargs) -> None:
        super().__init__(parent, root, *args, **kwargs)

    def publish(self) -> None:
        self.freq_meter.grid(row=0, column=0, padx=10, sticky=tk.NSEW)
        self.gain_meter.grid(row=0, column=1, padx=10, sticky=tk.NSEW)
        self.temp_meter.grid(row=0, column=2, padx=10, sticky=tk.NSEW)

        self.con_status_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.sig_status_label.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)

        self.meter_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self.sonsens_frame.pack(side=tk.TOP, expand=True, padx=5, pady=5, anchor=tk.CENTER)
        self.overview_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=0, pady=0)
        self.pack()


class StatusFrameCatch(StatusFrame):
    def __init__(self, parent: ttk.Frame, root: Root, *args, **kwargs) -> None:
        super().__init__(parent, root, *args, **kwargs)
        self.freq_meter['amountttotal'] = 6_000_000 / const.DIVIDE_TO_KHZ

    def publish(self) -> None:
        self.freq_meter.grid(row=0, column=0, padx=10, sticky=tk.NSEW)
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


class StatusFrame40KHZ(StatusFrame):
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
