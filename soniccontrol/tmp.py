from __future__ import annotations

from typing import Union, TYPE_CHECKING

import tkinter as tk
import tkinter.ttk as ttk
import ttkbootstrap as ttkb

from tkinter import messagebox
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.scrolled import ScrolledFrame

from sonicpackage import Command, SerialConnection
from soniccontrol.sonicmeasure import SonicMeasure

if TYPE_CHECKING:
    from soniccontrol.core import Root
    from soniccontrol._notebook import ScNotebook
    


class Hometab(ttk.Frame):
    
    @property
    def root(self) -> Root:
        return self._root
    
    @property
    def serial(self) -> SerialConnection:
        return self._serial
    
    def __init__(self, parent: ScNotebook, root: Root, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        
        self._root: Root = root
        self._serial: SerialConnection = root.serial
        
        self._frq: tk.IntVar = tk.IntVar()
        self._gain: tk.IntVar = tk.IntVar()
        self._mode: tk.StringVar = tk.StringVar()
        self._wipe_inf_or_def: tk.BooleanVar = tk.BooleanVar()
        self._wipe_var: tk.IntVar = tk.IntVar()
        
        self.topframe: ttk.Frame = ttk.Frame(self)
        self.botframe: ttk.Frame = ttk.Frame(self)
        
        self._initialize_topframe()
        self._initialize_botframe()
        
    def _initialize_topframe(self) -> None:
        self.control_frame: ttk.LabelFrame = ttk.LabelFrame(self.topframe, text="Manual Control")
        
        self.set_val_btn: ttk.Button = ttk.Button(
            self.control_frame,
            text='Set Frequency and Gain',
            command=self.set_val,
            bootstyle='dark.TButton',
        )
        
        self._initialize_frq_frame()
        self._initialize_gain_frame()
        self._initialize_mode_frame()
        self._initialize_utils_frame()
        
        self.us_control_frame: ttk.Frame = ttk.Frame(self)
        
        self.us_on_button: ttk.Button = ttk.Button(
            self.us_control_frame,
            text='ON',
            style='success.TButton',
            width=10,
            command=self.set_signal_on
        )
        
        ToolTip(self.us_on_button, text="Turn the ultrasound signal on")
        
        self.us_off_button: ttk.Button = ttk.Button(
            self.us_control_frame,
            text='OFF',
            style='danger.TButton',
            width=10,
            command=self.set_signal_off
        )
        
        ToolTip(self.us_off_button, text="Turn the ultrasound signal off")
    
    def set_val(self) -> None:
        self.insert_feed(self.set_frq())
        self.insert_feed(self.set_gain())    
    
    def set_signal_on(self) -> None:
        self.insert_feed(
            self.serial.send_and_get(Command.SET_SIGNAL_ON)
        )
    
    def set_signal_off(self) -> None:
        self.insert_feed(
            self.serial.send_and_get(Command.SET_SIGNAL_OFF)
        )
    
    def _initialize_frq_frame(self) -> None:
        self.frq_frame: ttk.Label = ttk.Label(self.control_frame)
        
        self.frq_spinbox: ttk.Spinbox = ttk.Spinbox(
            self.frq_frame,
            increment=100,
            textvariable=self._frq,
            width=16,
            style="dark.TSpinbox",
            command=self.set_frq
        )
        
        ToolTip(
            self.frq_spinbox,
            text="Configure the frequency of your device"
        )
        
        self.scroll_digit: ttk.Spinbox = ttk.Spinbox(
            self.frq_frame,
            from_=1,
            to=6,
            increment=1,
            width=5,
            style="secondary.TSpinbox",
            command=self.set_scroll_digit,
        )
    
    def set_frq(self) -> str:
        answer: str = self.serial.send_and_get(
            Command.SET_FRQ + self._frq.get()
        )
        
        return answer
    
    def set_scroll_digit(self) -> None:
        self.frq_spinbox.config(
            increment = str(10 ** (int(self.scroll_digit.get())-1))
        )
    
    def _initialize_gain_frame(self) -> None:
        self.gain_frame: ttk.Frame = ttk.Frame(self.control_frame)
        
        self.gain_spinbox: ttk.Spinbox = ttk.Spinbox(
            self.gain_frame,
            increment=10,
            textvariable=self._gain,
            width=5,
            style='dark.TSpinbox',
            command=self.set_gain
        )
        
        ToolTip(
            self.gain_frame, 
            text="Configure the gain for your device"
        )
        
        self.gain_scale: ttk.Scale = ttk.Scale(
            self.gain_frame,
            length=180,
            orient=tk.HORIZONTAL,
            style="primary.TScale",
            variable=self._gain,
        )
        
    def set_gain(self) -> None:
        answer: str = self.serial.send_and_get(
            Command.SET_GAIN + self._gain.get()
        )
        
        return answer
    
    def _initialize_mode_frame(self) -> None:
        self.mode_frame: ttk.Label = ttk.Label(self.control_frame)
        
        self.wipemode_button: ttkb.Radiobutton = ttkb.Radiobutton(
            self.mode_frame,
            text='Wipe mode',
            value=False,
            variable=self._mode,
            bootstyle='dark-outline-toolbutton',
            width=12,
            command=self.change_mode
        )
        
        self.catchmode_button: ttkb.Radiobutton = ttkb.Radiobutton(
            self.frq_mode_frame,
            text='Catch mode',
            value=True,
            variable=self._mode,
            bootstyle='dark-outline-toolbutton',
            width=12,
            command=self.change_mode
        )
        
    def change_mode(self) -> None:
        pass
    
    def _initialize_utils_frame(self) -> None:
        self.utils_frame: ttk.Frame = ttk.Frame(self.topframe)
        
        self.sonic_measure_button: ttk.Button = ttk.Button(
            self.utils_frame,
            text='Sonic measure',
            style='dark.TButton',
            image=self.root.graph_img,
            compound=tk.TOP,
            command=self.publish_sonicmeasure
        )
        
        self.serial_monitor_btn: ttk.Button = ttk.Button(
            self.utils_frame,
            text='Serial Monitor',
            style='secondary.TButton',
            width=12,
            command=self.root.publish_serial_monitor,
        )
        
    def publish_sonicmeasure(self) -> None:
        self.sonicmeasure: SonicMeasure = SonicMeasure(self.root)
    
    def _initialize_botframe(self) -> None:
        self.output_frame: ttk.Frame = ttk.LabelFrame(self.botframe, text="Feedback")
        
        self.feedback_frame: ScrolledFrame = ScrolledFrame(
            self.output_frame,
            height=200,
            width=300,   
        )
        
        self.feedback_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.output_frame.pack(anchor=tk.N, side=tk.TOP, padx=10, pady=10, expand=True, fill=tk.BOTH)
        self.botframe.pack(side=tk.TOP)
        
    def insert_feed(self, text: str) -> None:
        if text is list:
            text = ' '.join(text)
        
        ttk.Label(
            self.feedback_frame, 
            text=text, 
            font=("Consolas", 10)
        ).pack(fill=tk.X, side=tk.TOP, anchor=tk.W)
        
        self.feedback_frame.update()
        self.feedback_frame.yview_moveto(1)
        
    def attach_data(self) -> None:
        pass
        
    def publish(self) -> None:
        pass
    

class HometabOldCatch(Hometab):
    
    def __init__(self, parent: ScNotebook, root: Root, *args, **kwargs) -> None:
        super().__init__(parent, root, *args, **kwargs)
        
    def _initialize_frq_frame(self) -> None:
        super()._initialize_frq_frame()
        
        self.frq_spinbox.configure(from_=50000, to=6000000)
        
    def _initialize_gain_frame(self) -> None:
        super()._initialize_gain_frame()
        
        self.gain_spinbox.configure(from_=0, to=150)
        self.gain_scale.configure(from_=0, to=150)
        
    def set_frq(self) -> None:
        return super().set_frq()
    
    def set_gain(self) -> None:
        return super().set_gain()
    
    def set_val(self) -> None:
        return super().set_val()
    
    def set_signal_on(self) -> None:
        return super().set_signal_on()
    
    def set_signal_off(self) -> None:
        return super().set_signal_off()
    
    def change_mode(self) -> None:
        frq_mode: bool = self._frq_mode.get()
        
        if frq_mode:
            answer: str = self.serial.send_and_get(Command.SET_MHZ)
        else:
            answer: str = self.serial.send_and_get(Command.SET_KHZ)
            
        self.insert_feed(answer)
    
    def attach_data(self) -> None:
        return super().attach_data()
    
    def publish(self) -> None:
        self.frq_spinbox.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.scroll_digit.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)
        
        self.gain_spinbox.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.gain_scale.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)
        
        self.wipemode_button.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.catchmode_button.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)
        
        self.frq_frame.pack(side=tk.TOP, expand=True, fill=tk.X)
        self.gain_frame.pack(side=tk.TOP, expand=True, fill=tk.X)
        self.mode_frame.pack(side=tk.TOP, expand=True, fill=tk.X)
        self.set_val_btn.pack(side=tk.TOP, expand=True, fill=tk.X, padx=10, pady=10)
        self.sonic_measure_button.pack(side=tk.TOP, padx=10, pady=10)
        self.serial_monitor_btn.pack(side=tk.TOP, padx=10, pady=5, expand=True, fill=tk.BOTH)
        
        self.control_frame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.utils_frame.grid(row=0, column=1, padx=20, pady=20, sticky=tk.NSEW)

        self.us_on_button.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.us_off_button.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)

        self.topframe.pack(side=tk.TOP, padx=10, pady=10)
        self.us_control_frame.pack(side=tk.TOP, padx=10, pady=10)
    

