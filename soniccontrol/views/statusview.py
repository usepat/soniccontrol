import ttkbootstrap as ttk

from soniccontrol.interfaces.layouts import Layout


class StatusBarView(ttk.Frame):
    def __init__(self, master: ttk.Window, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)

    @property
    def layouts(self) -> set[Layout]:
        ...


class StatusView(ttk.Frame):
    def __init__(self, master: ttk.Window, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)

    @property
    def layouts(self) -> set[Layout]:
        ...
