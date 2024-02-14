import ttkbootstrap as ttk

from soniccontrol import utils
from soniccontrol.components.horizontalscrolled import HorizontalScrolledFrame
from soniccontrol.interfaces.layouts import Layout
from soniccontrol.utils import constants as const


class StatusBarView(ttk.Frame):
    def __init__(self, master: ttk.Window, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)
        self._master: ttk.Window = master

        self._main_frame: ttk.Frame = ttk.Frame(self, style=ttk.SECONDARY)

        self._program_state_frame: ttk.Frame = ttk.Frame(self._main_frame)
        self._program_state_label: ttk.Label = ttk.Label(
            self._program_state_frame, style=const.style.INVERSE_SECONDARY
        )

        self._scrolled_info_frame: HorizontalScrolledFrame = HorizontalScrolledFrame(
            self._main_frame, style=ttk.SECONDARY, autohide=True
        )
        self._scrolled_info_frame.hide_scrollbars()

        self._freq_frame: ttk.Frame = ttk.Frame(self._scrolled_info_frame)
        self._freq_label: ttk.Label = ttk.Label(
            self._freq_frame, style=const.style.INVERSE_SECONDARY
        )

        self._gain_frame: ttk.Frame = ttk.Frame(self._scrolled_info_frame)
        self._gain_label: ttk.Label = ttk.Label(
            self._gain_frame,
            style=const.style.INVERSE_SECONDARY,
        )

        self._temperature_frame: ttk.Frame = ttk.Frame(self._scrolled_info_frame)
        self._temperature_label: ttk.Label = ttk.Label(
            self._temperature_frame,
            style=const.style.INVERSE_SECONDARY,
        )

        self._mode_frame: ttk.Frame = ttk.Frame(self._scrolled_info_frame)
        self._mode_label: ttk.Label = ttk.Label(
            self._mode_frame,
            style=const.style.INVERSE_SECONDARY,
        )

        self._urms_frame: ttk.Frame = ttk.Frame(self._scrolled_info_frame)
        self._urms_label: ttk.Label = ttk.Label(
            self._urms_frame,
            style=const.style.INVERSE_SECONDARY,
        )

        self._irms_frame: ttk.Frame = ttk.Frame(self._scrolled_info_frame)
        self._irms_label: ttk.Label = ttk.Label(
            self._irms_frame,
            style=const.style.INVERSE_SECONDARY,
        )

        self._phase_frame: ttk.Frame = ttk.Frame(self._scrolled_info_frame)
        self._phase_label: ttk.Label = ttk.Label(
            self._phase_frame,
            style=const.style.INVERSE_SECONDARY,
        )

        self._signal_frame: ttk.Frame = ttk.Frame(self)
        ICON_LABEL_PADDING: tuple[int, int, int, int] = (8, 0, 0, 0)
        self._connection_label: ttk.Label = ttk.Label(
            self._signal_frame,
            style=const.style.INVERSE_DANGER,
            padding=ICON_LABEL_PADDING,
            image=utils.ImageLoader.load_image(
                const.images.CONNECTION_ICON_WHITE, const.misc.BUTTON_ICON_SIZE
            ),
            compound=ttk.LEFT,
        )
        self._signal_label: ttk.Label = ttk.Label(
            self._signal_frame,
            style=const.style.INVERSE_DANGER,
            padding=ICON_LABEL_PADDING,
            image=utils.ImageLoader.load_image(
                const.images.LIGHTNING_ICON_WHITE, const.misc.BUTTON_ICON_SIZE
            ),
            compound=ttk.LEFT,
        )
        self._init_publish()

    @property
    def layouts(self) -> set[Layout]:
        ...

    def _init_publish(self) -> None:
        self._program_state_label.pack(side=ttk.LEFT, ipadx=5)
        self._freq_label.pack(side=ttk.LEFT)
        self._gain_label.pack(side=ttk.LEFT)
        self._mode_label.pack(side=ttk.LEFT)
        self._temperature_label.pack(side=ttk.LEFT)
        self._urms_label.pack(side=ttk.LEFT)
        self._irms_label.pack(side=ttk.LEFT)
        self._phase_label.pack(side=ttk.LEFT)

        self._signal_frame.pack(side=ttk.RIGHT)
        self._signal_label.pack(side=ttk.RIGHT, ipadx=3)
        self._connection_label.pack(side=ttk.RIGHT, ipadx=3)


