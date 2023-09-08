import ttkbootstrap as ttk
from typing import Tuple, Any
from soniccontrol.core.interfaces import (
    Root,
    RootChild,
    Tabable,
    Connectable,
    WidthLayout,
    HeightLayout,
)
import soniccontrol.core.components as components
import soniccontrol.constants as const


class SonicControl(Root):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, *kwargs)
        self.set_layouts(
            [
                WidthLayout(min_size=800, command=self.add_secondary_notebook),
                WidthLayout(min_size=100, command=self.remove_secondary_notebook),
                HeightLayout(min_size=600, command=self.add_statusframe),
                HeightLayout(min_size=500, command=self.remove_statusframe),
            ]
        )
        self.geometry("500x410")
        self.minsize(width=310, height=410)
        self.wm_title("SonicControl")
        ttk.Style("sandstone")

        self.main_frame: ttk.Panedwindow = ttk.Panedwindow(self, orient=ttk.HORIZONTAL)
        self.util_frame: ttk.Frame = ttk.Frame(self)

        self.notebook_frame: ttk.Frame = ttk.Frame(self.main_frame)
        self.notebook: components.Notebook = self.add_rootchild(
            components.Notebook(self.notebook_frame)
        )

        self.secondary_notebook_frame: ttk.Frame = ttk.Frame(self.main_frame)
        self.secondary_notebook: components.Notebook = components.Notebook(
            self.secondary_notebook_frame
        )

        self.home_frame: RootChild = self.add_rootchild(
            components.HomeFrame(self, image=self.home_image)
        )
        self.scripting_frame: RootChild = self.add_rootchild(
            components.ScriptingFrame(self, image=self.script_image)
        )
        self.connection_frame: RootChild = self.add_rootchild(
            components.ConnectionFrame(self, image=self.connection_image)
        )
        self.settings_frame: RootChild = self.add_rootchild(
            components.SettingsFrame(self, image=self.settings_image)
        )
        self.info_frame: RootChild = self.add_rootchild(
            components.InfoFrame(self, image=self.info_image)
        )
        self.sonicmeasure_frame: RootChild = self.add_rootchild(
            components.SonicMeasureFrame(self, image=self.graph_image)
        )
        self.serialmonitor_frame: RootChild = self.add_rootchild(
            components.SerialMonitorFrame(self, image=self.console_image)
        )
        self.statusbar: RootChild = self.add_rootchild(
            components.StatusBar(self, image=self.status_image)
        )
        self.status_frame: RootChild = self.add_rootchild(
            components.StatusFrame(self.notebook_frame, image=self.status_image)
        )

        # INITIALIZING Notebook States
        self.frames_for_disconnected_state: Tuple[Tabable, ...] = (
            self.connection_frame,
            self.info_frame,
        )
        self.frames_for_unkown_device_state: Tuple[
            Tabable, ...
        ] = self.frames_for_disconnected_state + (self.serialmonitor_frame,)
        self.frames_for_soniccatch: Tuple[Tabable, ...] = (
            self.home_frame,
            self.scripting_frame,
            self.sonicmeasure_frame,
            self.serialmonitor_frame,
            self.connection_frame,
            self.settings_frame,
            self.info_frame,
        )
        self.frames_for_primary_notebook: Tuple[Tabable, ...] = (
            self.home_frame,
            self.scripting_frame,
            self.connection_frame,
            self.settings_frame,
            self.info_frame,
        )
        self.frames_for_secondary_notebook: Tuple[Tabable, ...] = (
            self.sonicmeasure_frame,
            self.serialmonitor_frame,
        )

        self.bind_events()
        self.publish()
        self.event_generate(const.Events.DISCONNECTED)

    def after_connect(self) -> None:
        for connectable in self.connectables:
            connectable.on_connect(
                Connectable.ConnectionData(
                    heading1="sonic",
                    heading2="catch",
                    subtitle="You are connected to",
                    firmware_info="SONICCATCH FIRMWARE",
                    tabs=self.frames_for_soniccatch,
                )
            )

    def publish(self) -> None:
        self.main_frame.pack(expand=True, fill=ttk.BOTH)
        self.main_frame.add(self.notebook_frame, weight=1)
        self.notebook.pack(expand=True, fill=ttk.BOTH)
        self.statusbar.pack(side=ttk.BOTTOM, fill=ttk.BOTH)
        self.secondary_notebook.pack(expand=True, fill=ttk.BOTH)

    def remove_statusframe(self, *args, **kwargs) -> None:
        self.status_frame.pack_forget()

    def add_statusframe(self, *args, **kwargs) -> None:
        self.status_frame.pack(fill=ttk.BOTH)

    def remove_secondary_notebook(self, *args, **kwargs) -> None:
        if not str(self.secondary_notebook_frame) in self.main_frame.panes():
            return
        self.main_frame.remove(self.secondary_notebook_frame)
        self.secondary_notebook.forget_tabs()
        self.notebook.forget_and_add_tabs(self.frames_for_soniccatch)

    def add_secondary_notebook(self, event: Any = None, *args, **kwargs) -> None:
        if (
            not self.sonicamp
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
        for child in self.disconnectables:
            child.on_disconnect(event)
        self.connected = False

    def on_configuration(self, event=None) -> None:
        pass
