import logging
from pathlib import Path
from typing import Callable, Tuple
import ttkbootstrap as ttk
from soniccontrol_gui.ui_component import UIComponent
from soniccontrol_gui.view import View
from soniccontrol.device_data import Status
from soniccontrol_gui.constants import (color, events, fonts, sizes,
                                                     style, ui_labels)
from soniccontrol_gui.utils.image_loader import ImageLoader
from soniccontrol_gui.widgets.horizontal_scrolled_frame import HorizontalScrolledFrame
from soniccontrol_gui.resources import images
from soniccontrol_gui.utils.widget_registry import WidgetRegistry



class StatusBar(UIComponent):
    def __init__(self, parent: UIComponent, parent_slot: View):
        self._logger = logging.getLogger(parent.logger.name + "." + StatusBar.__name__)
        
        self._logger.debug("Create Statusbar")
        self._view = StatusBarView(parent_slot)
        self._status_panel = StatusPanel(self, self._view.panel_frame)
        self._status_panel_expanded = False
        super().__init__(parent, self._view, self._logger)
        self._view.set_status_clicked_command(self.on_expand_status_panel)
        self._view.expand_panel_frame(self._status_panel_expanded)

    def on_expand_status_panel(self) -> None:
        self._logger.debug("Expand status panel")
        self._status_panel_expanded = not self._status_panel_expanded
        self._view.expand_panel_frame(self._status_panel_expanded)

    def on_update_status(self, status: Status):
        temperature = status.temperature if status.temperature is not None else 0
        self._view.update_labels(
            f"{status.communication_mode}",
            f"Freq.: {status.frequency / 1000} kHz",
            f"Gain: {status.gain} %",
            f"Temp.: {temperature} °C",
            f"Urms: {status.urms} mV",
            f"Irms: {status.irms} mA",
            f"Phase: {status.phase} °",
            f"Signal: {'ON'if status.signal else 'OFF'}"
        )
        if self._status_panel_expanded:
            self._status_panel.on_update_status(status)


class StatusPanel(UIComponent):
    def __init__(self, parent: UIComponent, parent_slot: View):
        self._view = StatusPanelView(parent_slot)
        super().__init__(parent, self._view)

    def on_update_status(self, status: Status):
        temperature = status.temperature if status.temperature else 0
        self._view.update_stats(
            status.frequency / 1000,
            status.gain,
            temperature,
            f"Urms: {status.urms} mV",
            f"Irms: {status.irms} mA",
            f"Phase: {status.phase} °",
            ui_labels.SIGNAL_ON if status.signal else ui_labels.SIGNAL_OFF
        )
        self._view.set_signal_image(
            images.LED_ICON_GREEN if status.signal else images.LED_ICON_RED, 
            sizes.LARGE_BUTTON_ICON_SIZE
        )

class StatusBarView(View):
    def __init__(
        self,
        master: ttk.Frame,
        *args,
        **kwargs
    ) -> None:
        super().__init__(master, *args, **kwargs)

    def _initialize_children(self) -> None:
        tab_name = "status_bar"

        self._panel_frame: ttk.Frame = ttk.Frame(self)
        self._status_bar_frame: ttk.Frame = ttk.Frame(self)
        self._mode_frame: ttk.Frame = ttk.Frame(self._status_bar_frame)
        self._mode_label: ttk.Label = ttk.Label(
            self._mode_frame,
            bootstyle=style.INVERSE_SECONDARY
        )
        WidgetRegistry.register_widget(self._mode_label, "mode_label", tab_name)

        self._scrolled_info: HorizontalScrolledFrame = HorizontalScrolledFrame(
            self._status_bar_frame, bootstyle=ttk.SECONDARY, autohide=False
        )
        self._scrolled_info.hide_scrollbars()

        self._freq_label: ttk.Label = ttk.Label(
            self._scrolled_info,
            bootstyle=style.INVERSE_SECONDARY,
        )
        WidgetRegistry.register_widget(self._freq_label, "freq_label", tab_name)

        self._gain_label: ttk.Label = ttk.Label(
            self._scrolled_info,
            bootstyle=style.INVERSE_SECONDARY,
        )
        WidgetRegistry.register_widget(self._gain_label, "gain_label", tab_name)

        self._temperature_label: ttk.Label = ttk.Label(
            self._scrolled_info,
            bootstyle=style.INVERSE_SECONDARY,
        )
        WidgetRegistry.register_widget(self._temperature_label, "temperature_label", tab_name)

        self._urms_label: ttk.Label = ttk.Label(
            self._scrolled_info,
            bootstyle=style.INVERSE_SECONDARY,
        )
        WidgetRegistry.register_widget(self._urms_label, "urms_label", tab_name)

        self._irms_label: ttk.Label = ttk.Label(
            self._scrolled_info,
            bootstyle=style.INVERSE_SECONDARY,
        )
        WidgetRegistry.register_widget(self._irms_label, "irms_label", tab_name)

        self._phase_label: ttk.Label = ttk.Label(
            self._scrolled_info,
            bootstyle=style.INVERSE_SECONDARY,
        )
        WidgetRegistry.register_widget(self._phase_label, "phase_label", tab_name)

        self._signal_frame: ttk.Frame = ttk.Frame(self._status_bar_frame)
        ICON_LABEL_PADDING: tuple[int, int, int, int] = (8, 0, 0, 0)
        self._signal_label: ttk.Label = ttk.Label(
            self._signal_frame,
            bootstyle=style.INVERSE_SECONDARY, # I just read bootystyle instead of bootstyle. lol
            padding=ICON_LABEL_PADDING,
            image=ImageLoader.load_image_resource(
                images.LIGHTNING_ICON_WHITE, sizes.BUTTON_ICON_SIZE
            ),
            compound=ttk.LEFT,
        )
        WidgetRegistry.register_widget(self._signal_label, "signal_label", tab_name)

        self.configure(bootstyle=ttk.SECONDARY)


    def _initialize_publish(self) -> None:
        self.pack(fill=ttk.BOTH, padx=3, pady=3)
        self._panel_frame.pack(side=ttk.TOP, fill=ttk.BOTH, expand=True)
        self._status_bar_frame.pack(side=ttk.BOTTOM, fill=ttk.X)
        self._signal_frame.pack(side=ttk.RIGHT)
        self._scrolled_info.pack(expand=True, fill=ttk.BOTH, side=ttk.RIGHT)
        self._mode_frame.pack(side=ttk.RIGHT)

        self._mode_label.pack(side=ttk.LEFT, ipadx=5)
        self._freq_label.pack(side=ttk.LEFT, padx=5)
        self._gain_label.pack(side=ttk.LEFT, padx=5)
        self._temperature_label.pack(side=ttk.LEFT, padx=5)
        self._urms_label.pack(side=ttk.LEFT, padx=5)
        self._irms_label.pack(side=ttk.LEFT, padx=5)
        self._phase_label.pack(side=ttk.LEFT, padx=5)
        self._signal_label.pack(side=ttk.RIGHT, ipadx=3)

    @property 
    def panel_frame(self) -> ttk.Frame:
        return self._panel_frame
    
    def expand_panel_frame(self, expand: bool) -> None:
        if expand:
            self._panel_frame.pack(side=ttk.TOP, fill=ttk.BOTH, expand=True)
        else:
            self._panel_frame.pack_forget()

    def set_status_clicked_command(self, command: Callable[[], None]) -> None:
        for child in self._scrolled_info.winfo_children():
            child.bind(events.CLICKED_EVENT, lambda _e: command())
        self._mode_label.bind(events.CLICKED_EVENT, lambda _e: command())
        self._signal_label.bind(events.CLICKED_EVENT, lambda _e: command())

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


