import abc
import attrs
from typing import Any, Iterable, Tuple, Optional
import ttkbootstrap as ttk

from soniccontrol.core.interfaces.layouts import Layout, WidthLayout, HeightLayout


class Disconnectable(abc.ABC):
    @abc.abstractmethod
    def on_disconnect(self, event: Any = None) -> None:
        ...


class Updatable(abc.ABC):
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
    @attrs.define
    class ConnectionData:
        heading1: str = attrs.field(default="not")
        heading2: str = attrs.field(default="connected")
        subtitle: str = attrs.field(default="Please connect to a SonicAmp system")
        firmware_info: str = attrs.field(default="")
        tabs: Tuple[Tabable] = attrs.field(factory=tuple)

    @abc.abstractmethod
    def on_connect(self, event: Any = None) -> None:
        ...


class Flashable(abc.ABC):
    @abc.abstractmethod
    def on_validation(self) -> None:
        ...

    @abc.abstractmethod
    def on_validation_success(self) -> None:
        ...

    @abc.abstractmethod
    def on_firmware_upload(self) -> None:
        ...


class Scriptable(abc.ABC):
    @abc.abstractmethod
    def on_script_start(self, event: Any = None) -> None:
        ...

    @abc.abstractmethod
    def on_script_stop(self, event: Any = None) -> None:
        ...


class Resizable(abc.ABC):
    @abc.abstractmethod
    def on_resizing(self, event: Any = None) -> None:
        ...

    @property
    @abc.abstractmethod
    def layouts(self) -> Iterable[Layout]:
        ...


class RootStringVar(ttk.StringVar):
    def __init__(
        self,
        master: Any = None,
        value: str | None = None,
        name: str | None = None,
    ) -> None:
        super().__init__(master, value, name)
        self.master = master
        self.dot_position: int = 0
        self.dot_text: str = "   "
        self.is_dot_animation_running: bool = False
        self.original_text: str = self.get()

    def animate_dots(self, text: str = "") -> None:
        self.is_dot_animation_running = True
        self.dot_animator(text=text)

    def stop_animation_of_dots(self) -> None:
        self.is_dot_animation_running = False

    def dot_animator(self, text: Optional[str] = None) -> None:
        if not self.is_dot_animation_running:
            return
        if text is not None:
            self.original_text = text
        if self.dot_position > 3:
            self.dot_position = 0

        self.dot_text = "." * self.dot_position + " " * (3 - self.dot_position)
        self.dot_text = f"{self.original_text}{self.dot_text}"

        self.set(self.dot_text)
        self.dot_position += 1
        self.master.after(500, self.dot_animator)

