import ttkbootstrap as ttk

from soniccontrol import soniccontrol_logger as logger
from soniccontrol import utils
from soniccontrol.components.horizontalscrolled import HorizontalScrolledFrame
from soniccontrol.interfaces.layouts import Layout
from soniccontrol.interfaces.view import View
from soniccontrol.utils import constants as const


class StatusBarView(View):
    def __init__(self, master: ttk.Window, *args, **kwargs) -> None:
        super().__init__(master, style=ttk.SECONDARY, *args, **kwargs)

    def _initialize_children(self) -> None:
        self._main_frame: ttk.Frame = ttk.Frame(self, style=ttk.SECONDARY)

        self._program_state_frame: ttk.Frame = ttk.Frame(self._main_frame)
        self._program_state_label: ttk.Label = ttk.Label(
            self._program_state_frame, style=const.style.INVERSE_SECONDARY
        )

        self._scrolled_info_frame: HorizontalScrolledFrame = HorizontalScrolledFrame(
            self._main_frame, style=ttk.SECONDARY, autohide=False
        )
        self._scrolled_info_frame.hide_scrollbars()

        self._freq_frame: ttk.Frame = ttk.Frame(
            self._scrolled_info_frame, style=ttk.SECONDARY
        )
        self._freq_label: ttk.Label = ttk.Label(
            self._freq_frame, style=const.style.INVERSE_SECONDARY
        )

        self._gain_frame: ttk.Frame = ttk.Frame(
            self._scrolled_info_frame, style=ttk.SECONDARY
        )
        self._gain_label: ttk.Label = ttk.Label(
            self._gain_frame,
            style=const.style.INVERSE_SECONDARY,
        )

        self._temperature_frame: ttk.Frame = ttk.Frame(
            self._scrolled_info_frame, style=ttk.SECONDARY
        )
        self._temperature_label: ttk.Label = ttk.Label(
            self._temperature_frame,
            style=const.style.INVERSE_SECONDARY,
        )

        self._mode_frame: ttk.Frame = ttk.Frame(
            self._scrolled_info_frame, style=ttk.SECONDARY
        )
        self._mode_label: ttk.Label = ttk.Label(
            self._mode_frame,
            style=const.style.INVERSE_SECONDARY,
        )

        self._urms_frame: ttk.Frame = ttk.Frame(
            self._scrolled_info_frame, style=ttk.SECONDARY
        )
        self._urms_label: ttk.Label = ttk.Label(
            self._urms_frame,
            style=const.style.INVERSE_SECONDARY,
        )

        self._irms_frame: ttk.Frame = ttk.Frame(
            self._scrolled_info_frame, style=ttk.SECONDARY
        )
        self._irms_label: ttk.Label = ttk.Label(
            self._irms_frame,
            style=const.style.INVERSE_SECONDARY,
        )

        self._phase_frame: ttk.Frame = ttk.Frame(
            self._scrolled_info_frame, style=ttk.SECONDARY
        )
        self._phase_label: ttk.Label = ttk.Label(
            self._phase_frame,
            style=const.style.INVERSE_SECONDARY,
        )

        self._signal_frame: ttk.Frame = ttk.Frame(self, style=ttk.SECONDARY)
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

    def _initialize_publish(self) -> None:
        self._main_frame.pack(side=ttk.LEFT, fill=ttk.X, expand=True)
        self._main_frame.columnconfigure(1, weight=const.misc.EXPAND)
        self._main_frame.rowconfigure(0, weight=const.misc.EXPAND)

        self._signal_frame.pack(side=ttk.RIGHT)
        self._signal_label.pack(side=ttk.RIGHT, ipadx=const.misc.SMALL_PADDING)
        self._connection_label.pack(side=ttk.RIGHT, ipadx=const.misc.SMALL_PADDING)

        self._program_state_frame.grid(
            row=0, column=0, sticky=ttk.EW, padx=const.misc.MEDIUM_PADDING
        )
        self._program_state_label.pack(side=ttk.LEFT)

        self._scrolled_info_frame.grid(row=0, column=1, sticky=ttk.EW)
        self._scrolled_info_frame.columnconfigure(0, weight=const.misc.EXPAND)
        self._scrolled_info_frame.columnconfigure(1, weight=const.misc.EXPAND)
        self._scrolled_info_frame.columnconfigure(2, weight=const.misc.EXPAND)
        self._scrolled_info_frame.columnconfigure(3, weight=const.misc.EXPAND)
        self._scrolled_info_frame.columnconfigure(4, weight=const.misc.EXPAND)
        self._scrolled_info_frame.columnconfigure(5, weight=const.misc.EXPAND)
        self._scrolled_info_frame.columnconfigure(6, weight=const.misc.EXPAND)
        self._scrolled_info_frame.rowconfigure(0, weight=const.misc.EXPAND)

        self._freq_frame.grid(
            row=0, column=0, padx=const.misc.MEDIUM_PADDING, sticky=ttk.EW
        )
        self._freq_label.pack(side=ttk.LEFT, fill=ttk.X, expand=True)

        self._gain_frame.grid(
            row=0, column=1, padx=const.misc.MEDIUM_PADDING, sticky=ttk.EW
        )
        self._gain_label.pack(side=ttk.LEFT, fill=ttk.X)

        self._mode_frame.grid(
            row=0, column=2, padx=const.misc.MEDIUM_PADDING, sticky=ttk.EW
        )
        self._mode_label.pack(side=ttk.LEFT, fill=ttk.X)

        self._temperature_frame.grid(
            row=0, column=3, padx=const.misc.MEDIUM_PADDING, sticky=ttk.EW
        )
        self._temperature_label.pack(side=ttk.LEFT, fill=ttk.X)

        self._urms_frame.grid(
            row=0, column=4, padx=const.misc.MEDIUM_PADDING, sticky=ttk.EW
        )
        self._urms_label.pack(side=ttk.LEFT, fill=ttk.X)

        self._irms_frame.grid(
            row=0, column=5, padx=const.misc.MEDIUM_PADDING, sticky=ttk.EW
        )
        self._irms_label.pack(side=ttk.LEFT, fill=ttk.X)

        self._phase_frame.grid(
            row=0, column=6, padx=const.misc.MEDIUM_PADDING, sticky=ttk.EW
        )
        self._phase_label.pack(side=ttk.LEFT, fill=ttk.X)

    def on_signal_turn_on(self, event: ttk.tk.Event) -> None:
        self._signal_label.configure(bootstyle=const.style.INVERSE_SUCCESS)

    def on_connected(self, event: ttk.tk.Event) -> None:
        self._scrolled_info_frame.grid()
        self._connection_label.configure(bootstyle=const.style.INVERSE_SUCCESS)

    def on_disconnected(self, event: ttk.tk.Event) -> None:
        self._scrolled_info_frame.grid_remove()
        self._signal_label.configure(bootstyle=const.style.INVERSE_DANGER)
        self._connection_label.configure(bootstyle=const.style.INVERSE_DANGER)

    def on_script_start(self, event: ttk.tk.Event) -> None:
        self._program_state_label.configure(bootstyle=const.style.INVERSE_SUCCESS)
        self._program_state_frame.configure(bootstyle=ttk.SUCCESS)

    def on_idle(self, event: ttk.tk.Event) -> None:
        self._program_state_frame.configure(bootstyle=ttk.SECONDARY)

    def on_auto_mode(self, event: ttk.tk.Event) -> None:
        self._program_state_frame.configure(bootstyle=ttk.PRIMARY)
        self._program_state_label.configure(bootstyle=const.style.INVERSE_PRIMARY)

    def on_signal_off(self, event: ttk.tk.Event) -> None:
        self._signal_label.configure(bootstyle=const.style.INVERSE_DANGER)

    def on_signal_on(self, event: ttk.tk.Event) -> None:
        self._signal_label.configure(bootstyle=const.style.INVERSE_SUCCESS)


