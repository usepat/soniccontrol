import logging
import tkinter as tk
from typing import Iterable
import ttkbootstrap as ttk
import PIL
from soniccontrol.interfaces import RootChild, Layout

logger = logging.getLogger(__name__)


class SettingsFrame(RootChild):
    def __init__(
        self, parent_frame: ttk.Frame, tab_title: str, image: PIL.Image, *args, **kwargs
    ):
        super().__init__(parent_frame, tab_title, image, *args, **kwargs)
        self.mode_frame: ttk.Frame = ttk.Frame(self)
        self.modes_menue: ttk.Combobox = ttk.Combobox(
            master=self.mode_frame,
            width=20,
            style="dark.TCombobox",
            state=tk.READABLE,
        )
        self.mode_button: ttk.Button = ttk.Button(
            self.mode_frame,
            bootstyle="secondary-outline",
            text="Set Mode",
        )
