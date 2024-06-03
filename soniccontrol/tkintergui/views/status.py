import ttkbootstrap as ttk
from typing import Any
from soniccontrol import soniccontrol_logger as logger
from soniccontrol.interfaces.view import View
from soniccontrol.tkintergui.utils.constants import (color, fonts, sizes,
                                                     style, ui_labels)
from soniccontrol.tkintergui.utils.image_loader import ImageLoader
from soniccontrol.tkintergui.widgets.horizontal_scrolled_frame import \
    HorizontalScrolledFrame
from soniccontrol.utils.files import images
import soniccontrol.tkintergui.models as models

class StatusBarView(View):
    def __init__(
        self,
        master: ttk.Window,
        *args,
        **kwargs
    ) -> None:
        super().__init__(master, *args, **kwargs)
        self.configure(bootstyle=ttk.SECONDARY)

    def _initialize_children(self) -> None:
        self._app_state_frame: ttk.Frame = ttk.Frame(self)
        self._app_state_label: ttk.Label = ttk.Label(
            self._app_state_frame,
            bootstyle=style.INVERSE_SECONDARY,
        )

        self._scrolled_info: HorizontalScrolledFrame = HorizontalScrolledFrame(
            self, bootstyle=ttk.SECONDARY, autohide=False
        )
        self._scrolled_info.hide_scrollbars()

        self._freq_frame: ttk.Frame = ttk.Frame(self._scrolled_info)
        self._freq_label: ttk.Label = ttk.Label(
            self._freq_frame,
            bootstyle=style.INVERSE_SECONDARY,
        )

        self._gain_frame: ttk.Frame = ttk.Frame(self._scrolled_info)
        self._gain_label: ttk.Label = ttk.Label(
            self._gain_frame,
            bootstyle=style.INVERSE_SECONDARY,
        )

        self._temperature_frame: ttk.Frame = ttk.Frame(self._scrolled_info)
        self._temperature_label: ttk.Label = ttk.Label(
            self._temperature_frame,
            bootstyle=style.INVERSE_SECONDARY,
        )

        self._mode_frame: ttk.Frame = ttk.Frame(self._scrolled_info)
        self._mode_label: ttk.Label = ttk.Label(
            self._mode_frame,
            bootstyle=style.INVERSE_SECONDARY,
            text="Mode:",
        )
        self._mode_label: ttk.Label = ttk.Label(
            self._mode_frame,
            bootstyle=style.INVERSE_SECONDARY,
        )

        self._urms_frame: ttk.Frame = ttk.Frame(self._scrolled_info)
        self._urms_label: ttk.Label = ttk.Label(
            self._urms_frame,
            bootstyle=style.INVERSE_SECONDARY,
        )

        self._irms_frame: ttk.Frame = ttk.Frame(self._scrolled_info)
        self._irms_label: ttk.Label = ttk.Label(
            self._irms_frame,
            bootstyle=style.INVERSE_SECONDARY,
        )

        self._phase_frame: ttk.Frame = ttk.Frame(self._scrolled_info)
        self._phase_label: ttk.Label = ttk.Label(
            self._phase_frame,
            bootstyle=style.INVERSE_SECONDARY,
        )

        self._signal_frame: ttk.Frame = ttk.Frame(self)
        ICON_LABEL_PADDING: tuple[int, int, int, int] = (8, 0, 0, 0)
        self._connection_label: ttk.Label = ttk.Label(
            self._signal_frame,
            bootstyle=style.INVERSE_SECONDARY,
            padding=ICON_LABEL_PADDING,
            image=ImageLoader.load_image(
                images.CONNECTION_ICON_WHITE, sizes.BUTTON_ICON_SIZE
            ),
            compound=ttk.LEFT,
        )
        self._signal_label: ttk.Label = ttk.Label(
            self._signal_frame,
            bootstyle=style.INVERSE_SECONDARY,
            padding=ICON_LABEL_PADDING,
            image=ImageLoader.load_image(
                images.LIGHTNING_ICON_WHITE, sizes.BUTTON_ICON_SIZE
            ),
            compound=ttk.LEFT,
        )
        
    def _initialize_publish(self) -> None:
        self._app_state_label.pack(side=ttk.LEFT, ipadx=5)

        self._freq_label.pack(side=ttk.LEFT)
        self._gain_label.pack(side=ttk.LEFT)
        self._mode_label.pack(side=ttk.LEFT)
        self._mode_label.pack(side=ttk.LEFT)
        self._temperature_label.pack(side=ttk.LEFT)
        self._urms_label.pack(side=ttk.LEFT)
        self._irms_label.pack(side=ttk.LEFT)
        self._phase_label.pack(side=ttk.LEFT)

        self._signal_frame.pack(side=ttk.RIGHT)
        self._connection_label.pack(side=ttk.RIGHT, ipadx=3)
        self._signal_label.pack(side=ttk.RIGHT, ipadx=3)

        self.on_connect()

    def attach_model(self, model: models.DeviceModel) -> None:
        self._app_state_label.configure(textvariable=model.app_task)
        self._freq_label.configure(textvariable=model.status_model.freq_khz_text)
        self._gain_label.configure(textvariable=model.status_model.gain_text)
        self._mode_label.configure(textvariable=model.status_model.relay_mode)
        self._temperature_label.configure(textvariable=model.status_model.temp_text)
        self._urms_label.configure(textvariable=model.status_model.urms_text)
        self._irms_label.configure(textvariable=model.status_model.irms_text)
        self._phase_label.configure(textvariable=model.status_model.phase_text)

    def on_script_start(self) -> None:
        self._app_state_frame.configure(bootstyle=ttk.SUCCESS)
        self._app_state_label.configure(bootstyle=style.INVERSE_SUCCESS)

    def on_script_stop(self) -> None:
        self._app_state_frame.configure(bootstyle=ttk.SECONDARY)
        self._app_state_label.configure(bootstyle=style.INVERSE_SECONDARY)

    def on_wipe_mode_change(self, event: Any = None) -> None:
        if self.root.sonicamp.status.wipe_mode:
            self.root.soniccontrol_state.animate_dots("Auto Mode")
            self._app_state_frame.configure(bootstyle=ttk.PRIMARY)
            self._app_state_label.configure(bootstyle=style.INVERSE_PRIMARY)
        else:
            self.root.soniccontrol_state.stop_animation_of_dots()
            self.root.soniccontrol_state.set("Manual")
            self._app_state_frame.configure(bootstyle=ttk.SECONDARY)
            self._app_state_label.configure(bootstyle=style.INVERSE_SECONDARY)

    def on_signal_change(self, event: Any = None, *args, **kwargs) -> None:
        if self.root.sonicamp.status.signal:
            self._signal_label.configure(bootstyle=style.INVERSE_SUCCESS)
        else:
            self._signal_label.configure(bootstyle=style.INVERSE_DANGER)

    def on_disconnect(self, event: Any = None) -> None:
        for child in self.winfo_children():
            child.pack_forget()
        self._initialize_publish()
        self._connection_label.configure(bootstyle=style.INVERSE_SECONDARY)
        self._signal_label.configure(bootstyle=style.INVERSE_SECONDARY)

    def on_connect(self, event=None) -> None:
        self._app_state_frame.pack(side=ttk.LEFT)
        self._scrolled_info.pack(side=ttk.LEFT, fill=ttk.X, expand=True)

        self._freq_frame.pack(side=ttk.LEFT, padx=5)
        self._gain_frame.pack(side=ttk.LEFT, padx=5)
        self._mode_frame.pack(side=ttk.LEFT, padx=5)
        self._temperature_frame.pack(side=ttk.LEFT, padx=5)

        self._urms_frame.pack(side=ttk.LEFT, padx=5)
        self._irms_frame.pack(side=ttk.LEFT, padx=5)
        self._phase_frame.pack(side=ttk.LEFT, padx=5)

        self._connection_label.configure(bootstyle=style.INVERSE_SUCCESS)


