from pathlib import Path
from typing import Dict, Optional, Tuple
import ttkbootstrap as ttk
from soniccontrol.interfaces.ui_component import UIComponent
from soniccontrol.interfaces.view import View
from soniccontrol.sonicpackage.amp_data import Status
from soniccontrol.tkintergui.utils.constants import (color, fonts, sizes,
                                                     style, ui_labels)
from soniccontrol.tkintergui.utils.image_loader import ImageLoader
from soniccontrol.tkintergui.widgets.horizontal_scrolled_frame import HorizontalScrolledFrame
from soniccontrol.utils.files import images



class StatusBar(UIComponent):
    def __init__(self, parent: UIComponent, parent_slot: View):
        min_height = 500
        self._view = AdaptiveFrame(parent_slot, min_height)
        self._status_bar_view = StatusBarView(self._view.frame_small)
        self._status_bar_expanded_view = StatusBarExpandedView(self._view.frame_large)
        super().__init__(parent, self._view)

    def on_update_status(self, status: Status):
        self._status_bar_view.update_labels(
            f"{status.communication_mode}",
            f"Freq.: {status.frequency / 1000} kHz",
            f"Gain: {status.gain} %",
            f"Temp.: {status.temperature} °C",
            f"Urms: {status.urms} mV",
            f"Irms: {status.irms} mA",
            f"Phase: {status.phase} °",
            f"Signal: {'ON'if status.signal else 'OFF'}"
        )
        self._status_bar_expanded_view.update_stats(
            status.frequency / 1000,
            status.gain,
            status.temperature,
            f"Urms: {status.urms} mV",
            f"Irms: {status.irms} mA",
            f"Phase: {status.phase} °",
            ui_labels.SIGNAL_ON if status.signal else ui_labels.SIGNAL_OFF
        )
        # set_signal_image


class AdaptiveFrame(View):
    def __init__(self, master: ttk.Frame, threshold: int, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)
        self._threshold = threshold
        self.bind("<Configure>", self._on_resize)
    
    @property
    def frame_small(self) -> Optional[View]:
        return self._frame_small

    @property
    def frame_large(self) -> Optional[View]:
        return self._frame_large

    def _initialize_children(self) -> None:
        self._frame_small: ttk.Frame = ttk.Frame(self)
        self._frame_large: ttk.Frame = ttk.Frame(self)

    def _initialize_publish(self) -> None:
        self._frame_small.grid(row=0, column=0, sticky=ttk.NSEW)
        self._frame_large.grid(row=0, column=0, sticky=ttk.NSEW)
        self._frame_large.grid_forget()

    def _on_resize(self, event):
        if event.height < self._threshold:
            self._frame_large.grid_forget()
            self._frame_small.grid(row=0, column=0, sticky=ttk.NSEW)
        else:
            self._frame_small.grid_forget()
            self._frame_large.grid(row=0, column=0, sticky=ttk.NSEW)