class HometabOldWipe(Hometab):
    
    def __init__(self, parent: ScNotebook, root: Root, *args, **kwargs) -> None:
        super().__init__(parent, root, *args, **kwargs)
        
        self._initialize_wipeframe()
        
        self.us_on_button: ttk.Button = ttk.Button(
            self.frq_control_frame,
            text='ON',
            style='success.TButton',
            width=10,
            command=self.set_signal_on)
        
        ToolTip(self.us_on_button, text="Turn the ultrasound signal on")
        
        self.us_off_button: ttk.Button = ttk.Button(
            self.topframe,
            text='OFF',
            style='danger.TButton',
            width=10,
            command=self.set_signal_off
        )
        
        ToolTip(self.us_off_button, text="Turn the ultrasound signal off")
        
    def _initialize_frq_frame(self) -> None:
        super()._initialize_frq_frame()
        self.frq_spinbox.configure(from_=50000, to=1200000)
        
    
    def _initialize_wipeframe(self) -> None:
        self.wipe_frame: ttk.LabelFrame = ttk.LabelFrame(self.topframe, text='Set up wiping')
        
        self.wipe_spinbox: ttk.Spinbox = ttk.Spinbox(
            self.wipe_frame,
            from_=1,
            increment=5,
            to=100,
            textvariable=self.wipe_var, 
            width=16,
            style='dark.TSpinbox',
        )
        
        ToolTip(self.wipe_spinbox, text="Set up wipe cycles")
        
        self.wipe_mode_frame: ttk.Label = ttk.Label(self.wipe_frame)
        
        self.def_wipe_button: ttkb.Radiobutton = ttkb.Radiobutton(
            self.wipe_mode_frame,
            text='Definite',
            value=True,
            variable=self._wipe_inf_or_def,
            bootstyle='dark-outline-toolbutton',
            width=6,
            command=self.handle_wipe_mode
        )
        
        self.inf_wipe_button: ttkb.Radiobutton = ttkb.Radiobutton(
            self.wipe_mode_frame,
            text='Infinite',
            value=False,
            variable=self._wipe_inf_or_def,
            bootstyle='dark-outline-toolbutton',
            width=6,
            command=self.handle_wipe_mode
        )
        
        self.start_wipe_button: ttk.Button = ttk.Button(
            self.wipe_frame,
            text='WIPE',
            style='primary.TButton',
            command=self.start_wiping
        )
        
    def handle_wipe_mode(self) -> None:
        if self.wipe_mode.get():
            self.wipe_spinbox.config(state=tk.NORMAL)
        
        else:
            self.wipe_spinbox.config(state=tk.DISABLED)
            
    def set_frq(self) -> None:
        return super().set_frq()
    
    def set_signal_on(self) -> None:
        return super().set_signal_on()
    
    def set_signal_off(self) -> None:
        self.root.wipe_mode.set(0)
        self.root.status_frame.wipe_progressbar.stop()
        return super().set_signal_off()
    
    def start_wiping(self) -> None:
        wipe_runs: int = self.wipe_mode.get()
        
        if wipe_runs:
            self.insert_feed(self.serial.send_get(Command.SET_WIPE_DEF + self.wipe_var.get()))
        
        else:
            self.insert_feed(self.serial.send_get(Command.SET_WIPE_INF))
            
        self.root.status_frame.wipe_progressbar.start()
        self.root.wipe_mode.set(1)
        
    def attach_data(self) -> None:
        return super().attach_data()
        
    def publish(self) -> None:
        """ Function to build children of this frame """
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
    

