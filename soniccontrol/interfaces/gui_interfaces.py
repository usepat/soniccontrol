import abc
import logging
from typing import Set, Iterable, List, Optional, Any

from soniccontrol.interfaces.layout import Layout
from soniccontrol.interfaces.exceptions import WrongArgument

logger = logging.getLogger(__name__)
# logger.setLevel(logging.WARNING)


class Disconnectable(abc.ABC):
    @abc.abstractmethod
    def on_disconnect(self, event=None) -> None:
        ...


class Connectable(abc.ABC):
    @abc.abstractmethod
    def on_connect(self, event=None) -> None:
        ...
        
    @abc.abstractmethod
    def on_refresh(self, event=None) -> None:
        ...

 
class Configurable(abc.ABC):
    @abc.abstractmethod
    def on_configuration(self, event=None) -> None:
        ...


class Scriptable(abc.ABC):
    @abc.abstractmethod
    def on_script_start(self, event=None) -> None:
        ...

    @abc.abstractmethod
    def on_script_stop(self, event=None) -> None:
        ...


class Updatable(abc.ABC):
    @abc.abstractmethod
    def on_update(self, event=None) -> None:
        ...


class Resizable(abc.ABC):
    @abc.abstractmethod
    def on_resizing(self, event: Any) -> None:
        ...
    
    @property
    @abc.abstractmethod
    def width_layouts(self) -> Iterable[Layout]:
        ...
    
    @property
    @abc.abstractmethod
    def height_layouts(self) -> Iterable[Layout]:
        ...
    