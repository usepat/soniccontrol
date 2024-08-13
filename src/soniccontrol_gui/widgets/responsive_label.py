import ttkbootstrap as ttk

from soniccontrol_gui.constants import events


class ResponsiveLabel(ttk.Label):
    def __init__(
        self,
        master: ttk.ttk.Widget,
        wraplength: int = 300,
        parent_reference: ttk.ttk.Widget | None = None,
        *args,
        **kwargs
    ) -> None:
        super().__init__(master, wraplength=wraplength, *args, **kwargs)
        self._parent_reference: ttk.ttk.Widget | None = parent_reference
        if self._parent_reference is None:
            return

        self.bind(events.RESIZING_EVENT, self.adapt, add=True)
        self._parent_reference.bind(events.RESIZING_EVENT, self.grow_bigger, add=True)
        self._old_width: int = self.winfo_vrootwidth()
        self._wraplength: int = wraplength

    def adapt(self, event: ttk.tk.Event) -> None:
        self._wraplength = event.width
        self.configure(wraplength=self._wraplength)

    def grow_bigger(self, event: ttk.tk.Event) -> None:
        if self.winfo_width() > event.width * 0.7:
            return
        self._wraplength += 1
        self.configure(wraplength=self._wraplength)
