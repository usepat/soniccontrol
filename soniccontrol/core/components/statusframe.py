import logging
import PIL
from typing import Iterable
import ttkbootstrap as ttk
from soniccontrol.interfaces import RootChild, Layout


logger = logging.getLogger(__name__)


class StatusFrame(RootChild):
    def __init__(
        self, parent_frame: ttk.Frame, tab_title: str, image: PIL.Image, *args, **kwargs
    ):
        super().__init__(parent_frame, tab_title, image, *args, **kwargs)
        # self._width_layouts: Iterable[Layout] = ()
        # self._height_layouts: Iterable[Layout] = ()
        # Small status
        self.freq_frame: ttk.Frame = ttk.Frame(self)
        self.freq_label: ttk.Label = ttk.Label(self.freq_frame)
        self.freq_value_label: ttk.Label = ttk.Label(self.freq_frame)

        self.gain_frame: ttk.Frame = ttk.Frame(self)
        self.gain_label: ttk.Label = ttk.Label(
            self.gain_frame,
            font=("QTypeOT-CondBook", 15),
        )
        self.gain_value_label: ttk.Label = ttk.Label(self.gain_frame)

        self.mode_frame: ttk.Frame = ttk.Frame(self)
        self.mode_label: ttk.Label = ttk.Label(
            self.mode_frame,
            font=("QTypeOT-CondBook", 15),
        )
        self.mode_value_label: ttk.Label = ttk.Label(self.mode_frame)

        self.urms_frame: ttk.Frame = ttk.Frame(self)
        self.urms_label: ttk.Label = ttk.Label(
            self.urms_frame,
            font=("QTypeOT-CondBook", 15),
        )
        self.urms_value_label: ttk.Label = ttk.Label(self.urms_frame)

        self.irms_frame: ttk.Frame = ttk.Frame(self)
        self.irms_label: ttk.Label = ttk.Label(
            self.irms_frame,
            font=("QTypeOT-CondBook", 15),
        )
        self.irms_value_label: ttk.Label = ttk.Label(self.irms_frame)

        self.phase_frame: ttk.Frame = ttk.Frame(self)
        self.phase_label: ttk.Label = ttk.Label(
            self.phase_frame,
            font=("QTypeOT-CondBook", 15),
        )
        self.phase_value_label: ttk.Label = ttk.Label(self.phase_frame)

        self.signal_frame: ttk.Frame = ttk.Frame(self)
        self.connection_label: ttk.Label = ttk.Label(
            self.signal_frame,
            font=("QTypeOT-CondBook", 15),
        )
        self.signal_label: ttk.Label = ttk.Label(
            self.signal_frame,
            font=("QTypeOT-CondBook", 15),
        )