class StatusView(View):
    def __init__(self, master: ttk.Window | ttk.tk.Widget, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)

    def _initialize_children(self) -> None:
        self._main_frame: ttk.Frame = ttk.Frame(self)
        self._meter_frame: ttk.Frame = ttk.Frame(self._main_frame)
        self._sonicmeasure_values_frame: ttk.Label = ttk.Label(
            self._main_frame, style=const.style.INVERSE_LIGHT
        )
        self._signal_frame: ttk.Label = ttk.Label(
            self._main_frame, background=const.misc.STATUS_MEDIUM_GREY
        )

        self._freq_meter: ttk.Meter = ttk.Meter(
            self._meter_frame,
            bootstyle=ttk.DARK,
            textright=const.ui.KHZ,
            subtext=const.ui.FREQUENCY,
            metersize=const.misc.METERSIZE,
        )
        self._gain_meter: ttk.Meter = ttk.Meter(
            self._meter_frame,
            bootstyle=ttk.SUCCESS,
            textright=const.ui.PERCENT,
            subtext=const.ui.GAIN,
            metersize=const.misc.METERSIZE,
        )
        self._temp_meter: ttk.Meter = ttk.Meter(
            self._meter_frame,
            bootstyle=ttk.WARNING,
            textright=const.ui.DEGREE_CELSIUS,
            subtext=const.ui.TEMPERATURE,
            metersize=const.misc.METERSIZE,
        )

        self._urms_label: ttk.Label = ttk.Label(
            self._sonicmeasure_values_frame,
            anchor=ttk.CENTER,
            style=ttk.PRIMARY,
            background=const.misc.STATUS_LIGHT_GREY,
            font=(const.fonts.QTYPE_OT, const.fonts.TEXT_SIZE),
        )
        self._irms_label: ttk.Label = ttk.Label(
            self._sonicmeasure_values_frame,
            anchor=ttk.CENTER,
            style=ttk.DANGER,
            background=const.misc.STATUS_LIGHT_GREY,
            font=(const.fonts.QTYPE_OT, const.fonts.TEXT_SIZE),
        )
        self._phase_label: ttk.Label = ttk.Label(
            self._sonicmeasure_values_frame,
            anchor=ttk.CENTER,
            style=ttk.INFO,
            foreground=const.misc.GREEN,
            background=const.misc.STATUS_LIGHT_GREY,
            font=(const.fonts.QTYPE_OT, const.fonts.TEXT_SIZE),
        )
        self._connection_label: ttk.Label = ttk.Label(
            self._signal_frame,
            anchor=ttk.CENTER,
            justify=ttk.CENTER,
            compound=ttk.LEFT,
            font=(const.fonts.QTYPE_OT, const.fonts.SMALL_HEADING_SIZE),
            foreground=const.misc.STATUS_LIGHT_GREY,
            background=const.misc.STATUS_MEDIUM_GREY,
            image=utils.ImageLoader.load_image(
                const.images.LED_ICON_RED, const.misc.LARGE_BUTTON_ICON_SIZE
            ),
            style=const.style.INVERSE_SECONDARY,
            text=const.ui.NOT_CONNECTED,
        )
        self._signal_label: ttk.Label = ttk.Label(
            self._signal_frame,
            anchor=ttk.CENTER,
            justify=ttk.CENTER,
            compound=ttk.LEFT,
            font=(const.fonts.QTYPE_OT, const.fonts.SMALL_HEADING_SIZE),
            foreground=const.misc.STATUS_LIGHT_GREY,
            background=const.misc.STATUS_MEDIUM_GREY,
            image=utils.ImageLoader.load_image(
                const.images.LED_ICON_RED, const.misc.LARGE_BUTTON_ICON_SIZE
            ),
            style=const.style.INVERSE_SECONDARY,
            text=const.ui.SIGNAL_OFF,
        )

    def _initialize_publish(self) -> None:
        self._main_frame.pack(expand=True, fill=ttk.BOTH)
        self._main_frame.columnconfigure(0, weight=const.misc.EXPAND)
        self._main_frame.rowconfigure(2, weight=const.misc.EXPAND)
        self._meter_frame.grid(row=0, column=0)
        self._sonicmeasure_values_frame.grid(row=1, column=0, sticky=ttk.EW)
        self._signal_frame.grid(row=2, column=0, sticky=ttk.EW)

        self._meter_frame.rowconfigure(0, weight=const.misc.EXPAND)
        self._freq_meter.grid(
            row=0,
            column=0,
            padx=const.misc.MEDIUM_PADDING,
            pady=const.misc.MEDIUM_PADDING,
        )
        self._gain_meter.grid(
            row=0,
            column=1,
            padx=const.misc.MEDIUM_PADDING,
            pady=const.misc.MEDIUM_PADDING,
        )
        self._temp_meter.grid(
            row=0,
            column=2,
            padx=const.misc.MEDIUM_PADDING,
            pady=const.misc.MEDIUM_PADDING,
        )

        self._sonicmeasure_values_frame.rowconfigure(0, weight=const.misc.EXPAND)
        self._sonicmeasure_values_frame.columnconfigure(0, weight=const.misc.EXPAND)
        self._sonicmeasure_values_frame.columnconfigure(1, weight=const.misc.EXPAND)
        self._sonicmeasure_values_frame.columnconfigure(2, weight=const.misc.EXPAND)
        self._urms_label.grid(
            row=0,
            column=0,
            padx=const.misc.SMALL_PADDING,
            pady=const.misc.MEDIUM_PADDING,
        )
        self._irms_label.grid(
            row=0,
            column=1,
            padx=const.misc.SMALL_PADDING,
            pady=const.misc.MEDIUM_PADDING,
        )
        self._phase_label.grid(
            row=0,
            column=2,
            padx=const.misc.SMALL_PADDING,
            pady=const.misc.MEDIUM_PADDING,
        )

        self._signal_frame.rowconfigure(0, weight=const.misc.EXPAND)
        self._signal_frame.columnconfigure(0, weight=const.misc.EXPAND)
        self._signal_frame.columnconfigure(1, weight=const.misc.EXPAND)
        self._connection_label.grid(
            row=1,
            column=0,
            padx=const.misc.SIDE_PADDING,
            pady=const.misc.MEDIUM_PADDING,
            sticky=ttk.E,
        )
        self._signal_label.grid(
            row=1,
            column=1,
            padx=const.misc.SIDE_PADDING,
            pady=const.misc.MEDIUM_PADDING,
            sticky=ttk.W,
        )

    def on_connect(self, event: ttk.tk.Event | None = None) -> None:
        self._connection_label.configure(
            image=utils.ImageLoader.load_image(
                const.images.LED_ICON_GREEN, const.misc.LARGE_BUTTON_ICON_SIZE
            )
        )

    def on_disconnect(self, event: ttk.tk.Event | None = None) -> None:
        self._connection_label.configure(
            image=utils.ImageLoader.load_image(
                const.images.LED_ICON_RED, const.misc.LARGE_BUTTON_ICON_SIZE
            )
        )

    def on_signal_on(self, event: ttk.tk.Event | None = None) -> None:
        self._signal_label.configure(
            image=utils.ImageLoader.load_image(
                const.images.LED_ICON_GREEN, const.misc.LARGE_BUTTON_ICON_SIZE
            )
        )

    def on_signal_off(self, event: ttk.tk.Event | None = None) -> None:
        self._signal_label.configure(
            image=utils.ImageLoader.load_image(
                const.images.LED_ICON_RED, const.misc.LARGE_BUTTON_ICON_SIZE
            )
        )
