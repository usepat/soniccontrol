from __future__ import annotations

import typing
import tkinter as tk
import tkinter.ttk as ttk
import ttkbootstrap as ttkb
import traceback

from tkinter import messagebox
from ttkbootstrap.scrolled import ScrolledFrame

from sonicpackage import (
    Command,
    SerialConnection,
    KhzMode,
    MhzMode,
    CatchMode,
    WipeMode,
    SonicInterface,
    ValueNotSupported
)
from soniccontrol.sonicmeasure import SonicMeasureWindow
from soniccontrol.helpers import ToolTip, logger

if typing.TYPE_CHECKING:
    from soniccontrol.core import Root
    from soniccontrol._notebook import ScNotebook


class Hometab(ttk.Frame):
    
    @property
    def root(self) -> Root:
        return self._root

    @property
    def serial(self) -> SerialConnection:
        return self._serial

    @property
    def amp_controller(self) -> SonicInterface:
        return self._amp_controller

    def __init__(self, parent: ScNotebook, root: Root, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)

        self._root: Root = root
        self._serial: SerialConnection = root.serial
        self._amp_controller: SonicInterface = root.amp_controller

        self._freq: tk.IntVar = tk.IntVar(value=self.root.sonicamp.status.frequency)
        self._gain: tk.IntVar = tk.IntVar(value=self.root.sonicamp.status.gain)
        self._mode: tk.StringVar = tk.StringVar()
        self._wipe_inf_or_def: tk.BooleanVar = tk.BooleanVar()
        self._wipe_var: tk.IntVar = tk.IntVar()

        self.topframe: ttk.Frame = ttk.Frame(self)
        self.botframe: ttk.Frame = ttk.Frame(self)

        self._initialize_topframe()
        self._initialize_botframe()

        logger.debug("Initialized hometab")

    def _initialize_topframe(self) -> None:
        self.control_frame: ttk.LabelFrame = ttk.LabelFrame(
            self.topframe, text="Manual Control"
        )
        self.set_val_btn: ttk.Button = ttk.Button(
            self.control_frame,
            text="Set Frequency and Gain",
            command=self.set_val,
            bootstyle="dark.TButton",
        )

        self._initialize_freq_frame()
        self._initialize_gain_frame()
        self._initialize_mode_frame()
        self._initialize_utils_frame()

        self.us_control_frame: ttk.Frame = ttk.Frame(self)
        self.us_on_button: ttk.Button = ttk.Button(
            self.us_control_frame,
            text="ON",
            style="success.TButton",
            width=10,
            command=self.set_signal_on,
        )
        ToolTip(self.us_on_button, text="Turn the ultrasound signal on")

        self.us_auto_button: ttk.Button = ttk.Button(
            self.us_control_frame,
            text="AUTO",
            style="primary.TButton",
            width=10,
            command=self.set_signal_auto,
        )
        ToolTip(self.us_auto_button, text="Turn on the AUTO mode")

        self.us_off_button: ttk.Button = ttk.Button(
            self.us_control_frame,
            text="OFF",
            style="danger.TButton",
            width=10,
            command=self.set_signal_off,
        )
        ToolTip(self.us_off_button, text="Turn the ultrasound signal off")

    def _initialize_freq_frame(self) -> None:
        self.freq_frame: ttk.Label = ttk.Label(self.control_frame)
        self.freq_spinbox: ttk.Spinbox = ttk.Spinbox(
            self.freq_frame,
            increment=100,
            textvariable=self._freq,
            width=16,
            style="dark.TSpinbox",
            command=self.set_freq,
        )
        ToolTip(self.freq_spinbox, text="Configure the frequency of your device")

        self.scroll_digit: ttk.Spinbox = ttk.Spinbox(
            self.freq_frame,
            from_=1,
            to=6,
            increment=1,
            width=5,
            style="secondary.TSpinbox",
            command=self.set_scroll_digit,
        )

    def _initialize_gain_frame(self) -> None:
        self.gain_frame: ttk.Frame = ttk.Frame(self.control_frame)
        self.gain_spinbox: ttk.Spinbox = ttk.Spinbox(
            self.gain_frame,
            increment=10,
            textvariable=self._gain,
            width=5,
            style="dark.TSpinbox",
            command=self.set_gain,
        )
        ToolTip(self.gain_frame, text="Configure the gain for your device")

        self.gain_scale: ttk.Scale = ttk.Scale(
            self.gain_frame,
            length=180,
            orient=tk.HORIZONTAL,
            style="primary.TScale",
            variable=self._gain,
        )

    def _initialize_mode_frame(self) -> None:
        self.mode_frame: ttk.Label = ttk.Label(self.control_frame)
        self.wipemode_button: ttkb.Radiobutton = ttkb.Radiobutton(
            self.mode_frame,
            text="Wipe mode",
            variable=self._mode,
            bootstyle="dark-outline-toolbutton",
            width=12,
            command=self.change_mode,
        )

        self.catchmode_button: ttkb.Radiobutton = ttkb.Radiobutton(
            self.mode_frame,
            text="Catch mode",
            variable=self._mode,
            bootstyle="dark-outline-toolbutton",
            width=12,
            command=self.change_mode,
        )

    def _initialize_utils_frame(self) -> None:
        self.utils_frame: ttk.Frame = ttk.Frame(self.topframe)
        self.sonic_measure_button: ttk.Button = ttk.Button(
            self.utils_frame,
            text="Sonic measure",
            style="dark.TButton",
            image=self.root.GRAPH_IMG,
            compound=tk.TOP,
            command=self.root.publish_sonicmeasure,
        )

        self.serial_monitor_btn: ttk.Button = ttk.Button(
            self.utils_frame,
            text="Serial Monitor",
            style="secondary.TButton",
            width=12,
            command=self.root.publish_serial_monitor,
        )

    def _initialize_botframe(self) -> None:
        self.output_frame: ttk.Frame = ttk.LabelFrame(self.botframe, text="Feedback")
        self.feedback_frame: ScrolledFrame = ScrolledFrame(
            self.output_frame,
            height=200,
            width=475,
        )

    def set_val(self) -> None:
        try:
            self.insert_feed(self.set_freq(True))
            self.insert_feed(self.set_gain(True))
        except ValueNotSupported as ve:
            messagebox.showerror(
                "Wrong frequency and/ or gain",
                f"The {self.root.sonicamp.type_} does not support the values you wanted to set"
            )

    def set_signal_on(self) -> None:
        self.insert_feed(self.amp_controller.set_signal_on())

    def set_signal_auto(self) -> None:
        self.insert_feed(self.amp_controller.set_signal_auto())
        self._set_khz()

    def set_signal_off(self) -> None:
        self.insert_feed(self.amp_controller.set_signal_off())

    def set_freq(self, called: bool = False) -> str:
        try:
            answer: str = self.root.sonicamp.set_freq(self._freq.get())
            return answer

        except ValueNotSupported as e:
            logger.debug(traceback.format_exc())
            if called: raise ValueNotSupported(e)
            messagebox.showwarning(
                "Value out of supported range",
                f"The value of frequency, you want to set is not supported under the current configurtation. The supported range is currently from {self.root.sonicamp.mode.freq_start} to {self.root.sonicamp.mode.freq_stop}",
            )

    def _set_khz(self) -> None:
        for child in self.gain_frame.children.values():
            child.configure(state=tk.DISABLED)
        self._mode.set("khz")

    def _set_mhz(self) -> None:
        for child in self.gain_frame.children.values():
            child.configure(state=tk.NORMAL)
        self._mode.set("mhz")

    def set_gain(self, called: bool = False) -> None:
        try:
            answer: str = self.root.sonicamp.set_gain(self._gain.get())
            return answer

        except ValueNotSupported as e:
            logger.debug(traceback.format_exc())
            if called: raise ValueNotSupported(e)
            messagebox.showwarning(
                "Value out of supported range",
                f"The value of gain, you want to set is not supported under the current configurtation. The supported range is currently from {self.root.sonicamp.mode.gain_start} to {self.root.sonicamp.mode.gain_stop}",
            )

    def set_scroll_digit(self) -> None:
        self.freq_spinbox.config(
            increment=str(10 ** (int(self.scroll_digit.get()) - 1))
        )

    def change_mode(self) -> None:
        pass

    def insert_feed(self, text: str) -> None:
        if text is list: text = " ".join(text)

        ttk.Label(self.feedback_frame, text=text, font=("Consolas", 10)).pack(
            fill=tk.X, side=tk.TOP, anchor=tk.W
        )

        self.feedback_frame.update()
        self.feedback_frame.yview_moveto(1)

    def attach_data(self) -> None:
        pass

    def publish(self) -> None:
        pass

    def after_publish(self) -> None:
        self.feedback_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.output_frame.pack(
            anchor=tk.N, side=tk.TOP, padx=10, pady=10, expand=True, fill=tk.BOTH
        )
        self.botframe.pack(side=tk.TOP)