# class StatusBarView(View):
#     def __init__(self, master: ttk.Window, *args, **kwargs) -> None:
#         super().__init__(master, style=ttk.SECONDARY, *args, **kwargs)
#
#     def _initialize_children(self) -> None:
#         self._main_frame: ttk.Frame = ttk.Frame(self, style=ttk.SECONDARY)
#
#         self._program_state_frame: ttk.Frame = ttk.Frame(self._main_frame)
#         self._program_state_label: ttk.Label = ttk.Label(
#             self._program_state_frame, style=style.INVERSE_SECONDARY
#         )
#
#         self._scrolled_info_frame: HorizontalScrolledFrame = HorizontalScrolledFrame(
#             self._main_frame, style=ttk.SECONDARY, autohide=False
#         )
#         self._scrolled_info_frame.hide_scrollbars()
#
#         self._freq_frame: ttk.Frame = ttk.Frame(
#             self._scrolled_info_frame, style=ttk.SECONDARY
#         )
#         self._freq_label: ttk.Label = ttk.Label(
#             self._freq_frame, style=style.INVERSE_SECONDARY
#         )
#
#         self._gain_frame: ttk.Frame = ttk.Frame(
#             self._scrolled_info_frame, style=ttk.SECONDARY
#         )
#         self._gain_label: ttk.Label = ttk.Label(
#             self._gain_frame,
#             style=style.INVERSE_SECONDARY,
#         )
#
#         self._temperature_frame: ttk.Frame = ttk.Frame(
#             self._scrolled_info_frame, style=ttk.SECONDARY
#         )
#         self._temperature_label: ttk.Label = ttk.Label(
#             self._temperature_frame,
#             style=style.INVERSE_SECONDARY,
#         )
#
#         self._mode_frame: ttk.Frame = ttk.Frame(
#             self._scrolled_info_frame, style=ttk.SECONDARY
#         )
#         self._mode_label: ttk.Label = ttk.Label(
#             self._mode_frame,
#             style=style.INVERSE_SECONDARY,
#         )
#
#         self._urms_frame: ttk.Frame = ttk.Frame(
#             self._scrolled_info_frame, style=ttk.SECONDARY
#         )
#         self._urms_label: ttk.Label = ttk.Label(
#             self._urms_frame,
#             style=style.INVERSE_SECONDARY,
#         )
#
#         self._irms_frame: ttk.Frame = ttk.Frame(
#             self._scrolled_info_frame, style=ttk.SECONDARY
#         )
#         self._irms_label: ttk.Label = ttk.Label(
#             self._irms_frame,
#             style=style.INVERSE_SECONDARY,
#         )
#
#         self._phase_frame: ttk.Frame = ttk.Frame(
#             self._scrolled_info_frame, style=ttk.SECONDARY
#         )
#         self._phase_label: ttk.Label = ttk.Label(
#             self._phase_frame,
#             style=style.INVERSE_SECONDARY,
#         )
#
#         self._signal_frame: ttk.Frame = ttk.Frame(self, style=ttk.SECONDARY)
#         ICON_LABEL_PADDING: tuple[int, int, int, int] = (8, 0, 0, 0)
#         self._connection_label: ttk.Label = ttk.Label(
#             self._signal_frame,
#             style=style.INVERSE_DANGER,
#             padding=ICON_LABEL_PADDING,
#             image=ImageLoader.load_image(
#                 images.CONNECTION_ICON_WHITE, sizes.BUTTON_ICON_SIZE
#             ),
#             compound=ttk.LEFT,
#         )
#         self._signal_label: ttk.Label = ttk.Label(
#             self._signal_frame,
#             style=style.INVERSE_DANGER,
#             padding=ICON_LABEL_PADDING,
#             image=ImageLoader.load_image(
#                 images.LIGHTNING_ICON_WHITE, sizes.BUTTON_ICON_SIZE
#             ),
#             compound=ttk.LEFT,
#         )
#
#     def _initialize_publish(self) -> None:
#         self._main_frame.pack(side=ttk.LEFT, fill=ttk.X, expand=True)
#
#         self._program_state_label.pack(ipadx=sizes.SMALL_PADDING)
#         self._freq_label.pack()
#         self._gain_label.pack()
#         self._mode_label.pack()
#         self._temperature_label.pack()
#         self._urms_label.pack()
#         self._irms_label.pack()
#         self._phase_label.pack()
#
#         self._signal_frame.pack(side=ttk.RIGHT)
#         self._connection_label.pack(side=ttk.RIGHT, ipadx=sizes.SMALL_PADDING)
#         self._signal_label.pack(side=ttk.RIGHT, ipadx=sizes.SMALL_PADDING)
#
#         self._scrolled_info_frame.pack(side=ttk.LEFT, fill=ttk.BOTH, expand=True)
#
#     def _initialize_publish(self) -> None:
#         self._main_frame.pack(side=ttk.LEFT, fill=ttk.X, expand=True)
#         self._main_frame.columnconfigure(1, weight=sizes.EXPAND)
#         self._main_frame.rowconfigure(0, weight=sizes.EXPAND)
#
#         self._signal_frame.pack(side=ttk.RIGHT)
#         self._signal_label.pack(side=ttk.RIGHT, ipadx=sizes.SMALL_PADDING)
#         self._connection_label.pack(side=ttk.RIGHT, ipadx=sizes.SMALL_PADDING)
#
#         self._program_state_frame.grid(row=0, column=0, sticky=ttk.EW)
#         self._program_state_label.pack(side=ttk.LEFT, padx=sizes.MEDIUM_PADDING)
#
#         self._scrolled_info_frame.grid(row=0, column=1, sticky=ttk.EW)
#         self._scrolled_info_frame.columnconfigure(0, weight=sizes.EXPAND)
#         self._scrolled_info_frame.columnconfigure(1, weight=sizes.EXPAND)
#         self._scrolled_info_frame.columnconfigure(2, weight=sizes.EXPAND)
#         self._scrolled_info_frame.columnconfigure(3, weight=sizes.EXPAND)
#         self._scrolled_info_frame.columnconfigure(4, weight=sizes.EXPAND)
#         self._scrolled_info_frame.columnconfigure(5, weight=sizes.EXPAND)
#         self._scrolled_info_frame.columnconfigure(6, weight=sizes.EXPAND)
#         self._scrolled_info_frame.rowconfigure(0, weight=sizes.EXPAND)
#
#         self._freq_frame.grid(row=0, column=0, padx=sizes.MEDIUM_PADDING, sticky=ttk.EW)
#         self._freq_label.pack(side=ttk.LEFT, fill=ttk.X, expand=True)
#
#         self._gain_frame.grid(row=0, column=1, padx=sizes.MEDIUM_PADDING, sticky=ttk.EW)
#         self._gain_label.pack(side=ttk.LEFT, fill=ttk.X)
#
#         self._mode_frame.grid(row=0, column=2, padx=sizes.MEDIUM_PADDING, sticky=ttk.EW)
#         self._mode_label.pack(side=ttk.LEFT, fill=ttk.X)
#
#         self._temperature_frame.grid(
#             row=0, column=3, padx=sizes.MEDIUM_PADDING, sticky=ttk.EW
#         )
#         self._temperature_label.pack(side=ttk.LEFT, fill=ttk.X)
#
#         self._urms_frame.grid(row=0, column=4, padx=sizes.MEDIUM_PADDING, sticky=ttk.EW)
#         self._urms_label.pack(side=ttk.LEFT, fill=ttk.X)
#
#         self._irms_frame.grid(row=0, column=5, padx=sizes.MEDIUM_PADDING, sticky=ttk.EW)
#         self._irms_label.pack(side=ttk.LEFT, fill=ttk.X)
#
#         self._phase_frame.grid(
#             row=0, column=6, padx=sizes.MEDIUM_PADDING, sticky=ttk.EW
#         )
#         self._phase_label.pack(side=ttk.LEFT, fill=ttk.X)
#
#     def on_connected(self, event: ttk.tk.Event) -> None:
#         self._scrolled_info_frame.grid()
#         self._connection_label.configure(bootstyle=style.INVERSE_SUCCESS)
#
#     def on_disconnected(self, event: ttk.tk.Event) -> None:
#         self._scrolled_info_frame.grid_remove()
#         self._signal_label.configure(bootstyle=style.INVERSE_DANGER)
#         self._connection_label.configure(bootstyle=style.INVERSE_DANGER)
#
#     def on_script_start(self, event: ttk.tk.Event) -> None:
#         self._program_state_label.configure(bootstyle=style.INVERSE_SUCCESS)
#         self._program_state_frame.configure(bootstyle=ttk.SUCCESS)
#
#     def on_idle(self, event: ttk.tk.Event | None = None) -> None:
#         self._program_state_frame.configure(bootstyle=ttk.SECONDARY)
#         self._program_state_label.configure(bootstyle=style.INVERSE_SECONDARY)
#
#     def on_auto_mode(self, event: ttk.tk.Event) -> None:
#         self._program_state_frame.configure(bootstyle=ttk.PRIMARY)
#         self._program_state_label.configure(bootstyle=style.INVERSE_PRIMARY)
#
#     def on_signal_off(self, event: ttk.tk.Event) -> None:
#         self._signal_label.configure(bootstyle=style.INVERSE_DANGER)
#         self.on_idle()
#
#     def on_signal_on(self, event: ttk.tk.Event) -> None:
#         self._signal_label.configure(bootstyle=style.INVERSE_SUCCESS)


