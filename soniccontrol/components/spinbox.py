from typing import Any, Callable

import ttkbootstrap as ttk
from soniccontrol.interfaces.tkintertypes import Event
from ttkbootstrap.scrolled import ScrolledFrame


class Spinbox(ttk.Spinbox):
    def __init__(
        self,
        master: ttk.tk.Widget,
        placeholder: str = "",
        scrolled_frame: ScrolledFrame | None = None,
        from_: int = 0,
        *args,
        **kwargs
    ) -> None:
        super().__init__(master, *args, **kwargs)

        self._from: int = from_

        self._placeholder: str = placeholder
        if self._placeholder and not self.get():
            self.delete(0, ttk.END)
            self.insert(0, self._placeholder)
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)

        self._scrolled_frame: ScrolledFrame | None = scrolled_frame
        if self._scrolled_frame is not None:
            self.bind("<Enter>", lambda _: self._scrolled_frame.disable_scrolling())
            self.bind("<Leave>", lambda _: self._scrolled_frame.enable_scrolling())

    @property
    def placeholder(self) -> str:
        return self._placeholder

    @placeholder.setter
    def placeholder(self, placeholder: str) -> None:
        self._placeholder = placeholder

    def _on_focus_in(self, _: Event) -> None:
        if self.get() == self._placeholder:
            self.delete(0, ttk.END)

    def _on_focus_out(self, _: Event) -> None:
        if (
            not self.get()
            or self.get() != self._placeholder
            or int(self.get()) <= self._from
        ):
            self.activate_placeholder()

    def activate_placeholder(self) -> None:
        self.delete(0, ttk.END)
        self.insert(0, self._placeholder)