"""
StatusFrameParent = Union[ttk.Frame, SCNotebook]
StatusData = Union[bool, int, Optional[int], Optional[float]]
StatusUpdater = Callable[[StatusData], None]
UpdateRegisterDict = Dict[str, Dict[str, Union[StatusData, StatusUpdater]]]


class SCStatusFrame(SCTab):
    def __init__(
        self,
        parent: StatusFrameParent,
        root: Root,
        tab_position: int,
        image,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(parent, root, tab_position, image, *args, **kwargs)
        self.update_register_dict: UpdateRegisterDict = {
            "frequency": {"value": 0, "updater": self.update_meter_freq},
            "gain": {"value": 0, "updater": self.update_meter_gain},
            "temperature": {"value": 0.0, "updater": self.update_meter_temp},
            "urms": {"value": 0.0, "updater": self.update_urms},
            "irms": {"value": 0.0, "updater": self.update_irms},
            "phase": {"value": 0.0, "updater": self.update_phase},
            "signal": {"value": False, "updater": self.update_signal},
            "connection": {"value": False, "updater": self.update_connection},
        }
        self._update_register_default: UpdateRegisterDict = copy.deepcopy(
            self.update_register_dict
        )

    def _initialize_tkinter_components(self) -> None:
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
            amounttotal=150,
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
            style="primary.TLabel",
            padding=(5, 0, 20, 0),
        )
        self.irms_label: ttk.Label = ttk.Label(
            self.sonsens_frame,
            font=self.root.qtype12,
            anchor=tk.CENTER,
            style="danger.TLabel",
            padding=(20, 0, 20, 0),
        )
        self.phase_label: ttk.Label = ttk.Label(
            self.sonsens_frame,
            font=self.root.qtype12,
            anchor=tk.CENTER,
            style="success.TLabel",
            padding=(20, 0, 5, 0),
        )

        # Overview Frame
        self.connection_status_label: ttkb.Label = ttkb.Label(
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

        self.signal_status_label: ttkb.Label = ttkb.Label(
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

        self.error_status_label: ttkb.Label = ttkb.Label(
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

    def show_error(self) -> None:
        pass

    def attach_data(self, status: Status) -> None:
        self.check_error(status.error)
        status_dict: Dict[StatusData] = status.__dict__
        updaters: Iterable[Tuple[StatusUpdater, StatusData]] = (
            (self.update_register_dict[key]["updater"], status_dict[key])
            for key in self.update_register_dict.keys()
            if self.update_register_dict[key]["value"] != status_dict.get(key)
        )
        for updater, data in updaters:
            updater(data)

    def abolish_data(self) -> None:
        for key in self._update_register_default.keys():
            self._update_register_default[key]["updater"](
                self._update_register_default[key]["value"]
            )

    def update_signal(self, state: bool) -> None:
        if state:
            self._toggle_virtual_led(
                self.signal_status_label, state, const.STRINGS.SIGNAL_ON_TXT
            )
        else:
            self._toggle_virtual_led(
                self.signal_status_label, state, const.STRINGS.SIGNAL_OFF_TXT
            )
        self.update_register_dict["signal"]["value"] = state

    def update_signal(self, state: bool) -> None:
        if state:
            self._toggle_virtual_led(
                self.connection_status_label, state, const.STRINGS.CONNECTED_TXT
            )
        else:
            self._toggle_virtual_led(
                self.connection_status_label, state, const.STRINGS.NOT_CONNECTED_TXT
            )
        self.update_register_dict["connection"]["value"] = state

    def update_meter_freq(self, freq: int) -> None:
        self._toggle_meter_frame(self.freq_meter, freq)
        self.update_register_dict["frequency"]["value"] = freq

    def update_meter_gain(self, gain: int) -> None:
        self._toggle_meter_frame(self.gain_meter, gain)
        self.update_register_dict["gain"]["value"] = gain

    def update_meter_temp(self, temp: int) -> None:
        if temp < 0:
            self._toggle_meter_frame(
                self.temp_meter, temp * (-1), const.numbers.MAX_NEGATIVE_TEMP, ttkb.INFO
            )
        else:
            self._toggle_meter_frame(
                self.temp_meter, temp, const.numbers.MAX_POSITIVE_TEMP, ttkb.WARNING
            )
        self._temp_using = temp

    def update_urms(self, urms: Union[float, int]) -> None:
        self.urms_label["text"] = f"urms: {urms}"
        self.update_register_dict["urms"]["value"] = urms

    def update_irms(self, irms: Union[float, int]) -> None:
        self.irms_label["text"] = f"irms: {irms}"
        self.update_register_dict["irms"]["value"] = irms

    def update_phase(self, phase: int) -> None:
        self.urms_label["text"] = f"phase: {phase}"
        self.update_register_dict["phase"]["value"] = phase

    def _toggle_virtual_led(self, label: ttk.Label, state: bool, text: str) -> None:
        image = (
            self.root.images.LED_GREEN_IMG if state else self.root.images.LED_RED_IMG
        )
        label["image"] = image
        label["text"] = text

    def _toggle_meter_frame(
        self,
        meter: ttkb.Meter,
        amountused: int,
        amounttotal: Optional[int] = None,
        style: Optional[str] = None,
    ) -> None:
        if (amounttotal is not None) or (amounttotal != meter["amounttotal"]):
            meter["amounttotal"] = amounttotal
        meter["amountused"] = (
            amountused if amountused != meter["amountused"] else meter["amountused"]
        )
        meter["bootstyle"] = (
            style if style != meter["bootstyle"] else meter["bootstyle"]
        )
"""