class HometabDutyWipe(Hometab):
    
    def __init__(self, parent: ScNotebook, root: Root, *args, **kwargs) -> None:
        super().__init__(parent, root, *args, **kwargs)
        
        self.gain_spinbox: ttk.Spinbox = ttk.Spinbox(
            self.control_frame,
            from_=0,
            increment=10,
            to=100,
            textvariable=self.root.gain,
            width=5,
            style='dark.TSpinbox',
        )
        
        ToolTip(self.gain_spinbox, text="Configure the gain for your device")
        
        self.set_val_btn: ttk.Button = ttk.Button(
            self.control_frame,
            text='Set Gain',
            command=self.set_gain,
            bootstyle='dark.TButton',
        )
        
        self.gain_scale: ttk.Scale = ttk.Scale(
            self.topframe,
            from_=0,
            to=100,
            name='gainscale',
            length=180,
            orient=tk.VERTICAL,
            style="primary.TScale",
            variable=self.root.gain,
        )
    
    def set_gain(self) -> None:
        return super().set_gain()
    
    def set_signal_on(self) -> None:
        return super().set_signal_on()
    
    def set_signal_off(self) -> None:
        return super().set_signal_off()
    
    def publish(self) -> None:
        """
        Method to publish children for the SonicWipe 40kHz Duty Cycle amp
        """
        self.gain_spinbox.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=5, pady=5)
        self.set_val_btn.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=5, pady=5)
        self.us_on_button.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=5, pady=5)
        self.us_off_button.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=5, pady=5)
        
        self.control_frame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.gain_scale.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)
        
        self.topframe.pack(side=tk.TOP, padx=10, pady=10)
        

class HometabCatch(Hometab):
    
    def __init__(self, parent: ScNotebook, root: Root, *args, **kwargs) -> None:
        super().__init__(parent, root, *args, **kwargs)
        
    def change_mode(self) -> None:
        return super().change_mode()
    
    def attach_data(self) -> None:
        return super().attach_data()
    
    def publish(self) -> None:
        return super().publish()
    

class HometabWipe(Hometab):
    
    def __init__(self, parent: ScNotebook, root: Root, *args, **kwargs) -> None:
        super().__init__(parent, root, *args, **kwargs)
        
    def attach_data(self) -> None:
        return super().attach_data()
    
    def publish(self) -> None:
        return super().publish()
    
    
        

    