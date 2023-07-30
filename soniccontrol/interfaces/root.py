from typing import Any, Optional, Iterable, Set
import tkinter as tk
import abc
import logging
import soniccontrol.constants as const
from soniccontrol.interfaces.gui_interfaces import Resizable
from soniccontrol.interfaces.resizer import Resizer
from soniccontrol.interfaces.layout import Layout

logger = logging.getLogger(__name__)


class Root(tk.Tk, Resizable):
    def __init__(self) -> None:
        super().__init__()
        self._width_layouts: Optional[Iterable[Layout]] = None
        self._height_layouts: Optional[Iterable[Layout]] = None
        self._resizer: Resizer = Resizer(self)
        logger.debug('initialized Root')
    
    @property
    def resizer(self) -> Resizer:
        return self._resizer
    
    @property
    def width_layouts(self) -> Iterable[Layout]:
        return self._width_layouts
    
    @property
    def height_layouts(self) -> Iterable[Layout]:
        return self._height_layouts
    
    def bind_events(self) -> None:
        self.bind(const.Events.RESIZING, self.on_resizing)
        
    def on_resizing(self, event: Any) -> None:
        return self.resizer.resize(event=event)