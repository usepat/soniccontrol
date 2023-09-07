from typing import Iterable
import logging
import ttkbootstrap as ttk
from soniccontrol.core.interfaces import (
    RootNotebook,
    WidthLayout,
    Layout,
    Connectable,
    RootChild,
)
import soniccontrol.constants as const

logger = logging.getLogger(__name__)


class Notebook(RootNotebook, Connectable):
    def __init__(self, parent_frame: ttk.Frame, *args, **kwargs):
        super().__init__(parent_frame, *args, **kwargs)
        self.set_layouts(
            [
                WidthLayout(min_size=400, command=self.show_tab_titles),
                WidthLayout(
                    command=self.show_images_without_titles,
                    condition=lambda event: (
                        len(self.tabs()) and (event.width / len(self.tabs())) < 60
                    ),
                ),
            ]
        )

        self.bind_events()

    def on_connect(self, connection_data: Connectable.ConnectionData) -> None:
        logger.debug(f"Connecting, adding tabs {connection_data.tabs}")
        self.forget_and_add_tabs(connection_data.tabs)

    def on_refresh(self, event=None) -> None:
        pass

    def bind_events(self) -> None:
        super().bind_events()
