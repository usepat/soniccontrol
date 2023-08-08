import logging
from typing import Iterable, Any
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledText, ScrolledFrame
from ttkbootstrap.tableview import Tableview, TableRow, TableColumn
import ttkbootstrap.constants as ttkconst
import PIL
from PIL.ImageTk import PhotoImage
import soniccontrol.constants as const
from soniccontrol.interfaces import Layout, RootChild, Connectable, Scriptable
from soniccontrol.interfaces.rootchild import RootChildFrame

logger = logging.getLogger(__name__)


class ScriptingFrame(RootChildFrame, Connectable, Scriptable):
    def __init__(
        self, parent_frame: ttk.Frame, tab_title: str, image: PIL.Image, *args, **kwargs
    ):
        super().__init__(parent_frame, tab_title, image, *args, **kwargs)
        #     self._width_layouts: Iterable[Layout] = ()
        #     self._height_layouts: Iterable[Layout] = ()
        self.current_task: ttk.StringVar = ttk.StringVar(value="Idle")
        self.top_frame: ScrolledFrame = ScrolledFrame(self, autohide=True)
        self.button_frame: ttk.Frame = ttk.Frame(self)

        self.start_image: PhotoImage = const.Images.get_image(
            const.Images.PLAY_IMG_WHITE, const.Images.BUTTON_ICON_SIZE
        )
        self.menue_image: PhotoImage = const.Images.get_image(
            const.Images.MENUE_IMG_WHITE, const.Images.BUTTON_ICON_SIZE
        )
        self.info_image: PhotoImage = const.Images.get_image(
            const.Images.INFO_IMG_WHITE, const.Images.BUTTON_ICON_SIZE
        )
        self.start_script_btn = ttk.Button(
            self.button_frame,
            text="Run",
            style=ttk.SUCCESS,
            image=self.start_image,
            compound=ttk.LEFT,
            command=lambda event: self.event_generate(const.Events.START_SCRIPT),
        )
        self.script_guide_btn = ttk.Button(
            self.button_frame,
            text="Function Helper",
            style=ttk.INFO,
            image=self.info_image,
            compound=ttk.LEFT,
            command=self.open_help,
        )

        self.menue: ttk.Menu = ttk.Menu(self.button_frame)
        self.menue_button: ttk.Menubutton = ttk.Menubutton(
            self.button_frame, image=self.menue_image, menu=self.menue, bootstyle="dark"
        )
        self.menue.add_command(label="Save Script", command=self.save_file)
        self.menue.add_command(label="Load Script", command=self.load_file)
        self.menue.add_command(label="Specify Log file path", command=self.open_logfile)

        self.scripting_frame: ttk.Labelframe = ttk.Labelframe(
            self.top_frame,
            text="Script Editor",
            padding=(5, 5, 5, 5),
        )
        self.scripttext: ttk.Text = ScrolledText(
            self.scripting_frame,
            autohide=True,
            height=30,
            width=50,
            font=("QType Square Light", 12),
        )
        self.script_status_frame: ttk.Frame = ttk.Frame(self)
        self.cur_task_label: ttk.Label = ttk.Label(
            self.script_status_frame,
            justify=ttk.CENTER,
            anchor=ttk.CENTER,
            bootstyle=ttk.DARK,
            textvariable=self.current_task,
        )
        self.sequence_status: ttk.Progressbar = ttk.Progressbar(
            self.script_status_frame,
            length=160,
            mode="indeterminate",
            orient=ttk.HORIZONTAL,
            bootstyle=ttk.DARK,
        )
        self.bind_events()

    def on_connect(self, event=None) -> None:
        return self.publish()

    def on_script_start(self, event=None) -> None:
        pass

    def on_script_stop(self, event=None) -> None:
        pass

    def load_file(self) -> None:
        script_filepath: str = ttk.filedialog.askopenfilename(
            defaultextension=".txt", filetypes=self._filetypes
        )

        with open(script_filepath, "r") as f:
            self.scripttext.delete(1.0, ttk.END)
            self.scripttext.insert(ttk.INSERT, f.read())

    def save_file(self) -> None:
        self.save_filename = ttk.filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=self._filetypes
        )

        with open(self.save_filename, "w") as f:
            f.write(self.scripttext.get(1.0, ttk.END))

    def open_logfile(self) -> None:
        self.logfile = ttk.filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=self._filetypes
        )
        logger.debug(f"The new logfile path is: {self.logfile}")

    def open_help(self) -> None:
        ScriptGuide(self, self.scripttext)

    def set_horizontal_button_layout(self) -> None:
        for child in self.button_frame.children.values():
            child.pack_forget()
        self.start_script_btn.pack(side=ttk.LEFT, padx=5, pady=3)
        self.script_guide_btn.pack(side=ttk.LEFT, padx=5, pady=3)
        self.menue_button.pack(side=ttk.RIGHT, padx=5, pady=3)

    def publish(self):
        self.button_frame.pack(anchor=ttk.N, padx=15, pady=5, fill=ttk.X)
        self.top_frame.pack(expand=True, fill=ttk.BOTH)
        self.set_horizontal_button_layout()

        self.scripting_frame.pack(padx=20, pady=5, fill=ttk.BOTH, expand=True)
        self.scripttext.pack(fill=ttk.BOTH, expand=True)

        self.script_status_frame.pack(side=ttk.BOTTOM, fill=ttk.X)
        self.cur_task_label.pack(fill=ttk.X, padx=5, pady=3, side=ttk.LEFT)
        self.sequence_status.pack(fill=ttk.X, padx=5, pady=3, side=ttk.RIGHT)


