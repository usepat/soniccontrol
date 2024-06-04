import abc

from soniccontrol.interfaces.view import View
from soniccontrol.tkintergui.utils.events import EventManager


class UIComponent(EventManager):
    def __init__(self, view):
        self._view = view

    @property
    def view(self):
        return self._view
    
    