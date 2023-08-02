import logging
from typing import Iterable, List, Union
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame
import PIL
from soniccontrol.interfaces import RootChild, Layout, Connectable, Updatable
from soniccontrol.interfaces.rootchild import RootChildFrame

logger = logging.getLogger(__name__)


class SerialMonitorFrame(RootChildFrame, Connectable, Updatable):
    def __init__(
        self, parent_frame: ttk.Frame, tab_title: str, image: PIL.Image, *args, **kwargs
    ):
        super().__init__(parent_frame, tab_title, image, *args, **kwargs)
        # self._width_layouts: Iterable[Layout] = ()
        # self._height_layouts: Iterable[Layout] = ()
        self.command_history: List[str] = list()
        self.index_history: int = -1

        self.output_frame: ttk.Frame = ttk.LabelFrame(self, text='OUTPUT')

        self.scrolled_frame: ScrolledFrame = ScrolledFrame(self.output_frame)
        self.scrolled_frame.autohide_scrollbar()
        self.scrolled_frame.enable_scrolling()

        self.input_frame: ttk.LabelFrame = ttk.LabelFrame(self, text='INPUT')
        self.command_field: ttk.Entry = ttk.Entry(
            self.input_frame, style=ttk.DARK)

        self.command_field.bind('<Return>', self.send_command)
        self.command_field.bind('<Up>', self.history_up)
        self.command_field.bind('<Down>', self.history_down)

        self.send_button: ttk.Button = ttk.Button(
            self.input_frame,
            text='Send',
            command=self.send_command,
            style=ttk.SUCCESS,
        )

        self.publish()

    def publish(self) -> None:
        self.command_field.pack(anchor=ttk.S, padx=10,pady=10, fill=ttk.X, expand=True, side=ttk.LEFT)
        self.send_button.pack(anchor=ttk.S, padx=10, pady=10, side=ttk.RIGHT)
        self.scrolled_frame.pack(
            anchor=ttk.N, fill=ttk.BOTH, padx=10, pady=10, side=ttk.TOP)

        self.input_frame.pack(anchor=ttk.S, fill=ttk.X, side=ttk.BOTTOM, padx=5, pady=5)
        self.output_frame.pack(anchor=ttk.N,
                               fill=ttk.BOTH, pady=5, padx=5, side=ttk.TOP)
    
    def send_command(self, event) -> None:
        command: str = self.command_field.get()
        self.command_history.insert(0, command)

        self.insert_text(f">>> {command}")

        if not self.is_internal_command(command=command):
            self.insert_text(f"sending command... {command}\n")

        self.scrolled_frame.yview_moveto(1)
        self.command_field.delete(0, ttk.END)
    
    def is_internal_command(self, command: str) -> bool:
        if command == "clear":
            for child in self.scrolled_frame.winfo_children():
                child.destroy()
        elif command == "help":
            self.insert_text(self.HELPTEXT)
        else:
            return False
        return True
    
    def insert_text(self, text: Union[str, List[str]]) -> None:
        if text is list:
            text = " ".join(text)

        ttk.Label(self.scrolled_frame, text=text, font=("Consolas", 10)).pack(
            fill=ttk.X, side=ttk.TOP, anchor=ttk.W
        )
        self.scrolled_frame.update()

    def history_up(self, event) -> None:
        if not self.command_history or self.index_history >= len(self.command_history)-1:
            return
        self.index_history += 1
        self.command_field.delete(0, ttk.END)
        self.command_field.insert(0, self.command_history[self.index_history])

    def history_down(self, event) -> None:
        if self.index_history == -1:
            return
        self.index_history -= 1
        self.command_field.delete(0, ttk.END)
        if self.index_history != -1:
            self.command_field.insert(0, self.command_history[self.index_history])
    
    def on_connect(self, event=None) -> None:
        return self.publish()
    
    def on_update(self, event=None) -> None:
        pass
