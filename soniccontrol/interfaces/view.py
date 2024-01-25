from typing import Protocol

import ttkbootstrap as ttk

from soniccontrol.interfaces.layouts import Layout

# TODO: Maybe use inheritance versus Protocol so that typechecking is really working
# TODO: Set on a rule that a TabView must be a ttk.Frame


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
