import ttkbootstrap as ttk
from typing import *
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
        self.current_device_frames: Tuple[Tabable] = ()
        self.notebook_frames: Dict[
            Literal["disconnected", "unknown device", "catch", "descale", "wipe"],
            Tuple[Tabable],
        ] = {
            "disconnected": (
                self.connection_frame,
                self.info_frame,
            ),
            "unknown device": (
                self.serialmonitor_frame,
                self.connection_frame,
                self.info_frame,
            ),
            "catch": (
                self.home_frame,
                self.scripting_frame,
                self.sonicmeasure_frame,
                self.serialmonitor_frame,
                self.connection_frame,
                self.settings_frame,
                self.info_frame,
            ),
            "wipe": (
                self.home_frame,
                self.scripting_frame,
                self.serialmonitor_frame,
                self.connection_frame,
                self.info_frame,
            ),
            "descale": (
                self.home_frame,
                self.scripting_frame,
                self.serialmonitor_frame,
                self.connection_frame,
                self.info_frame,
            ),
        }
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
        # What should happen with the gui, after connection happens
        match self.sonicamp.info.device_type:
            case "catch":
                heading1 = "sonic"
                self.current_device_frames = self.notebook_frames["catch"]
            case "descale":
                heading1 = "sonic"
                self.current_device_frames = self.notebook_frames["descale"]
            case "wipe":
                heading1 = "sonic"
                self.current_device_frames = self.notebook_frames["wipe"]
            case _:
                heading1 = "unknown device"
                self.current_device_frames = self.notebook_frames["unknown device"]

        for connectable in self.connectables:
            connectable.on_connect(
                Connectable.ConnectionData(
                    heading1=heading1,
                    heading2=self.sonicamp.info.device_type,
                    subtitle="You are connected to",
                    firmware_info=self.sonicamp.info.firmware_info,
                    tabs=self.current_device_frames,
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
        self.notebook.forget_and_add_tabs(self.current_device_frames)

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
        self.notebook.forget_and_add_tabs(self.notebook_frames["disconnected"])
        for child in self.disconnectables:
            child.on_disconnect(event)
        self.connected = False

    def on_configuration(self, event=None) -> None:
        pass
