import ttkbootstrap as ttk
from numpy import delete

from soniccontrol.interfaces.tkintertypes import Event


class Spinbox(ttk.Spinbox):
    def __init__(
        self, master: ttk.tk.Widget, placeholder: str = "", *args, **kwargs
    ) -> None:
        super().__init__(master, *args, **kwargs)
        self._placeholder: str = placeholder
        if self._placeholder and not self.get():
            self.delete(0, ttk.END)
            self.insert(0, self._placeholder)
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)

    @property
    def placeholder(self) -> str:
        return self._placeholder

    @placeholder.setter
    def placeholder(self, placeholder: str) -> None:
        self._placeholder = placeholder

    def configure(self, placeholder: str = "", *args, **kwargs) -> None:
        self._placeholder = placeholder
        super().configure(*args, **kwargs)

    def _on_focus_in(self, _: Event) -> None:
        if self.get() == self._placeholder:
            self.delete(0, ttk.END)

    def _on_focus_out(self, _: Event) -> None:
        if not self.get() and self.get() != 0:
            self.insert(0, self._placeholder)
