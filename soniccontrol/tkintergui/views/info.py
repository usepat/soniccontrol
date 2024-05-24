from typing import Any

import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame

from soniccontrol import __version__
from soniccontrol.interfaces.view import TabView
from soniccontrol.tkintergui.utils.constants import fonts, sizes, ui_labels
from soniccontrol.tkintergui.utils.image_loader import ImageLoader
from soniccontrol.utils.files import images


class HelpFrame(ttk.Frame):
    def __init__(
        self,
        master: ttk.tk.Widget,
        heading: str,
        image: ttk.ImageTk.PhotoImage | None,
        content: list[str | ttk.ImageTk.PhotoImage | dict[str, Any]],
        paragraph_padding: int = sizes.MEDIUM_PADDING,
        wraplength: int = 0,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(master, *args, **kwargs)
        self._master: ttk.tk.Widget = master
        self._wraplength: int = wraplength
        self._paragraph_padding: int = paragraph_padding
        self.columnconfigure(0, weight=sizes.EXPAND)

        ttk.Label(
            self,
            text=heading,
            font=(
                fonts.QTYPE_OT_CONDLIGHT,
                fonts.SMALL_HEADING_SIZE,
            ),
            image=image if image is not None else "",
            compound=ttk.LEFT,
            anchor=ttk.CENTER,
            justify=ttk.CENTER,
        ).grid(row=0, column=0, sticky=ttk.W, pady=self._paragraph_padding)

        for index, parameters in enumerate(content):
            (
                ttk.Label(self, **parameters)
                if isinstance(parameters, dict)
                else ttk.Label(
                    self,
                    wraplength=self._wraplength,
                    text=parameters if isinstance(parameters, str) else "",
                    anchor=(
                        ttk.CENTER
                        if isinstance(parameters, ttk.ImageTk.PhotoImage)
                        else ttk.W
                    ),
                    justify=(
                        ttk.CENTER
                        if isinstance(parameters, ttk.ImageTk.PhotoImage)
                        else ttk.LEFT
                    ),
                    image=(
                        parameters
                        if isinstance(parameters, ttk.ImageTk.PhotoImage)
                        else ""
                    ),
                )
            ).grid(
                row=index + 1,
                column=0,
                sticky=ttk.EW,
                pady=self._paragraph_padding,
                padx=sizes.LARGE_PADDING,
            )

            self.rowconfigure(index + 1, weight=sizes.DONT_EXPAND)


class InfoView(TabView):
    def __init__(self, master: ttk.Window, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)

    @property
    def image(self) -> ttk.ImageTk.PhotoImage:
        return ImageLoader.load_image(images.INFO_ICON_BLACK, (25, 25))

    @property
    def tab_title(self) -> str:
        return ui_labels.INFO_LABEL

    def _initialize_children(self) -> None:
        self._main_frame: ttk.Frame = ttk.Frame(self)
        self._heading_frame: ttk.Frame = ttk.Frame(self._main_frame)

        self._heading_part_one: ttk.Label = ttk.Label(
            self._heading_frame,
            text=ui_labels.SONIC_LABEL,
            font=(fonts.QTYPE_OT_CONDLIGHT, fonts.HEADING_SIZE),
            justify=ttk.CENTER,
            anchor=ttk.CENTER,
        )
        self._heading_part_two: ttk.Label = ttk.Label(
            self._heading_frame,
            text=ui_labels.CONTROL_LABEL,
            font=(fonts.QTYPE_OT, fonts.HEADING_SIZE),
            justify=ttk.CENTER,
            anchor=ttk.CENTER,
        )

        self._scroll_frame: ScrolledFrame = ScrolledFrame(self._main_frame)
        self._body_frame: ttk.Frame = ttk.Frame(self._scroll_frame)

        font: tuple[str, int] = (
            fonts.QTYPE_OT_CONDLIGHT,
            fonts.TEXT_SIZE,
        )
        self._home_help_frame: HelpFrame = HelpFrame(
            self._body_frame,
            wraplength=400,
            heading=ui_labels.HOME_LABEL,
            image=ImageLoader.load_image(images.HOME_ICON_BLACK, sizes.TAB_ICON_SIZE),
            content=[
                ui_labels.HOME_HELP_INTRODUCTION,
                ImageLoader.load_image(images.HOME_CONTROL_PANEL, (300, 200)),
                ui_labels.HOME_HELP_CONTROL_PANEL,
                {
                    "text": ui_labels.FREQUENCY,
                    "font": font,
                },
                ui_labels.HOME_HELP_FREQUENCY,
                {
                    "text": ui_labels.GAIN,
                    "font": font,
                },
                ui_labels.HOME_HELP_GAIN,
                {
                    "text": ui_labels.CATCH_MODE_LABEL,
                    "font": font,
                },
                ui_labels.HOME_HELP_CATCH,
                {
                    "text": ui_labels.WIPE_MODE_LABEL,
                    "font": font,
                },
                ui_labels.HOME_HELP_WIPE,
                ui_labels.HOME_HELP_SET_VALUES,
                ui_labels.HOME_HELP_OUTPUT,
                ImageLoader.load_image(images.HOME_SIGNAL_CONTROL_PANEL, (400, 35)),
                ui_labels.HOME_HELP_SIGNAL_CONTROL_PANEL,
                {
                    "text": ui_labels.SIGNAL_ON,
                    "font": font,
                },
                ui_labels.HOME_HELP_ON,
                {
                    "text": ui_labels.SIGNAL_OFF,
                    "font": font,
                },
                ui_labels.HOME_HELP_OFF,
                {
                    "text": ui_labels.AUTO_LABEL,
                    "font": font,
                },
                ui_labels.HOME_HELP_AUTO,
            ],
        )

        self._footer_frame: ttk.Frame = ttk.Frame(self._main_frame)
        self._company_name: ttk.Label = ttk.Label(
            self._footer_frame, text=ui_labels.COMPANY_NAME, anchor=ttk.CENTER
        )
        self._version: ttk.Label = ttk.Label(
            self._footer_frame,
            text=f"{ui_labels.VERSION_LABEL}: {__version__}",
            anchor=ttk.CENTER,
        )

    def _initialize_publish(self) -> None:
        self._main_frame.pack(expand=True, fill=ttk.BOTH)
        self._main_frame.columnconfigure(0, weight=sizes.EXPAND)
        self._main_frame.rowconfigure(0, weight=sizes.DONT_EXPAND, minsize=40)
        self._main_frame.rowconfigure(1, weight=sizes.EXPAND)
        self._main_frame.rowconfigure(2, weight=sizes.DONT_EXPAND, minsize=15)
        self._heading_frame.grid(row=0, column=0, sticky=ttk.EW)
        self._scroll_frame.grid(row=1, column=0, sticky=ttk.NSEW)
        self._footer_frame.grid(row=2, column=0, sticky=ttk.EW)

        self._heading_frame.columnconfigure(0, weight=sizes.EXPAND)
        self._heading_frame.columnconfigure(1, weight=sizes.EXPAND)
        self._heading_frame.rowconfigure(0, weight=sizes.EXPAND)
        self._heading_part_one.grid(row=0, column=0, sticky=ttk.E)
        self._heading_part_two.grid(row=0, column=1, sticky=ttk.W)

        self._scroll_frame.columnconfigure(0, weight=sizes.EXPAND)
        self._scroll_frame.rowconfigure(0, weight=sizes.EXPAND)
        self._body_frame.grid(row=0, column=0, sticky=ttk.NS)
        self._home_help_frame.grid(row=0, column=0, sticky=ttk.NSEW)

        self._footer_frame.columnconfigure(0, weight=sizes.EXPAND)
        self._footer_frame.columnconfigure(1, weight=sizes.EXPAND)
        self._footer_frame.rowconfigure(0, weight=sizes.EXPAND)
        self._company_name.grid(row=0, column=0, sticky=ttk.NSEW)
        self._version.grid(row=0, column=1, sticky=ttk.NSEW)

    def set_small_width_layout(self) -> None:
        ...

    def set_large_width_layout(self) -> None:
        ...

    def publish(self) -> None:
        ...
