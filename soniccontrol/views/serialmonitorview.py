import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame

import soniccontrol.utils.constants as const
from soniccontrol import utils
from soniccontrol.interfaces.layouts import Layout


class SerialMonitorView(ttk.Frame):
    def __init__(self, master: ttk.Window, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)
        self._master: ttk.Window = master
        self._image: ttk.ImageTk.PhotoImage = utils.give_image(
            const.images.CONSOLE_ICON_BLACK, (25, 25)
        )

        self._mainframe: ttk.Frame = ttk.Frame(self)
        self._output_frame: ttk.Labelframe = ttk.Labelframe(
            self._mainframe, text=const.ui.OUTPUT_LABEL
        )
        self._scrolled_frame: ScrolledFrame = ScrolledFrame(
            self._output_frame, autohide=True
        )
        self._input_frame: ttk.Frame = ttk.Frame(self._mainframe)
        self._read_button: ttk.Checkbutton = ttk.Checkbutton(
            self._input_frame, text=const.ui.AUTO_READ_LABEL, style="dark-square-toggle"
        )
        self._command_field: 

    @property
    def image(self) -> ttk.ImageTk.PhotoImage:
        return self._image

    @property
    def tab_title(self) -> str:
        return const.ui.SERIAL_MONITOR_LABEL

    @property
    def layouts(self) -> set[Layout]:
        ...

    def set_small_width_layout(self) -> None:
        ...

    def set_large_width_layout(self) -> None:
        ...

    def publish(self) -> None:
        ...