class StatusBarView(View):
    def __init__(
        self,
        master: ttk.Frame,
        *args,
        **kwargs
    ) -> None:
        super().__init__(master, *args, **kwargs)

    def _initialize_children(self) -> None:
        self._mode_frame: ttk.Frame = ttk.Frame(self)
        self._mode_label: ttk.Label = ttk.Label(
            self._mode_frame,
            bootstyle=style.INVERSE_SECONDARY,
        )

        self._scrolled_info: HorizontalScrolledFrame = HorizontalScrolledFrame(
            self, bootstyle=ttk.SECONDARY, autohide=False
        )
        self._scrolled_info.hide_scrollbars()

        self._freq_label: ttk.Label = ttk.Label(
            self._scrolled_info,
            bootstyle=style.INVERSE_SECONDARY,
        )

        self._gain_label: ttk.Label = ttk.Label(
            self._scrolled_info,
            bootstyle=style.INVERSE_SECONDARY,
        )

        self._temperature_label: ttk.Label = ttk.Label(
            self._scrolled_info,
            bootstyle=style.INVERSE_SECONDARY,
        )


        self._urms_label: ttk.Label = ttk.Label(
            self._scrolled_info,
            bootstyle=style.INVERSE_SECONDARY,
        )

        self._irms_label: ttk.Label = ttk.Label(
            self._scrolled_info,
            bootstyle=style.INVERSE_SECONDARY,
        )

        self._phase_label: ttk.Label = ttk.Label(
            self._scrolled_info,
            bootstyle=style.INVERSE_SECONDARY,
        )

        self._signal_frame: ttk.Frame = ttk.Frame(self)
        ICON_LABEL_PADDING: tuple[int, int, int, int] = (8, 0, 0, 0)
        self._signal_label: ttk.Label = ttk.Label(
            self._signal_frame,
            bootstyle=style.INVERSE_SECONDARY, # I just read bootystyle instead of bootstyle. lol
            padding=ICON_LABEL_PADDING,
            image=ImageLoader.load_image(
                images.LIGHTNING_ICON_WHITE, sizes.BUTTON_ICON_SIZE
            ),
            compound=ttk.LEFT,
        )
        self.configure(bootstyle=ttk.SECONDARY)
        

    def _initialize_publish(self) -> None:
        self._signal_frame.pack(side=ttk.RIGHT)
        self._scrolled_info.pack(side=ttk.RIGHT)
        self._mode_frame.pack(side=ttk.RIGHT)

        self._mode_label.pack(side=ttk.LEFT, ipadx=5)
        self._freq_label.pack(side=ttk.LEFT, padx=5)
        self._gain_label.pack(side=ttk.LEFT, padx=5)
        self._temperature_label.pack(side=ttk.LEFT, padx=5)
        self._urms_label.pack(side=ttk.LEFT, padx=5)
        self._irms_label.pack(side=ttk.LEFT, padx=5)
        self._phase_label.pack(side=ttk.LEFT, padx=5)
        self._signal_label.pack(side=ttk.RIGHT, ipadx=3)


    def on_script_start(self) -> None:
        self._mode_frame.configure(bootstyle=ttk.SUCCESS)
        self._mode_label.configure(bootstyle=style.INVERSE_SUCCESS)

    def on_script_stop(self) -> None:
        self._mode_frame.configure(bootstyle=ttk.SECONDARY)
        self._mode_label.configure(bootstyle=style.INVERSE_SECONDARY)

    def update_labels(self, mode: str, freq: str, gain: str, temp: str, urms: str, irms: str, phase: str, signal: str):
        self._mode_label.configure(text=mode)
        self._freq_label.configure(text=freq)
        self._gain_label.configure(text=gain)
        self._temperature_label.configure(text=temp)
        self._urms_label.configure(text=urms)
        self._irms_label.configure(text=irms)
        self._phase_label.configure(text=phase)
        self._signal_label.configure(text=signal)


