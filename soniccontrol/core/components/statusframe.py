import logging
import PIL
from PIL.ImageTk import PhotoImage
from typing import Iterable, Any, Optional
import ttkbootstrap as ttk
from soniccontrol.interfaces import (
    RootChild,
    Layout,
    Connectable,
    Disconnectable,
    Updatable,
)
from soniccontrol.interfaces.rootchild import RootChildFrame
import soniccontrol.constants as const
from soniccontrol.interfaces.root import Root

logger = logging.getLogger(__name__)


class StatusBarFrame(RootChildFrame, Connectable, Disconnectable, Updatable):
    def __init__(
        self, parent_frame: ttk.Frame, tab_title: str, image: PIL.Image, *args, **kwargs
    ):
        super().__init__(parent_frame, tab_title, image, *args, **kwargs)
        # self._width_layouts: Iterable[Layout] = ()
        # self._height_layouts: Iterable[Layout] = ()
        # Small status
        self.configure(bootstyle=ttk.SECONDARY)
        self.connection_image: PhotoImage = const.Images.get_image(
            const.Images.CONNECTION_IMG_WHITE, const.Images.BUTTON_ICON_SIZE
        )
        self.signal_image: PhotoImage = const.Images.get_image(
            const.Images.LIGHTNING_IMG_WHITE, const.Images.BUTTON_ICON_SIZE
        )

        self.soniccontrol_state_frame: ttk.Frame = ttk.Frame(self)
        self.soniccontrol_state_label: ttk.Label = ttk.Label(
            self.soniccontrol_state_frame, bootstyle="inverse-secondary"
        )
        self.soniccontrol_value_label: ttk.Label = ttk.Label(
            self.soniccontrol_state_frame, bootstyle="inverse-secondary"
        )

        self.freq_frame: ttk.Frame = ttk.Frame(self)
        self.freq_value_label: ttk.Label = ttk.Label(
            self.freq_frame,
            textvariable=self.root.frequency_text,
            bootstyle="inverse-secondary",
        )

        self.gain_frame: ttk.Frame = ttk.Frame(self)
        self.gain_value_label: ttk.Label = ttk.Label(
            self.gain_frame,
            textvariable=self.root.gain_text,
            bootstyle="inverse-secondary",
        )

        self.temperature_frame: ttk.Frame = ttk.Frame(self)
        self.temperature_value_label: ttk.Label = ttk.Label(
            self.temperature_frame,
            textvariable=self.root.temperature_text,
            bootstyle="inverse-secondary",
        )

        self.mode_frame: ttk.Frame = ttk.Frame(self)
        self.mode_label: ttk.Label = ttk.Label(
            self.mode_frame,
            bootstyle="inverse-secondary",
            text="Mode:",
        )
        self.mode_value_label: ttk.Label = ttk.Label(
            self.mode_frame,
            textvariable=self.root.mode,
            bootstyle="inverse-secondary",
        )

        self.urms_frame: ttk.Frame = ttk.Frame(self)
        self.urms_value_label: ttk.Label = ttk.Label(
            self.urms_frame,
            textvariable=self.root.urms_text,
            bootstyle="inverse-secondary",
        )

        self.irms_frame: ttk.Frame = ttk.Frame(self)
        self.irms_value_label: ttk.Label = ttk.Label(
            self.irms_frame,
            textvariable=self.root.irms_text,
            bootstyle="inverse-secondary",
        )

        self.phase_frame: ttk.Frame = ttk.Frame(self)
        self.phase_value_label: ttk.Label = ttk.Label(
            self.phase_frame,
            textvariable=self.root.phase_text,
            bootstyle="inverse-secondary",
        )

        self.signal_frame: ttk.Frame = ttk.Frame(self)
        self.connection_label: ttk.Label = ttk.Label(
            self.signal_frame,
            bootstyle="inverse-secondary",
            # textvariable=self.root.connection_status,
            image=self.connection_image,
            compound=ttk.LEFT,
        )
        self.signal_label: ttk.Label = ttk.Label(
            self.signal_frame,
            bootstyle="inverse-secondary",
            # text='No signal output',
            image=self.signal_image,
            compound=ttk.LEFT,
        )
        self.bind_events()
        self.publish()

    def on_update(self) -> None:
        pass

    def on_error(self) -> None:
        pass

    def on_signal_change(self, event: Any = None) -> None:
        pass

    def on_temperature_change(self, event: Any = None) -> None:
        pass

    def on_frequency_change(self, event: Any = None) -> None:
        pass

    def on_gain_change(self, event: Any = None) -> None:
        pass

    def on_urms_change(self, event: Any = None) -> None:
        pass

    def on_irms_change(self, event: Any = None) -> None:
        pass

    def on_phase_change(self, event: Any = None) -> None:
        pass

    def on_mode_change(self, event: Any = None) -> None:
        pass

    def on_signal_change(self, event: Any = None, *args, **kwargs) -> None:
        if self.root.signal.get():
            self.signal_label.configure(bootstyle="inverse-success")
        else:
            self.signal_label.configure(bootstyle="inverse-danger")

    def on_disconnect(self, event: Any = None) -> None:
        for child in self.winfo_children():
            child.pack_forget()
        self.publish_signal_connection_frame()
        self.connection_label.configure(bootstyle="inverse-secondary")
        self.signal_label.configure(bootstyle="inverse-secondary")

    def publish_signal_connection_frame(self, *args, **kwargs) -> None:
        self.signal_frame.pack(side=ttk.RIGHT)
        self.connection_label.pack(side=ttk.RIGHT, ipadx=3)
        self.signal_label.pack(side=ttk.RIGHT, ipadx=3)

    def on_connect(self, event=None) -> None:
        self.soniccontrol_state_frame.pack(side=ttk.LEFT, padx=5)
        self.soniccontrol_value_label.configure(text="Manual")

        self.freq_frame.pack(side=ttk.LEFT, padx=5)
        self.gain_frame.pack(side=ttk.LEFT, padx=5)
        self.mode_frame.pack(side=ttk.LEFT, padx=5)
        self.temperature_frame.pack(side=ttk.LEFT, padx=5)

        self.urms_frame.pack(side=ttk.LEFT, padx=5)
        self.irms_frame.pack(side=ttk.LEFT, padx=5)
        self.phase_frame.pack(side=ttk.LEFT, padx=5)

        self.connection_label.configure(bootstyle="inverse-success")

    def publish(self) -> None:
        self.soniccontrol_state_label.pack(side=ttk.LEFT)
        self.soniccontrol_value_label.pack(side=ttk.LEFT)

        self.freq_value_label.pack(side=ttk.LEFT)
        self.gain_value_label.pack(side=ttk.LEFT)
        self.mode_label.pack(side=ttk.LEFT)
        self.mode_value_label.pack(side=ttk.LEFT)
        self.temperature_value_label.pack(side=ttk.LEFT)
        self.urms_value_label.pack(side=ttk.LEFT)
        self.irms_value_label.pack(side=ttk.LEFT)
        self.phase_value_label.pack(side=ttk.LEFT)

        self.publish_signal_connection_frame()