class HometabOldCatch(Hometab):

    def __init__(self, parent: ScNotebook, root: Root) -> None:
        super().__init__(parent, root)
        self._mode.set("mhz")

    def _initialize_freq_frame(self) -> None:
        super()._initialize_freq_frame()
        self.freq_spinbox.configure(
            from_=self.root.sonicamp.mode.freq_start, 
            to=self.root.sonicamp.mode.freq_stop
        )

    def _initialize_gain_frame(self) -> None:
        super()._initialize_gain_frame()
        self.gain_spinbox.configure(
            from_=self.root.sonicamp.mode.gain_start, 
            to=self.root.sonicamp.mode.gain_stop
        )
        self.gain_scale.configure(
            from_=self.root.sonicamp.mode.gain_start, 
            to=self.root.sonicamp.mode.gain_stop
        )

    def _initialize_mode_frame(self) -> None:
        super()._initialize_mode_frame()
        self.wipemode_button.configure(value="khz")
        self.catchmode_button.configure(value="mhz")

    def change_mode(self) -> None:
        mode: str = self._mode.get()

        if (mode == "khz") and (self.root.sonicamp.mode == MhzMode()):
            answer: str = self.root.sonicamp.set_mode(KhzMode())
            self._set_khz()

        elif (mode == "mhz") and (self.root.sonicamp.mode == KhzMode()):
            answer: str = self.root.sonicamp.set_mode(MhzMode())
            self._set_mhz()

        self.insert_feed(answer)

    def set_val(self) -> None:
        try:
            self.insert_feed(self.set_freq(True))
            if isinstance(self.root.sonicamp.mode, KhzMode): return
            self.insert_feed(self.set_gain(True))
        except ValueNotSupported as ve:
            messagebox.showerror(
                "Wrong frequency and/ or gain",
                f"The {self.root.sonicamp.type_} does not support the values you wanted to set"
            )

    def attach_data(self) -> None:
        super().attach_data()
        self.freq_spinbox.configure(
            from_=self.root.sonicamp.mode.freq_start, 
            to=self.root.sonicamp.mode.freq_stop
        )

        if isinstance(self.root.sonicamp.mode, KhzMode) and self._mode.get() == "mhz":
            self._set_khz()
        elif isinstance(self.root.sonicamp.mode, MhzMode) and self._mode.get() == "khz":
            self._set_mhz()

    def publish(self) -> None:
        super().publish()
        self.freq_spinbox.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.scroll_digit.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)

        self.gain_spinbox.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.gain_scale.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)

        self.wipemode_button.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.catchmode_button.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)

        self.freq_frame.pack(side=tk.TOP, expand=True, fill=tk.X)
        self.gain_frame.pack(side=tk.TOP, expand=True, fill=tk.X)
        self.mode_frame.pack(side=tk.TOP, expand=True, fill=tk.X)
        self.set_val_btn.pack(side=tk.TOP, expand=True, fill=tk.X, padx=10, pady=10)
        self.sonic_measure_button.pack(side=tk.TOP, padx=10, pady=10)
        self.serial_monitor_btn.pack(side=tk.TOP, padx=10, pady=5, expand=True, fill=tk.BOTH)

        self.control_frame.grid(row=1, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.utils_frame.grid(row=1, column=1, padx=20, pady=20, sticky=tk.NSEW)
        
        self.us_on_button.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.us_auto_button.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)
        self.us_off_button.grid(row=0, column=2, padx=10, pady=10, sticky=tk.NSEW)

        self.topframe.pack(side=tk.TOP, padx=10, pady=10)
        self.us_control_frame.pack(side=tk.TOP, padx=10, pady=10)

        super().after_publish()