class StatusBarExpandedView(View):
    def __init__(self, master: ttk.Window | ttk.tk.Widget, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)

    def _initialize_children(self) -> None:
        self._main_frame: ttk.Frame = ttk.Frame(self)
        self._meter_frame: ttk.Frame = ttk.Frame(self._main_frame)
        self._sonicmeasure_values_frame: ttk.Frame = ttk.Frame(
            self._main_frame
        )
        self._signal_frame: ttk.Label = ttk.Label(
            self._main_frame, background=color.STATUS_MEDIUM_GREY
        )

        self._freq_meter: ttk.Meter = ttk.Meter(
            self._meter_frame,
            bootstyle=ttk.DARK,
            textright=ui_labels.KHZ,
            subtext=ui_labels.FREQUENCY,
            metersize=sizes.METERSIZE,
        )
        self._gain_meter: ttk.Meter = ttk.Meter(
            self._meter_frame,
            bootstyle=ttk.SUCCESS,
            textright=ui_labels.PERCENT,
            subtext=ui_labels.GAIN,
            metersize=sizes.METERSIZE,
        )
        self._temp_meter: ttk.Meter = ttk.Meter(
            self._meter_frame,
            bootstyle=ttk.WARNING,
            textright=ui_labels.DEGREE_CELSIUS,
            subtext=ui_labels.TEMPERATURE,
            metersize=sizes.METERSIZE,
        )
        self._urms_label: ttk.Label = ttk.Label(
            self._sonicmeasure_values_frame,
            anchor=ttk.CENTER,
            style=ttk.PRIMARY,
            background=color.STATUS_LIGHT_GREY,
            font=(fonts.QTYPE_OT, fonts.TEXT_SIZE),
        )
        self._irms_label: ttk.Label = ttk.Label(
            self._sonicmeasure_values_frame,
            anchor=ttk.CENTER,
            style=ttk.DANGER,
            background=color.STATUS_LIGHT_GREY,
            font=(fonts.QTYPE_OT, fonts.TEXT_SIZE),
        )
        self._phase_label: ttk.Label = ttk.Label(
            self._sonicmeasure_values_frame,
            anchor=ttk.CENTER,
            style=ttk.INFO,
            foreground=color.DARK_GREEN,
            background=color.STATUS_LIGHT_GREY,
            font=(fonts.QTYPE_OT, fonts.TEXT_SIZE),
        )
        self._signal_label: ttk.Label = ttk.Label(
            self._signal_frame,
            anchor=ttk.CENTER,
            justify=ttk.CENTER,
            compound=ttk.LEFT,
            font=(fonts.QTYPE_OT, fonts.SMALL_HEADING_SIZE),
            foreground=color.STATUS_LIGHT_GREY,
            background=color.STATUS_MEDIUM_GREY,
            style=style.INVERSE_SECONDARY,
        )

    def _initialize_publish(self) -> None:
        self._main_frame.pack(expand=True, fill=ttk.BOTH)
        self._main_frame.columnconfigure(0, weight=sizes.EXPAND)
        self._main_frame.rowconfigure(2, weight=sizes.EXPAND)
        self._meter_frame.grid(row=0, column=0)
        self._sonicmeasure_values_frame.grid(row=1, column=0, sticky=ttk.EW)
        self._signal_frame.grid(row=2, column=0, sticky=ttk.EW)

        self._meter_frame.rowconfigure(0, weight=sizes.EXPAND)
        self._freq_meter.grid(
            row=0,
            column=0,
            padx=sizes.MEDIUM_PADDING,
            pady=sizes.MEDIUM_PADDING,
        )
        self._gain_meter.grid(
            row=0,
            column=1,
            padx=sizes.MEDIUM_PADDING,
            pady=sizes.MEDIUM_PADDING,
        )
        self._temp_meter.grid(
            row=0,
            column=2,
            padx=sizes.MEDIUM_PADDING,
            pady=sizes.MEDIUM_PADDING,
        )

        self._sonicmeasure_values_frame.rowconfigure(0, weight=sizes.EXPAND)
        self._sonicmeasure_values_frame.columnconfigure(0, weight=sizes.EXPAND)
        self._sonicmeasure_values_frame.columnconfigure(1, weight=sizes.EXPAND)
        self._sonicmeasure_values_frame.columnconfigure(2, weight=sizes.EXPAND)
        self._urms_label.grid(
            row=0,
            column=0,
            padx=sizes.SMALL_PADDING,
            pady=sizes.MEDIUM_PADDING,
        )
        self._irms_label.grid(
            row=0,
            column=1,
            padx=sizes.SMALL_PADDING,
            pady=sizes.MEDIUM_PADDING,
        )
        self._phase_label.grid(
            row=0,
            column=2,
            padx=sizes.SMALL_PADDING,
            pady=sizes.MEDIUM_PADDING,
        )

        self._signal_frame.rowconfigure(0, weight=sizes.EXPAND)
        self._signal_frame.columnconfigure(0, weight=sizes.EXPAND)
        self._signal_frame.columnconfigure(1, weight=sizes.EXPAND)
        self._signal_label.grid(
            row=1,
            column=1,
            padx=sizes.SIDE_PADDING,
            pady=sizes.MEDIUM_PADDING,
            sticky=ttk.W,
        )

    def set_signal_image(self, image_path: Path, sizing: Tuple[int, int]) -> None:
        self._signal_label.configure(
            image=ImageLoader.load_image(image_path, sizing)
        )

    def update_stats(self, freq: int, gain: int, temp: float, urms: str, irms: str, phase: str, signal: str):
        self._freq_meter.configure(amountused=freq)
        self._gain_meter.configure(amountused=gain)
        self._temp_meter.configure(amountused=temp)
        self._urms_label.configure(text=urms)
        self._irms_label.configure(text=irms)
        self._phase_label.configure(text=phase)
        self._signal_label.configure(text=signal)
