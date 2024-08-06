from typing import Any, Callable

import ttkbootstrap as ttk


class Card(ttk.Labelframe):
    def __init__(
        self,
        master: ttk.tk.Widget | ttk.tk.Misc,
        heading: str,
        data: dict[str, str],
        command: Callable[[Any], Any] | None,
        *args,
        **kwargs,
    ):
        super().__init__(master, *args, **kwargs)
        self._master: ttk.tk.Widget | ttk.tk.Misc = master
        self._heading: str = heading
        self._data: dict[str, str] = data
        self._command: Callable[[Any], Any] | None = command

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self._heading_label: ttk.Label = ttk.Label(
            self, font=("QTypeOT", 15), text=self._heading
        )
        self._heading_label.grid(row=0, column=0, sticky=ttk.EW, pady=5, padx=5)

        self._data_frame: ttk.Frame = ttk.Frame(self)
        self._data_frame.grid(row=1, column=0, pady=5, padx=5, sticky=ttk.NSEW)
        self._data_frame.columnconfigure(0, weight=1)

        for heading, text in self._data.items():
            ttk.Label(
                self._data_frame,
                font=("TkDefault", 12, "bold"),
                text=f"{heading}:",
                padding=(0, 3, 0, 0),
            ).grid(row=self._data_frame.grid_size()[1], column=0, sticky=ttk.EW)
            ttk.Label(
                self._data_frame,
                font=("TkDefault", 10),
                text=text,
                padding=(0, 0, 0, 3),
            ).grid(row=self._data_frame.grid_size()[1], column=0, sticky=ttk.EW)

        if self._command is not None:
            self.configure_command(self._command)
        self.mark_default()

    @staticmethod
    def bind_deep(
        widget: ttk.tk.Widget, event: str, func: Callable[[Any], Any]
    ) -> None:
        widget.bind(event, func, "+")
        for child in widget.winfo_children():
            Card.bind_deep(child, event, func)

    @staticmethod
    def mark_card(widget: ttk.tk.Widget, style: str) -> None:
        if isinstance(widget, (ttk.Label, ttk.LabelFrame)):
            widget.configure(bootstyle=style)
        for child in widget.winfo_children():
            Card.mark_card(child, style)

    def mark_hover(self, event: str | None = None) -> None:
        self.mark_card(self, "dark")

    def mark_clicked(self, event: str | None = None) -> None:
        self.mark_card(self, "info")

    def mark_default(self, event: str | None = None) -> None:
        self.mark_card(self, "secondary")

    def configure_command(self, command: Callable[..., Any]):
        self._command = command
        self.bind_deep(self, "<Enter>", self.mark_hover)
        self.bind_deep(self, "<Leave>", self.mark_default)
        self.bind_deep(self, "<Button-1>", self.mark_clicked)
        self.bind_deep(self, "<Button-1>", self._command)
        self.bind_deep(self, "<ButtonRelease-1>", self.mark_hover)
