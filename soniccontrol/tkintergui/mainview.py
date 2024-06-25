from typing import Any, get_type_hints

import attrs
import ttkbootstrap as ttk
from icecream import ic

from soniccontrol import soniccontrol_logger as logger
from soniccontrol.tkintergui.utils.constants import sizes, ui_labels
from soniccontrol.tkintergui.utils.image_loader import ImageLoader
from soniccontrol.tkintergui.views.home import HomeView
from soniccontrol.tkintergui.views.info import InfoView
from soniccontrol.tkintergui.views.editor import EditorView
from soniccontrol.tkintergui.views.serialmonitor import SerialMonitorView
from soniccontrol.tkintergui.views.settings import SettingsView
from soniccontrol.tkintergui.views.sonicmeasure import SonicMeasureView
from soniccontrol.tkintergui.views.status import StatusBar
from soniccontrol.tkintergui.widgets.notebook import Notebook
from soniccontrol.tkintergui.utils.events import Event, PropertyChangeEvent

@attrs.frozen
class SonicControlViews:
    home: HomeView = attrs.field()
    scripting: EditorView = attrs.field()
    settings: SettingsView = attrs.field()
    info: InfoView = attrs.field()
    sonicmeasure: SonicMeasureView = attrs.field()
    serialmonitor: SerialMonitorView = attrs.field()
    statusbar: StatusBar = attrs.field()


class MainView(ttk.Window):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        ImageLoader(self)

        self.wm_title(ui_labels.IDLE_TITLE)
        ttk.Style(ui_labels.THEME)
        self.option_add("*Font", "OpenSans 10")
        self._default_font = ttk.font.nametofont("TkDefaultFont")
        self._default_font.configure(family="OpenSans", size=10)

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

        self.columnconfigure(0, weight=sizes.EXPAND)
        self.rowconfigure(0, weight=sizes.EXPAND)
        self.rowconfigure(1, weight=sizes.DONT_EXPAND)
        self.grid_rowconfigure(1, minsize=16)
        self._main_frame.grid(row=0, column=0, sticky=ttk.NSEW)
        self._views.statusbar.grid(row=1, column=0, sticky=ttk.EW)

        self._left_frame.columnconfigure(0, weight=sizes.EXPAND)
        self._left_frame.rowconfigure(0, weight=sizes.EXPAND)
        self._left_frame.rowconfigure(1, weight=sizes.DONT_EXPAND, minsize=0)

        self._left_frame.rowconfigure(1, weight=0, minsize=60)
        self._left_notebook.grid(row=0, column=0, sticky=ttk.NSEW)
        self._status_frame.grid(row=1, column=0, sticky=ttk.EW)

        self._main_frame.add(self._left_frame, weight=sizes.DONT_EXPAND)
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

    @property
    def views(self) -> SonicControlViews:
        return self._views

    def resize(self, event: Any, *args: Any, **kwargs: Any) -> None:
        if event.widget is not self:
            return

        if event.height < 600:
            self.remove_status_frame()
        # elif self.misc_vars.program_state.get() != "Disconnected":
        #     self._status_frame.grid()

        notebook_tkinter_path: str = self._right_notebook.winfo_pathname(
            self._right_notebook.winfo_id()
        )
        # if (
        #     event.width > 1000
        #     and notebook_tkinter_path not in self._main_frame.panes()
        #     and self.misc_vars.program_state.get() != "Disconnected"
        # ):
        #     self._main_frame.add(self._right_notebook, weight=sizes.EXPAND)
        #     self._right_notebook.add_tabs(
        #         [self.views.sonicmeasure, self.views.serialmonitor],
        #         show_titles=True,
        #         show_images=True,
        #     )
        # elif (
        #     event.width < 1000
        #     and notebook_tkinter_path in self._main_frame.panes()
        #     and self.misc_vars.program_state.get() != "Disconnected"
        # ):
        #     SONICMEASURE_TABINDEX: int = 2
        #     SERIALMONITOR_TABINDEX: int = 3
        #     self._main_frame.forget(self._right_notebook)
        #     self._left_notebook.add_tabs(
        #         [
        #             (SONICMEASURE_TABINDEX, self.views.sonicmeasure),
        #             (SERIALMONITOR_TABINDEX, self.views.serialmonitor),
        #         ],
        #         keep_tabs=True,
        #         show_titles=True,
        #         show_images=True,
        #     )
        #
        if (event.width / len(self._left_notebook.tabs())) < 55:
            self._left_notebook.configure_tabs(show_titles=False, show_images=True)
        else:
            self._left_notebook.configure_tabs(show_titles=True, show_images=True)

    def remove_status_frame(self) -> None:
        self._status_frame.grid_remove()
        self._left_frame.rowconfigure(1, weight=0, minsize=0)

    def on_frequency_change(self, event: PropertyChangeEvent) -> None:
        logger.debug("Frequency changed to: %s", event)
        pass

    def on_gain_change(self, event: PropertyChangeEvent) -> None:
        logger.debug("Gain changed to: %s", event)
        pass

    def on_temp_change(self, event: PropertyChangeEvent) -> None:
        logger.debug("Temperature changed to: %s", event)
        pass

    def on_urms_change(self, event: PropertyChangeEvent) -> None:
        logger.debug("Urms changed to: %s", event)
        pass

    def on_irms_change(self, event: PropertyChangeEvent) -> None:
        logger.debug("Irms changed to: %s", event)
        pass

    def on_phase_change(self, event: PropertyChangeEvent) -> None:
        logger.debug("Phase changed to: %s", event)
        pass

    def on_signal_change(self, event: PropertyChangeEvent) -> None:
        logger.debug("Signal changed to: %s", event)
        pass

    def on_wipe_mode_change(self, event: PropertyChangeEvent) -> None:
        logger.debug("Wipe mode changed to: %s", event)
        pass

    def on_relay_mode_change(self, event: PropertyChangeEvent) -> None:
        logger.debug("Relay mode changed to: %s", event)
        pass

    def on_connection_attempt_event(self, event: Event) -> None:
        logger.debug(f"Connection attempt event {event}")
        pass

    def on_connection_established_event(self, event: Event) -> None:
        logger.debug(f"Connection established event {event}")
        pass

    def on_disconnection_event(self, event: Event) -> None:
        logger.debug(f"Disconnection event {event}")
        self.remove_status_frame()
        self._main_frame.forget(self._right_notebook)
        self._left_notebook.add_tabs(
            [self.views.connection, self.views.info],
            show_titles=True,
            show_images=True,
        )
        pass

    def on_script_start_event(self, event: Event) -> None:
        logger.debug(f"Script start event {event}")
        pass

    def on_script_stop_event(self, event: Event) -> None:
        logger.debug(f"Script stop event {event}")
        pass

    def on_script_pause_event(self, event: Event) -> None:
        logger.debug(f"Script pause event {event}")
        pass

    def on_firmware_flash_event(self, event: Event) -> None:
        logger.debug(f"Firmware flash event {event}")
        pass

    def on_sonicmeasure_start_event(self, event: Event) -> None:
        logger.debug(f"Sonicmeasure start event {event}")
        pass

    def on_sonicmeasure_stop_event(self, event: Event) -> None:
        logger.debug(f"Sonicmeasure stop event {event}")
        pass

    def on_auto_mode_event(self, event: Event) -> None:
        logger.debug(f"Auto mode event {event}")
        pass

    def on_manual_mode_event(self, event: Event) -> None:
        logger.debug(f"Manual mode event {event}")
        pass

    def on_save_config_event(self, event: Event) -> None:
        logger.debug(f"Save config event {event}")
        pass