class HometabOldWipe(Hometab):
    def __init__(self, parent: ScNotebook, root: Root, *args, **kwargs) -> None:
        super().__init__(parent, root, *args, **kwargs)
        self._initialize_wipeframe()
        self.us_on_button: ttk.Button = ttk.Button(
            self.control_frame,
            text="ON",
            style="success.TButton",
            width=10,
            command=self.set_signal_on,
        )
        ToolTip(self.us_on_button, text="Turn the ultrasound signal on")

        self.us_off_button: ttk.Button = ttk.Button(
            self.topframe,
            text="OFF",
            style="danger.TButton",
            width=10,
            command=self.set_signal_off,
        )
        ToolTip(self.us_off_button, text="Turn the ultrasound signal off")

    def _initialize_freq_frame(self) -> None:
        super()._initialize_freq_frame()
        self.freq_spinbox.configure(from_=50000, to=1200000, width=10)

    def _initialize_wipeframe(self) -> None:
        self.wipe_frame: ttk.LabelFrame = ttk.LabelFrame(
            self.topframe, text="Set up wiping"
        )

        self.wipe_spinbox: ttk.Spinbox = ttk.Spinbox(
            self.wipe_frame,
            from_=1,
            increment=5,
            to=100,
            textvariable=self._wipe_var,
            width=16,
            style="dark.TSpinbox",
        )
        ToolTip(self.wipe_spinbox, text="Set up wipe cycles")

        self.wipe_mode_frame: ttk.Label = ttk.Label(self.wipe_frame)
        self.def_wipe_button: ttkb.Radiobutton = ttkb.Radiobutton(
            self.wipe_mode_frame,
            text="Definite",
            value=True,
            variable=self._wipe_inf_or_def,
            bootstyle="dark-outline-toolbutton",
            width=6,
            command=self.handle_wipe_mode,
        )
        self.inf_wipe_button: ttkb.Radiobutton = ttkb.Radiobutton(
            self.wipe_mode_frame,
            text="Infinite",
            value=False,
            variable=self._wipe_inf_or_def,
            bootstyle="dark-outline-toolbutton",
            width=6,
            command=self.handle_wipe_mode,
        )
        self.start_wipe_button: ttk.Button = ttk.Button(
            self.wipe_frame,
            text="WIPE",
            style="primary.TButton",
            command=self.start_wiping,
        )

    def handle_wipe_mode(self) -> None:
        if self._wipe_inf_or_def.get(): self.wipe_spinbox.config(state=tk.NORMAL)
        else: self.wipe_spinbox.config(state=tk.DISABLED)

    def set_freq(self) -> None:
        return super().set_freq()
    
    def set_val(self) -> None:
        self.insert_feed(self.set_freq())

    def set_signal_on(self) -> None:
        return super().set_signal_on()

    def set_signal_off(self) -> None:
        self.root.status_frame.wipe_progressbar.stop()
        return super().set_signal_off()

    def start_wiping(self) -> None:
        wipe_runs: int = self._wipe_inf_or_def.get()
        
        if wipe_runs:
            self.insert_feed(self.serial.send_and_get(Command.SET_WIPE_DEF + self._wipe_var.get()))
        else:
            self.insert_feed(self.serial.send_and_get(Command.SET_WIPE_INF))
        
        self.root.status_frame.wipe_progressbar.start()

    def attach_data(self) -> None:
        return super().attach_data()

    def publish(self) -> None:
        super().publish()
        self.freq_spinbox.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.scroll_digit.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)
        self.freq_frame.pack(side=tk.TOP, expand=True, fill=tk.X)
        self.set_val_btn.pack(side=tk.TOP, expand=True, fill=tk.X, padx=10, pady=10)
        self.us_on_button.pack(side=tk.TOP, expand=True, fill=tk.X, padx=10, pady=10)

        self.wipe_spinbox.pack(side=tk.TOP, expand=True, padx=10, pady=10, fill=tk.X)
        self.inf_wipe_button.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.def_wipe_button.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)
        self.wipe_mode_frame.pack(side=tk.TOP, expand=True, fill=tk.X)
        self.start_wipe_button.pack(
            side=tk.TOP, expand=True, padx=10, pady=10, fill=tk.X
        )

        self.wipe_frame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.control_frame.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)

        self.us_off_button.grid(
            row=1, column=0, columnspan=2, padx=10, pady=10, sticky=tk.NSEW
        )

        self.topframe.pack(side=tk.TOP, padx=20, pady=20)

        super().after_publish()


