import logging
from typing import Optional

from soniccontrol_gui.view import View
from sonicpackage.events import EventManager


class UIComponent(EventManager):
    def __init__(self, parent: Optional["UIComponent"], view: View, logger: logging.Logger = logging.getLogger("ui")):
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
    
    