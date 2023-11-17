from abc import ABC, abstractmethod
from typing_extensions import Any, Iterable
from ttkbootstrap import tk


class EventMixin(ABC):
    """
    This class acts as BaseClass for EventMixins.
    EventMixins are to be inhereted from the concrete
    Tkinter Frame implementations to be able to react
    on a certain event.

    The Root class detects the Mixin Type and calls the
    undelying method accordingly, when the associated
    event takes place.
    """

    pass


class Disconnectable(EventMixin):
    """
    This is a Mixin class to identify a tkinter Widget,
    that should react on the event:

    EVENT: <<Disconnected>>
    """

    @abstractmethod
    def on_disconnected(self, event: Any = None) -> None:
        ...


class Updatable(EventMixin):
    """
    This is a Mixin class to identify a tkinter Widget,
    that should react on the event:

    EVENT: <<StatusChanged>>

    This class is also a BaseClass for concrete StatusUpdates
    to make a concrete Updatable one should use the concrete
    Updatables.
    """

    def on_update(self) -> None:
        """This method is called if a status has changed"""
        ...


class FrequencyUpdatable(Updatable):
    """
    Updatable Mixin Subtype, that focuses on the event that
    the attribute FREQUENCY has changed.
        Event: frequency change
    """

    def on_frequency_change(self) -> None:
        ...


class GainUpdatable(Updatable):
    """
    Updatable Mixin Subtype, that focuses on the event that
    the attribute GAIN has changed.
        Event: gain change
    """

    def on_gain_change(self) -> None:
        ...


class SignalUpdatable(Updatable):
    """
    Updatable Mixin Subtype, that focuses on the event that
    the attribute SIGNAL has changed.
        Event: signal change
    """

    def on_signal_change(self) -> None:
        ...


class WipeModeUpdatable(Updatable):
    """
    Updatable Mixin Subtype, that focuses on the event that
    the attribute WIPE_MODE has changed.
        Event: wipe_mode change
    """

    def on_wipe_mode_change(self) -> None:
        ...


class ProtocolUpdatable(Updatable):
    """
    Updatable Mixin Subtype, that focuses on the event that
    the attribute PROTOCOL has changed.
        Event: protocol change
    """

    def on_protocol_change(self) -> None:
        ...


class RelayModeUpdatable(Updatable):
    """
    Updatable Mixin Subtype, that focuses on the event that
    the attribute RELAY_MODE has changed.
        Event: relay_mode change
    """

    def on_relay_mode_change(self) -> None:
        ...


class CommunicationModeUpdatable(Updatable):
    """
    Updatable Mixin Subtype, that focuses on the event that
    the attribute COMMUNICATION_MODE has changed.
        Event: communication_mode change
    """

    def on_communication_mode_change(self) -> None:
        ...


class Tabable(ABC):
    """
    This Mixin is used to make a tkinter Frame tabable
    in a tkinter Notebook. It is because a RootNotebook
    expects a Tabable to have an tab_title and an image.
    """

    @property
    @abstractmethod
    def tab_title(self) -> str:
        ...

    @property
    @abstractmethod
    def image(self) -> tk.PhotoImage:
        ...


class Connectable(EventMixin):
    """
    This is a Mixin class to identify a tkinter Widget,
    that should react on the event:

    EVENT: <<Connected>>
    """

    @abstractmethod
    def on_connect(self) -> None:
        ...

    @abstractmethod
    def on_connection_attempt(self) -> None:
        ...


class Flashable(EventMixin):
    """
    This is a Mixin class to identify a tkinter Widget,
    that should react on the event:

    EVENT:
        <<FlashingValidated>>
        <<FlashingStarted>>
    """

    @abstractmethod
    def on_validation(self) -> None:
        ...

    @abstractmethod
    def on_flashing(self) -> None:
        ...


class Scriptable(EventMixin):
    """
    This is a Mixin class to identify a tkinter Widget,
    that should react on the event:

    EVENT:
        <<ScriptStarted>>
        <<ScriptFinished>>
    """

    @abstractmethod
    def on_script_start(self) -> None:
        ...

    @abstractmethod
    def on_script_stop(self) -> None:
        ...


class Resizable(EventMixin):
    """
    This is a Mixin class to identify a tkinter Widget,
    that should react on the event:

    EVENT: <<Configure>>

    This is a special Mixin that is required by the Resizer
    API of RootChildren.
    """

    @abstractmethod
    def on_resizing(self) -> None:
        ...

    @property
    @abstractmethod
    def layouts(self) -> Iterable[Layout]:
        ...

