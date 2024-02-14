import soniccontrol.utils.constants as const
import ttkbootstrap as ttk
from soniccontrol.interfaces.layouts import Layout
from ttkbootstrap.scrolled import ScrolledFrame

from soniccontrol import utils


class SerialMonitorView(ttk.Frame):
    def __init__(self, master: ttk.Window, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)
        self._master: ttk.Window = master

        self._main_frame: ttk.Frame = ttk.Frame(self)
        self._output_frame: ttk.Labelframe = ttk.Labelframe(
            self._main_frame, text=const.ui.OUTPUT_LABEL
        )
        self._scrolled_frame: ScrolledFrame = ScrolledFrame(
            self._output_frame, autohide=True
        )
        self._input_frame: ttk.Labelframe = ttk.Labelframe(
            self._main_frame, text=const.ui.INPUT_LABEL, padding=(3, 1, 3, 4)
        )
        self._read_button: ttk.Checkbutton = ttk.Checkbutton(
            self._input_frame, text=const.ui.AUTO_READ_LABEL, style="dark-square-toggle"
        )
        self._command_field: ttk.Entry = ttk.Entry(self._input_frame, style=ttk.DARK)
        self._send_button: ttk.Button = ttk.Button(
            self._input_frame,
            text=const.ui.SEND_LABEL,
            style=ttk.SUCCESS,
            image=utils.ImageLoader.load_image(const.images.PLAY_ICON_WHITE, (13, 13)),
            compound=ttk.RIGHT,
        )
        self._init_publish()

    @property
    def image(self) -> ttk.ImageTk.PhotoImage:
        return utils.ImageLoader.load_image(const.images.CONSOLE_ICON_BLACK, (25, 25))

    @property
    def tab_title(self) -> str:
        return const.ui.SERIAL_MONITOR_LABEL

    @property
    def layouts(self) -> set[Layout]:
        ...

    def _init_publish(self) -> None:
        self._main_frame.pack(expand=True, fill=ttk.BOTH)
        self._main_frame.columnconfigure(0, weight=1)
        self._main_frame.rowconfigure(0, weight=1)
        self._main_frame.rowconfigure(1, weight=0, minsize=40)
        self._output_frame.grid(row=0, column=0, sticky=ttk.NSEW, pady=5, padx=10)
        self._scrolled_frame.pack(expand=True, fill=ttk.BOTH, pady=5, padx=5)

        self._input_frame.grid(row=1, column=0, sticky=ttk.EW, pady=5, padx=10)
        self._input_frame.columnconfigure(0, weight=1)
        self._input_frame.columnconfigure(1, weight=10)
        self._input_frame.columnconfigure(2, weight=3)
        self._read_button.grid(row=0, column=0, sticky=ttk.EW, padx=5, pady=5)
        self._command_field.grid(row=0, column=1, sticky=ttk.EW, padx=5, pady=5)
        self._send_button.grid(row=0, column=2, sticky=ttk.EW, padx=5, pady=5)

    def set_small_width_layout(self) -> None:
        ...

    def set_large_width_layout(self) -> None:
        ...

    def publish(self) -> None:
        ...
