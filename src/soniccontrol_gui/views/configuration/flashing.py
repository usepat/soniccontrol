
from typing import Final
from soniccontrol_gui.ui_component import UIComponent
from soniccontrol_gui.view import TabView
from sonicpackage.sonicamp_ import SonicAmp

import ttkbootstrap as ttk

from soniccontrol_gui.constants import sizes, ui_labels
from sonicpackage.events import PropertyChangeEvent
from soniccontrol_gui.views.core.app_state import AppState
from soniccontrol_gui.resources import images
from soniccontrol_gui.utils.image_loader import ImageLoader
from soniccontrol_gui.widgets.file_browse_button import FileBrowseButtonView


class Flashing(UIComponent):
    def __init__(self, parent: UIComponent, device: SonicAmp | None = None, app_state: AppState | None = None):
        self._device = device
        self._app_state = app_state
        self._view = FlashingView(parent.view)
        super().__init__(self, self._view)
        if self._app_state:
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
        return ImageLoader.load_image_resource(images.SETTINGS_ICON_BLACK, sizes.TAB_ICON_SIZE)

    @property
    def tab_title(self) -> str:
        return ui_labels.FLASHER_LABEL
    
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

