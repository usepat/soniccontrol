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
    def on_disconnect(self, event: Any = None) -> None:
        ...


class Tabable(abc.ABC):
    @property
    @abc.abstractmethod
    def tab_title(self) -> None:
        ...

    @property
    @abc.abstractmethod
    def image(self) -> None:
        ...


class Connectable(abc.ABC):
    @dataclass
    class ConnectionData:
        heading1: str = field(default="not")
        heading2: str = field(default="connected")
        subtitle: str = field(default="Please connect to a SonicAmp system")
        firmware_info: str = field(default_factory=str)
        tabs: Tuple[Tabable] = field(default_factory=tuple)

    @abc.abstractmethod
    def on_connect(self, event: Any = None) -> None:
        ...


class Configurable(abc.ABC):
    @abc.abstractmethod
    def on_configuration(self, event: Any = None) -> None:
        ...


class Scriptable(abc.ABC):
    @abc.abstractmethod
    def on_script_start(self, event: Any = None) -> None:
        ...

    @abc.abstractmethod
    def on_script_stop(self, event: Any = None) -> None:
        ...

    @abc.abstractmethod
    def on_feedback(self, event: Any = None) -> None:
        ...


class Updatable(abc.ABC):
    @abc.abstractmethod
    def on_update(self, event: Any = None) -> None:
        ...

    @abc.abstractmethod
    def on_frequency_change(self, event: Any = None) -> None:
        ...

    @abc.abstractmethod
    def on_gain_change(self, event: Any = None) -> None:
        ...

    @abc.abstractmethod
    def on_temperature_change(self, event: Any = None) -> None:
        ...

    @abc.abstractmethod
    def on_urms_change(self, event: Any = None) -> None:
        ...

    @abc.abstractmethod
    def on_irms_change(self, event: Any = None) -> None:
        ...

    @abc.abstractmethod
    def on_phase_change(self, event: Any = None) -> None:
        ...

    @abc.abstractmethod
    def on_mode_change(self, event: Any = None) -> None:
        ...

    @abc.abstractmethod
    def on_signal_change(self, event: Any = None) -> None:
        ...


class Resizable(abc.ABC):
    @abc.abstractmethod
    def on_resizing(self, event: Any = None) -> None:
        ...

    @property
    @abc.abstractmethod
    def width_layouts(self) -> Iterable[Layout]:
        ...

    @property
    @abc.abstractmethod
    def height_layouts(self) -> Iterable[Layout]:
        ...


class Feedbackable(abc.ABC):
    @abc.abstractmethod
    def on_feedback(self, event: Any = None) -> None:
        ...
