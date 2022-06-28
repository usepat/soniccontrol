from __future__ import annotations

from typing import Union, TYPE_CHECKING

import tkinter as tk
import tkinter.ttk as ttk
import ttkbootstrap as ttkb

from tkinter import messagebox
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.scrolled import ScrolledFrame

from sonicpackage import (
    Command,
    SerialConnection,
    KhzMode,
    MhzMode,
    CatchMode,
    WipeMode,
    ValueNotSupported,
)
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
        self.control_frame: ttk.LabelFrame = ttk.LabelFrame(
            self.topframe, text="Manual Control"
        )

        self.set_val_btn: ttk.Button = ttk.Button(
            self.control_frame,
            text="Set Frequency and Gain",
            command=self.set_val,
            bootstyle="dark.TButton",
        )

        self._initialize_frq_frame()
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

        self.us_off_button: ttk.Button = ttk.Button(
            self.us_control_frame,
            text="OFF",
            style="danger.TButton",
            width=10,
            command=self.set_signal_off,
        )

        ToolTip(self.us_off_button, text="Turn the ultrasound signal off")

    def set_val(self) -> None:
        self.insert_feed(self.set_frq())
        self.insert_feed(self.set_gain())

    def set_signal_on(self) -> None:
        self.insert_feed(self.serial.send_and_get(Command.SET_SIGNAL_ON))

    def set_signal_off(self) -> None:
        self.insert_feed(self.serial.send_and_get(Command.SET_SIGNAL_OFF))

    def _initialize_frq_frame(self) -> None:
        self.frq_frame: ttk.Label = ttk.Label(self.control_frame)

        self.frq_spinbox: ttk.Spinbox = ttk.Spinbox(
            self.frq_frame,
            increment=100,
            textvariable=self._frq,
            width=16,
            style="dark.TSpinbox",
            command=self.set_frq,
        )

        ToolTip(self.frq_spinbox, text="Configure the frequency of your device")

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
        try:
            answer: str = self.root.sonicamp.set_frq(self._frq.get())
            return answer

        except ValueNotSupported as e:
            messagebox.showwarning(
                "Value out of supported range",
                f"The value of frequency, you want to set is not supported under the current configurtation. The supported range is currently from {self.root.sonicamp.mode.frq_start} to {self.root.sonicamp.mode.frq_stop}",
            )

    def set_scroll_digit(self) -> None:
        self.frq_spinbox.config(increment=str(10 ** (int(self.scroll_digit.get()) - 1)))

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

    def set_gain(self) -> None:
        
        try:
            answer: str = self.root.sonicamp.set_gain(self._gain.get())
            return answer
    
        except ValueNotSupported as e:
                messagebox.showwarning(
                    "Value out of supported range",
                    f"The value of gain, you want to set is not supported under the current configurtation. The supported range is currently from {self.root.sonicamp.mode.gain_start} to {self.root.sonicamp.mode.gain_stop}",
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

    def change_mode(self) -> None:
        pass

    def _initialize_utils_frame(self) -> None:
        self.utils_frame: ttk.Frame = ttk.Frame(self.topframe)

        self.sonic_measure_button: ttk.Button = ttk.Button(
            self.utils_frame,
            text="Sonic measure",
            style="dark.TButton",
            image=self.root.graph_img,
            compound=tk.TOP,
            command=self.publish_sonicmeasure,
        )

        self.serial_monitor_btn: ttk.Button = ttk.Button(
            self.utils_frame,
            text="Serial Monitor",
            style="secondary.TButton",
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

    def insert_feed(self, text: str) -> None:
        if text is list:
            text = " ".join(text)

        ttk.Label(self.feedback_frame, text=text, font=("Consolas", 10)).pack(
            fill=tk.X, side=tk.TOP, anchor=tk.W
        )

        self.feedback_frame.update()
        self.feedback_frame.yview_moveto(1)

    def attach_data(self) -> None:
        pass

    def publish(self) -> None:
        self.feedback_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.output_frame.pack(
            anchor=tk.N, side=tk.TOP, padx=10, pady=10, expand=True, fill=tk.BOTH
        )
        self.botframe.pack(side=tk.TOP)


class HometabOldCatch(Hometab):
    def __init__(self, parent: ScNotebook, root: Root, *args, **kwargs) -> None:
        super().__init__(parent, root, *args, **kwargs)
        
        self._mode.set("mhz")

    def _initialize_frq_frame(self) -> None:
        super()._initialize_frq_frame()

        self.frq_spinbox.configure(
            from_=self.root.sonicamp.mode.frq_start, to=self.root.sonicamp.mode.frq_stop
        )

    def _initialize_gain_frame(self) -> None:
        super()._initialize_gain_frame()

        self.gain_spinbox.configure(from_=0, to=150)
        self.gain_scale.configure(from_=0, to=150)

    def _initialize_mode_frame(self) -> None:
        super()._initialize_mode_frame()

        self.wipemode_button.configure(value="khz")
        self.catchmode_button.configure(value="mhz")

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
        mode: str = self._mode.get()

        if mode == "khz":
            answer: str = self.root.sonicamp.set_mode(KhzMode())
            
            for child in self.gain_frame.children.values():
                child.configure(state=tk.DISABLED)
            
        elif mode == "mhz":
            answer: str = self.root.sonicamp.set_mode(MhzMode())
            
            for child in self.gain_frame.children.values():
                child.configure(state=tk.NORMAL)

        self.insert_feed(answer)

    def attach_data(self) -> None:
        self.frq_spinbox.configure(
            from_=self.root.sonicamp.mode.frq_start, to=self.root.sonicamp.mode.frq_stop
        )

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
        self.serial_monitor_btn.pack(
            side=tk.TOP, padx=10, pady=5, expand=True, fill=tk.BOTH
        )

        self.control_frame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.utils_frame.grid(row=0, column=1, padx=20, pady=20, sticky=tk.NSEW)

        self.us_on_button.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.us_off_button.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)

        self.topframe.pack(side=tk.TOP, padx=10, pady=10)
        self.us_control_frame.pack(side=tk.TOP, padx=10, pady=10)

        super().publish()


class HometabOldWipe(Hometab):
    def __init__(self, parent: ScNotebook, root: Root, *args, **kwargs) -> None:
        super().__init__(parent, root, *args, **kwargs)

        self._initialize_wipeframe()

        self.us_on_button: ttk.Button = ttk.Button(
            self.frq_control_frame,
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

    def _initialize_frq_frame(self) -> None:
        super()._initialize_frq_frame()
        self.frq_spinbox.configure(from_=50000, to=1200000)

    def _initialize_wipeframe(self) -> None:
        self.wipe_frame: ttk.LabelFrame = ttk.LabelFrame(
            self.topframe, text="Set up wiping"
        )

        self.wipe_spinbox: ttk.Spinbox = ttk.Spinbox(
            self.wipe_frame,
            from_=1,
            increment=5,
            to=100,
            textvariable=self.wipe_var,
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
            self.insert_feed(
                self.serial.send_get(Command.SET_WIPE_DEF + self.wipe_var.get())
            )

        else:
            self.insert_feed(self.serial.send_get(Command.SET_WIPE_INF))

        self.root.status_frame.wipe_progressbar.start()
        self.root.wipe_mode.set(1)

    def attach_data(self) -> None:
        return super().attach_data()

    def publish(self) -> None:
        """Function to build children of this frame"""
        self.frq_spinbox.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.scroll_digit.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)
        self.frq_frame.pack(side=tk.TOP, expand=True, fill=tk.X)
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

        super().publish()


class HometabDutyWipe(Hometab):
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

    def set_gain(self) -> None:
        gain: int = int(super().set_gain())

        if gain:
            self.insert_feed(f"Gain setted to {gain}%")
            self.root.status_frame.change_values(gain=gain)

        else:
            messagebox.showwarning(
                "Error", "Something went wrong, try again, or restart the application"
            )

    def set_signal_on(self) -> None:
        if self.serial.send_and_get(Command.SET_SIGNAL_ON):

            self.insert_feed("Signal ON")
            self.root.status_frame.signal_on()

        else:
            messagebox.showwarning(
                "Error", "Something went wrong, try again, or restart the application"
            )

    def set_signal_off(self) -> None:
        if self.serial.send_and_get(Command.SET_SIGNAL_OFF):

            self.insert_feed("Signal OFF")
            self.root.status_frame.signal_off()

        else:
            messagebox.showwarning(
                "Error", "Something went wrong, try again, or restart the application"
            )

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
        
        super().publish()


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


# from __future__ import annotations

# from typing import Union, TYPE_CHECKING

# import tkinter as tk
# import tkinter.ttk as ttk
# import ttkbootstrap as ttkb

# from tkinter import messagebox
# from ttkbootstrap.tooltip import ToolTip

# from sonicpackage import Command, SerialConnection
# from soniccontrol.sonicmeasure import SonicMeasure

# if TYPE_CHECKING:
#     from soniccontrol.core import Root
#     from soniccontrol._notebook import ScNotebook


# class HomeTab(ttk.Frame):
#     """
#     This is the Parent class of every other instance of object
#     that is used for the Home Tab. It has basic attributes and
#     methods, that every variation of Hometab should have:

#         - A control frame, that has all the controls for the sonicamp
#         - An output frame, that shows the concrete answer from a sonicamp
#         - Buttons like: US ON, US OFF and serialmonitor

#     And methods for the corrresponding objects that the Hometab has like
#     insert_feed() for inserting text into the output frame

#     Inheritance:
#         ttk (tkinter.ttk.Frame): the tkinter Frame
#     """

#     @property
#     def root(self) -> Root:
#         return self._root

#     @property
#     def serial(self) -> SerialConnection:
#         return self._serial

#     def __init__(self, parent: ScNotebook, root: Root, *args, **kwargs) -> None:
#         super().__init__(parent, *args, **kwargs)

#         self._root: Root = root
#         self._serial: SerialConnection = root.serial

#         self._frq: tk.IntVar = tk.IntVar()
#         self._gain: tk.IntVar = tk.IntVar()
#         self._frq_mode: tk.BooleanVar = tk.BooleanVar()
#         self._is_on: bool = False

#         self.topframe: ttk.Frame = ttk.Frame(self)
#         self.control_frame: ttk.Labelframe = ttk.LabelFrame(self.topframe, text='Manual Control')

#         # Frq frame
#         self.frq_frame: ttk.Label = ttk.Label(self.control_frame)

#         self.frq_spinbox: ttk.Spinbox = ttk.Spinbox(
#             self.frq_frame,
#             from_=600000,
#             increment=100,
#             to=6000000,
#             textvariable=self._frq,
#             width=16,
#             style='dark.TSpinbox',
#             command=self.set_frq)

#         ToolTip(self.frq_spinbox, text="Configure the frequency of your device")

#         self.scroll_digit: ttk.Spinbox = ttk.Spinbox(
#             self.frq_frame,
#             from_=1,
#             increment=1,
#             to=6,
#             validate=None,
#             width=5,
#             style='secondary.TSpinbox',
#             command=self.set_scrolldigit)

#         ToolTip(self.scroll_digit, text="Set the digit you want to scroll in the Frequency field")

#         # Gain Frame
#         self.gain_frame: ttk.Frame = ttk.Frame(self.control_frame)

#         self.gain_spinbox: ttk.Spinbox = ttk.Spinbox(
#             self.gain_frame,
#             from_=0,
#             increment=10,
#             to=150,
#             textvariable=self._gain,
#             width=5,
#             style='dark.TSpinbox',
#             command=self.set_gain)

#         ToolTip(self.gain_frame, text="Configure the gain for your device")

#         self.gain_scale: ttk.Scale = ttk.Scale(
#             self.gain_frame,
#             from_=0,
#             to=150,
#             name='gainscale',
#             length=180,
#             orient=tk.HORIZONTAL,
#             style="primary.TScale",
#             variable=self._gain,)

#         # kHz MHz Frame
#         self.frq_mode_frame: ttk.Label = ttk.Label(self.control_frame)

#         self.khz_button: ttkb.Radiobutton = ttkb.Radiobutton(
#             self.frq_mode_frame,
#             text='Wipe mode',
#             value=False,
#             variable=self._frq_mode,
#             bootstyle='dark-outline-toolbutton',
#             width=12,
#             command=self.change_frq_mode)

#         self.mhz_button: ttkb.Radiobutton = ttkb.Radiobutton(
#             self.frq_mode_frame,
#             text='Catch mode',
#             value=True,
#             variable=self._frq_mode,
#             bootstyle='dark-outline-toolbutton',
#             width=12,
#             command=self.change_frq_mode)

#         # Other children of the control frame
#         self.set_val_btn: ttk.Button = ttk.Button(
#             self.control_frame,
#             text='Set Frequency and Gain',
#             command=self.set_val,
#             bootstyle='dark.TButton',)

#         self.utils_frame: ttk.Frame = ttk.Frame(self.topframe)

#         self.sonic_measure_button: ttk.Button = ttk.Button(
#             self.utils_frame,
#             text='Sonic measure',
#             style='dark.TButton',
#             image=self.root.graph_img,
#             compound=tk.TOP,
#             command=self.publish_sonicmeasure)

#         self.serial_monitor_btn: ttk.Button = ttk.Button(
#             self.utils_frame,
#             text='Serial Monitor',
#             style='secondary.TButton',
#             width=12,
#             command=self.root.publish_serial_monitor,)

#         self.us_control_frame: ttk.Frame = ttk.Frame(self)

#         self.us_on_button: ttk.Button = ttk.Button(
#             self.us_control_frame,
#             text='ON',
#             style='success.TButton',
#             width=10,
#             command=self.signal_on)

#         ToolTip(self.us_on_button, text="Turn the ultrasound signal on")

#         self.us_off_button: ttk.Button = ttk.Button(
#             self.us_control_frame,
#             text='OFF',
#             style='danger.TButton',
#             width=10,
#             command=self.signal_off)

#         ToolTip(self.us_off_button, text="Turn the ultrasound signal off")

#         # Bot Frame - Feedback Frame
#         self.botframe: ttk.Frame = ttk.Frame(self)

#         self.output_frame: ttk.Frame = ttk.LabelFrame(self.botframe, text='Feedback')
#         container: ttk.Frame = ttk.Frame(self.output_frame)
#         self.canvas: tk.Canvas = tk.Canvas(container)
#         scrollbar: ttk.Scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=self.canvas.yview)
#         self.scrollable_frame: ttk.Frame = ttk.Frame(self.canvas)

#         self.scrollable_frame.bind(
#             "<Configure>",
#             lambda x: self.canvas.configure(scrollregion=self.canvas.bbox(tk.ALL)))

#         self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor=tk.NW)
#         self.canvas.configure(yscrollcommand=scrollbar.set)

#         container.pack(anchor=tk.N, expand=True, fill=tk.BOTH, padx=5, pady=5, side=tk.TOP)
#         self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
#         scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

#     def set_frq(self) -> None:
#         """
#         Method that sets the given freqeuency value from
#         the spinbox to the sonicamp
#         """
#         frq: int = self._frq.get()
#         answer: str = self.serial.send_and_get(Command.SET_FRQ + frq)
#         self.insert_feed(answer)

#     def set_gain(self) -> None:
#         """
#         Method that sets the given gain value from the
#         gain spinbox to the sonicamp
#         """
#         gain: int = self._gain.get()
#         answer: str = self.serial.send_and_get(Command.SET_GAIN + gain)
#         self.insert_feed(answer)

#     def change_frq_mode(self) -> None:
#         """
#         Method that sets the given frq mode value from the
#         radioboxes to the soniccatch-amp
#         """
#         frq_mode: bool = self._frq_mode.get()

#         if frq_mode:
#             answer: str = self.serial.send_and_get(Command.SET_KHZ)

#         else:
#             answer: str = self.serial.send_and_get(Command.SET_MHZ)

#         self.insert_feed(answer)

#     def signal_on(self) -> None:
#         """
#         Method that changes the signal output from the sonicamp
#         to ON. If not, ignores the
#         """
#         answer: str = self.serial.send_and_get(Command.SET_SIGNAL_ON)
#         self.insert_feed(answer)
#         self._is_on: bool = True

#     def signal_off(self) -> None:
#         """
#         Method that changes the signal output from the wipe
#         according to the given value in the GUI
#         """
#         answer: str = self.serial.send_and_get(Command.SET_SIGNAL_ON)
#         self.insert_feed(answer)
#         self._is_on: bool = True

#     def set_val(self) -> None:
#         """
#         Function that will be called after pressing the <Set Frequency and Gain> Button
#         It firstly checks if the values are supported under the current relay setting
#         """
#         frq: int = self._frq.get()
#         gain: int = self._gain.get()

#         if self.check_mode(frq):

#             self.insert_feed(self.serial.send_get(Command.SET_GAIN + gain))
#             self.insert_feed(self.serial.send_get(Command.SET_FRQ + frq))

#         else:

#             messagebox.showwarning(
#                 "Wrong Frequency Value",
#                 "This frequency cannot be setted under the current frequency range mode. Please use the spinbox once again")

#     def check_mode(self, frq: int) -> bool:
#         """
#         Checks the current frq mode and compares the given frq to
#         the supported values at the currently connected sonicamp

#         Args:
#             frq (int): The frq to check, that it is possible to set that

#         Returns:
#             bool: The boolean value if it is supported. True for green light
#         """
#         if frq >= self.root.sonicamp.status.frq_range_start or frq <= self.root.sonicamp.status.frq_range_stop:
#             return True

#         else:
#             return False

#     def change_values(self, frq: int = None, gain: int = None, frq_mode: bool = None, signal: bool = None) -> None:
#         pass

#     def insert_feed(self, text: Union[str, list]) -> None:
#         """
#         Function that inserts a string or a list into the feedback frame

#         Args:
#             text (Union[str, list]): The text, that should be inserted
#         """
#         if text is list:
#             text = ' '.join(text)

#         ttk.Label(self.scrollable_frame, text=text, font=("Consolas", 10)).pack(fill=tk.X, side=tk.TOP, anchor=tk.W)
#         self.canvas.update()
#         self.canvas.yview_moveto(1)

#     def publish(self) -> None:
#         """
#         Publish method to show the children of the Hometab
#         Because every instance of the Hometab has a feedback
#         Frame, the said child is published here
#         """
#         self.output_frame.pack(anchor=tk.N, side=tk.TOP, padx=10, pady=10, expand=True, fill=tk.BOTH)
#         self.botframe.pack(side=tk.TOP)


# class HomeTabCatch(HomeTab):

#     def __init__(self, parent: ScNotebook, root: Root, *args, **kwargs) -> None:
#         super().__init__(parent, root, *args, **kwargs)

#         self.config(height=200, width=200)


#     def set_val(self) -> None:
#         """
#         Function that will be called after pressing the <Set Frequency and Gain> Button
#         It firstly checks if the values are supported under the current relay setting
#         """
#         frq: int = self.root.frq.get()
#         gain: int = self.root.gain.get()

#         if self.check_range(frq):

#             self.insert_feed(self.serial.send_get(Command.SET_GAIN + gain))
#             self.insert_feed(self.serial.send_get(Command.SET_FRQ + frq))

#         else:

#             messagebox.showwarning(
#                 "Wrong Frequency Value",
#                 "This frequency cannot be setted under the current frequency range mode. Please use the spinbox once again")

#     def set_frq(self) -> None:
#         """Sets the frequency"""
#         frq: int = self.root.frq.get()

#         if self.check_range(frq):

#             self.serial.send_get(Command.SET_FRQ + frq)

#         else:

#             messagebox.showwarning(
#                 "Wrong Frequency Value",
#                 "This frequency cannot be setted under the current frequency range mode. Please use the spinbox once again")

#     def check_range(self, frq: int) -> bool:
#         """
#         Checks the current setting of the relay on the sonicamp and
#         returns true if the passed frequency is being supported under the
#         current relay setting.

#         Args:
#             frq (int): The to be checked frequency

#         Returns:
#             bool: Result if that frequency is possible to set or not
#         """
#         if self.root.frq_range.get() == "khz" and (frq > 1200000 or frq < 50000):
#             return False

#         elif self.root.frq_range.get() == "mhz" and frq < 60000:
#             return False

#         return True

#     def attach_data(self) -> None:

#         if self.root.frq_range.get() == "khz":

#             self.frq_spinbox.config(
#                 from_=50000,
#                 to=1200000,)
#             self.gain_scale.config(state=tk.DISABLED)
#             self.gain_spinbox.config(state=tk.DISABLED)

#         else:

#             self.frq_spinbox.config(
#                 from_=600000,
#                 to=6000000,)
#             self.gain_scale.config(state=tk.NORMAL)
#             self.gain_spinbox.config(state=tk.NORMAL)

#     def publish_sonicmeasure(self) -> None:
#         self.sonicmeasure: SonicMeasure = SonicMeasure(self.root)

#     def publish(self) -> None:
#         """
#         Function to build children of this frame
#         """
#         self.frq_spinbox.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
#         self.scroll_digit.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)

#         self.gain_spinbox.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
#         self.gain_scale.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)

#         self.khz_button.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
#         self.mhz_button.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)

#         self.frq_frame.pack(side=tk.TOP, expand=True, fill=tk.X)
#         self.gain_frame.pack(side=tk.TOP, expand=True, fill=tk.X)
#         self.frq_mode_frame.pack(side=tk.TOP, expand=True, fill=tk.X)
#         self.set_val_btn.pack(side=tk.TOP, expand=True, fill=tk.X, padx=10, pady=10)
#         self.sonic_measure_button.pack(side=tk.TOP, padx=10, pady=10)
#         self.serial_monitor_btn.pack(side=tk.TOP, padx=10, pady=5, expand=True, fill=tk.BOTH)

#         self.control_frame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
#         self.utils_frame.grid(row=0, column=1, padx=20, pady=20, sticky=tk.NSEW)

#         self.us_on_button.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
#         self.us_off_button.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)

#         self.topframe.pack(side=tk.TOP, padx=10, pady=10)
#         self.us_control_frame.pack(side=tk.TOP, padx=10, pady=10)

#         super().publish()

#     def set_scrolldigit(self) -> None:
#         """
#         Function regarding the scroll digit combobox
#         """
#         self.frq_spinbox.config(
#             increment = str(10 ** (int(self.scroll_digit.get())-1)))


# class HomeTabWipe(HomeTab):
#     """
#     Part of the ScNotebook object and resposible for
#     the manual control of a sonicwipe (pre-revision 2.1)

#     Inheritance:
#         HomeTab (ttk.Frame): the general HomeTab class
#         that every Hometab inherites from
#     """
#     def __init__(self, parent: ScNotebook, root: Root, *args, **kwargs) -> None:
#         super().__init__(parent, root, *args, **kwargs)

#         self.config(height=200, width=200)

#         self.wipe_var: tk.IntVar = tk.IntVar(value=5)

#         self.wipe_mode: tk.BooleanVar = tk.BooleanVar(value=True)

#         self.frq_control_frame: ttk.LabelFrame = ttk.LabelFrame(self.topframe, text='Set up frequency')

#         # Frq frame
#         self.frq_frame: ttk.Label = ttk.Label(self.frq_control_frame)

#         self.frq_spinbox: ttk.Spinbox = ttk.Spinbox(
#             self.frq_frame,
#             from_=50000,
#             increment=100,
#             to=1200000,
#             textvariable=self.root.frq,
#             width=8,
#             style='dark.TSpinbox',
#             command=self.set_frq)

#         ToolTip(self.frq_spinbox, text="Configure the frequency of your device")

#         self.scroll_digit: ttk.Spinbox = ttk.Spinbox(
#             self.frq_frame,
#             from_=1,
#             increment=1,
#             to=6,
#             validate=None,
#             width=5,
#             style='secondary.TSpinbox',
#             command=self.set_scrolldigit)

#         ToolTip(self.scroll_digit, text="Set the digit you want to scroll in the frequency field")

#         self.set_val_btn: ttk.Button = ttk.Button(
#             self.frq_control_frame,
#             text='Set Frequency',
#             bootstyle='dark.TButton',
#             command=lambda: self.insert_feed(self.serial.send_get(Command.SET_FRQ + self.root.frq.get())))

#         self.us_on_button: ttk.Button = ttk.Button(
#             self.frq_control_frame,
#             text='ON',
#             style='success.TButton',
#             width=10,
#             command=lambda: self.insert_feed(self.serial.send_get(Command.SET_SIGNAL_ON)))

#         ToolTip(self.us_on_button, text="Turn the ultrasound signal on")

#         self.wipe_frame: ttk.LabelFrame = ttk.LabelFrame(self.topframe, text='Set up wiping')

#         self.wipe_spinbox: ttk.Spinbox = ttk.Spinbox(
#             self.wipe_frame,
#             from_=1,
#             increment=5,
#             to=100,
#             textvariable=self.wipe_var,
#             width=16,
#             style='dark.TSpinbox',)

#         ToolTip(self.wipe_spinbox, text="Set up wipe cycles")

#         self.wipe_mode_frame: ttk.Label = ttk.Label(self.wipe_frame)

#         self.def_wipe_button: ttkb.Radiobutton = ttkb.Radiobutton(
#             self.wipe_mode_frame,
#             text='Definite',
#             value=True,
#             variable=self.wipe_mode,
#             bootstyle='dark-outline-toolbutton',
#             width=6,
#             command=self.handle_wipe_mode)

#         self.inf_wipe_button: ttkb.Radiobutton = ttkb.Radiobutton(
#             self.wipe_mode_frame,
#             text='Infinite',
#             value=False,
#             variable=self.wipe_mode,
#             bootstyle='dark-outline-toolbutton',
#             width=6,
#             command=self.handle_wipe_mode)

#         # self.protocol_menu: ttk.Button = ttk.Button(
#         #     self.wipe_frame)
#         self.start_wipe_button: ttk.Button = ttk.Button(
#             self.wipe_frame,
#             text='WIPE',
#             style='primary.TButton',
#             command=self.start_wiping)

#         self.us_off_button: ttk.Button = ttk.Button(
#             self.topframe,
#             text='OFF',
#             style='danger.TButton',
#             width=10,
#             command=self.set_signal_off)

#         ToolTip(self.us_off_button, text="Turn the ultrasound signal off")

#     def set_frq(self) -> None:
#         """
#         Sets the frequency of the sonicamp
#         """
#         self.serial.send_get(Command.SET_FRQ + self.root.frq.get())

#     def set_signal_off(self) -> None:
#         """
#         What action to do after pressing the off button
#         """
#         self.root.wipe_mode.set(0)
#         self.root.status_frame.wipe_progressbar.stop()
#         self.insert_feed(self.serial.send_get(Command.SET_SIGNAL_OFF))

#     def handle_wipe_mode(self) -> None:
#         """
#         Handles the definite/ indefinite WIPE modes
#         """
#         # In case its set to definite
#         if self.wipe_mode.get():
#             self.wipe_spinbox.config(state=tk.NORMAL)

#         else:
#             self.wipe_spinbox.config(state=tk.DISABLED)

#     def start_wiping(self) -> None:
#         """
#         Method that handles what to do after pressing the
#         WIPE Button
#         """
#         # In case its set to definite
#         wipe_runs: int = self.wipe_mode.get()

#         if wipe_runs:
#             self.insert_feed(self.serial.send_get(Command.SET_WIPE_DEF + self.wipe_var.get()))

#         else:
#             self.insert_feed(self.serial.send_get(Command.SET_WIPE_INF))

#         self.root.status_frame.wipe_progressbar.start()
#         self.root.wipe_mode.set(1)

#     def attach_data(self) -> None:
#         """Attaches data to the hometab"""
#         self.frq_spinbox.config(
#             from_=50000,
#             to=1200000)

#     def publish(self) -> None:
#         """ Function to build children of this frame """
#         self.frq_spinbox.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
#         self.scroll_digit.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)
#         self.frq_frame.pack(side=tk.TOP, expand=True, fill=tk.X)
#         self.set_val_btn.pack(side=tk.TOP, expand=True, fill=tk.X, padx=10, pady=10)
#         self.us_on_button.pack(side=tk.TOP, expand=True, fill=tk.X, padx=10, pady=10)

#         self.wipe_spinbox.pack(side=tk.TOP, expand=True, padx=10, pady=10, fill=tk.X)
#         self.inf_wipe_button.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
#         self.def_wipe_button.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)
#         self.wipe_mode_frame.pack(side=tk.TOP, expand=True, fill=tk.X)
#         self.start_wipe_button.pack(side=tk.TOP, expand=True, padx=10, pady=10, fill=tk.X)

#         self.wipe_frame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
#         self.frq_control_frame.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)

#         self.us_off_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky=tk.NSEW)

#         self.topframe.pack(side=tk.TOP, padx=20, pady=20)
#         super().publish()

#     def set_scrolldigit(self) -> None:
#         """ Function regarding the scroll digit combobox """
#         self.frq_spinbox.config(
#             increment = str(10 ** (int(self.scroll_digit.get())-1)))


# class HometabDutyWipe(HomeTab):
#     """
#     The Hometab variation for the sonicwipe 40kHz Duty Cycle
#     amp. Instead of relying on a thread from the root, it handles
#     the GUI manually after pressing a button and getting a
#     response from the sonicwipe

#     Args:
#         HomeTab (ttk.Frame): The HomeTab parent class
#     """
#     def __init__(self, parent: ScNotebook, root: Root, *args, **kwargs) -> None:
#         super().__init__(parent, root, *args, **kwargs)

#         self.control_frame["text"] = 'Manual Control'

#         self.gain_spinbox: ttk.Spinbox = ttk.Spinbox(
#             self.control_frame,
#             from_=0,
#             increment=10,
#             to=100,
#             textvariable=self.root.gain,
#             width=5,
#             style='dark.TSpinbox',)

#         ToolTip(self.gain_spinbox, text="Configure the gain for your device")

#         self.set_val_btn: ttk.Button = ttk.Button(
#             self.control_frame,
#             text='Set Gain',
#             command=self.set_gain,
#             bootstyle='dark.TButton',)

#         self.us_on_button["command"] = self.set_signal_on
#         self.us_off_button["command"] = self.set_signal_off

#         self.gain_scale: ttk.Scale = ttk.Scale(
#             self.topframe,
#             from_=0,
#             to=100,
#             name='gainscale',
#             length=180,
#             orient=tk.VERTICAL,
#             style="primary.TScale",
#             variable=self.root.gain,)

#     def publish(self) -> None:
#         """
#         Method to publish children for the SonicWipe 40kHz Duty Cycle amp
#         """
#         self.gain_spinbox.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=5, pady=5)
#         self.set_val_btn.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=5, pady=5)
#         self.us_on_button.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=5, pady=5)
#         self.us_off_button.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=5, pady=5)

#         self.control_frame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
#         self.gain_scale.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)

#         self.topframe.pack(side=tk.TOP, padx=10, pady=10)

#         super().publish()

#     def set_gain(self) -> None:
#         """
#         Method to set the gain of a 40kHz Duty Cycle Wipe and
#         show the result accordingly in the whole Tkinter GUI.
#         Espescially considering the Statusframe of the application

#         Args:
#             gain (int): the value of to be setted gain
#         """
#         gain: int = int(self.serial.send_and_get(Command.SET_GAIN + self.gain_spinbox.get()))

#         if gain:

#             self.insert_feed(f'Gain setted to {gain}%')
#             self.root.status_frame.change_values(gain=gain)

#         else:
#             messagebox.showwarning("Error", "Something went wrong, try again, or restart the application")

#     def set_signal_on(self) -> None:
#         """
#         Method to set the US signal ON and update the GUI accordingly
#         """
#         if self.serial.send_and_get(Command.SET_SIGNAL_ON):

#             self.insert_feed('Signal ON')
#             self.root.status_frame.signal_on()

#         else:
#             messagebox.showwarning("Error", "Something went wrong, try again, or restart the application")

#     def set_signal_off(self) -> None:
#         """
#         Method to set the US signal OFF and update the GUI accordingly
#         """
#         if self.serial.send_and_get(Command.SET_SIGNAL_OFF):

#             self.insert_feed("Signal OFF")
#             self.root.status_frame.signal_off()

#         else:
#             messagebox.showwarning("Error", "Something went wrong, try again, or restart the application")

#     def attach_data(self) -> None:
#         pass


# class HomeTabCatchRev21(HomeTabCatch):

#     def __init__(self, parent: ScNotebook, root: Root, *args, **kwargs) -> None:
#         super().__init__(parent, root, *args, **kwargs)

#     def publish(self) -> None:
#         return super().publish()

#     def attach_data(self) -> None:
#         return super().attach_data()


# class HomeTabWipeRev21(HomeTabWipe):

#     def __init__(self, parent: ScNotebook, root: Root, *args, **kwargs) -> None:
#         super().__init__(parent, root, *args, **kwargs)

#     def publish(self) -> None:
#         return super().publish()

#     def attach_data(self) -> None:
#         return super().attach_data()
