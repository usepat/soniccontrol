from typing import Callable, List, Optional, cast
import logging
from async_tkinter_loop import async_handler
import ttkbootstrap as ttk
import tkinter as tk

from ttkbootstrap.dialogs.dialogs import Messagebox

from soniccontrol_gui.ui_component import UIComponent
from soniccontrol_gui.utils.image_loader import ImageLoader
from soniccontrol_gui.view import TabView
from sonicpackage.communication.communicator import Communicator
from sonicpackage.procedures.procedure_controller import ProcedureController
from sonicpackage.sonicamp_ import SonicAmp
from soniccontrol_gui.state_fetching.logger import DeviceLogFilter, LogStorage, NotDeviceLogFilter
from soniccontrol_gui.state_fetching.updater import Updater
from soniccontrol_gui.constants import sizes, ui_labels
from sonicpackage.events import Event
from soniccontrol_gui.views.configuration.configuration import Configuration
from soniccontrol_gui.views.configuration.flashing import Flashing
from soniccontrol_gui.views.core.app_state import AppState, ExecutionState
from soniccontrol_gui.views.home import Home
from soniccontrol_gui.views.info import Info
from soniccontrol_gui.views.control.logging import Logging, LoggingTab
from soniccontrol_gui.views.control.editor import Editor
from soniccontrol_gui.views.control.proc_controlling import ProcControlling
from soniccontrol_gui.views.control.serialmonitor import SerialMonitor
from soniccontrol_gui.views.measure.sonicmeasure import SonicMeasure
from soniccontrol_gui.views.core.status import StatusBar
from soniccontrol_gui.widgets.notebook import Notebook
from soniccontrol_gui.resources import images


class DeviceWindow(UIComponent):
    CLOSE_EVENT = "Close"

    def __init__(self, logger: logging.Logger, deviceWindowView: "DeviceWindowView", communicator: Communicator):
        self._logger = logger
        self._communicator = communicator
        self._view = deviceWindowView
        super().__init__(None, self._view, self._logger)
        self._app_state = AppState(self._logger)

        self._view.add_close_callback(self.close)
        self._communicator.subscribe(Communicator.DISCONNECTED_EVENT, lambda _e: self.on_disconnect())
    
        self._app_state.execution_state = ExecutionState.IDLE

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
        await self._communicator.close_communication()

class RescueWindow(DeviceWindow):
    def __init__(self, communicator: Communicator, root, connection_name: str):
        self._logger: logging.Logger = logging.getLogger(connection_name + ".ui")
        try:
            self._communicator = communicator
            self._view = DeviceWindowView(root, title=f"Rescue Window - {connection_name}")
            super().__init__(self._logger, self._view, self._communicator)

            self._logger.debug("Create logStorage for storing logs")
            self._logStorage = LogStorage()
            log_storage_handler = self._logStorage.create_log_handler()
            logging.getLogger(connection_name).addHandler(log_storage_handler)
            not_device_log_filter = NotDeviceLogFilter()
            log_storage_handler.addFilter(not_device_log_filter)
            log_storage_handler.setLevel(logging.DEBUG)

            self._logger.debug("Create views")
            self._serialmonitor = SerialMonitor(self, self._communicator)
            self._logging = LoggingTab(self, self._logStorage.logs)

            self._logger.debug("Created all views, add them as tabs")
            self._view.add_tab_views([
                self._serialmonitor.view, 
                self._logging.view, 
            ])

            self._logger.debug("add callbacks and listeners to event emitters")
            self._app_state.subscribe_property_listener(AppState.EXECUTION_STATE_PROP_NAME, self._serialmonitor.on_execution_state_changed)
        except Exception as e:
            self._logger.error(e)
            raise

class KnownDeviceWindow(DeviceWindow):
    def __init__(self, device: SonicAmp, root, connection_name: str):
        self._logger: logging.Logger = logging.getLogger(connection_name + ".ui")
        try:
            self._device = device
            self._view = DeviceWindowView(root, title=f"Device Window - {connection_name}")
            super().__init__(self._logger, self._view, self._device.serial)

            self._updater = Updater(self._device)
            self._proc_controller = ProcedureController(self._device)

            self._logger.debug("Create views")
            self._home = Home(self, self._device)
            self._sonicmeasure = SonicMeasure(self)
            self._serialmonitor = SerialMonitor(self, self._device.serial)
            self._logging = Logging(self, connection_name)
            self._editor = Editor(self, self._device, self._app_state)
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
            self._updater.subscribe("update", lambda e: self._sonicmeasure.on_status_update(e.data["status"]))
            self._updater.subscribe("update", lambda e: self._status_bar.on_update_status(e.data["status"]))
            self._updater.execute()
            self._app_state.subscribe_property_listener(AppState.EXECUTION_STATE_PROP_NAME, self._serialmonitor.on_execution_state_changed)
            self._app_state.subscribe_property_listener(AppState.EXECUTION_STATE_PROP_NAME, self._configuration.on_execution_state_changed)
            self._app_state.subscribe_property_listener(AppState.EXECUTION_STATE_PROP_NAME, self._home.on_execution_state_changed)
        except Exception as e:
            self._logger.error(e)
            raise


class DeviceWindowView(tk.Toplevel):
    def __init__(self, root, *args, **kwargs) -> None:
        title = kwargs.pop("title", "Device Window")
        super().__init__(root, *args, **kwargs)
        self.title(title)
        self.geometry('450x550')
        self.minsize(450, 400)
        self.iconphoto(True, ImageLoader.load_image_resource(images.LOGO, sizes.LARGE_BUTTON_ICON_SIZE))


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
