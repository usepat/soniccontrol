import logging
from typing import Iterable
import ttkbootstrap as ttk
import PIL
from soniccontrol.interfaces import RootChild, Layout, WidthLayout
from soniccontrol import __version__

logger = logging.getLogger(__name__)


class InfoFrame(RootChild):
    INFOTEXT: str = (
        "Welcome to soniccontrol, a light-weight application to\n"
        "control  sonicamp  systems over  the serial interface.\n"
        'For   help,   click   the   "Manual"  button    below.\n'
        "\n"
        "(c) usePAT G.m.b.H\n"
    )
    INFOTEXT_SMALL: str = (
        "Welcome  to     soniccontrol,\n"
        "a light-weight application to\n"
        "control   sonicamp    systems\n"
        "over  the  serial  interface.\n"
        "For        help,        click\n"
        'the  "Manual"   button  below\n'
        "\n"
        "(c) usePAT G.m.b.H\n"
    )

    def __init__(
        self, parent_frame: ttk.Frame, tab_title: str, image: PIL.Image, *args, **kwargs
    ):
        super().__init__(parent_frame, tab_title, image, *args, **kwargs)
        self._width_layouts: Iterable[Layout] = (
            WidthLayout(
                min_width=450,
                command=self.set_large_info,
            ),
            WidthLayout(
                min_width=400,
                command=self.set_small_info,
            ),
            WidthLayout(min_width=300, command=self.set_large_width_heading),
            WidthLayout(min_width=100, command=self.set_small_width_heading),
        )
        #     self._height_layouts: Iterable[Layout] = ()
        self.heading_frame: ttk.Frame = ttk.Frame(self)

        self.soniccontrol_logo1: ttk.Label = ttk.Label(
            self.heading_frame,
            text="sonic",
            padding=(10, 0, 2, 10),
            font="QTypeOT-CondLight 30",
            borderwidth=-2,
        )

        self.soniccontrol_logo2: ttk.Label = ttk.Label(
            self.heading_frame,
            text="control",
            padding=(2, 0, 0, 10),
            font="QTypeOT-CondBook 30 bold",
            borderwidth=-2,
        )

        self.info_label: ttk.Label = ttk.Label(self, text=InfoFrame.INFOTEXT)
        self.controlframe: ttk.Frame = ttk.Frame(self)
        self.manual_btn: ttk.Button = ttk.Button(
            self.controlframe, text="Help Manual", command=self.open_manual
        )
        self.version_label: ttk.Label = ttk.Label(
            self,
            text=f"Version: {__version__}",
        )
        self.bind_events()
        self.publish()

    def set_small_width_heading(self, *args, **kwargs) -> None:
        for child in self.heading_frame.children.values():
            child.grid_forget()
        self.soniccontrol_logo1.pack(fill=ttk.X, anchor=ttk.CENTER)
        self.soniccontrol_logo2.pack(fill=ttk.X, anchor=ttk.CENTER)

    def set_large_width_heading(self, *args, **kwargs) -> None:
        for child in self.heading_frame.children.values():
            child.pack_forget()
        self.soniccontrol_logo1.grid(row=1, column=0, columnspan=1, sticky=ttk.E)
        self.soniccontrol_logo2.grid(row=1, column=1, columnspan=1, sticky=ttk.W)

    def set_small_info(self, *args, **kwargs) -> None:
        logger.debug("setting small info text")
        self.info_label["text"] = InfoFrame.INFOTEXT_SMALL

    def set_large_info(self, *args, **kwargs) -> None:
        self.info_label["text"] = InfoFrame.INFOTEXT

    @staticmethod
    def open_manual() -> None:
        pass

    def publish(self) -> None:
        self.soniccontrol_logo1.grid(row=0, column=0)
        self.soniccontrol_logo2.grid(row=0, column=1)
        self.heading_frame.pack(padx=20, pady=20)
        self.info_label.pack()
        self.controlframe.pack()
        self.manual_btn.pack()
        self.version_label.pack(anchor=ttk.S, side=ttk.BOTTOM, padx=10, pady=10)
