from typing import Any, Callable

import ttkbootstrap as ttk


class Card(ttk.Labelframe):
    def __init__(
        self,
        master: ttk.tk.Widget,
        heading: str,
        data: dict[str, str],
        command: Callable[..., Any] | None,
        *args,
        **kwargs,
    ):
        super().__init__(master, *args, **kwargs)
        self._master: ttk.tk.Widget = master
        self._heading: str = heading
        self._data: dict[str, str] = data
        self._command: Callable[..., Any] | None = command

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self._heading_label: ttk.Label = ttk.Label(
            self, font=("QTypeOT", 15), text=self._heading
        )
        self._heading_label.grid(row=0, column=0)

        self._data_frame: ttk.Frame = ttk.Frame(self)
        self._data_frame.grid(row=1, column=0)
        self._data_frame.columnconfigure(0, weight=1)

        for heading, text in self._data.items():
            ttk.Label(
                self._data_frame, font=("TkDefault", 12, "bold"), text=f"{heading}:"
            ).grid(row=self._data_frame.grid_size()[1], column=0)
            ttk.Label(self._data_frame, font=("TkDefault", 12, "bold"), text=text).grid(
                row=self._data_frame.grid_size()[1], column=0
            )

        self.bind_deep(self, "<Button-1>", self._command)
        self.bind_deep(self, "<Enter>", self.mark)
        self.bind_deep(self, "<Leave>", self.unmark)

    @staticmethod
    def bind_deep(widget: ttk.tk.Widget, event: str, func: Callable) -> None:
        widget.bind(event, func, "+")
        for child in widget.winfo_children():
            Card.bind_deep(child, event, func)

    @staticmethod
    def deep_mark(widget: ttk.tk.Widget) -> None:
        pass

    @staticmethod
    def unmark(widget: ttk.tk.Widget, event: str | None) -> None:
        pass

    def mark(self, event: str | None) -> None:
        pass

    def configure_command(self, command: Callable[..., Any]):
        self._command = command
