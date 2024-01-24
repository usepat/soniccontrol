import ttkbootstrap as ttk

from soniccontrol.interfaces.layouts import Layout


class SettingsView(ttk.Frame):
    def __init__(
        self, master: ttk.tk.Widget | ttk.tk.Misc | None, *args, **kwargs
    ) -> None:
        super().__init__(master, *args, **kwargs)

    @property
    def image(self) -> ttk.tk.PhotoImage:
        ...

    @property
    def tab_title(self) -> str:
        ...

    @property
    def layouts(self) -> set[Layout]:
        ...

    def publish(self) -> None:
        ...
