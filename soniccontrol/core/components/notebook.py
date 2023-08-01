import ttkbootstrap as ttk

from typing import List, Iterable

from soniccontrol.interfaces import (
    RootNotebook,
    WidthLayout,
    HeightLayout,
    Layout,
)
import soniccontrol.constants as const
from soniccontrol.interfaces import Layout, Connectable, RootChild


class Notebook(RootNotebook, Connectable):
    def __init__(self, parent_frame: ttk.Frame, *args, **kwargs):
        super().__init__(parent_frame, *args, **kwargs)
        self._width_layouts: Iterable[Layout] = (
            WidthLayout(
                min_width=400,
                command=self.show_tab_titles
            ),
            Layout(
                condition=lambda event: len(self.tabs()) and (event.width / len(self.tabs())) < 60,
                command=self.show_images_without_titles
            ),
        )
        self._height_layouts: Iterable[Layout] = tuple()
        
        self.bind_events()
    
    def on_connect(self, connection_data: Connectable.ConnectionData) -> None:
        selected_tab: RootChild = self.select()
        self.forget_tabs()
        self.add_tabs(connection_data.tabs)
        self.select(selected_tab)
        
    def on_refresh(self, event=None) -> None:
        pass
    
    def bind_events(self) -> None:
        super().bind_events()