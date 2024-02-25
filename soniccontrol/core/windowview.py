from typing import Any, get_type_hints

import attrs
import soniccontrol.utils.constants as const
import ttkbootstrap as ttk
from soniccontrol.components.notebook import Notebook
from soniccontrol.interfaces.layouts import Layout
from soniccontrol.interfaces.root import Root
from soniccontrol.utils import ImageLoader
from soniccontrol.views.connectionview import ConnectionView
from soniccontrol.views.homeview import HomeView
from soniccontrol.views.infoview import InfoView
from soniccontrol.views.scriptingview import ScriptingView
from soniccontrol.views.serialmonitorview import SerialMonitorView
from soniccontrol.views.settingsview import SettingsView
from soniccontrol.views.sonicmeasureview import SonicMeasureView
from soniccontrol.views.statusview import StatusBarView, StatusView

from soniccontrol import soniccontrol_logger as logger


@attrs.frozen
class SonicControlViews:
    home: HomeView = attrs.field()
    scripting: ScriptingView = attrs.field()
    connection: ConnectionView = attrs.field()
    settings: SettingsView = attrs.field()
    info: InfoView = attrs.field()
    sonicmeasure: SonicMeasureView = attrs.field()
    serialmonitor: SerialMonitorView = attrs.field()
    statusview: StatusView = attrs.field()
    statusbar: StatusBarView = attrs.field()


# TODO: look how to abstract the class, so that the images are stored in one place and referenced in the children views


class MainView(Root):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def _initialize_children(self) -> None:
        self.wm_title(const.ui.IDLE_TITLE)
        ttk.Style(const.ui.THEME)

        # tkinter components
        self._main_frame: ttk.Panedwindow = ttk.Panedwindow(
            self, orient=ttk.HORIZONTAL, style=ttk.SECONDARY
        )
        self._left_frame: ttk.Frame = ttk.Frame(self)
        self._left_notebook: Notebook = Notebook(self._left_frame)
        self._status_frame: StatusView = StatusView(self._left_frame)
        self._right_notebook: Notebook = Notebook(self)

        self._views: SonicControlViews = SonicControlViews(
            **{
                key: view(self)
                for key, view in get_type_hints(SonicControlViews).items()
            }
        )
        self._views.statusbar.configure(bootstyle=ttk.SECONDARY)

    @property
    def layouts(self) -> set[Layout]:
        ...

    @property
    def views(self) -> SonicControlViews:
        return self._views

    def publish(self) -> None:
        ...

    def _initialize_publish(self) -> None:
        self.columnconfigure(0, weight=const.misc.EXPAND)
        self.rowconfigure(0, weight=const.misc.EXPAND)
        self.rowconfigure(1, weight=const.misc.DONT_EXPAND)
        self.grid_rowconfigure(1, minsize=16)
        self._main_frame.grid(row=0, column=0, sticky=ttk.NSEW)
        self._views.statusbar.grid(row=1, column=0, sticky=ttk.EW)

        self._left_frame.columnconfigure(0, weight=const.misc.EXPAND)
        self._left_frame.rowconfigure(0, weight=const.misc.EXPAND)
        self._left_frame.rowconfigure(1, weight=const.misc.DONT_EXPAND, minsize=0)

        self._left_frame.rowconfigure(1, weight=0, minsize=60)
        self._left_notebook.grid(row=0, column=0, sticky=ttk.NSEW)
        self._status_frame.grid(row=1, column=0, sticky=ttk.EW)

        self._main_frame.add(self._left_frame, weight=const.misc.DONT_EXPAND)
        self._left_notebook.add_tabs(
            [
                self.views.home,
                self.views.scripting,
                self.views.sonicmeasure,
                self.views.serialmonitor,
                self.views.connection,
                self.views.settings,
                self.views.info,
            ],
            show_titles=True,
            show_images=True,
        )

    def resize(self, event: Any, *args: Any, **kwargs: Any) -> None:
        if event.widget is not self:
            return

        if event.height < 600:
            self._status_frame.grid_remove()
            self._left_frame.rowconfigure(1, weight=0, minsize=0)
        else:
            self._status_frame.grid()

        notebook_tkinter_path: str = self._right_notebook.winfo_pathname(
            self._right_notebook.winfo_id()
        )
        if event.width > 1000 and notebook_tkinter_path not in self._main_frame.panes():
            self._main_frame.add(self._right_notebook, weight=const.misc.EXPAND)
            self._right_notebook.add_tabs(
                [self.views.sonicmeasure, self.views.serialmonitor],
                show_titles=True,
                show_images=True,
            )
        elif event.width < 1000 and notebook_tkinter_path in self._main_frame.panes():
            self._main_frame.forget(self._right_notebook)
            self._left_notebook.add_tabs(
                [self.views.sonicmeasure, self.views.serialmonitor],
                keep_tabs=True,
                show_titles=True,
                show_images=True,
            )

        if (event.width / len(self._left_notebook.tabs())) < 55:
            self._left_notebook.configure_tabs(show_titles=False, show_images=True)
        else:
            self._left_notebook.configure_tabs(show_titles=True, show_images=True)

    def set_large_width_layout(self) -> None:
        ...

    def set_small_width_layout(self) -> None:
        ...

    def on_disconnect(self) -> None:
        ...

    def on_firmware_flash(self) -> None:
        ...
