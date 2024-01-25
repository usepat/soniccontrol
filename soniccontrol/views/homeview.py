import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame

import soniccontrol.utils as utils
import soniccontrol.utils.constants as const
from soniccontrol.components.spinbox import Spinbox
from soniccontrol.interfaces.layouts import Layout


class HomeView(ttk.Frame):
    def __init__(self, master: ttk.Window, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)
        self._master: ttk.Window = master
        self._image = utils.give_image(const.images.HOME_ICON_BLACK, (25, 25))

        self._main_frame: ScrolledFrame = ScrolledFrame(self, autohide=True)
        self._top_frame: ttk.Frame = ttk.Frame(self._main_frame)

        # Control Frame - Setting Frequency, Gain, Mode
        self._control_frame: ttk.Labelframe = ttk.Labelframe(
            self._top_frame, text=const.ui.HOME_CONTROL_LABEL
        )
        self._freq_spinbox: Spinbox = Spinbox(
            self._control_frame, placeholder=const.ui.FREQ_PLACEHOLDER, style=ttk.DARK
        )
        self._gain_control_frame: ttk.Frame = ttk.Frame(self._control_frame)
        self._gain_spinbox: Spinbox = Spinbox(
            self._gain_control_frame,
            placeholder=const.ui.GAIN_PLACEHOLDER,
            style=ttk.DARK,
        )
        self._gain_scale: ttk.Scale = ttk.Scale(
            self._gain_control_frame, orient=ttk.HORIZONTAL, style=ttk.SUCCESS
        )
        self._mode_frame: ttk.Frame = ttk.Frame(self._control_frame)
        self._wipe_mode_button: ttk.Radiobutton = ttk.Radiobutton(
            self._mode_frame,
            text=const.ui.WIPE_MODE_LABEL,
            value=const.ui.WIPE_LABEL,
            style="dark-outline-toolbutton",
        )
        self._catch_mode_button: ttk.Radiobutton = ttk.Radiobutton(
            self._mode_frame,
            text=const.ui.CATCH_MODE_LABEL,
            value=const.ui.CATCH_LABEL,
            style="dark-outline-toolbutton",
        )
        self._set_values_button: ttk.Button = ttk.Button(
            self._control_frame, text=const.ui.SET_VALUES_LABEL, style=ttk.DARK
        )

        # Bot Frame with Feedback Output
        self._bot_frame: ttk.Frame = ttk.Frame(self._main_frame)
        self._output_frame: ttk.Frame = ttk.Labelframe(
            self._bot_frame, text=const.ui.OUTPUT_LABEL
        )
        self._feedback_frame: ScrolledFrame = ScrolledFrame(self._output_frame)

        # UltraSound Control Frame
        self._us_control_frame: ttk.Frame = ttk.Frame(self)
        self._us_on_button: ttk.Button = ttk.Button(
            self._us_control_frame, text=const.ui.ON_LABEL, style=ttk.SUCCESS
        )
        self._us_off_button: ttk.Button = ttk.Button(
            self._us_control_frame, text=const.ui.OFF_LABEL, style=ttk.DANGER
        )
        self._us_auto_button: ttk.Button = ttk.Button(
            self._us_control_frame, text=const.ui.AUTO_LABEL, style=ttk.PRIMARY
        )

        self._init_publish()

    @property
    def image(self) -> ttk.ImageTk.PhotoImage:
        return self._image

    @property
    def tab_title(self) -> str:
        return const.ui.HOME_LABEL

    @property
    def layouts(self) -> set[Layout]:
        ...

    def _init_publish(self) -> None:
        self._main_frame.pack(fill=ttk.BOTH, expand=True)
        self._top_frame.pack(pady=10, padx=10)

        self._control_frame.pack(fill=ttk.X)
        self._freq_spinbox.pack(fill=ttk.X, padx=10, pady=10)

        self._gain_control_frame.columnconfigure(0, weight=1)
        self._gain_control_frame.columnconfigure(1, weight=1)
        self._gain_control_frame.pack(fill=ttk.X)
        self._gain_spinbox.grid(row=0, column=0, padx=10, pady=10, sticky=ttk.EW)
        self._gain_scale.grid(row=0, column=1, padx=10, pady=10, sticky=ttk.EW)

        self._mode_frame.columnconfigure(0, weight=1)
        self._mode_frame.columnconfigure(1, weight=1)
        self._mode_frame.pack(fill=ttk.X)
        self._wipe_mode_button.grid(row=0, column=0, padx=10, pady=10, sticky=ttk.EW)
        self._catch_mode_button.grid(row=0, column=1, padx=10, pady=10, sticky=ttk.EW)

        self._set_values_button.pack(fill=ttk.X, padx=10, pady=10)

        self._us_control_frame.columnconfigure(0, weight=1)
        self._us_control_frame.columnconfigure(1, weight=1)
        self._us_control_frame.columnconfigure(2, weight=1)
        self._us_control_frame.pack(pady=10, padx=10, fill=ttk.X, anchor=ttk.CENTER)
        self._us_on_button.grid(row=0, column=0, padx=10, pady=10, sticky=ttk.EW)
        self._us_auto_button.grid(row=0, column=1, padx=10, pady=10, sticky=ttk.EW)
        self._us_off_button.grid(row=0, column=2, padx=10, pady=10, sticky=ttk.EW)

        self._bot_frame.pack()
        self._feedback_frame.pack(padx=10, pady=10, fill=ttk.BOTH)
        self._output_frame.pack(anchor=ttk.N, padx=10, pady=10, fill=ttk.BOTH)

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

    def on_feedback(self) -> None:
        ...

    def on_wipe_mode_toggle(self) -> None:
        ...

    def on_auto_mode_toggle(self) -> None:
        ...