class HometabWipe40KHZ(Hometab):
    def __init__(self, parent: ScNotebook, root: Root, *args, **kwargs) -> None:
        super().__init__(parent, root, *args, **kwargs)
        self.gain_spinbox: ttk.Spinbox = ttk.Spinbox(
            self.control_frame,
            from_=0,
            increment=10,
            to=100,
            textvariable=self._gain,
            width=5,
            style="dark.TSpinbox",
        )
        ToolTip(self.gain_spinbox, text="Configure the gain for your device")

        self.set_val_btn: ttk.Button = ttk.Button(
            self.control_frame,
            text="Set Gain",
            command=self.set_gain,
            bootstyle="dark.TButton",
        )
        
        self.us_on_button: ttk.Button = ttk.Button(
            self.control_frame,
            text='ON',
            style='success.TButton',
            width=10,
            command=self.set_signal_on)
        
        ToolTip(self.us_on_button, text="Turn the ultrasound signal on")
        
        self.us_off_button: ttk.Button = ttk.Button(
            self.control_frame,
            text='OFF',
            style='danger.TButton',
            width=10,
            command=self.set_signal_off)
        
        ToolTip(self.us_off_button, text="Turn the ultrasound signal off")

        self.gain_scale: ttk.Scale = ttk.Scale(
            self.topframe,
            from_=0,
            to=100,
            name="gainscale",
            length=180,
            orient=tk.VERTICAL,
            style="primary.TScale",
            variable=self._gain,
        )

    def _initialize_botframe(self) -> None:
        super()._initialize_botframe()
        self.feedback_frame.config(width=200)
    
    def set_gain(self) -> None:
        gain: int = int(super().set_gain())
        self.insert_feed(f"Gain setted to {gain}%")
        self.root.status_frame.change_values(gain=gain)

    def set_signal_on(self) -> None:
        is_on: Union[str, bool] = self.serial.send_and_get(Command.SET_SIGNAL_ON)

        if isinstance(is_on, str):
            self.insert_feed(is_on)
            self.root.status_frame.signal_on()
            
        elif isinstance(is_on, bool):
            self.insert_feed("Signal ON")
            self.root.status_frame.signal_on()

        else: messagebox.showwarning(
                "Error", 
                "Something went wrong, try again, or restart the application"
            )

    def set_signal_off(self) -> None:
        if self.serial.send_and_get(Command.SET_SIGNAL_OFF):
            self.insert_feed("Signal OFF")
            self.root.status_frame.signal_off()

        else: messagebox.showwarning(
                "Error", "Something went wrong, try again, or restart the application"
            )

    def publish(self) -> None:
        super().publish()
        self.gain_spinbox.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=5, pady=5)
        self.set_val_btn.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=5, pady=5)
        self.us_on_button.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=5, pady=5)
        self.us_off_button.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=5, pady=5)

        self.control_frame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.gain_scale.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)

        self.topframe.pack(side=tk.TOP, padx=10, pady=10)
        
        super().after_publish()


