import tkinter as tk
from typing import List
import ttkbootstrap as ttk

from soniccontrol.interfaces.ui_component import UIComponent
from soniccontrol.interfaces.view import TabView
from soniccontrol.state_updater.updater import Updater
from soniccontrol.tkintergui.utils.constants import sizes, ui_labels
from soniccontrol.tkintergui.utils.image_loader import ImageLoader
from soniccontrol.tkintergui.views.sonicmeasure import SonicMeasure
from soniccontrol.tkintergui.views.status import StatusView
from soniccontrol.tkintergui.widgets.notebook import Notebook


class MainWindow(UIComponent):
    def __init__(self):
        self._updater = Updater()
        self._sonicmeasure = SonicMeasure()
        super().__init__(MainWindowView([self._sonicmeasure.view]))

        self._updater._event_emitter.subscribe("update", self._sonicmeasure.on_status_update)


class MainWindowView(tk.Window):
    def __init__(self, tab_views: List[TabView],  *args, **kwargs) -> None:
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
        self._right_notebook: Notebook = Notebook(self)

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
            tab_views,
            show_titles=True,
            show_images=True,
        )