class StatusView(View):
    def __init__(self, master: ttk.Window | ttk.tk.Widget, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)

    def _initialize_children(self) -> None:
        self._main_frame: ttk.Frame = ttk.Frame(self)
        self._meter_frame: ttk.Frame = ttk.Frame(self._main_frame)
        self._sonicmeasure_values_frame: ttk.Label = ttk.Label(
            self._main_frame, style=style.INVERSE_LIGHT
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
        self._connection_label: ttk.Label = ttk.Label(
            self._signal_frame,
            anchor=ttk.CENTER,
            justify=ttk.CENTER,
            compound=ttk.LEFT,
            font=(fonts.QTYPE_OT, fonts.SMALL_HEADING_SIZE),
            foreground=color.STATUS_LIGHT_GREY,
            background=color.STATUS_MEDIUM_GREY,
            image=ImageLoader.load_image(
                images.LED_ICON_RED, sizes.LARGE_BUTTON_ICON_SIZE
            ),
            style=style.INVERSE_SECONDARY,
            text=ui_labels.NOT_CONNECTED,
        )
        self._signal_label: ttk.Label = ttk.Label(
            self._signal_frame,
            anchor=ttk.CENTER,
            justify=ttk.CENTER,
            compound=ttk.LEFT,
            font=(fonts.QTYPE_OT, fonts.SMALL_HEADING_SIZE),
            foreground=color.STATUS_LIGHT_GREY,
            background=color.STATUS_MEDIUM_GREY,
            image=ImageLoader.load_image(
                images.LED_ICON_RED, sizes.LARGE_BUTTON_ICON_SIZE
            ),
            style=style.INVERSE_SECONDARY,
            text=ui_labels.SIGNAL_OFF,
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
        self._connection_label.grid(
            row=1,
            column=0,
            padx=sizes.SIDE_PADDING,
            pady=sizes.MEDIUM_PADDING,
            sticky=ttk.E,
        )
        self._signal_label.grid(
            row=1,
            column=1,
            padx=sizes.SIDE_PADDING,
            pady=sizes.MEDIUM_PADDING,
            sticky=ttk.W,
        )

    def on_connect(self, event: ttk.tk.Event | None = None) -> None:
        self._connection_label.configure(
            image=ImageLoader.load_image(
                images.LED_ICON_GREEN, sizes.LARGE_BUTTON_ICON_SIZE
            )
        )

    def on_disconnect(self, event: ttk.tk.Event | None = None) -> None:
        self._connection_label.configure(
            image=ImageLoader.load_image(
                images.LED_ICON_RED, sizes.LARGE_BUTTON_ICON_SIZE
            )
        )

    def on_signal_on(self, event: ttk.tk.Event | None = None) -> None:
        self._signal_label.configure(
            image=ImageLoader.load_image(
                images.LED_ICON_GREEN, sizes.LARGE_BUTTON_ICON_SIZE
            )
        )

    def on_signal_off(self, event: ttk.tk.Event | None = None) -> None:
        self._signal_label.configure(
            image=ImageLoader.load_image(
                images.LED_ICON_RED, sizes.LARGE_BUTTON_ICON_SIZE
            )
        )
