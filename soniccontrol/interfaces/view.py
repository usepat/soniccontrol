from typing import Protocol
import ttkbootstrap as ttk
from soniccontrol.interfaces.layouts import Layout


class View(Protocol):
    @property
    def layouts(self) -> set[Layout]:
        ...


class TabView(View, Protocol):
    @property
    def tab_title(self) -> str:
        ...

    @property
    def image(self) -> ttk.PhotoImage:
        ...
