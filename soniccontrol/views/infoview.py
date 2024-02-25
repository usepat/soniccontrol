import soniccontrol.utils.constants as constants
import ttkbootstrap as ttk
from soniccontrol.interfaces.layouts import Layout
from soniccontrol.interfaces.view import TabView
from ttkbootstrap.scrolled import ScrolledFrame

from soniccontrol import __version__, utils


class InfoView(TabView):
    def __init__(self, master: ttk.Window, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)

    @property
    def image(self) -> ttk.ImageTk.PhotoImage:
        return utils.ImageLoader.load_image(constants.images.INFO_ICON_BLACK, (25, 25))

    @property
    def tab_title(self) -> str:
        return constants.ui.INFO_LABEL

    @property
    def layouts(self) -> set[Layout]:
        ...

    def _initialize_children(self) -> None:
        self._main_frame: ttk.Frame = ttk.Frame(self)
        self._heading_frame: ttk.Frame = ttk.Frame(self._main_frame)

        self._heading_part_one: ttk.Label = ttk.Label(
            self._heading_frame,
            text=constants.ui.SONIC_LABEL,
            font=(constants.fonts.QTYPE_OT_CONDLIGHT, constants.fonts.HEADING_SIZE),
            justify=ttk.CENTER,
            anchor=ttk.CENTER,
        )
        self._heading_part_two: ttk.Label = ttk.Label(
            self._heading_frame,
            text=constants.ui.CONTROL_LABEL,
            font=(constants.fonts.QTYPE_OT, constants.fonts.HEADING_SIZE),
            justify=ttk.CENTER,
            anchor=ttk.CENTER,
        )

        self._body_frame: ScrolledFrame = ScrolledFrame(self._main_frame)
        self._footer_frame: ttk.Frame = ttk.Frame(self._main_frame)
        self._company_name: ttk.Label = ttk.Label(
            self._footer_frame, text=constants.ui.COMPANY_NAME, anchor=ttk.CENTER
        )
        self._version: ttk.Label = ttk.Label(
            self._footer_frame,
            text=f"{constants.ui.VERSION_LABEL}: {__version__}",
            anchor=ttk.CENTER,
        )

    def _initialize_publish(self) -> None:
        self._main_frame.pack(expand=True, fill=ttk.BOTH)
        self._main_frame.columnconfigure(0, weight=constants.misc.EXPAND)
        self._main_frame.rowconfigure(0, weight=constants.misc.DONT_EXPAND, minsize=40)
        self._main_frame.rowconfigure(1, weight=constants.misc.EXPAND)
        self._main_frame.rowconfigure(2, weight=constants.misc.DONT_EXPAND, minsize=15)
        self._heading_frame.grid(row=0, column=0, sticky=ttk.EW)
        self._body_frame.grid(row=1, column=0, sticky=ttk.NSEW)
        self._footer_frame.grid(row=2, column=0, sticky=ttk.EW)

        self._heading_frame.columnconfigure(0, weight=constants.misc.EXPAND)
        self._heading_frame.columnconfigure(1, weight=constants.misc.EXPAND)
        self._heading_frame.rowconfigure(0, weight=constants.misc.EXPAND)
        self._heading_part_one.grid(row=0, column=0, sticky=ttk.E)
        self._heading_part_two.grid(row=0, column=1, sticky=ttk.W)

        self._footer_frame.columnconfigure(0, weight=constants.misc.EXPAND)
        self._footer_frame.columnconfigure(1, weight=constants.misc.EXPAND)
        self._footer_frame.rowconfigure(0, weight=constants.misc.EXPAND)
        self._company_name.grid(row=0, column=0, sticky=ttk.NSEW)
        self._version.grid(row=0, column=1, sticky=ttk.NSEW)

    def set_small_width_layout(self) -> None:
        ...

    def set_large_width_layout(self) -> None:
        ...

    def publish(self) -> None:
        ...
