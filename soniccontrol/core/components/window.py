from typing import Set, Dict, Tuple, Any, Callable, Iterable, Optional
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
    Feedbackable,
)
from soniccontrol.interfaces.layout import Layout, HeightLayout
import sonicpackage as sp
from soniccontrol.sonicamp import SonicAmpAgent, Command

logger = logging.getLogger(__name__)


class SonicControl(Root, Disconnectable, Connectable, Configurable, Updatable):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._width_layouts: Iterable[Layout] = (
            WidthLayout(min_width=800, command=self.add_secondary_notebook),
            WidthLayout(min_width=100, command=self.remove_secondary_notebook),
        )
        self._height_layouts: Iterable[Layout] = (
            HeightLayout(min_height=600, command=self.add_statusframe),
            HeightLayout(min_height=500, command=self.remove_statusframe),
        )

        self.geometry("500x410")
        self.minsize(width=310, height=410)
        self.wm_title("SonicControl")
        ttk.Style("sandstone")

        self.connected: bool = False
        self.main_frame: ttk.Panedwindow = ttk.Panedwindow(self, orient=ttk.HORIZONTAL)
        self.util_frame: ttk.Frame = ttk.Frame(self)

        self.notebook_frame: ttk.Frame = ttk.Frame(self.main_frame)
        self.notebook: components.Notebook = components.Notebook(self.notebook_frame)

        self.secondary_notebook_frame: ttk.Frame = ttk.Frame(self.main_frame)
        self.secondary_notebook: components.Notebook = components.Notebook(
            self.secondary_notebook_frame
        )

        self.home_frame: RootChild = components.HomeFrame(
            self,
            tab_title="Home",
            image=const.Images.get_image(
                const.Images.HOME_IMG_BLACK, const.Images.TAB_ICON_SIZE
            ),
        )
        self.scripting_frame: RootChild = components.ScriptingFrame(
            self,
            tab_title="Scripting",
            image=const.Images.get_image(
                const.Images.SCRIPT_IMG_BLACK, const.Images.TAB_ICON_SIZE
            ),
        )
        self.connection_frame: RootChild = components.ConnectionFrame(
            self,
            tab_title="Connection",
            image=const.Images.get_image(
                const.Images.CONNECTION_IMG_BLACK, const.Images.TAB_ICON_SIZE
            ),
        )
        self.settings_frame: RootChild = components.SettingsFrame(
            self,
            tab_title="Settings",
            image=const.Images.get_image(
                const.Images.SETTINGS_IMG_BLACK, const.Images.TAB_ICON_SIZE
            ),
        )
        self.info_frame: RootChild = components.InfoFrame(
            self,
            tab_title="About",
            image=const.Images.get_image(
                const.Images.INFO_IMG_BLACK, const.Images.TAB_ICON_SIZE
            ),
        )
        self.sonicmeasure_frame: RootChild = components.SonicMeasureFrame(
            self,
            tab_title="Sonic Measure",
            image=const.Images.get_image(
                const.Images.LINECHART_IMG_BLACK, const.Images.TAB_ICON_SIZE
            ),
        )
        self.serialmonitor_frame: RootChild = components.SerialMonitorFrame(
            self,
            tab_title="Serial Monitor",
            image=const.Images.get_image(const.Images.CONSOLE_IMG_BLACK, (30, 30)),
        )
        self.statusbar_frame: RootChild = components.StatusBarFrame(
            self,
            tab_title="Status",
            image=const.Images.get_image(
                const.Images.STATUS_IMG_BLACK, const.Images.TAB_ICON_SIZE
            ),
        )
        self.status_frame: RootChild = components.StatusFrame(
            self.notebook_frame,
            tab_title="Status",
            image=const.Images.get_image(
                const.Images.STATUS_IMG_BLACK, const.Images.TAB_ICON_SIZE
            ),
        )

        # INITIALIZING Event iterables
        self.smart_children: Set[RootComponent] = set(
            {
                self.home_frame,
                self.connection_frame,
                self.scripting_frame,
                self.info_frame,
                self.settings_frame,
                self.sonicmeasure_frame,
                self.serialmonitor_frame,
                self.statusbar_frame,
                self.status_frame,
                self.notebook,
            }
        )

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
            if isinstance(child, Feedbackable):
                self.feedbackables.add(child)

        # INITIALIZING Notebook States
        self.frames_for_disconnected_state: Tuple[RootChild] = (
            self.connection_frame,
            self.settings_frame,
            self.info_frame,
        )
        self.frames_for_unkown_device_state: Tuple[
            RootChild
        ] = self.frames_for_disconnected_state + (self.serialmonitor_frame,)
        self.frames_for_soniccatch: Tuple[RootChild] = (
            self.home_frame,
            self.scripting_frame,
            self.sonicmeasure_frame,
            self.serialmonitor_frame,
            self.connection_frame,
            self.settings_frame,
            self.info_frame,
        )
        self.frames_for_primary_notebook: Tuple[RootChild] = (
            self.home_frame,
            self.scripting_frame,
            self.connection_frame,
            self.settings_frame,
            self.info_frame,
        )
        self.frames_for_secondary_notebook: Tuple[RootChild] = (
            self.sonicmeasure_frame,
            self.serialmonitor_frame,
        )

        self.bind_events()
        self.publish()
        self.event_generate(const.Events.DISCONNECTED)
        logger.debug("initialized SonicControl")

    def bind_events(self) -> None:
        super().bind_events()
        # self.bind(const.Events.RESIZING, self.resizer.on_resizing)
        self.bind(const.Events.DISCONNECTED, self.on_disconnect)
        self.bind(const.Events.CONNECTION_ATTEMPT, self.on_connect)

    def check_output_queue(self, command: Command) -> None:
        if command.callback is not None:
            command.callback(command.answer)

    def publish(self) -> None:
        self.main_frame.pack(expand=True, fill=ttk.BOTH)
        self.main_frame.add(self.notebook_frame, weight=1)
        # self.notebook_frame.pack(expand=True, fill=ttk.BOTH)
        self.notebook.pack(expand=True, fill=ttk.BOTH)
        # self.status_frame.pack(fill=ttk.BOTH)
        self.statusbar_frame.pack(side=ttk.BOTTOM, fill=ttk.BOTH)
        self.secondary_notebook.pack(expand=True, fill=ttk.BOTH)

    def remove_statusframe(self, *args, **kwargs) -> None:
        logger.debug("removing status frame")
        self.status_frame.pack_forget()

    def add_statusframe(self, *args, **kwargs) -> None:
        logger.debug("adding status frame")
        self.status_frame.pack(fill=ttk.BOTH)

    def remove_secondary_notebook(self, *args, **kwargs) -> None:
        if not str(self.secondary_notebook_frame) in self.main_frame.panes():
            return
        logger.debug(f"removing secondary notebook")
        self.main_frame.remove(self.secondary_notebook_frame)
        self.secondary_notebook.forget_tabs()
        self.notebook.forget_and_add_tabs(self.frames_for_soniccatch)

    def add_secondary_notebook(self, event: Any = None, *args, **kwargs) -> None:
        if (
            not self.connected
            or str(self.secondary_notebook_frame) in self.main_frame.panes()
        ):
            return
        self.notebook.forget_and_add_tabs(self.frames_for_primary_notebook)
        self.secondary_notebook.forget_and_add_tabs(self.frames_for_secondary_notebook)
        self.main_frame.add(self.secondary_notebook_frame, weight=2)

    def on_disconnect(self, event=None) -> None:
        self.stop_status_engine()
        self.status_frame.pack_forget()
        self.remove_secondary_notebook()
        self.notebook.forget_and_add_tabs(self.frames_for_disconnected_state)
        logger.debug(f"disconnectables {self.disconnectables}")
        for child in self.disconnectables:
            logger.debug(f"calling on_disconnect for {child}")
            child.on_disconnect(event)
        self.connected = False

    def on_configuration(self, event=None) -> None:
        pass
