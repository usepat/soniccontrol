import ttkbootstrap as ttk

from typing import List, Iterable

from soniccontrol.interfaces import (
    RootNotebook,
    WidthLayout,
    HeightLayout,
    Layout,
)
import soniccontrol.constants as const
from soniccontrol.interfaces.layout import Layout

class Notebook(RootNotebook):
    def __init__(self, parent_frame: ttk.Frame, *args, **kwargs):
        super().__init__(parent_frame, *args, **kwargs)
        self._width_layouts: Iterable[Layout] = (
            Layout(
                condition=lambda event: len(self.tabs()) and (event.width / len(self.tabs())) < 60,
                command=lambda event: self.configure_tabs(tab_titles=False, images=True)
            ),
            WidthLayout(
                min_width=300,
                command=self.show_tab_titles
            ),
        )
        self._height_layouts: Iterable[Layout] = (
            HeightLayout(
                min_height=100,
                command=self.hide_images
            ),
            HeightLayout(
                min_height=400,
                command=self.show_images
            )
        )
        self.bind_events()
    
    def bind_events(self) -> None:
        super().bind_events()