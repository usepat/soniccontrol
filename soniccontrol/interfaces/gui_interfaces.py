import abc
import logging
from dataclasses import dataclass, field
from typing import Set, Iterable, List, Optional, Any, Tuple

from soniccontrol.interfaces.layout import Layout
from soniccontrol.interfaces.exceptions import WrongArgument

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


class Disconnectable(abc.ABC):
    @abc.abstractmethod
    def on_disconnect(self, event=None) -> None:
        ...


class Tabable(abc.ABC):
    pass

class Connectable(abc.ABC):
    @dataclass
    class ConnectionData:
        heading1: str = field(default='not')
        heading2: str = field(default='connected')
        subtitle: str = field(default='Please connect to a SonicAmp system')
        firmware_info: str = field(default_factory=str)
        tabs: Tuple[Tabable] = field(default_factory=tuple)
    
    @abc.abstractmethod
    def on_connect(self, event=None) -> None:
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
    