class StatusPanelView(View):
    def __init__(self, master: ttk.Window | ttk.tk.Widget, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)

    def _initialize_children(self) -> None:
        tab_name = "status_panel"

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
        WidgetRegistry.register_widget(self._freq_meter, "freq_meter", tab_name)

        self._gain_meter: ttk.Meter = ttk.Meter(
            self._meter_frame,
            bootstyle=ttk.SUCCESS,
            textright=ui_labels.PERCENT,
            subtext=ui_labels.GAIN,
            metersize=sizes.METERSIZE,
        )
        WidgetRegistry.register_widget(self._gain_meter, "gain_meter", tab_name)

        self._temp_meter: ttk.Meter = ttk.Meter(
            self._meter_frame,
            bootstyle=ttk.WARNING,
            textright=ui_labels.DEGREE_CELSIUS,
            subtext=ui_labels.TEMPERATURE,
            metersize=sizes.METERSIZE,
        )
        WidgetRegistry.register_widget(self._temp_meter, "temp_meter", tab_name)

        self._urms_label: ttk.Label = ttk.Label(
            self._sonicmeasure_values_frame,
            anchor=ttk.CENTER,
            style=ttk.PRIMARY,
            background=color.STATUS_LIGHT_GREY,
            font=(fonts.QTYPE_OT, fonts.TEXT_SIZE),
        )
        WidgetRegistry.register_widget(self._urms_label, "urms_label", tab_name)

        self._irms_label: ttk.Label = ttk.Label(
            self._sonicmeasure_values_frame,
            anchor=ttk.CENTER,
            style=ttk.DANGER,
            background=color.STATUS_LIGHT_GREY,
            font=(fonts.QTYPE_OT, fonts.TEXT_SIZE),
        )
        WidgetRegistry.register_widget(self._irms_label, "irms_label", tab_name)

        self._phase_label: ttk.Label = ttk.Label(
            self._sonicmeasure_values_frame,
            anchor=ttk.CENTER,
            style=ttk.INFO,
            foreground=color.DARK_GREEN,
            background=color.STATUS_LIGHT_GREY,
            font=(fonts.QTYPE_OT, fonts.TEXT_SIZE),
        )
        WidgetRegistry.register_widget(self._phase_label, "phase_label", tab_name)

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
        WidgetRegistry.register_widget(self._signal_label, "signal_label", tab_name)


    def _initialize_publish(self) -> None:
        self.pack(fill=ttk.X, padx=3, pady=3)
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
            image=ImageLoader.load_image_resource(str(image_path), sizing)
        )

    def update_stats(self, freq: float, gain: float, temp: float, urms: str, irms: str, phase: str, signal: str):
        self._freq_meter.configure(amountused=freq)
        self._gain_meter.configure(amountused=gain)
        self._temp_meter.configure(amountused=temp)
        self._urms_label.configure(text=urms)
        self._irms_label.configure(text=irms)
        self._phase_label.configure(text=phase)
        self._signal_label.configure(text=signal)
