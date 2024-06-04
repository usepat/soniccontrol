import abc
from typing import Optional

from soniccontrol.interfaces.view import View
from soniccontrol.tkintergui.utils.events import EventManager


class UIComponent(EventManager):
    def __init__(self, parent: Optional["UIComponent"], view):
        super().__init__()
        self._parent = parent
        self._view = view

    @property
    def view(self):
        return self._view
    
    @property
    def parent(self):
        return self._parent
    
    