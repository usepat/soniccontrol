from typing import Callable
from async_tkinter_loop import async_handler
from ttkbootstrap.scrolled import ScrolledFrame
from soniccontrol.interfaces.ui_component import UIComponent
from soniccontrol.interfaces.view import TabView, View
from soniccontrol.sonicpackage.amp_data import Info, Version
from soniccontrol.sonicpackage.sonicamp_ import SonicAmp

import ttkbootstrap as ttk

from soniccontrol.tkintergui.utils.events import PropertyChangeEvent
from soniccontrol.tkintergui.utils.image_loader import ImageLoader
from soniccontrol.tkintergui.views.core.app_state import ExecutionState
from soniccontrol.tkintergui.widgets.spinbox import Spinbox
from soniccontrol.utils.files import images
from soniccontrol.tkintergui.utils.constants import ui_labels, sizes


class Home(UIComponent):
    def __init__(self, parent: UIComponent, device: SonicAmp):
        self._device = device
        self._view = HomeView(parent.view)
        super().__init__(parent, self._view)
        self._view.set_disconnect_button_command(self._on_disconnect_pressed)
        self._view.set_send_button_command(self._on_send_pressed)
        self._initialize_info()

    def _initialize_info(self) -> None:
        def version_to_str(version: Version) -> str:
            return "v" + ".".join(map(str, version))

        device_type = self._device.info.device_type
        firmware_version = version_to_str(self._device.info.firmware_version)
        protocol_version = "v" + str(self._device.serial.protocol.major_version)
        self._view.set_device_type(device_type)
        self._view.set_firmware_version(firmware_version)
        self._view.set_protocol_version(protocol_version)

    @async_handler
    async def _on_disconnect_pressed(self) -> None:
        await self._device.disconnect()

    @async_handler
    async def _on_send_pressed(self) -> None:
        freq = self._view.freq
        gain = self._view.gain
        signal = self._view.signal

        await self._device.set_frequency(freq)
        await self._device.set_gain(gain)
        if signal:
            await self._device.set_signal_on()
        else:
            await self._device.set_signal_off()

    def on_execution_state_changed(self, e: PropertyChangeEvent) -> None:
        execution_state: ExecutionState = e.new_value
        self._view.set_disconnect_button_enabled(execution_state != ExecutionState.NOT_RESPONSIVE)
        self._view.set_send_button_enabled(execution_state == ExecutionState.IDLE)


