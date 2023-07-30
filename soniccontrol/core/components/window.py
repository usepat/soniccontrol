from typing import Set, Dict, Tuple, Any, Callable, Iterable
import ttkbootstrap as ttk
import logging
import soniccontrol.constants as const
import soniccontrol.core.components as components
from soniccontrol.interfaces import (
    Root,
    RootChild,
    WidthLayout,
    RootComponent,
    Disconnectable,
    Connectable,
    Updatable,
    Scriptable,
    Configurable,
)
from soniccontrol.interfaces.layout import Layout

logger = logging.getLogger(__name__)

class SonicControl(Root, Disconnectable, Connectable, Configurable, Updatable):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._width_layouts: Iterable[Layout] = (
            WidthLayout(
                min_width=100,
                command=self.remove_secondary_notebook
            ),
            WidthLayout(
                min_width=1000,
                command=self.add_secondary_notebook
            )
        )
        # self._height_layouts: Iterable[Layout] = ()

        self.geometry("500x400")
        self.minsize(width=201, height=300)
        self.wm_title("SonicControl")
        ttk.Style("sandstone")

        self.util_frame: ttk.Frame = ttk.Frame(self)

        self.notebook_frame: ttk.Frame = ttk.Frame(self)
        self.notebook: RootChild = components.Notebook(self.notebook_frame)

        self.home_frame: RootChild = components.HomeFrame(
            self, tab_title="Home", image=const.HOME_RAW_IMG
        )
        self.scripting_frame: RootChild = components.ScriptingFrame(
            self, tab_title="Scripting", image=const.SCRIPT_RAW_IMG
        )
        self.connection_frame: RootChild = components.ConnectionFrame(
            self, tab_title="Connection", image=const.CONNECTION_RAW_IMG
        )
        self.settings_frame: RootChild = components.SettingsFrame(
            self, tab_title="Settings", image=const.SETTINGS_RAW_IMG
        )
        self.info_frame: RootChild = components.InfoFrame(
            self, tab_title="About", image=const.INFO_RAW_IMG
        )
        self.sonicmeasure_frame: RootChild = components.SonicMeasureFrame(
            self, tab_title="Sonic Measure", image=const.SONIC_MEASURE_RAW_IMG
        )
        self.serialmonitor_frame: RootChild = components.SerialMonitorFrame(
            self, tab_title="Serial Monitor", image=const.CONSOLE_RAW_IMG
        )
        self.statusframe_frame: RootChild = components.StatusFrame(
            self, tab_title="Status", image=const.STATUS_RAW_IMG
        )

        # INITIALIZING Event iterables
        self.smart_children: Set[RootComponent] = set({
            self.home_frame,
            self.connection_frame,
            self.scripting_frame,
            self.info_frame,
            self.settings_frame,
            self.sonicmeasure_frame,
            self.serialmonitor_frame,
            self.statusframe_frame
        })

        self.disconnectables: Set[RootComponent] = set()
        self.connectables: Set[RootComponent] = set()
        self.configurables: Set[RootComponent] = set()
        self.updatables: Set[RootComponent] = set()
        self.scriptables: Set[RootComponent] = set()
        
        for child in self.smart_children:
            if isinstance(child, Disconnectable):
                self.disconnectables.add(child)
            if isinstance(child, Connectable):
                self.connectables.add(child)
            if isinstance(child, Configurable):
                self.configurables.add(child)
            if isinstance(child, Updatable):
                self.updatables.add(child)
            if isinstance(child, Scriptable):
                self.scriptables.add(child)
        
        # INITIALIZING Notebook States
        self.frames_for_disconnected_state: Tuple[RootChild] = (
            self.connection_frame,
            self.settings_frame,
            self.info_frame,
        )
        self.frames_for_unkown_device_state: Tuple[RootChild] = self.frames_for_disconnected_state + (self.serialmonitor_frame,)
        self.frames_for_soniccatch: Tuple[RootChild] = (
            self.home_frame,
            self.scripting_frame,
            self.sonicmeasure_frame,
            self.serialmonitor_frame,
            self.connection_frame,
            self.settings_frame,
            self.info_frame,
        )

        self.bind_events()
        self.publish()
        self.event_generate(const.Events.DISCONNECTED)
        logger.debug('initialized SonicControl')

    def bind_events(self) -> None:
        super().bind_events()
        # self.bind(const.Events.RESIZING, self.resizer.on_resizing)
        self.bind(const.Events.DISCONNECTED, self.on_disconnect)
        self.bind(const.Events.CONNECTION_ATTEMPT, self.on_connect)

    def publish(self) -> None:
        self.notebook_frame.pack(expand=True, fill=ttk.BOTH)
        self.notebook.pack(expand=True, fill=ttk.BOTH)

    def remove_secondary_notebook(self) -> None:
        pass

    def add_secondary_notebook(self) -> None:
        pass

    def on_disconnect(self, event=None) -> None:
        self.stop_status_engine()
        self.notebook.forget_and_add_tabs(self.frames_for_disconnected_state)
        logger.debug(f"disconnectables {self.disconnectables}")
        for child in self.disconnectables:
            logger.debug(f"calling on_disconnect for {child}")
            child.on_disconnect(event)
        logger.debug("Reacted to disconnect event")

    def stop_status_engine(self) -> None:
        pass

    def on_connect(self, event=None) -> None:
        pass
    
    def on_configuration(self, event=None) -> None:
        pass
    
    def on_refresh(self, event=None) -> None:
        pass
    
    def on_update(self, event=None) -> None:
        pass
