from ttkbootstrap.scrolled import ScrolledFrame
from soniccontrol.interfaces.ui_component import UIComponent
from soniccontrol.interfaces.view import TabView, View
from soniccontrol.sonicpackage.sonicamp_ import SonicAmp

import ttkbootstrap as ttk

from soniccontrol.tkintergui.utils.image_loader import ImageLoader
from soniccontrol.tkintergui.widgets.spinbox import Spinbox
from soniccontrol.utils.files import images
from soniccontrol.tkintergui.utils.constants import ui_labels, sizes


class Home(UIComponent):
    def __init__(self, parent: UIComponent, device: SonicAmp):
        pass


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

        # Control Frame - Setting Frequency, Gain, Signal
        self._control_frame: ttk.Labelframe = ttk.Labelframe(
            self._main_frame, text=ui_labels.HOME_CONTROL_LABEL
        )
        self._freq_spinbox: Spinbox = Spinbox(
            self._control_frame,
            placeholder=ui_labels.FREQ_PLACEHOLDER,
            scrolled_frame=self._main_frame,
            style=ttk.DARK,
        )
        self._signal_button: ttk.Checkbutton = ttk.Checkbutton(
            self._control_frame,
            bootstyle="round-toggle"
        )
        self._gain_spinbox: Spinbox = Spinbox(
            self._control_frame,
            placeholder=ui_labels.GAIN_PLACEHOLDER,
            scrolled_frame=self._main_frame,
            style=ttk.DARK,
        )
        self._gain_scale: ttk.Scale = ttk.Scale(
            self._control_frame,
            orient=ttk.HORIZONTAL,
            style=ttk.SUCCESS,
            from_=0,
            to=150,
        )
        self._disconnect_button = ttk.Button(
            self._control_frame, text=ui_labels.DISCONNECT_LABEL
        )


    def _initialize_publish(self) -> None:
        pass