class HometabCatch(Hometab):
    def __init__(self, parent: ScNotebook, root: Root, *args, **kwargs) -> None:
        super().__init__(parent, root, *args, **kwargs)
        self._mode.set('catch')

    def _initialize_freq_frame(self) -> None:
        super()._initialize_freq_frame()
        self.freq_spinbox.configure(
            from_=self.root.sonicamp.mode.freq_start, to=self.root.sonicamp.mode.freq_stop
        )

    def _initialize_gain_frame(self) -> None:
        super()._initialize_gain_frame()

        self.gain_spinbox.configure(from_=0, to=150)
        self.gain_scale.configure(from_=0, to=150)
        
    def _initialize_mode_frame(self) -> None:
        super()._initialize_mode_frame()
        
        self.wipemode_button.configure(value='wipe')
        self.catchmode_button.configure(value='catch')

    def change_mode(self) -> None:
        mode: str = self._mode.get()

        if mode == "wipe":
            answer: str = self.root.sonicamp.set_mode(KhzMode())
            
        elif mode == "catch":
            answer: str = self.root.sonicamp.set_mode(MhzMode())
                
        self.insert_feed(answer)

    def attach_data(self) -> None:
        self.freq_spinbox.configure(
            from_=self.root.sonicamp.mode.freq_start, to=self.root.sonicamp.mode.freq_stop
        )

    def publish(self) -> None:
        super().publish()
        self.freq_spinbox.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.scroll_digit.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)

        self.gain_spinbox.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.gain_scale.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)

        self.wipemode_button.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.catchmode_button.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)

        self.freq_frame.pack(side=tk.TOP, expand=True, fill=tk.X)
        self.gain_frame.pack(side=tk.TOP, expand=True, fill=tk.X)
        self.mode_frame.pack(side=tk.TOP, expand=True, fill=tk.X)
        self.set_val_btn.pack(side=tk.TOP, expand=True, fill=tk.X, padx=10, pady=10)
        self.sonic_measure_button.pack(side=tk.TOP, padx=10, pady=10)
        self.serial_monitor_btn.pack(
            side=tk.TOP, padx=10, pady=5, expand=True, fill=tk.BOTH
        )

        self.control_frame.grid(row=1, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.utils_frame.grid(row=1, column=1, padx=20, pady=20, sticky=tk.NSEW)

        self.us_on_button.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.us_auto_button.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)
        self.us_off_button.grid(row=0, column=2, padx=10, pady=10, sticky=tk.NSEW)

        self.topframe.pack(side=tk.TOP, padx=10, pady=10)
        self.us_control_frame.pack(side=tk.TOP, padx=10, pady=10)
        
        return super().after_publish()


