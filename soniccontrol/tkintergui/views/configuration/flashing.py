
from typing import Final
from soniccontrol.interfaces.ui_component import UIComponent
from soniccontrol.interfaces.view import TabView
from soniccontrol.sonicpackage.sonicamp_ import SonicAmp

import ttkbootstrap as ttk

from soniccontrol.tkintergui.utils.constants import sizes, ui_labels
from soniccontrol.tkintergui.utils.events import PropertyChangeEvent
from soniccontrol.tkintergui.views.core.app_state import AppState
from soniccontrol.utils.files import images
from soniccontrol.tkintergui.utils.image_loader import ImageLoader
from soniccontrol.tkintergui.widgets.file_browse_button import FileBrowseButtonView


class Flashing(UIComponent):
    def __init__(self, parent: UIComponent, device: SonicAmp, app_state: AppState):
        self._device = device
        self._app_state = app_state
        self._view = FlashingView(parent.view)
        super().__init__(self, self._view)
        self._app_state.subscribe_property_listener(AppState.EXECUTION_STATE_PROP_NAME, self._on_execution_state_changed)

    def _flash(self) -> None:
        pass

    def _on_execution_state_changed(self, e: PropertyChangeEvent) -> None:
        pass

class FlashingView(TabView):
    def __init__(self, master: ttk.Frame, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

    @property
    def image(self) -> ttk.ImageTk.PhotoImage:
        return ImageLoader.load_image(images.SETTINGS_ICON_BLACK, sizes.TAB_ICON_SIZE)

    @property
    def tab_title(self) -> str:
        return ui_labels.SETTINGS_LABEL
    
    def _initialize_children(self) -> None:
        FLASH_PADDING: Final[tuple[int, int, int, int]] = (5, 0, 5, 5)
        self._flash_frame: ttk.Labelframe = ttk.Labelframe(
            self, padding=FLASH_PADDING
        )
        self._browse_flash_file_button: FileBrowseButtonView = FileBrowseButtonView(
            self._flash_frame, text=ui_labels.SPECIFY_PATH_LABEL
        )
        self._submit_button: ttk.Button = ttk.Button(
            self._flash_frame, text=ui_labels.SUBMIT_LABEL, style=ttk.DARK
        )

    def _initialize_publish(self) -> None:
        self._flash_frame.pack(expand=True, fill=ttk.BOTH)
        self._flash_frame.columnconfigure(0, weight=sizes.EXPAND)
        self._flash_frame.rowconfigure(0, weight=sizes.DONT_EXPAND)
        self._flash_frame.rowconfigure(1, weight=sizes.DONT_EXPAND)
        self._browse_flash_file_button.grid(
            row=0,
            column=0,
            padx=sizes.MEDIUM_PADDING,
            pady=sizes.MEDIUM_PADDING,
            sticky=ttk.EW,
        )
        self._submit_button.grid(
            row=1,
            column=0,
            padx=sizes.MEDIUM_PADDING,
            pady=sizes.MEDIUM_PADDING,
            sticky=ttk.EW,
        )

