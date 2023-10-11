from typing import Optional, List, Union
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame
from async_tkinter_loop import async_handler
from PIL.ImageTk import PhotoImage
from soniccontrol.core.interfaces import RootChild, Connectable, Root
from soniccontrol.sonicpackage.sonicamp import Command


class SerialMonitorFrame(RootChild, Connectable):
    def __init__(
        self,
        master: Root,
        tab_title: str = "Serial Monitor",
        image: Optional[PhotoImage] = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(master, tab_title, image=image, *args, **kwargs)

        self.autoread: ttk.BooleanVar = ttk.BooleanVar(value=False)
        self.command_history: List[str] = list()
        self.index_history: int = -1

        self.mainframe: ttk.Frame = ttk.Frame(self)

        self.output_frame: ttk.Labelframe = ttk.LabelFrame(
            self.mainframe, text="OUTPUT"
        )
        self.scrolled_frame: ScrolledFrame = ScrolledFrame(self.output_frame)
        self.scrolled_frame.autohide_scrollbar()
        self.scrolled_frame.enable_scrolling()

        self.input_frame: ttk.LabelFrame = ttk.LabelFrame(
            self.mainframe, text="INPUT", padding=(5, 0, 5, 3)
        )
        self.read_button: ttk.Checkbutton = ttk.Checkbutton(
            self.input_frame,
            text="Autoread",
            variable=self.autoread,
            style="dark-square-toggle",
            command=self.read_engine,
        )
        self.command_field: ttk.Entry = ttk.Entry(self.input_frame, style=ttk.DARK)

        self.command_field.bind("<Return>", self.send_command)
        self.command_field.bind("<Up>", self.history_up)
        self.command_field.bind("<Down>", self.history_down)

        self.send_button: ttk.Button = ttk.Button(
            self.input_frame,
            text="Send",
            command=self.send_command,
            style=ttk.SUCCESS,
        )

        self.publish()

    @async_handler
    async def read_engine(self) -> None:
        if not self.autoread.get():
            return
        self.insert_text(await self.root.sonicamp.execute_command(""))
        self.after(1000, self.read_engine)

    def publish(self) -> None:
        self.read_button.pack(padx=5, pady=10, side=ttk.LEFT)

        self.command_field.pack(padx=5, pady=10, fill=ttk.X, side=ttk.LEFT, expand=True)
        self.send_button.pack(padx=5, pady=10, side=ttk.RIGHT)
        self.scrolled_frame.pack(
            anchor=ttk.N, fill=ttk.BOTH, pady=5, side=ttk.TOP, expand=True
        )

        self.input_frame.pack(fill=ttk.X, side=ttk.BOTTOM, padx=5, pady=5)
        self.output_frame.pack(
            anchor=ttk.N, fill=ttk.BOTH, pady=5, padx=5, side=ttk.TOP, expand=True
        )

        self.mainframe.pack(fill=ttk.BOTH, expand=True, padx=5, pady=5)

    @async_handler
    async def send_command(self, event) -> None:
        command: str = self.command_field.get()
        self.command_history.insert(0, command)

        self.insert_text(f">>> {command}")

        if not self.is_internal_command(command=command):
            self.insert_text(await self.root.sonicamp.execute_command(command))

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
        self.scrolled_frame.yview_moveto(1)

    def history_up(self, event) -> None:
        if (
            not self.command_history
            or self.index_history >= len(self.command_history) - 1
        ):
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
