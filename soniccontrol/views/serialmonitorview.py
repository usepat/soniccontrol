import soniccontrol.utils.constants as const
import ttkbootstrap as ttk
from soniccontrol.interfaces.layouts import Layout
from soniccontrol.interfaces.view import TabView
from ttkbootstrap.scrolled import ScrolledFrame

from soniccontrol import utils


class SerialMonitorView(TabView):
    def __init__(self, master: ttk.Window, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)

    @property
    def image(self) -> ttk.ImageTk.PhotoImage:
        return utils.ImageLoader.load_image(
            const.images.CONSOLE_ICON_BLACK, const.misc.TAB_ICON_SIZE
        )

    @property
    def tab_title(self) -> str:
        return const.ui.SERIAL_MONITOR_LABEL

    @property
    def layouts(self) -> set[Layout]:
        ...

    def _initialize_children(self) -> None:
        self._main_frame: ttk.Frame = ttk.Frame(self)
        self._output_frame: ttk.Labelframe = ttk.Labelframe(
            self._main_frame, text=const.ui.OUTPUT_LABEL
        )
        self._scrolled_frame: ScrolledFrame = ScrolledFrame(
            self._output_frame, autohide=True
        )
        INPUT_FRAME_PADDING = (3, 1, 3, 4)
        self._input_frame: ttk.Labelframe = ttk.Labelframe(
            self._main_frame, text=const.ui.INPUT_LABEL, padding=INPUT_FRAME_PADDING
        )
        self._read_button: ttk.Checkbutton = ttk.Checkbutton(
            self._input_frame,
            text=const.ui.AUTO_READ_LABEL,
            style=const.style.DARK_SQUARE_TOGGLE,
        )
        self._command_field: ttk.Entry = ttk.Entry(self._input_frame, style=ttk.DARK)
        self._send_button: ttk.Button = ttk.Button(
            self._input_frame,
            text=const.ui.SEND_LABEL,
            style=ttk.SUCCESS,
            image=utils.ImageLoader.load_image(
                const.images.PLAY_ICON_WHITE, const.misc.BUTTON_ICON_SIZE
            ),
            compound=ttk.RIGHT,
        )

    def _initialize_publish(self) -> None:
        self._main_frame.pack(expand=True, fill=ttk.BOTH)
        self._main_frame.columnconfigure(0, weight=const.misc.EXPAND)
        self._main_frame.rowconfigure(0, weight=const.misc.EXPAND)
        self._main_frame.rowconfigure(1, weight=const.misc.DONT_EXPAND, minsize=40)
        self._output_frame.grid(
            row=0,
            column=0,
            sticky=ttk.NSEW,
            pady=const.misc.MEDIUM_PADDING,
            padx=const.misc.LARGE_PADDING,
        )
        self._scrolled_frame.pack(
            expand=True,
            fill=ttk.BOTH,
            pady=const.misc.MEDIUM_PADDING,
            padx=const.misc.MEDIUM_PADDING,
        )

        self._input_frame.grid(
            row=1,
            column=0,
            sticky=ttk.EW,
            pady=const.misc.MEDIUM_PADDING,
            padx=const.misc.LARGE_PADDING,
        )
        self._input_frame.columnconfigure(0, weight=1)
        self._input_frame.columnconfigure(1, weight=10)
        self._input_frame.columnconfigure(2, weight=3)
        self._read_button.grid(
            row=0,
            column=0,
            sticky=ttk.EW,
            padx=const.misc.MEDIUM_PADDING,
            pady=const.misc.MEDIUM_PADDING,
        )
        self._command_field.grid(
            row=0,
            column=1,
            sticky=ttk.EW,
            padx=const.misc.MEDIUM_PADDING,
            pady=const.misc.MEDIUM_PADDING,
        )
        self._send_button.grid(
            row=0,
            column=2,
            sticky=ttk.EW,
            padx=const.misc.MEDIUM_PADDING,
            pady=const.misc.MEDIUM_PADDING,
        )

    def set_small_width_layout(self) -> None:
        ...

    def set_large_width_layout(self) -> None:
        ...

    def publish(self) -> None:
        ...
