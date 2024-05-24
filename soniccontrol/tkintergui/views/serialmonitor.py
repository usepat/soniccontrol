import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame

from soniccontrol.interfaces.view import TabView
from soniccontrol.tkintergui.utils.constants import sizes, style, ui_labels
from soniccontrol.tkintergui.utils.image_loader import ImageLoader
from soniccontrol.utils.files import images


class SerialMonitorView(TabView):
    def __init__(self, master: ttk.Window, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)

    @property
    def image(self) -> ttk.ImageTk.PhotoImage:
        return ImageLoader.load_image(images.CONSOLE_ICON_BLACK, sizes.TAB_ICON_SIZE)

    @property
    def tab_title(self) -> str:
        return ui_labels.SERIAL_MONITOR_LABEL

    def _initialize_children(self) -> None:
        self._main_frame: ttk.Frame = ttk.Frame(self)
        self._output_frame: ttk.Labelframe = ttk.Labelframe(
            self._main_frame, text=ui_labels.OUTPUT_LABEL
        )
        self._scrolled_frame: ScrolledFrame = ScrolledFrame(
            self._output_frame, autohide=True
        )
        INPUT_FRAME_PADDING = (3, 1, 3, 4)
        self._input_frame: ttk.Labelframe = ttk.Labelframe(
            self._main_frame, text=ui_labels.INPUT_LABEL, padding=INPUT_FRAME_PADDING
        )
        self._read_button: ttk.Checkbutton = ttk.Checkbutton(
            self._input_frame,
            text=ui_labels.AUTO_READ_LABEL,
            style=style.DARK_SQUARE_TOGGLE,
        )
        self._command_field: ttk.Entry = ttk.Entry(self._input_frame, style=ttk.DARK)
        self._send_button: ttk.Button = ttk.Button(
            self._input_frame,
            text=ui_labels.SEND_LABEL,
            style=ttk.SUCCESS,
            image=ImageLoader.load_image(
                images.PLAY_ICON_WHITE, sizes.BUTTON_ICON_SIZE
            ),
            compound=ttk.RIGHT,
        )

    def _initialize_publish(self) -> None:
        self._main_frame.pack(expand=True, fill=ttk.BOTH)
        self._main_frame.columnconfigure(0, weight=sizes.EXPAND)
        self._main_frame.rowconfigure(0, weight=sizes.EXPAND)
        self._main_frame.rowconfigure(1, weight=sizes.DONT_EXPAND, minsize=40)
        self._output_frame.grid(
            row=0,
            column=0,
            sticky=ttk.NSEW,
            pady=sizes.MEDIUM_PADDING,
            padx=sizes.LARGE_PADDING,
        )
        self._scrolled_frame.pack(
            expand=True,
            fill=ttk.BOTH,
            pady=sizes.MEDIUM_PADDING,
            padx=sizes.MEDIUM_PADDING,
        )

        self._input_frame.grid(
            row=1,
            column=0,
            sticky=ttk.EW,
            pady=sizes.MEDIUM_PADDING,
            padx=sizes.LARGE_PADDING,
        )
        self._input_frame.columnconfigure(0, weight=1)
        self._input_frame.columnconfigure(1, weight=10)
        self._input_frame.columnconfigure(2, weight=3)
        self._read_button.grid(
            row=0,
            column=0,
            sticky=ttk.EW,
            padx=sizes.MEDIUM_PADDING,
            pady=sizes.MEDIUM_PADDING,
        )
        self._command_field.grid(
            row=0,
            column=1,
            sticky=ttk.EW,
            padx=sizes.MEDIUM_PADDING,
            pady=sizes.MEDIUM_PADDING,
        )
        self._send_button.grid(
            row=0,
            column=2,
            sticky=ttk.EW,
            padx=sizes.MEDIUM_PADDING,
            pady=sizes.MEDIUM_PADDING,
        )

    def set_small_width_layout(self) -> None:
        ...

    def set_large_width_layout(self) -> None:
        ...

    def publish(self) -> None:
        ...
