import abc

import ttkbootstrap as ttk


class View(ttk.Frame):
    def __init__(self, master: ttk.tk.Widget | ttk.Window, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)
        self._master: ttk.tk.Widget | ttk.Window = master
        self._initialize_children()
        self._initialize_publish()

    @property
    def parent(self) -> ttk.tk.Widget | ttk.Window:
        return self._master

    @abc.abstractmethod
    def _initialize_children(self) -> None:
        ...

    @abc.abstractmethod
    def _initialize_publish(self) -> None:
        ...


class TabView(View):
    def __init__(self, master: ttk.tk.Widget | ttk.Window, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)

    @property
    @abc.abstractmethod
    def tab_title(self) -> str:
        ...

    @property
    @abc.abstractmethod
    def image(self) -> ttk.ImageTk.PhotoImage:
        ...
