import pathlib
from typing import Any, TypedDict

import attrs
import soniccontrol.utils.constants as constants
import ttkbootstrap as ttk
from soniccontrol.interfaces.layouts import Layout
from soniccontrol.interfaces.view import TabView
from ttkbootstrap.scrolled import ScrolledFrame

from soniccontrol import __version__, utils


@attrs.define(slots=True)
class LableParameters:
    text: str = attrs.field()
    image: ttk.ImageTk.PhotoImage | None = attrs.field(default=None)
    font: tuple[str, int] | None = attrs.field(default=None)
    row: int | None = attrs.field(default=None)
    column: int | None = attrs.field(default=None)
    compound: str | None = attrs.field(default=ttk.LEFT)
    anchor: str | None = attrs.field(default=ttk.CENTER)
    justify: str | None = attrs.field(default=ttk.CENTER)
    sticky: str | None = attrs.field(default=None)
    pady: int | None = attrs.field(default=None)
    padx: int | None = attrs.field(default=None)
    columnspan: int | None = attrs.field(default=None)
    _init_keys: list[str] = ["text", "image", "justify", "anchor", "font", "compound"]
    _layout_keys: list[str] = ["row", "column", "columnspan", "sticky", "pady", "padx"]

    def initialize_parameters(self) -> dict[str, Any]:
        return {
            key: getattr(self, key)
            for key in self._init_keys
            if getattr(self, key) is not None
        }

    def layout_parameters(self) -> dict[str, Any]:
        return {
            key: getattr(self, key)
            for key in self._layout_keys
            if getattr(self, key) is not None
        }


class HelpFrame(ttk.Frame):
    def __init__(
        self,
        master: ttk.tk.Widget,
        content: list[LableParameters],
        wraplength: int = 0,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(master, *args, **kwargs)
        self.columnconfigure(0, weight=constants.misc.EXPAND)
        for index, parameters in enumerate(content):
            if None in (parameters.row, parameters.column):
                parameters.row = index
                parameters.column = 0
                self.rowconfigure(index, weight=constants.misc.DONT_EXPAND)
            ttk.Label(
                self, wraplength=wraplength, **parameters.initialize_parameters()
            ).grid(**parameters.layout_parameters())


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

        self._scroll_frame: ScrolledFrame = ScrolledFrame(self._main_frame)
        self._body_frame: ttk.Frame = ttk.Frame(self._scroll_frame)

        self._home_help_frame: HelpFrame = HelpFrame(
            self._body_frame,
            wraplength=300,
            content=[
                LableParameters(
                    text=constants.ui.HOME_LABEL,
                    font=(
                        constants.fonts.QTYPE_OT_CONDLIGHT,
                        constants.fonts.SMALL_HEADING_SIZE,
                    ),
                    image=utils.ImageLoader.load_image(
                        constants.images.HOME_ICON_BLACK, constants.misc.TAB_ICON_SIZE
                    ),
                    sticky=ttk.W,
                ),
                LableParameters(
                    text=constants.ui.HOME_HELP_INTRODUCTION,
                    justify=ttk.LEFT,
                    sticky=ttk.EW,
                    anchor=ttk.W,
                    padx=constants.misc.LARGE_PADDING,
                ),
                LableParameters(
                    text=constants.ui.HOME_HELP_CONTROL_PANEL,
                    justify=ttk.LEFT,
                    sticky=ttk.EW,
                    anchor=ttk.W,
                    padx=constants.misc.LARGE_PADDING,
                ),
                LableParameters(
                    text=constants.ui.HOME_HELP_FREQUENCY,
                    justify=ttk.LEFT,
                    sticky=ttk.EW,
                    anchor=ttk.W,
                    padx=constants.misc.LARGE_PADDING,
                ),
                LableParameters(
                    text=constants.ui.HOME_HELP_GAIN,
                    justify=ttk.LEFT,
                    sticky=ttk.EW,
                    anchor=ttk.W,
                    padx=constants.misc.LARGE_PADDING,
                ),
                LableParameters(
                    text=constants.ui.HOME_HELP_CATCH,
                    justify=ttk.LEFT,
                    sticky=ttk.EW,
                    anchor=ttk.W,
                    padx=constants.misc.LARGE_PADDING,
                ),
                LableParameters(
                    text=constants.ui.HOME_HELP_WIPE,
                    justify=ttk.LEFT,
                    anchor=ttk.W,
                    sticky=ttk.EW,
                    padx=constants.misc.LARGE_PADDING,
                ),
                LableParameters(
                    text=constants.ui.HOME_HELP_SET_VALUES,
                    justify=ttk.LEFT,
                    anchor=ttk.W,
                    sticky=ttk.EW,
                    padx=constants.misc.LARGE_PADDING,
                ),
                LableParameters(
                    text=constants.ui.HOME_HELP_OUTPUT,
                    justify=ttk.LEFT,
                    anchor=ttk.W,
                    sticky=ttk.EW,
                    padx=constants.misc.LARGE_PADDING,
                ),
                LableParameters(
                    text=constants.ui.HOME_HELP_SIGNAL_CONTROL_PANEL,
                    justify=ttk.LEFT,
                    anchor=ttk.W,
                    sticky=ttk.EW,
                    padx=constants.misc.LARGE_PADDING,
                ),
                LableParameters(
                    text=constants.ui.HOME_HELP_ON,
                    justify=ttk.LEFT,
                    anchor=ttk.W,
                    sticky=ttk.EW,
                    padx=constants.misc.LARGE_PADDING,
                ),
                LableParameters(
                    text=constants.ui.HOME_HELP_OFF,
                    justify=ttk.LEFT,
                    anchor=ttk.W,
                    sticky=ttk.EW,
                    padx=constants.misc.LARGE_PADDING,
                ),
                LableParameters(
                    text=constants.ui.HOME_HELP_AUTO,
                    justify=ttk.LEFT,
                    anchor=ttk.W,
                    sticky=ttk.EW,
                    padx=constants.misc.LARGE_PADDING,
                ),
            ],
        )

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
        self._scroll_frame.grid(row=1, column=0, sticky=ttk.NSEW)
        self._footer_frame.grid(row=2, column=0, sticky=ttk.EW)

        self._heading_frame.columnconfigure(0, weight=constants.misc.EXPAND)
        self._heading_frame.columnconfigure(1, weight=constants.misc.EXPAND)
        self._heading_frame.rowconfigure(0, weight=constants.misc.EXPAND)
        self._heading_part_one.grid(row=0, column=0, sticky=ttk.E)
        self._heading_part_two.grid(row=0, column=1, sticky=ttk.W)

        self._scroll_frame.columnconfigure(0, weight=constants.misc.EXPAND)
        self._scroll_frame.rowconfigure(0, weight=constants.misc.EXPAND)
        self._body_frame.grid(row=0, column=0, sticky=ttk.NS)
        self._home_help_frame.grid(row=0, column=0, sticky=ttk.NSEW)

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
