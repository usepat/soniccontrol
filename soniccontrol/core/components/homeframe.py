import logging
import tkinter as tk
from typing import Iterable, Any
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame
import PIL
from soniccontrol.interfaces import RootChild, WidthLayout
import soniccontrol.constants as const
from soniccontrol.interfaces import Layout, Connectable, Feedbackable
from soniccontrol.sonicamp import Command

logger = logging.getLogger(__name__)


class HomeFrame(RootChild, Connectable, Feedbackable):
    def __init__(
        self, parent_frame: ttk.Frame, tab_title: str, image: PIL.Image, *args, **kwargs
    ):
        super().__init__(parent_frame, tab_title, image, *args, **kwargs)
        self._width_layouts = (
            WidthLayout(min_width=400, command=self.set_large_width_uscontrolframe),
            WidthLayout(min_width=10, command=self.set_small_width_uscontrolframe),
        )

        self._debounce_time_ms: int = 250
        self._debounce_job: Any = None

        self.topframe: ttk.Frame = ttk.Frame(self)
        # control frame
        self.control_frame: ttk.LabelFrame = ttk.LabelFrame(
            self.topframe, text="Manual Control"
        )
        self.freq_spinbox: ttk.Spinbox = ttk.Spinbox(
            self.control_frame,
            increment=100,
            from_=20_000,
            to=6_000_000,
            textvariable=self.root._freq,
            width=16,
            bootstyle=ttk.DARK,
            command=self.set_frequency,
        )
        self.gain_frame: ttk.Frame = ttk.Frame(self.control_frame)
        self.gain_spinbox: ttk.Spinbox = ttk.Spinbox(
            self.gain_frame,
            increment=10,
            from_=0,
            to=150,
            textvariable=self.root._gain,
            style=ttk.DARK,
            command=self.set_gain,
        )
        self.gain_scale: ttk.Scale = ttk.Scale(
            self.gain_frame,
            # length=170,
            from_=0,
            to=150,
            orient=tk.HORIZONTAL,
            style=ttk.SUCCESS,
            variable=self.root._gain,
            command=self.set_gain,
        )
        self.mode_frame: ttk.Label = ttk.Label(self.control_frame)

        self.wipemode_button: ttk.Radiobutton = ttk.Radiobutton(
            self.mode_frame,
            text="Wipe mode",
            variable=self.root.mode,
            value="Wipe",
            bootstyle="dark-outline-toolbutton",
            command=self.set_wipe_mode,
        )
        self.catchmode_button: ttk.Radiobutton = ttk.Radiobutton(
            self.mode_frame,
            text="Catch mode",
            variable=self.root.mode,
            value="Catch",
            bootstyle="dark-outline-toolbutton",
            command=self.set_catch_mode,
        )
        self.set_val_btn: ttk.Button = ttk.Button(
            self.control_frame,
            text="Set Frequency and Gain",
            bootstyle=ttk.DARK,
            command=self.set_values,
        )
        # signal control
        self.us_control_frame: ttk.Frame = ttk.Frame(self)
        self.us_on_button: ttk.Button = ttk.Button(
            self.us_control_frame,
            text="ON",
            bootstyle=ttk.SUCCESS,
            width=10,
            command=lambda: self.root.sonicamp.add_job(
                Command("!ON", callback=self.on_feedback), 0
            ),
        )

        self.us_auto_button: ttk.Button = ttk.Button(
            self.us_control_frame,
            text="AUTO",
            bootstyle=ttk.PRIMARY,
            width=10,
            command=lambda: self.root.sonicamp.add_job(
                Command("!AUTO", callback=self.on_feedback), 0
            ),
        )

        self.us_off_button: ttk.Button = ttk.Button(
            self.us_control_frame,
            text="OFF",
            bootstyle=ttk.DANGER,
            width=10,
            command=lambda: self.root.sonicamp.add_job(
                Command("!OFF", callback=self.on_feedback), 0
            ),
        )

        self.botframe: ttk.Frame = ttk.Frame(self)
        self.output_frame: ttk.Frame = ttk.LabelFrame(self.botframe, text="Feedback")
        self.feedback_frame: ScrolledFrame = ScrolledFrame(
            self.output_frame,
            height=200,
            width=475,
        )
        self.bind_events()

        self.freq_spinbox_placeholder = "Set Frequency..."
        self.freq_spinbox.delete(0, tk.END)
        self.freq_spinbox.insert(0, self.freq_spinbox_placeholder)
        self.freq_spinbox.bind("<FocusIn>", self.on_freq_spinbox_focus_in)
        self.freq_spinbox.bind("<FocusOut>", self.on_freq_spinbox_focus_out)

        self.gain_spinbox_placeholder = "Set Gain..."
        self.gain_spinbox.delete(0, tk.END)
        self.gain_spinbox.insert(0, self.gain_spinbox_placeholder)
        self.gain_spinbox.bind("<FocusIn>", self.on_gain_spinbox_focus_in)
        self.gain_spinbox.bind("<FocusOut>", self.on_gain_spinbox_focus_out)

    def on_gain_spinbox_focus_in(self, event):
        current_value = self.gain_spinbox.get()
        if current_value == self.gain_spinbox_placeholder:
            self.gain_spinbox.delete(0, tk.END)

    def on_gain_spinbox_focus_out(self, event):
        current_value = self.gain_spinbox.get()
        if not current_value:
            self.gain_spinbox.insert(0, self.gain_spinbox_placeholder)

    def on_freq_spinbox_focus_in(self, event):
        current_value = self.freq_spinbox.get()
        if current_value == self.freq_spinbox_placeholder:
            self.freq_spinbox.delete(0, tk.END)

    def on_freq_spinbox_focus_out(self, event):
        current_value = self.freq_spinbox.get()
        if not current_value:
            self.freq_spinbox.insert(0, self.freq_spinbox_placeholder)

    def on_connect(self, connection_data: Connectable.ConnectionData) -> None:
        return self.publish()

    def on_refresh(self, event=None) -> None:
        pass

    def publish(self) -> None:
        self.topframe.pack(side=tk.TOP, padx=10, pady=10)
        self.control_frame.pack(side=tk.TOP, fill=tk.X)
        self.freq_spinbox.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        self.gain_frame.pack(side=tk.TOP, fill=tk.X)
        self.gain_spinbox.grid(row=0, column=0, padx=10, pady=10)
        self.gain_scale.grid(row=0, column=1, padx=10, pady=10, sticky=tk.EW)

        self.mode_frame.pack(side=tk.TOP, fill=tk.X)
        self.wipemode_button.pack(
            side=ttk.LEFT, expand=True, fill=ttk.X, padx=10, pady=10
        )
        self.catchmode_button.pack(
            side=ttk.LEFT, expand=True, fill=ttk.X, padx=10, pady=10
        )

        self.set_val_btn.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        self.us_control_frame.pack(side=tk.TOP, padx=10, pady=10)

        self.botframe.pack(side=tk.TOP)
        self.feedback_frame.pack(
            side=tk.LEFT,
        )
        self.output_frame.pack(anchor=tk.N, side=tk.TOP, padx=10, pady=10, fill=tk.BOTH)

    def set_small_width_uscontrolframe(self, *args, **kwargs) -> None:
        for child in self.us_control_frame.children.values():
            child.grid_forget()
        self.us_on_button.pack(side=ttk.TOP, fill=ttk.X, padx=5, pady=5)
        self.us_auto_button.pack(side=ttk.TOP, fill=ttk.X, padx=5, pady=5)
        self.us_off_button.pack(side=ttk.TOP, fill=ttk.X, padx=5, pady=5)

    def set_large_width_uscontrolframe(self, *args, **kwargs) -> None:
        for i, child in enumerate(self.us_control_frame.children.values()):
            child.pack_forget()
        self.us_on_button.grid(row=0, column=0, padx=10, pady=10, sticky=tk.EW)
        self.us_auto_button.grid(row=0, column=1, padx=10, pady=10, sticky=tk.EW)
        self.us_off_button.grid(row=0, column=2, padx=10, pady=10, sticky=tk.EW)

    def set_frequency(self, event: Any = None) -> None:
        def _set_frequency() -> None:
            self.root.sonicamp.add_job(
                Command(
                    message=f"!f={self.root._freq.get()}", callback=self.on_feedback
                ),
                0,
            )
            self._debounce_job = None

        if self._debounce_job is not None:
            self.after_cancel(self._debounce_job)
        self._debounce_job = self.after(self._debounce_time_ms, _set_frequency)

    def set_gain(self, event: Any = None) -> None:
        logger.debug(event)

        def _set_gain() -> None:
            self.root.sonicamp.add_job(
                Command(
                    message=f"!g={self.root._gain.get()}", callback=self.on_feedback
                ),
                0,
            )
            self._debounce_job = None

        if self._debounce_job is not None:
            self.after_cancel(self._debounce_job)
        self._debounce_job = self.after(self._debounce_time_ms, _set_gain)

    def set_wipe_mode(self) -> None:
        self.root.sonicamp.add_job(Command("!KHZ", callback=self.on_feedback), 0)
        for child in self.gain_frame.winfo_children():
            child.configure(state=ttk.DISABLED)

    def set_catch_mode(self) -> None:
        self.root.sonicamp.add_job(Command("!MHZ", callback=self.on_feedback), 0)
        for child in self.gain_frame.winfo_children():
            child.configure(state=ttk.NORMAL)

    def set_values(self) -> None:
        self.root.sonicamp.add_job(
            Command(message=f"!f={self.root._freq.get()}", callback=self.on_feedback), 0
        )
        self.root.sonicamp.add_job(
            Command(message=f"!g={self.root._gain.get()}", callback=self.on_feedback), 1
        )

    def on_feedback(self, text: str) -> None:
        ttk.Label(self.feedback_frame, text=text, font=("Consolas", 10)).pack(
            fill=tk.X, side=tk.TOP, anchor=tk.W
        )
        self.feedback_frame.update()
        self.feedback_frame.yview_moveto(1)
