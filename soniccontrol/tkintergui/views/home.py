import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame

from soniccontrol.interfaces.view import TabView
from soniccontrol.tkintergui.utils.constants import sizes, style, ui_labels
from soniccontrol.tkintergui.utils.image_loader import ImageLoader
from soniccontrol.tkintergui.widgets.spinbox import Spinbox
from soniccontrol.utils.files import images


class HomeView(TabView):
    def __init__(self, master: ttk.Window, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)
        self._setter_widgets: set[ttk.ttk.Widget] = {
            self._freq_spinbox,
            self._gain_spinbox,
            self._gain_scale,
            self._wipe_mode_button,
            self._catch_mode_button,
            self._set_values_button,
        }

    @property
    def image(self) -> ttk.ImageTk.PhotoImage:
        return ImageLoader.load_image(images.HOME_ICON_BLACK, (25, 25))

    @property
    def tab_title(self) -> str:
        return ui_labels.HOME_LABEL

    def _initialize_children(self) -> None:
        self._main_frame: ScrolledFrame = ScrolledFrame(self, autohide=True)
        self._top_frame: ttk.Frame = ttk.Frame(self._main_frame)

        # Control Frame - Setting Frequency, Gain, Mode
        self._control_frame: ttk.Labelframe = ttk.Labelframe(
            self._top_frame, text=ui_labels.HOME_CONTROL_LABEL
        )
        self._freq_spinbox: Spinbox = Spinbox(
            self._control_frame,
            placeholder=ui_labels.FREQ_PLACEHOLDER,
            scrolled_frame=self._main_frame,
            style=ttk.DARK,
        )
        self._gain_control_frame: ttk.Frame = ttk.Frame(self._control_frame)
        self._gain_spinbox: Spinbox = Spinbox(
            self._gain_control_frame,
            placeholder=ui_labels.GAIN_PLACEHOLDER,
            scrolled_frame=self._main_frame,
            style=ttk.DARK,
        )
        self._gain_scale: ttk.Scale = ttk.Scale(
            self._gain_control_frame,
            orient=ttk.HORIZONTAL,
            style=ttk.SUCCESS,
            from_=0,
            to=150,
        )
        self._mode_frame: ttk.Frame = ttk.Frame(self._control_frame)
        self._wipe_mode_button: ttk.Radiobutton = ttk.Radiobutton(
            self._mode_frame,
            text=ui_labels.WIPE_MODE_LABEL,
            value=ui_labels.WIPE_LABEL,
            style=style.DARK_OUTLINE_TOOLBUTTON,
        )
        self._catch_mode_button: ttk.Radiobutton = ttk.Radiobutton(
            self._mode_frame,
            text=ui_labels.CATCH_MODE_LABEL,
            value=ui_labels.CATCH_LABEL,
            style=style.DARK_OUTLINE_TOOLBUTTON,
        )
        self._set_values_button: ttk.Button = ttk.Button(
            self._control_frame, text=ui_labels.SET_VALUES_LABEL, style=ttk.DARK
        )

        # Bot Frame with Feedback Output
        self._bot_frame: ttk.Frame = ttk.Frame(self._main_frame)
        self._output_frame: ttk.Labelframe = ttk.Labelframe(
            self._bot_frame, text=ui_labels.OUTPUT_LABEL
        )
        self._feedback_frame: ScrolledFrame = ScrolledFrame(self._output_frame)

        # UltraSound Control Frame
        self._us_control_frame: ttk.Frame = ttk.Frame(self)
        self._us_on_button: ttk.Button = ttk.Button(
            self._us_control_frame, text=ui_labels.ON_LABEL, style=ttk.SUCCESS
        )
        self._us_off_button: ttk.Button = ttk.Button(
            self._us_control_frame, text=ui_labels.OFF_LABEL, style=ttk.DANGER
        )
        self._us_auto_button: ttk.Button = ttk.Button(
            self._us_control_frame, text=ui_labels.AUTO_LABEL, style=ttk.PRIMARY
        )

    def _initialize_publish(self) -> None:
        # TODO: Comments to know in which row and order one is initializing the layout
        self.columnconfigure(0, weight=sizes.EXPAND)
        self.rowconfigure(0, weight=sizes.EXPAND)
        self.rowconfigure(1, weight=sizes.DONT_EXPAND, minsize=30)
        self._main_frame.grid(row=0, column=0, sticky=ttk.NSEW)
        self._top_frame.pack(pady=sizes.LARGE_PADDING, padx=sizes.LARGE_PADDING)

        self._control_frame.pack(fill=ttk.X)
        self._freq_spinbox.pack(
            fill=ttk.X, padx=sizes.LARGE_PADDING, pady=sizes.LARGE_PADDING
        )

        self._gain_control_frame.columnconfigure(0, weight=sizes.EXPAND)
        self._gain_control_frame.columnconfigure(1, weight=sizes.EXPAND)
        self._gain_control_frame.pack(fill=ttk.X)
        self._gain_spinbox.grid(
            row=0,
            column=0,
            padx=sizes.LARGE_PADDING,
            pady=sizes.LARGE_PADDING,
            sticky=ttk.EW,
        )
        self._gain_scale.grid(
            row=0,
            column=1,
            padx=sizes.LARGE_PADDING,
            pady=sizes.LARGE_PADDING,
            sticky=ttk.EW,
        )

        self._mode_frame.columnconfigure(0, weight=sizes.EXPAND)
        self._mode_frame.columnconfigure(1, weight=sizes.EXPAND)
        self._mode_frame.pack(fill=ttk.X)
        self._wipe_mode_button.grid(
            row=0,
            column=0,
            padx=sizes.LARGE_PADDING,
            pady=sizes.LARGE_PADDING,
            sticky=ttk.EW,
        )
        self._catch_mode_button.grid(
            row=0,
            column=1,
            padx=sizes.LARGE_PADDING,
            pady=sizes.LARGE_PADDING,
            sticky=ttk.EW,
        )

        self._set_values_button.pack(
            fill=ttk.X, padx=sizes.LARGE_PADDING, pady=sizes.LARGE_PADDING
        )

        self._us_control_frame.columnconfigure(0, weight=sizes.EXPAND)
        self._us_control_frame.columnconfigure(1, weight=sizes.EXPAND)
        self._us_control_frame.columnconfigure(2, weight=sizes.EXPAND)
        self._us_control_frame.grid(
            row=1,
            column=0,
            padx=sizes.LARGE_PADDING,
            pady=sizes.MEDIUM_PADDING,
            sticky=ttk.EW,
        )
        self._us_on_button.grid(
            row=0, column=0, padx=sizes.LARGE_PADDING, sticky=ttk.EW
        )
        self._us_auto_button.grid(
            row=0, column=1, padx=sizes.LARGE_PADDING, sticky=ttk.EW
        )
        self._us_off_button.grid(
            row=0, column=2, padx=sizes.LARGE_PADDING, sticky=ttk.EW
        )

        self._bot_frame.pack()
        self._feedback_frame.pack(
            padx=sizes.LARGE_PADDING, pady=sizes.LARGE_PADDING, fill=ttk.BOTH
        )
        self._output_frame.pack(
            anchor=ttk.N,
            padx=sizes.LARGE_PADDING,
            pady=sizes.LARGE_PADDING,
            fill=ttk.BOTH,
        )

    def on_feedback(self, feedback: str) -> None:
        ttk.Label(self._feedback_frame, text=feedback, font=("Consolas", 10)).pack(
            fill=ttk.X, side=ttk.TOP, anchor=ttk.W
        )
        self._feedback_frame.update()
        self._feedback_frame.yview_moveto(1)

    def enable_gain(self) -> None:
        self._change_gain(ttk.NORMAL)

    def disable_gain(self) -> None:
        self._change_gain(ttk.DISABLED)

    def _change_gain(self, state: str) -> None:
        for child in self._gain_control_frame.winfo_children():
            child.configure(state=state)

    def disable_control_panel(self, *args, **kwargs) -> None:
        for child in self._setter_widgets:
            child.configure(state=ttk.DISABLED)

    def enable_control_panel(self, *args, **kwargs) -> None:
        for child in self._setter_widgets:
            child.configure(state=ttk.NORMAL)

    def publish(self) -> None:
        ...

    def set_small_width_layout(self) -> None:
        ...

    def set_large_widht_layout(self) -> None:
        ...

    def on_relay_mode_mhz(self) -> None:
        ...

    def on_relay_mode_khz(self) -> None:
        ...

    def on_wipe_mode_toggle(self) -> None:
        ...

    def on_auto_mode_toggle(self) -> None:
        ...
