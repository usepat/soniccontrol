import logging
from typing import Iterable
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledText, ScrolledFrame
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
        self.button_frame: ttk.Frame = ttk.Frame(self.top_frame)
        
        self.start_image: PhotoImage = const.Images.get_image(const.Images.PLAY_IMG_WHITE, const.Images.BUTTON_ICON_SIZE)
        self.menue_image: PhotoImage =const.Images.get_image(const.Images.MENUE_IMG_WHITE, const.Images.BUTTON_ICON_SIZE)
        self.info_image: PhotoImage = const.Images.get_image(const.Images.INFO_IMG_WHITE, const.Images.BUTTON_ICON_SIZE)
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
            self.button_frame,
            image=self.menue_image,
            menu=self.menue,
            bootstyle='dark'
        )
        self.menue.add_command(label='Save Script', command=self.save_file)
        self.menue.add_command(label='Load Script', command=self.load_file)
        self.menue.add_command(label='Specify Log file path', command=self.open_logfile)
        
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
            font=('QType Square Light', 12),
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
            bootstyle=ttk.DARK
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
        pass

    def set_horizontal_button_layout(self) -> None:
        for child in self.button_frame.children.values():
            child.pack_forget()
        self.start_script_btn.pack(side=ttk.LEFT, padx=5, pady=3)
        self.script_guide_btn.pack(side=ttk.LEFT, padx=5, pady=3)
        self.menue_button.pack(side=ttk.RIGHT, padx=5, pady=3)

    def publish(self):
        self.top_frame.pack(expand=True, fill=ttk.BOTH)
        # self.top_frame.place(relheight=1, relwidth=1, relx=0, rely=0)
        self.button_frame.pack(anchor=ttk.N, padx=15, pady=5, fill=ttk.X)
        self.set_horizontal_button_layout()
        
        self.scripting_frame.pack(padx=20, pady=5, fill=ttk.BOTH, expand=True)
        self.scripttext.pack(fill=ttk.BOTH, expand=True)
        
        self.script_status_frame.pack(side=ttk.BOTTOM, fill=ttk.X)
        self.cur_task_label.pack(fill=ttk.X, padx=5, pady=3, side=ttk.LEFT)
        self.sequence_status.pack(fill=ttk.X, padx=5, pady=3, side=ttk.RIGHT)