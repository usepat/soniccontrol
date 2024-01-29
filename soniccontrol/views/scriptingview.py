import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame, ScrolledText

from soniccontrol import utils
from soniccontrol.interfaces.layouts import Layout
from soniccontrol.utils import constants as const


class ScriptingView(ttk.Frame):
    def __init__(self, master: ttk.Window, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)
        self._master: ttk.Window = master

        self._navigation_button_frame: ttk.Frame = ttk.Frame(self)
        self._main_frame: ScrolledFrame = ScrolledFrame(self)
        self._start_button: ttk.Button = ttk.Button(
            self._navigation_button_frame,
            text=const.ui.START_LABEL,
            style=ttk.SUCCESS,
            image=utils.ImageLoader.load_image(const.images.PLAY_ICON_WHITE, (13, 13)),
            compound=ttk.LEFT,
        )
        self._scripting_guide_button: ttk.Button = ttk.Button(
            self._navigation_button_frame,
            text=const.ui.GUIDE_LABEL,
            style=ttk.INFO,
            image=utils.ImageLoader.load_image(const.images.INFO_ICON_WHITE, (13, 13)),
            compound=ttk.LEFT,
        )
        self._menue: ttk.Menu = ttk.Menu(self._navigation_button_frame)
        self._menue_button: ttk.Menubutton = ttk.Menubutton(
            self._navigation_button_frame,
            menu=self._menue,
            style=ttk.DARK,
            image=utils.ImageLoader.load_image(const.images.MENUE_ICON_WHITE, (13, 13)),
        )
        self._menue.add_command(label=const.ui.SAVE_LABEL)
        self._menue.add_command(label=const.ui.LOAD_LABEL)
        self._menue.add_command(label=const.ui.SPECIFY_PATH_LABEL)
        self._scripting_frame: ttk.Labelframe = ttk.Labelframe(
            self._main_frame, text=const.ui.SCRIPT_EDITOR_LABEL, padding=(6, 1, 6, 7)
        )
        self._scripting_text: ScrolledText = ScrolledText(
            self._scripting_frame, autohide=True
        )

        self._script_status_frame: ttk.Frame = ttk.Frame(self)
        self._current_task_label: ttk.Label = ttk.Label(
            self._script_status_frame, justify=ttk.CENTER, style=ttk.DARK
        )
        self._progressbar: ttk.Progressbar = ttk.Progressbar(
            self._script_status_frame,
            mode=ttk.INDETERMINATE,
            orient=ttk.HORIZONTAL,
            style=ttk.DARK,
        )
        self._init_publish()

    @property
    def image(self) -> ttk.ImageTk.PhotoImage:
        return utils.ImageLoader.load_image(const.images.SCRIPT_ICON_BLACK, (25, 25))

    @property
    def tab_title(self) -> str:
        return const.ui.SCRIPTING_LABEL

    @property
    def layouts(self) -> set[Layout]:
        ...

    def _init_publish(self) -> None:
        self._navigation_button_frame.pack(anchor=ttk.N, padx=15, pady=5, fill=ttk.X)
        self._start_button.pack(side=ttk.LEFT, padx=5, pady=5)
        self._scripting_guide_button.pack(side=ttk.LEFT, padx=5, pady=5)
        self._menue_button.pack(side=ttk.RIGHT, padx=5, pady=5)

        self._main_frame.pack(expand=True, fill=ttk.BOTH)
        self._scripting_frame.pack(expand=True, fill=ttk.BOTH, padx=20, pady=10)
        self._scripting_text.pack(expand=True, fill=ttk.BOTH)

        self._script_status_frame.columnconfigure(0, weight=3)
        self._script_status_frame.columnconfigure(1, weight=1)
        self._script_status_frame.pack(side=ttk.BOTTOM, fill=ttk.X, padx=20, pady=5)
        self._current_task_label.grid(row=0, column=0, columnspan=2, sticky=ttk.EW)
        self._progressbar.grid(row=0, column=1, sticky=ttk.EW)

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
