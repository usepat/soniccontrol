import ttkbootstrap as ttk


class Entry(ttk.Entry):
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

    def _on_focus_in(self, _: ttk.tk.Event) -> None:
        if self.get() == self._placeholder:
            self.delete(0, ttk.END)

    def _on_focus_out(self, _: ttk.tk.Event) -> None:
        if not self.get() and not self.get().isnumeric():
            self.insert(0, self._placeholder)
