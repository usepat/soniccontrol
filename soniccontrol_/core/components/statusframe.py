from typing import Optional, Any
import ttkbootstrap as ttk
from PIL.ImageTk import PhotoImage

from soniccontrol.core.interfaces import (
    RootChild,
    Connectable,
    Disconnectable,
    Updatable,
    Root,
)
from soniccontrol.core.components.horzontal_scrolled import HorizontalScrolledFrame


class StatusBar(RootChild, Connectable, Disconnectable, Updatable):
    def __init__(
        self,
        master: Root,
        tab_title: str = "Status Bar",
        image: Optional[PhotoImage] = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(master, tab_title, image=image, *args, **kwargs)
        self.configure(bootstyle=ttk.SECONDARY)

        self.soniccontrol_state_frame: ttk.Frame = ttk.Frame(self)
        self.soniccontrol_state_label: ttk.Label = ttk.Label(
            self.soniccontrol_state_frame,
            bootstyle="inverse-secondary",
            textvariable=self.root.soniccontrol_state,
        )

        self.scrolled_info: HorizontalScrolledFrame = HorizontalScrolledFrame(
            self, bootstyle=ttk.SECONDARY, autohide=False
        )
        self.scrolled_info.hide_scrollbars()

        self.freq_frame: ttk.Frame = ttk.Frame(self.scrolled_info)
        self.freq_value_label: ttk.Label = ttk.Label(
            self.freq_frame,
            textvariable=self.root.status_frequency_text_var,
            bootstyle="inverse-secondary",
        )

        self.gain_frame: ttk.Frame = ttk.Frame(self.scrolled_info)
        self.gain_value_label: ttk.Label = ttk.Label(
            self.gain_frame,
            textvariable=self.root.status_gain_text,
            bootstyle="inverse-secondary",
        )

        self.temperature_frame: ttk.Frame = ttk.Frame(self.scrolled_info)
        self.temperature_value_label: ttk.Label = ttk.Label(
            self.temperature_frame,
            textvariable=self.root.temperature_text,
            bootstyle="inverse-secondary",
        )

        self.mode_frame: ttk.Frame = ttk.Frame(self.scrolled_info)
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

        self.urms_frame: ttk.Frame = ttk.Frame(self.scrolled_info)
        self.urms_value_label: ttk.Label = ttk.Label(
            self.urms_frame,
            textvariable=self.root.urms_text,
            bootstyle="inverse-secondary",
        )

        self.irms_frame: ttk.Frame = ttk.Frame(self.scrolled_info)
        self.irms_value_label: ttk.Label = ttk.Label(
            self.irms_frame,
            textvariable=self.root.irms_text,
            bootstyle="inverse-secondary",
        )

        self.phase_frame: ttk.Frame = ttk.Frame(self.scrolled_info)
        self.phase_value_label: ttk.Label = ttk.Label(
            self.phase_frame,
            textvariable=self.root.phase_text,
            bootstyle="inverse-secondary",
        )

        self.signal_frame: ttk.Frame = ttk.Frame(self)
        self.connection_label: ttk.Label = ttk.Label(
            self.signal_frame,
            bootstyle="inverse-secondary",
            image=self.root.connection_image_white,
            compound=ttk.LEFT,
        )
        self.signal_label: ttk.Label = ttk.Label(
            self.signal_frame,
            bootstyle="inverse-secondary",
            image=self.root.signal_image_white,
            compound=ttk.LEFT,
        )
        self.bind_events()
        self.publish()

    def on_update(self, event: Any = None) -> None:
        pass

    def on_script_start(self) -> None:
        self.soniccontrol_state_frame.configure(bootstyle=ttk.SUCCESS)
        self.soniccontrol_state_label.configure(bootstyle="inverse-success")

    def on_script_stop(self) -> None:
        self.soniccontrol_state_frame.configure(bootstyle=ttk.SECONDARY)
        self.soniccontrol_state_label.configure(bootstyle="inverse-secondary")

    def on_wipe_mode_change(self, event: Any = None) -> None:
        if self.root.sonicamp.status.wipe_mode:
            self.root.soniccontrol_state.animate_dots("Auto Mode")
            self.soniccontrol_state_frame.configure(bootstyle=ttk.PRIMARY)
            self.soniccontrol_state_label.configure(bootstyle="inverse-primary")
        else:
            self.root.soniccontrol_state.stop_animation_of_dots()
            self.root.soniccontrol_state.set("Manual")
            self.soniccontrol_state_frame.configure(bootstyle=ttk.SECONDARY)
            self.soniccontrol_state_label.configure(bootstyle="inverse-secondary")

    def on_signal_change(self, event: Any = None, *args, **kwargs) -> None:
        if self.root.sonicamp.status.signal:
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
        self.soniccontrol_state_frame.pack(side=ttk.LEFT)
        self.scrolled_info.pack(side=ttk.LEFT, fill=ttk.X, expand=True)

        self.freq_frame.pack(side=ttk.LEFT, padx=5)
        self.gain_frame.pack(side=ttk.LEFT, padx=5)
        self.mode_frame.pack(side=ttk.LEFT, padx=5)
        self.temperature_frame.pack(side=ttk.LEFT, padx=5)

        self.urms_frame.pack(side=ttk.LEFT, padx=5)
        self.irms_frame.pack(side=ttk.LEFT, padx=5)
        self.phase_frame.pack(side=ttk.LEFT, padx=5)

        self.connection_label.configure(bootstyle="inverse-success")

    def publish(self) -> None:
        self.soniccontrol_state_label.pack(side=ttk.LEFT, ipadx=5)

        self.freq_value_label.pack(side=ttk.LEFT)
        self.gain_value_label.pack(side=ttk.LEFT)
        self.mode_label.pack(side=ttk.LEFT)
        self.mode_value_label.pack(side=ttk.LEFT)
        self.temperature_value_label.pack(side=ttk.LEFT)
        self.urms_value_label.pack(side=ttk.LEFT)
        self.irms_value_label.pack(side=ttk.LEFT)
        self.phase_value_label.pack(side=ttk.LEFT)

        self.publish_signal_connection_frame()


class StatusFrame(RootChild, Connectable, Updatable):
    def __init__(
        self,
        master: Root,
        tab_title: str = "Status",
        image: Optional[PhotoImage] = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(master, tab_title, image=image, *args, **kwargs)
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
            amountused=self.root.status_frequency_khz_var.get(),
            textright="kHz",
            subtext="Frequency",
            metersize=150,
        )

        self.gain_meter: ttk.Meter = ttk.Meter(
            self.meter_frame,
            bootstyle=ttk.SUCCESS,
            amounttotal=150,
            amountused=self.root.status_gain.get(),
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
            bootstyle=ttk.SUCCESS,
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
            image=self.root.signal_off_image,
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
            image=self.root.signal_off_image,
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

    def on_frequency_change(self, event: Any = None) -> None:
        self.freq_meter.configure(
            amountused=self.root.status_frequency_khz_var.get() / 1000
        )

    def on_gain_change(self, event: Any = None) -> None:
        self.gain_meter.configure(amountused=self.root.status_gain.get())

    def on_temperature_change(self, event: Any = None) -> None:
        self.temp_meter.configure(amountused=self.root.temperature.get())

    def on_signal_change(self, event: Any = None, *args, **kwargs) -> None:
        if self.root.sonicamp.status.signal:
            self.signal_status_label.configure(
                text="signal ON",
                image=self.root.signal_on_image,
            )
        else:
            self.signal_status_label.configure(
                text="signal OFF",
                image=self.root.signal_off_image,
            )

    def on_connect(self, event: Any = None) -> None:
        self.connection_status_label["image"] = self.root.signal_on_image
        self.connection_status_label["text"] = "connected"
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

        self.overview_frame.pack(fill=ttk.X, ipadx=3, pady=3)
        self.connection_status_label.pack(fill=ttk.X, side=ttk.LEFT, expand=True)
        self.signal_status_label.pack(fill=ttk.X, side=ttk.LEFT, expand=True)
