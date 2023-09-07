from typing import Iterable, Optional
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame
from PIL.ImageTk import PhotoImage
from soniccontrol.core.interfaces import RootChild, WidthLayout, Root
from soniccontrol import __version__


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
        self,
        master: Root,
        tab_title: str = "About",
        image: Optional[PhotoImage] = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(master, tab_title, image=image, *args, **kwargs)
        self.set_layouts(
            [
                WidthLayout(min_size=450, command=self.set_large_info),
                WidthLayout(min_size=400, command=self.set_small_info),
                WidthLayout(min_size=300, command=self.set_large_width_heading),
                WidthLayout(min_size=100, command=self.set_small_width_heading),
            ]
        )

        self.main_frame: ScrolledFrame = ScrolledFrame(self)
        self.heading_frame: ttk.Frame = ttk.Frame(self.main_frame)

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

        self.info_label: ttk.Label = ttk.Label(self.main_frame, text=InfoFrame.INFOTEXT)
        self.controlframe: ttk.Frame = ttk.Frame(self.main_frame)
        self.manual_btn: ttk.Button = ttk.Button(
            self.controlframe, text="Help Manual", command=self.open_manual
        )
        self.version_label: ttk.Label = ttk.Label(
            self.main_frame,
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
        self.info_label["text"] = InfoFrame.INFOTEXT_SMALL

    def set_large_info(self, *args, **kwargs) -> None:
        self.info_label["text"] = InfoFrame.INFOTEXT

    @staticmethod
    def open_manual() -> None:
        pass

    def publish(self) -> None:
        self.main_frame.pack(expand=True, fill=ttk.BOTH)
        self.soniccontrol_logo1.grid(row=0, column=0)
        self.soniccontrol_logo2.grid(row=0, column=1)
        self.heading_frame.pack(padx=20, pady=20, expand=True)
        self.info_label.pack(expand=True)
        self.controlframe.pack(expand=True)
        self.manual_btn.pack()
        self.version_label.pack(anchor=ttk.S, side=ttk.BOTTOM, padx=10, pady=10)