class HometabWipe(Hometab):
    def __init__(self, parent: ScNotebook, root: Root, *args, **kwargs) -> None:
        super().__init__(parent, root, *args, **kwargs)
        
        self._initialize_wipeframe()
        
        self.us_on_button: ttk.Button = ttk.Button(
            self.control_frame,
            text="ON",
            style="success.TButton",
            width=10,
            command=self.set_signal_on,
        )

        ToolTip(self.us_on_button, text="Turn the ultrasound signal on")

        self.us_off_button: ttk.Button = ttk.Button(
            self.topframe,
            text="OFF",
            style="danger.TButton",
            width=10,
            command=self.set_signal_off,
        )

        ToolTip(self.us_off_button, text="Turn the ultrasound signal off")

    def _initialize_freq_frame(self) -> None:
        super()._initialize_freq_frame()

        self.freq_spinbox.configure(
            from_=self.root.sonicamp.mode.freq_start, to=self.root.sonicamp.mode.freq_stop
        )

    def _initialize_gain_frame(self) -> None:
        super()._initialize_gain_frame()
        
        self.gain_spinbox.configure(from_=0, to=150)
        self.gain_scale.configure(from_=0, to=150)     
        
    def _initialize_wipeframe(self) -> None:
        self.wipe_frame: ttk.LabelFrame = ttk.LabelFrame(
            self.topframe, text="Set up wiping"
        )

        self.wipe_spinbox: ttk.Spinbox = ttk.Spinbox(
            self.wipe_frame,
            from_=1,
            increment=5,
            to=100,
            textvariable=self._wipe_var,
            width=16,
            style="dark.TSpinbox",
        )

        ToolTip(self.wipe_spinbox, text="Set up wipe cycles")

        self.wipe_mode_frame: ttk.Label = ttk.Label(self.wipe_frame)

        self.def_wipe_button: ttkb.Radiobutton = ttkb.Radiobutton(
            self.wipe_mode_frame,
            text="Definite",
            value=True,
            variable=self._wipe_inf_or_def,
            bootstyle="dark-outline-toolbutton",
            width=6,
            command=self.handle_wipe_mode,
        )

        self.inf_wipe_button: ttkb.Radiobutton = ttkb.Radiobutton(
            self.wipe_mode_frame,
            text="Infinite",
            value=False,
            variable=self._wipe_inf_or_def,
            bootstyle="dark-outline-toolbutton",
            width=6,
            command=self.handle_wipe_mode,
        )

        self.start_wipe_button: ttk.Button = ttk.Button(
            self.wipe_frame,
            text="WIPE",
            style="primary.TButton",
            command=self.start_wiping,
        )
        
    def start_wiping(self) -> None:
        wipe_runs: int = self._wipe_inf_or_def.get()
        self.insert_feed(
            self.serial.send_and_get(Command.SET_WIPE_DEF + self._wipe_var.get())
        ) if wipe_runs else self.insert_feed(self.serial.send_and_get(Command.SET_WIPE_INF))
        
    def handle_wipe_mode(self) -> None:
        self.wipe_spinbox.config(
            state=tk.NORMAL
        ) if self._wipe_inf_or_def.get() else self.wipe_spinbox.config(state=tk.DISABLED)

    def attach_data(self) -> None:
        return super().attach_data()

    def publish(self) -> None:
        """Function to build children of this frame"""
        super().publish()
        self.freq_spinbox.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.scroll_digit.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)
        self.freq_frame.pack(side=tk.TOP, expand=True, fill=tk.X)
        self.set_val_btn.pack(side=tk.TOP, expand=True, fill=tk.X, padx=10, pady=10)
        self.us_on_button.pack(side=tk.TOP, expand=True, fill=tk.X, padx=10, pady=10)

        self.wipe_spinbox.pack(side=tk.TOP, expand=True, padx=10, pady=10, fill=tk.X)
        self.inf_wipe_button.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.def_wipe_button.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)
        self.wipe_mode_frame.pack(side=tk.TOP, expand=True, fill=tk.X)
        self.start_wipe_button.pack(
            side=tk.TOP, expand=True, padx=10, pady=10, fill=tk.X
        )

        self.wipe_frame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.control_frame.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)

        self.us_off_button.grid(
            row=1, column=0, columnspan=2, padx=10, pady=10, sticky=tk.NSEW
        )

        self.topframe.pack(side=tk.TOP, padx=20, pady=20)

        super().after_publish()