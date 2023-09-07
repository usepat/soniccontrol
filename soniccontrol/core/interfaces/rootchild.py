import tkinter as tk
from typing import Optional, Any, TYPE_CHECKING, Iterable
from PIL.ImageTk import PhotoImage
import ttkbootstrap as ttk

import soniccontrol.constants as const
from soniccontrol.core.interfaces.layouts import Layout
from soniccontrol.core.interfaces.resizer import Resizer
from soniccontrol.core.interfaces.gui_interfaces import Tabable, Resizable
from soniccontrol.core.interfaces.root import Root


class RootChild(ttk.Frame, Tabable, Resizable):
    def __init__(
        self,
        root: Root,
        tab_title: str,
        image: PhotoImage,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(master=root, *args, **kwargs)
        self._layouts: Optional[Iterable[Layout]] = None
        self._tab_title: str = tab_title
        self._image: PhotoImage = image
        self._resizer: Resizer = Resizer(self)

    @property
    def root(self) -> Root:
        return self.winfo_toplevel()

    @property
    def resizer(self) -> Resizer:
        return self._resizer

    @property
    def layouts(self) -> Optional[Iterable[Layout]]:
        return self._layouts

    @property
    def tab_title(self) -> str:
        return self._tab_title

    @property
    def image(self) -> PhotoImage:
        return self._image

    def set_layouts(self, layouts: Iterable[Layout]) -> None:
        self._layouts = layouts
        self._resizer = Resizer(self)

    def bind_events(self) -> None:
        self.bind(const.Events.RESIZING, self.on_resizing)

    def on_resizing(self, event: Any) -> None:
        return self.resizer.resize(event=event)