class StatusView(ttk.Frame):
    def __init__(self, master: ttk.Window | ttk.tk.Widget, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)
        self._master: ttk.Window | ttk.tk.Widget = master

        self._main_frame: ttk.Frame = ttk.Frame(self)
        self._meter_frame: ttk.Frame = ttk.Frame(self._main_frame)
        self._sonicmeasure_values_frame: ttk.Label = ttk.Label(
            self._main_frame, background="lightgrey"
        )
        self._signal_frame: ttk.Label = ttk.Label(self._main_frame, background="grey")

        self._freq_meter: ttk.Meter = ttk.Meter(
            self._meter_frame,
            bootstyle=ttk.DARK,
            textright=const.ui.KHZ,
            subtext=const.ui.FREQUENCY,
            metersize=130,
        )
        self._gain_meter: ttk.Meter = ttk.Meter(
            self._meter_frame,
            bootstyle=ttk.SUCCESS,
            textright=const.ui.PERCENT,
            subtext=const.ui.GAIN,
            metersize=130,
        )
        self._temp_meter: ttk.Meter = ttk.Meter(
            self._meter_frame,
            bootstyle=ttk.WARNING,
            textright=const.ui.DEGREE_CELSIUS,
            subtext=const.ui.TEMPERATURE,
            metersize=130,
        )

        self._urms_label: ttk.Label = ttk.Label(
            self._sonicmeasure_values_frame,
            anchor=ttk.CENTER,
            style=ttk.PRIMARY,
            background="lightgrey",
            text="URMS: 1000.10",
            font=("QTypeOT", 10),
        )
        self._irms_label: ttk.Label = ttk.Label(
            self._sonicmeasure_values_frame,
            anchor=ttk.CENTER,
            style=ttk.DANGER,
            background="lightgrey",
            text="IRMS: 1000.100",
            font=("QTypeOT", 10),
        )
        self._phase_label: ttk.Label = ttk.Label(
            self._sonicmeasure_values_frame,
            anchor=ttk.CENTER,
            style=ttk.INFO,
            background="lightgrey",
            text="PHASE: 1000.1000",
            font=("QTypeOT", 10),
        )

        self._connection_label: ttk.Label = ttk.Label(
            self._signal_frame,
            anchor=ttk.CENTER,
            justify=ttk.CENTER,
            compound=ttk.LEFT,
            font=("QTypeOT", 15),
            foreground="white",
            background="grey",
            image=utils.ImageLoader.load_image(const.images.LED_ICON_RED, (20, 20)),
            style=const.style.INVERSE_SECONDARY,
            text=const.ui.NOT_CONNECTED,
        )
        self._signal_label: ttk.Label = ttk.Label(
            self._signal_frame,
            anchor=ttk.CENTER,
            justify=ttk.CENTER,
            compound=ttk.LEFT,
            font=("QTypeOT", 15),
            foreground="white",
            background="grey",
            image=utils.ImageLoader.load_image(const.images.LED_ICON_RED, (20, 20)),
            style=const.style.INVERSE_SECONDARY,
            text=const.ui.SIGNAL_OFF,
        )
        self._init_publish()

    @property
    def layouts(self) -> set[Layout]:
        ...

    def _init_publish(self) -> None:
        self._main_frame.pack(expand=True, fill=ttk.BOTH)
        self._main_frame.columnconfigure(0, weight=1)
        self._meter_frame.grid(row=0, column=0)
        self._sonicmeasure_values_frame.grid(row=1, column=0, sticky=ttk.EW)
        self._signal_frame.grid(row=2, column=0, sticky=ttk.EW)

        self._meter_frame.rowconfigure(0, weight=1)
        self._freq_meter.grid(row=0, column=0, padx=5, pady=5)
        self._gain_meter.grid(row=0, column=1, padx=5, pady=5)
        self._temp_meter.grid(row=0, column=2, padx=5, pady=5)

        self._sonicmeasure_values_frame.rowconfigure(0, weight=1)
        self._sonicmeasure_values_frame.columnconfigure(0, weight=1)
        self._sonicmeasure_values_frame.columnconfigure(1, weight=1)
        self._sonicmeasure_values_frame.columnconfigure(2, weight=1)
        self._urms_label.grid(row=0, column=0, padx=10, pady=5)
        self._irms_label.grid(row=0, column=1, padx=10, pady=5)
        self._phase_label.grid(row=0, column=2, padx=10, pady=5)

        self._signal_frame.rowconfigure(0, weight=1)
        self._signal_frame.columnconfigure(0, weight=1)
        self._signal_frame.columnconfigure(1, weight=1)
        self._connection_label.grid(row=0, column=0, padx=15, pady=5)
        self._signal_label.grid(row=0, column=1, padx=15, pady=5)
