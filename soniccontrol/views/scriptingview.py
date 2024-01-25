import ttkbootstrap as ttk

from soniccontrol import utils
from soniccontrol.interfaces.layouts import Layout
from soniccontrol.utils import constants as const


class ScriptingView(ttk.Frame):
    def __init__(self, master: ttk.Window, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)
        self._master: ttk.Window = master
        self._image: ttk.ImageTk.PhotoImage = utils.give_image(
            const.images.SCRIPT_ICON_BLACK, (25, 25)
        )

    @property
    def image(self) -> ttk.ImageTk.PhotoImage:
        return self._image

    @property
    def tab_title(self) -> str:
        return const.ui.SCRIPTING_LABEL

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