class ScriptGuide(ttk.Toplevel):
    def __init__(self, parent, scripttext, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self.scripttext: ttk.ScrolledText = scripttext
        column_data: Iterable[Any] = (
            (
                "frequency",
                "frequency: int",
                "Set the frequency of the device",
                "frequency 1000000",
            ),
            ("gain", "gain: int", "Set the Gain of the device", "gain 100"),
            (
                "hold",
                "hold: int,\nunit: 'ms' or 's'",
                "Hold the state of the device\nfor a certain amount of time",
                "hold 10s",
            ),
            (
                "ramp_freq",
                "start: int,\nstop: int,\nstep: int,\non_signal_hold: int,\nunit: 'ms' or 's',\noff_signal_hold: int,\nunit: 'ms' or 's'",
                "Ramp up the frequency from\none point to another",
                "ramp_freq 1000000 2000000 1000 100ms 100ms",
            ),
        )
        self.scrolled_frame: ScrolledFrame = ScrolledFrame(self)
        self.scrolled_frame.pack(expand=True, fill=ttk.BOTH)
        for data in column_data:
            label: ttk.Labelframe = ttk.Labelframe(self.scrolled_frame, text=data[2])

            def insert_text(event: Any = None, data_for_script=data) -> None:
                logger.debug("inserting text...")
                self.scripttext.insert(
                    self.scripttext.index(ttk.INSERT), f"{data_for_script[3]}\n"
                )

            def unmark_label(event: Any = None, lbl: ttk.Label = label) -> None:
                lbl.configure(bootstyle=ttk.DEFAULT)
                for child in lbl.children.values():
                    child.configure(bootstyle=ttk.DEFAULT)

            def mark_label(event: Any = None, lbl: ttk.Label = label) -> None:
                lbl.configure(bootstyle=ttk.PRIMARY)
                for child in lbl.children.values():
                    child.configure(bootstyle=ttk.PRIMARY)

            label.pack(expand=True, fill=ttk.X, padx=25, pady=15)
            ttk.Label(
                label,
                font=("QType CondBook", 20),
                text=data[0],
            ).pack(expand=True, fill=ttk.X, padx=10, pady=5)

            ttk.Label(label, text=f"Arguments:", font=("Arial", 15, "bold")).pack(
                expand=True, fill=ttk.X, pady=0, padx=10
            )
            ttk.Label(label, text=f"{data[1]}").pack(
                expand=True, fill=ttk.X, padx=10, pady=0
            )

            ttk.Label(label, text=f"Example:", font=("Arial", 15, "bold")).pack(
                expand=True, fill=ttk.X, pady=0, padx=10
            )
            ttk.Label(label, text=f"Example:\n{data[3]}").pack(
                expand=True, fill=ttk.X, pady=0, padx=10
            )

            label.bind("<Button-1>", insert_text)
            for child in label.children.values():
                child.bind("<Button-1>", insert_text)
            label.bind("<Enter>", mark_label)
            label.bind("<Leave>", unmark_label)

    def insert_text(self) -> None:
        print("lol")


class ScriptingGuideCard(ttk.Labelframe):
    def __init__(self, *args, **kwargs) -> None:
        self.keyword_label: ttk.Label = ttk.Label(
            self,
            font=("QType CondBook", 20),
            text=self.data["keyword"],
        )

        self.description_frame: ttk.Frame = ttk.Frame(self)
        self.description_title: ttk.Label = ttk.Label(
            self.description_frame, text=f"Description:", font=("Arial", 13, "bold")
        )
        self.description_label: ttk.Label = ttk.Label(
            self.description_frame, text=self.data["Description"]
        )

        self.arguments_frame: ttk.Frame = ttk.Frame(self)
        self.arguments_title: ttk.Label = ttk.Label(
            self.arguments_frame, text=f"Arguments:", font=("Arial", 13, "bold")
        )
        self.arguments_label: ttk.Label = ttk.Label(
            self.arguments_frame, text=self.data["arguments"]
        )

        self.example_frame: ttk.Frame = ttk.Frame(self)
        self.example_title: ttk.Label = ttk.Label(
            self.example_frame, text=f"Example:", font=("Arial", 13, "bold")
        )
        self.example_label: ttk.Label = ttk.Label(
            self.example_frame, text=self.data["example"]
        )

        self.bind_deep(self, "<Button-1>", self.insert_text)
        self.bind_deep(self, "<Enter>", self.mark)
        self.bind_deep(self, "<Leave>", self.unmark)

    @staticmethod
    def bind_deep(widget, event, handler) -> None:
        widget.bind(event, handler)
        for child in widget.winfo_children():
            ScriptGuide.bind_deep(child, event, handler)

    def unmark(self) -> None:
        self.configure(bootstyle=ttk.DEFAULT)
        for child in self.winfo_children():
            self.configure(bootstyle=ttk.DEFAULT)

    def mark(self) -> None:
        pass

    def insert_text(self) -> None:
        pass