class StatusFrame(RootChildFrame, Connectable, Updatable):
    def __init__(
        self, parent_frame: Root, tab_title: str, image: PIL.Image, *args, **kwargs
    ) -> None:
        super().__init__(parent_frame, tab_title, image, *args, **kwargs)
        # self._width_layouts: Iterable[Layout] = ()
        # self._height_layouts: Iterable[Layout] = ()
        self.signal_off_image: PhotoImage = const.Images.get_image(
            const.Images.LED_RED_IMG,
            (25, 25),
        )
        self.signal_on_image: PhotoImage = const.Images.get_image(
            const.Images.LED_GREEN_IMG, (25, 25)
        )
        self._initialize_tkinter_components()
        self.bind_events()

    def _initialize_tkinter_components(self) -> None:
        self.meter_frame: ttk.Frame = ttk.Label(self)
        self.overview_frame: ttk.Frame = ttk.Frame(self)
        self.sonicmeasure_frame: ttk.Frame = ttk.Frame(self, padding=(0, 3, 3, 0))

        # Meter Frame
        self.freq_meter: ttk.Meter = ttk.Meter(
            self.meter_frame,
            bootstyle=ttk.DARK,
            amounttotal=6_000,
            amountused=self.root.frequency.get(),
            textright="kHz",
            subtext="Frequency",
            metersize=150,
        )

        self.gain_meter: ttk.Meter = ttk.Meter(
            self.meter_frame,
            bootstyle=ttk.SUCCESS,
            amounttotal=150,
            amountused=self.root.gain.get(),
            textright="%",
            subtext="Gain",
            metersize=150,
        )

        self.temp_meter: ttk.Meter = ttk.Meter(
            self.meter_frame,
            bootstyle=ttk.WARNING,
            amounttotal=500,
            amountused=self.root.temperature.get(),
            textright="°C",
            subtext="Thermometer not found",
            metersize=150,
        )

        # SonSens Frame
        self.urms_frame: ttk.Frame = ttk.Frame(self.sonicmeasure_frame)
        self.urms_value_label: ttk.Label = ttk.Label(
            self.urms_frame,
            textvariable=self.root.urms_text,
            anchor=ttk.CENTER,
            bootstyle=ttk.PRIMARY,
        )

        self.irms_frame: ttk.Frame = ttk.Frame(self.sonicmeasure_frame)
        self.irms_value_label: ttk.Label = ttk.Label(
            self.irms_frame,
            textvariable=self.root.irms_text,
            anchor=ttk.CENTER,
            bootstyle=ttk.DANGER,
        )

        self.phase_frame: ttk.Frame = ttk.Frame(self.sonicmeasure_frame)
        self.phase_value_label: ttk.Label = ttk.Label(
            self.phase_frame,
            textvariable=self.root.phase_text,
            bootstyle=ttk.DANGER,
            anchor=ttk.CENTER,
        )

        # Overview Frame
        self.connection_status_label: ttk.Label = ttk.Label(
            self.overview_frame,
            font="QTypeOT-CondBook 15",
            padding=(5, 0, 5, 0),
            justify=ttk.CENTER,
            anchor=ttk.CENTER,
            compound=ttk.LEFT,
            width=15,
            image=self.signal_off_image,
            bootstyle="inverse-light",
            text="not connected",
        )

        self.signal_status_label: ttk.Label = ttk.Label(
            self.overview_frame,
            font="QTypeOT-CondBook 15",
            padding=(5, 0, 5, 0),
            justify=ttk.CENTER,
            anchor=ttk.CENTER,
            compound=ttk.LEFT,
            width=10,
            image=self.signal_off_image,
            # bootstyle="inverse-secondary",
            bootstyle="inverse-light",
            text="signal off",
        )

        self.error_status_label: ttk.Label = ttk.Label(
            self.overview_frame,
            font="QTypeOT-CondBook 15",
            padding=(5, 5, 5, 5),
            justify=ttk.CENTER,
            anchor=ttk.CENTER,
            compound=ttk.CENTER,
            relief=ttk.RIDGE,
            width=10,
            text=None,
        )

    def on_error(self) -> None:
        pass

    def on_signal_change(self, event: Any = None) -> None:
        pass

    def on_frequency_change(self, event: Any = None) -> None:
        self.freq_meter.configure(amountused=self.root.frequency.get())

    def on_gain_change(self, event: Any = None) -> None:
        self.gain_meter.configure(amountused=self.root.gain.get())

    def on_temperature_change(self, event: Any = None) -> None:
        logger.debug("Executing temp update....")
        self.temp_meter.configure(amountused=self.root.temperature.get())

    def on_urms_change(self, event: Any = None) -> None:
        pass

    def on_irms_change(self, event: Any = None) -> None:
        pass

    def on_phase_change(self, event: Any = None) -> None:
        pass

    def on_mode_change(self, event: Any = None) -> None:
        pass

    def on_signal_change(self, event: Any = None, *args, **kwargs) -> None:
        if self.root.signal.get():
            self.signal_status_label.configure(
                text="signal ON",
                image=self.signal_on_image,
            )
        else:
            self.signal_status_label.configure(
                text="signal OFF",
                image=self.signal_off_image,
            )

    def on_connect(self, event: Any = None) -> None:
        self.connection_status_label["image"] = self.signal_on_image
        return self.publish()

    def on_update(self, event: Any = None) -> None:
        pass

    def publish(self) -> None:
        self.meter_frame.pack(fill=ttk.X, anchor=ttk.CENTER, pady=3)
        self.freq_meter.pack(side=ttk.LEFT, fill=ttk.X, expand=True, anchor=ttk.E)
        self.gain_meter.pack(side=ttk.LEFT, fill=ttk.X, expand=True, anchor=ttk.CENTER)
        self.temp_meter.pack(side=ttk.LEFT, fill=ttk.X, expand=True, anchor=ttk.W)

        self.sonicmeasure_frame.pack(fill=ttk.X, anchor=ttk.CENTER, expand=True, pady=3)
        self.urms_value_label.pack(side=ttk.LEFT, anchor=ttk.E, expand=True)
        self.irms_value_label.pack(side=ttk.LEFT, anchor=ttk.CENTER, expand=True)
        self.phase_value_label.pack(side=ttk.LEFT, anchor=ttk.W, expand=True)

        self.urms_frame.pack(
            side=ttk.LEFT, padx=5, fill=ttk.X, expand=True, anchor=ttk.E
        )
        self.irms_frame.pack(
            side=ttk.LEFT, padx=5, fill=ttk.X, expand=True, anchor=ttk.CENTER
        )
        self.phase_frame.pack(
            side=ttk.LEFT, padx=5, fill=ttk.X, expand=True, anchor=ttk.W
        )

        # self.urms_frame.grid(row=0, column=0, sticky=ttk.NSEW)
        # self.irms_frame.grid(row=0, column=1, sticky=ttk.NSEW)
        # self.phase_frame.grid(row=0, column=2, sticky=ttk.NSEW)

        self.overview_frame.pack(fill=ttk.X, ipadx=3, pady=3)
        self.connection_status_label.pack(fill=ttk.X, side=ttk.LEFT, expand=True)
        self.signal_status_label.pack(fill=ttk.X, side=ttk.LEFT, expand=True)


"""
class SCStatusFrame(RootChildFrame, Connectable):
    def __init__(
        self,
        parent: ttk.Frame,
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
