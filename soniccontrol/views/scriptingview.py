import ttkbootstrap as ttk

from soniccontrol.interfaces.layouts import Layout


class ScriptingView(ttk.Frame):
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

    def set_small_width_layout(self) -> None:
        ...

    def set_large_width_layout(self) -> None:
        ...

    def publish(self) -> None:
        ...

    def on_script_start(self) -> None:
        ...

    def on_script_stop(self) -> None:
        ...

    def hightlight_line(self, line_idx: int) -> None:
        ...

    def load_script(self) -> None:
        ...

    def save_script(self) -> None:
        ...


class ScriptingGuide(ttk.Toplevel):
    def __init__(self, script_text: ttk.ScrolledText, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def insert_text(self, text: str) -> None:
        ...
