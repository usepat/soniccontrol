from typing import Callable, List, Optional, cast
import logging
from async_tkinter_loop import async_handler
import ttkbootstrap as ttk
import tkinter as tk

from ttkbootstrap.dialogs.dialogs import Messagebox

from soniccontrol.interfaces.ui_component import UIComponent
from soniccontrol.interfaces.view import TabView
from soniccontrol.sonicpackage.interfaces import Communicator
from soniccontrol.sonicpackage.procedures.procedure_controller import ProcedureController
from soniccontrol.sonicpackage.sonicamp_ import SonicAmp
from soniccontrol.state_updater.logger import DeviceLogFilter, LogStorage
from soniccontrol.state_updater.updater import Updater
from soniccontrol.tkintergui.utils.constants import sizes, ui_labels
from soniccontrol.tkintergui.utils.events import Event
from soniccontrol.tkintergui.views.configuration.configuration import Configuration
from soniccontrol.tkintergui.views.configuration.flashing import Flashing
from soniccontrol.tkintergui.views.core.app_state import AppState, ExecutionState
from soniccontrol.tkintergui.views.home import Home
from soniccontrol.tkintergui.views.info import Info
from soniccontrol.tkintergui.views.control.logging import Logging
from soniccontrol.tkintergui.views.control.editor import Editor
from soniccontrol.tkintergui.views.control.proc_controlling import ProcControlling
from soniccontrol.tkintergui.views.control.serialmonitor import SerialMonitor
from soniccontrol.tkintergui.views.measure.sonicmeasure import SonicMeasure
from soniccontrol.tkintergui.views.core.status import StatusBar
from soniccontrol.tkintergui.widgets.notebook import Notebook


class DeviceWindow(UIComponent):
    CLOSE_EVENT = "Close"

    def __init__(self, device: SonicAmp, root, logger: logging.Logger):
        self._logger: logging.Logger = logging.getLogger(logger.name + ".ui")
        try:
            self._device = device
            self._view = DeviceWindowView(root)
            super().__init__(None, self._view)

            self._app_state = AppState()
            self._updater = Updater(self._device)
            self._proc_controller = ProcedureController(self._device)

            self._logger.debug("Create logStorage for storing logs")
            self._logStorage = LogStorage()
            log_storage_handler = self._logStorage.create_log_handler()
            logger.addHandler(log_storage_handler)
            device_log_filter = DeviceLogFilter()
            log_storage_handler.addFilter(device_log_filter)

            self._logger.debug("Create views")
            self._home = Home(self, self._device)
            self._sonicmeasure = SonicMeasure(self)
            self._serialmonitor = SerialMonitor(self, self._device)
            self._logging = Logging(self, self._logStorage.logs)
            self._editor = Editor(self, root, self._device, self._app_state)
            self._status_bar = StatusBar(self, self._view.status_bar_slot)
            self._info = Info(self)
            self._configuration = Configuration(self, self._device)
            self._flashing = Flashing(self, self._device, self._app_state)
            self._proc_controlling = ProcControlling(self, self._proc_controller, self._app_state)

            self._logger.debug("Created all views, add them as tabs")
            self._view.add_tab_views([
                self._home.view,
                self._sonicmeasure.view, 
                self._serialmonitor.view, 
                self._logging.view, 
                self._editor.view, 
                self._info.view,
                self._configuration.view, 
                self._flashing.view,
                self._proc_controlling.view
            ])

            self._logger.debug("add callbacks and listeners to event emitters")
            self._view.add_close_callback(self.close)
            self._device.serial.subscribe(Communicator.DISCONNECTED_EVENT, lambda _e: self.on_disconnect())
            self._updater.subscribe("update", lambda e: self._sonicmeasure.on_status_update(e.data["status"]))
            self._updater.subscribe("update", lambda e: self._status_bar.on_update_status(e.data["status"]))
            self._updater.execute()
            self._app_state.subscribe_property_listener(AppState.EXECUTION_STATE_PROP_NAME, self._serialmonitor.on_execution_state_changed)
            self._app_state.subscribe_property_listener(AppState.EXECUTION_STATE_PROP_NAME, self._configuration.on_execution_state_changed)
            self._app_state.subscribe_property_listener(AppState.EXECUTION_STATE_PROP_NAME, self._home.on_execution_state_changed)

            self._app_state.execution_state = ExecutionState.IDLE
        except Exception as e:
            self._logger.error(e)
            raise

    def on_disconnect(self) -> None:
        if not self._view.is_open:
            return # Window was closed already
        
        self._app_state.execution_state = ExecutionState.NOT_RESPONSIVE
        
        # Window is open, Ask User if he wants to close it
        answer: Optional[str] = cast(Optional[str], Messagebox.okcancel(ui_labels.DEVICE_DISCONNECTED_MSG, ui_labels.DEVICE_DISCONNECTED_TITLE))
        if answer is None or answer == "Cancel":
            return
        else:
            self.close()

    @async_handler
    async def close(self) -> None:
        self._logger.info("Close window")
        self.emit(Event(DeviceWindow.CLOSE_EVENT))
        self._view.close()
        await self._device.disconnect()


class DeviceWindowView(tk.Toplevel):
    def __init__(self, root, *args, **kwargs) -> None:
        super().__init__(root, *args, **kwargs)
        self.title("Device Window")
        self.geometry('450x550')
        self.minsize(450, 400)

        self.wm_title(ui_labels.IDLE_TITLE)
        ttk.Style(ui_labels.THEME)
        self.option_add("*Font", "OpenSans 10")
        self._default_font = ttk.font.nametofont("TkDefaultFont")
        self._default_font.configure(family="OpenSans", size=10)

        # tkinter components
        self._frame: ttk.Frame = ttk.Frame(self)
        self._notebook: Notebook = Notebook(self._frame)
        self._status_bar_slot: ttk.Frame = ttk.Frame(self._frame)

        self._frame.pack(fill=ttk.BOTH, expand=True)
        self._status_bar_slot.pack(side=ttk.BOTTOM, fill=ttk.X)
        self._notebook.pack(side=ttk.TOP, fill=ttk.BOTH, expand=True)

        self._notebook.add_tabs(
            [],
            show_titles=True,
            show_images=True,
        )


    @property
    def status_bar_slot(self) -> ttk.Frame:
        return self._status_bar_slot
    
    @property
    def is_open(self) -> bool:
        return self.winfo_exists()

    def add_tab_views(self, tab_views: List[TabView]):
        self._notebook.add_tabs(
            tab_views,
            show_titles=True,
            show_images=True,
        )

    def add_close_callback(self, callback: Callable[[], None]) -> None:
        self.protocol("WM_DELETE_WINDOW", callback)

    def close(self) -> None:
        self.destroy()