class HomeView(TabView):
    def __init__(self, master: View, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)

    @property
    def image(self) -> ttk.ImageTk.PhotoImage:
        return ImageLoader.load_image(images.HOME_ICON_BLACK, sizes.TAB_ICON_SIZE)

    @property
    def tab_title(self) -> str:
        return ui_labels.HOME_LABEL
    
    def _initialize_children(self) -> None:
        self._main_frame: ScrolledFrame = ScrolledFrame(self, autohide=True)

        # info frame - displays device type, protocol type, firmware type
        self._info_frame: ttk.LabelFrame = ttk.LabelFrame(
            self._main_frame, text=ui_labels.INFO_LABEL
        )
        self._device_type_label = ttk.Label(
            self._info_frame, text=ui_labels.DEVICE_TYPE_LABEL.format("N/A")
        )
        self._firmware_version_label = ttk.Label(
            self._info_frame, text=ui_labels.FIRMWARE_VERSION_LABEL.format("N/A")
        )
        self._protocol_version_label = ttk.Label(
            self._info_frame, text=ui_labels.PROTOCOL_VERSION_LABEL.format("N/A")
        )
        self._disconnect_button = ttk.Button(
            self._info_frame, text=ui_labels.DISCONNECT_LABEL
        )

        # Control Frame - Setting Frequency, Gain, Signal
        self._control_frame: ttk.Labelframe = ttk.Labelframe(
            self._main_frame, text=ui_labels.HOME_CONTROL_LABEL
        )

        self._freq_frame: ttk.LabelFrame = ttk.LabelFrame(
            self._control_frame, text=ui_labels.FREQUENCY
        )
        self._freq: ttk.IntVar = ttk.IntVar(value=0)
        self._freq_spinbox: Spinbox = Spinbox(
            self._freq_frame,
            placeholder=ui_labels.FREQ_PLACEHOLDER,
            scrolled_frame=self._main_frame,
            style=ttk.DARK,
            textvariable=self._freq
        )
        self._freq_scale: ttk.Scale = ttk.Scale(
            self._freq_frame,
            orient=ttk.HORIZONTAL,
            style=ttk.SUCCESS,
            from_=0,
            to=1000000, # TODO: set correct values
            variable=self._freq
        )

        self._signal_frame: ttk.LabelFrame = ttk.LabelFrame(
            self._control_frame, text=ui_labels.SIGNAL_LABEL
        )
        self._signal = ttk.BooleanVar = ttk.BooleanVar(value=False)
        self._signal_button: ttk.Checkbutton = ttk.Checkbutton(
            self._signal_frame,
            bootstyle="round-toggle", #type: ignore
            variable=self._signal
        )

        self._gain_frame: ttk.LabelFrame = ttk.LabelFrame(
            self._control_frame, text=ui_labels.GAIN
        )
        self._gain: ttk.IntVar = ttk.IntVar(value=0)
        self._gain_spinbox: Spinbox = Spinbox(
            self._gain_frame,
            placeholder=ui_labels.GAIN_PLACEHOLDER,
            scrolled_frame=self._main_frame,
            style=ttk.DARK,
            textvariable=self._gain
        )
        self._gain_scale: ttk.Scale = ttk.Scale(
            self._gain_frame,
            orient=ttk.HORIZONTAL,
            style=ttk.SUCCESS,
            from_=0,
            to=150,
            variable=self._gain
        )

        self._send_button = ttk.Button(
            self._control_frame, text=ui_labels.SEND_LABEL
        )

    def _initialize_publish(self) -> None:
        self._main_frame.pack(fill=ttk.BOTH, expand=True)
        
        self._info_frame.pack(fill=ttk.X)
        self._device_type_label.grid(
            row=0, 
            column=0, 
            padx=sizes.LARGE_PADDING, 
            pady=sizes.MEDIUM_PADDING, 
            sticky=ttk.W
        )
        self._firmware_version_label.grid(
            row=1, 
            column=0, 
            padx=sizes.LARGE_PADDING, 
            pady=sizes.MEDIUM_PADDING, 
            sticky=ttk.W
        )
        self._protocol_version_label.grid(
            row=2, 
            column=0, 
            padx=sizes.LARGE_PADDING, 
            pady=sizes.MEDIUM_PADDING, 
            sticky=ttk.W
        )
        self._disconnect_button.grid(
            row=3, 
            column=0, 
            padx=sizes.LARGE_PADDING, 
            pady=sizes.MEDIUM_PADDING, 
            sticky=ttk.W
        )

        self._control_frame.pack(fill=ttk.BOTH, expand=True)
        self._freq_frame.grid(
            row=0, 
            column=0, 
            padx=sizes.LARGE_PADDING, 
            pady=sizes.LARGE_PADDING, 
            sticky=ttk.NSEW
        )
        self._freq_spinbox.grid(
            row=0, 
            column=0, 
            padx=sizes.LARGE_PADDING, 
            pady=sizes.MEDIUM_PADDING, 
            sticky=ttk.EW
        )
        self._freq_scale.grid(
            row=1, 
            column=0, 
            padx=sizes.LARGE_PADDING, 
            pady=sizes.MEDIUM_PADDING, 
            sticky=ttk.EW
        )

        self._signal_frame.grid(
            row=0, 
            column=1, 
            padx=sizes.LARGE_PADDING, 
            pady=sizes.LARGE_PADDING, 
            sticky=ttk.NSEW
        )
        self._signal_button.grid(
            row=0, 
            column=0, 
            padx=sizes.LARGE_PADDING, 
            pady=sizes.MEDIUM_PADDING, 
            sticky=ttk.EW
        )

        self._gain_frame.grid(
            row=0, 
            column=2, 
            padx=sizes.LARGE_PADDING, 
            pady=sizes.LARGE_PADDING, 
            sticky=ttk.NSEW
        )
        self._gain_spinbox.grid(
            row=0, 
            column=0, 
            padx=sizes.LARGE_PADDING, 
            pady=sizes.MEDIUM_PADDING, 
            sticky=ttk.EW
        )
        self._gain_scale.grid(
            row=1, 
            column=0, 
            padx=sizes.LARGE_PADDING, 
            pady=sizes.MEDIUM_PADDING, 
            sticky=ttk.EW
        )

        self._send_button.grid(
            row=1, 
            column=1, 
            padx=sizes.LARGE_PADDING, 
            pady=sizes.LARGE_PADDING, 
            sticky=ttk.EW
        )

    @property 
    def freq(self) -> int:
        return self._freq.get()
    
    @property
    def gain(self) -> int:
        return self._gain.get()
    
    @property 
    def signal(self) -> bool:
        return self._signal.get()
    
    def set_device_type(self, text: str) -> None:
        self._device_type_label.configure(text=ui_labels.DEVICE_TYPE_LABEL.format(text)) 

    def set_firmware_version(self, text: str) -> None:
        self._firmware_version_label.configure(text=ui_labels.FIRMWARE_VERSION_LABEL.format(text)) 

    def set_protocol_version(self, text: str) -> None:
        self._protocol_version_label.configure(text=ui_labels.PROTOCOL_VERSION_LABEL.format(text)) 

    def set_disconnect_button_command(self, command: Callable[[], None]) -> None:
        self._disconnect_button.configure(command=command)

    def set_send_button_command(self, command: Callable[[], None]) -> None:
        self._send_button.configure(command=command)

    def set_disconnect_button_enabled(self, enabled: bool) -> None:
        self._disconnect_button.configure(state=ttk.NORMAL if enabled else ttk.DISABLED)

    def set_send_button_enabled(self, enabled: bool) -> None:
        self._send_button.configure(state=ttk.NORMAL if enabled else ttk.DISABLED)
