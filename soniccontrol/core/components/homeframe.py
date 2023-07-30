import logging
import tkinter as tk
from typing import Iterable
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame
import PIL
from soniccontrol.interfaces import RootChild, WidthLayout
import soniccontrol.constants as const
from soniccontrol.interfaces.layout import Layout

logger = logging.getLogger(__name__)


class HomeFrame(RootChild):
    def __init__(
        self, parent_frame: ttk.Frame, tab_title: str, image: PIL.Image, *args, **kwargs
    ):
        super().__init__(parent_frame, tab_title, image, *args, **kwargs)
        # Tkinter variables
        self._freq: tk.IntVar = tk.IntVar()
        self._gain: tk.IntVar = tk.IntVar()
        self._mode: tk.StringVar = tk.StringVar()
        self._wipe_inf_or_def: tk.BooleanVar = tk.BooleanVar()
        self._wipe_var: tk.IntVar = tk.IntVar()

        self.topframe: ttk.Frame = ttk.Frame(self)
        # control frame
        self.control_frame: ttk.LabelFrame = ttk.LabelFrame(
            self.topframe, text="Manual Control"
        )
        self.freq_spinbox: ttk.Spinbox = ttk.Spinbox(
            self.control_frame,
            increment=100,
            textvariable=self._freq,
            width=16,
            bootstyle=ttk.DARK,
            command=lambda: self.event_generate(const.Events.SET_FREQ),
        )
        self.gain_frame: ttk.Frame = ttk.Frame(self.control_frame)
        self.gain_spinbox: ttk.Spinbox = ttk.Spinbox(
            self.gain_frame,
            increment=10,
            textvariable=self._gain,
            width=5,
            style=ttk.DARK,
            command=lambda: self.event_generate(const.Events.SET_GAIN),
        )
        self.gain_scale: ttk.Scale = ttk.Scale(
            self.gain_frame,
            length=180,
            orient=tk.HORIZONTAL,
            style=ttk.SUCCESS,
            variable=self._gain,
        )
        self.mode_frame: ttk.Label = ttk.Label(self.control_frame)
        self.wipemode_button: ttk.Radiobutton = ttk.Radiobutton(
            self.mode_frame,
            text="Wipe mode",
            variable=self._mode,
            bootstyle="dark-outline-toolbutton",
            width=12,
            command=lambda: self.event_generate(const.Events.SET_MODE),
        )
        self.catchmode_button: ttk.Radiobutton = ttk.Radiobutton(
            self.mode_frame,
            text="Catch mode",
            variable=self._mode,
            bootstyle="dark-outline-toolbutton",
            width=12,
            command=lambda: self.event_generate(const.Events.SET_MODE),
        )
        self.set_val_btn: ttk.Button = ttk.Button(
            self.control_frame,
            text="Set Frequency and Gain",
            bootstyle=ttk.DARK,
            command=lambda: self.event_generate(const.Events.SET_VALUES),
        )
        # signal control
        self.us_control_frame: ttk.Frame = ttk.Frame(self)
        self.us_on_button: ttk.Button = ttk.Button(
            self.us_control_frame,
            text="ON",
            bootstyle=ttk.SUCCESS,
            width=10,
            command=lambda: self.event_generate(const.Events.SET_SIGNAL_ON),
        )

        self.us_auto_button: ttk.Button = ttk.Button(
            self.us_control_frame,
            text="AUTO",
            bootstyle=ttk.PRIMARY,
            width=10,
            command=lambda: self.event_generate(const.Events.SET_SIGNAL_AUTO),
        )

        self.us_off_button: ttk.Button = ttk.Button(
            self.us_control_frame,
            text="OFF",
            bootstyle=ttk.DANGER,
            width=10,
            command=lambda: self.event_generate(const.Events.SET_SIGNAL_OFF),
        )

        self.botframe: ttk.Frame = ttk.Frame(self)
        self.output_frame: ttk.Frame = ttk.LabelFrame(self.botframe, text="Feedback")
        self.feedback_frame: ScrolledFrame = ScrolledFrame(
            self.output_frame,
            height=200,
            width=475,
        )

    def publish(self) -> None:
        self.topframe.pack(side=tk.TOP, padx=10, pady=10)
        self.control_frame.pack(side=tk.TOP, expand=True, fill=tk.X)
        self.freq_spinbox.pack(side=tk.TOP, expand=True, fill=tk.X, padx=10, pady=10)

        self.gain_frame.pack(side=tk.TOP, expand=True, fill=tk.X)
        self.gain_spinbox.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.gain_scale.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)

        self.mode_frame.pack(side=tk.TOP, expand=True, fill=tk.X)
        self.wipemode_button.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.catchmode_button.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)

        self.set_val_btn.pack(side=tk.TOP, expand=True, fill=tk.X, padx=10, pady=10)

        self.us_control_frame.pack(side=tk.TOP, padx=10, pady=10)

        self.botframe.pack(side=tk.TOP)
        self.feedback_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.output_frame.pack(
            anchor=tk.N, side=tk.TOP, padx=10, pady=10, expand=True, fill=tk.BOTH
        )

    def set_small_width_uscontrolframe(self) -> None:
        for child in self.us_control_frame.children.values():
            child.grid_forget()
        self.us_on_button.pack(side=ttk.TOP, fill=ttk.X, padx=5, pady=5)
        self.us_auto_button.pack(side=ttk.TOP, fill=ttk.X, padx=5, pady=5)
        self.us_off_button.pack(side=ttk.TOP, fill=ttk.X, padx=5, pady=5)

    def set_large_width_uscontrolframe(self) -> None:
        for i, child in enumerate(self.us_control_frame.children.values()):
            child.pack_forget()
        self.us_on_button.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.us_auto_button.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)
        self.us_off_button.grid(row=0, column=2, padx=10, pady=10, sticky=tk.NSEW)


class HomeFrameWidthLayout100(WidthLayout):
    def __init__(self, subject: HomeFrame) -> None:
        super().__init__(subject)

    @property
    def minimum_size(self) -> int:
        return 300

    def apply(self, event) -> None:
        self.subject.set_small_width_uscontrolframe()


class HomeFrameWidthLayout300(WidthLayout):
    def __init__(self, subject: HomeFrame) -> None:
        super().__init__(subject)

    @property
    def minimum_size(self) -> int:
        return 400

    def apply(self, event) -> None:
        self.subject.set_large_width_uscontrolframe()
