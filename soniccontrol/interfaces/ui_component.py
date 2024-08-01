import abc
import logging
from typing import Optional

from soniccontrol.interfaces.view import View
from soniccontrol.tkintergui.utils.events import EventManager


class UIComponent(EventManager):
    def __init__(self, parent: Optional["UIComponent"], view, logger: logging.Logger = logging.getLogger("ui")):
        super().__init__()
        self._parent = parent
        self._view = view
        self._logger = logger

    @property
    def view(self):
        return self._view
    
    @property
    def parent(self):
        return self._parent
    
    @property
    def logger(self):
        return self._logger
    
    