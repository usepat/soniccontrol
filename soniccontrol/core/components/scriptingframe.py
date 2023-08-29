import logging
from typing import Iterable, Any, Dict, Callable, Tuple, Union, Literal, Optional
import copy
import queue
import time
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledText, ScrolledFrame
from ttkbootstrap.tableview import Tableview, TableRow, TableColumn
from ttkbootstrap.dialogs.dialogs import Messagebox
import ttkbootstrap.constants as ttkconst
import PIL
import sys
from PIL.ImageTk import PhotoImage
import datetime
import soniccontrol.constants as const
from soniccontrol.interfaces import Layout, RootChild, Connectable, Scriptable
from soniccontrol.interfaces.rootchild import RootChildFrame
from soniccontrol.sonicamp import SonicAmpAgent, Command
from sonicpackage import SonicThread

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
        self.stop_image: PhotoImage = const.Images.get_image(
            const.Images.PAUSE_IMG_WHITE, const.Images.BUTTON_ICON_SIZE
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
            command=self.start_script,
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

    def start_script(self) -> None:
        self.sequence = Sequence(self.root.sonicamp, self.scripttext.get(1.0, ttk.END))
        self.sequence.daemon = True
        self.start_script_btn.configure(
            text="Stop",
            bootstyle=ttk.DANGER,
            image=self.stop_image,
            command=self.stop_script,
        )

        self.root.soniccontrol_state.animate_dots(text="Script Running")
        self.root.statusbar_frame.configure(bootstyle=ttk.SUCCESS)

        self.sequence_status.start()
        self.menue_button.configure(state=ttk.DISABLED)
        self.sequence.start()
        self.sequence.resume()
        self.script_engine()

    def script_engine(self) -> None:
        logger.debug("Scripting engine...")
        if self.sequence.shutdown_request.is_set():
            self.stop_script()
            return

        logger.debug("Checking exceptions...")
        if self.sequence.exceptions_queue.qsize():
            exc_info = self.sequence.exceptions_queue.get()
            logger.warning(f"{exc_info}")
            e: Exception = exc_info[1]
            Messagebox.show_warning(f"{e}")
            self.stop_script()
            return

        logger.debug("Checking output...")
        while self.sequence.output_queue.qsize():
            sequence_dict: Dict[str, Any] = self.sequence.output_queue.get()
            logger.debug(f"Script info {sequence_dict}")
            self.highlight_line(sequence_dict["line"])
            # self.cur_task_label["text"] = sequence_dict.get("info")
            self.current_task.set((sequence_dict["info"]))
        self.after(100, self.script_engine)

    def stop_script(self) -> None:
        logger.debug(f"Stopping script")
        if not self.sequence.shutdown_request.is_set():
            self.sequence.shutdown()

        self.root.soniccontrol_state.stop_animation_of_dots()
        self.root.statusbar_frame.configure(bootstyle=ttk.SECONDARY)
        self.root.soniccontrol_state.set("Manual")

        self.start_script_btn.configure(
            text="Run",
            style="success.TButton",
            image=self.start_image,
            command=self.start_script,
        )
        self.current_task.set("Idle")
        self.menue_button.configure(state=ttk.NORMAL)
        self.scripttext.tag_remove("currentLine", 1.0, "end")
        self.sequence_status.stop()

    def highlight_line(self, line: int) -> None:
        logger.debug(f"Highlighting line {line}")
        line += 1
        self.scripttext.tag_remove("currentLine", 1.0, "end")
        self.scripttext.tag_add("currentLine", f"{line}.0", f"{line}.end")
        self.scripttext.tag_configure(
            "currentLine", background="#3e3f3a", foreground="#dfd7ca"
        )

    def on_feedback(self, text: str) -> None:
        self.cur_task_label.configure(text=text)

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

        self.card_data: Tuple[Dict[str, str], ...] = (
            {
                "keyword": "frequency",
                "arguments": "frequency: uint",
                "description": "Set the frequency of the device",
                "example": "frequency 1000000",
            },
            {
                "keyword": "gain",
                "arguments": "gain: uint",
                "description": "Set the Gain of the device",
                "example": "gain 100",
            },
            {
                "keyword": "hold",
                "arguments": "hold: int,\nunit: 'ms' or 's'",
                "description": "Hold the state of the device\nfor a certain amount of time",
                "example": "hold 10s",
            },
            {
                "keyword": "ramp_freq",
                "arguments": "start: uint,\nstop: uint,\nstep: int,\non_signal_hold: uint,\nunit: 'ms' or 's',\noff_signal_hold: uint,\nunit: 'ms' or 's'",
                "description": "Ramp up the frequency from\none point to another",
                "example": "ramp_freq 1000000 2000000 1000 100ms 100ms",
            },
            {
                "keyword": "ramp_gain",
                "arguments": "start: uint,\nstop: uint,\nstep: int,\non_signal_hold: uint,\nunit: 'ms' or 's',\noff_signal_hold: uint,\nunit: 'ms' or 's'",
                "description": "Ramp up the gain from\none point to another",
                "example": "ramp_gain 10 100 10 100ms 100ms",
            },
            {
                "keyword": "chirp_freq_series",
                "arguments": "start: uint,\ndifference: uint,\nstep: int,\non_signal_hold: uint,\nunit: 'ms' or 's',\noff_signal_hold: uint,\nunit: 'ms' or 's'\ntimes: uint",
                "description": "Ramp up the frequency from\nthe start to the upper and lower difference.",
                "example": "chirp_freq_series 1000000 2000000 1000 100ms 100ms",
            },
        )

        self.scrolled_frame: ScrolledFrame = ScrolledFrame(self)
        self.scrolled_frame.pack(expand=True, fill=ttk.BOTH)

        for data in self.card_data:
            card: ScriptingGuideCard = ScriptingGuideCard(
                self.scrolled_frame,
                data,
                lambda event: self.insert_text(data["example"]),
            )
            card.pack(expand=True, fill=ttk.BOTH, padx=20, pady=15)
            card.publish()

    def insert_text(self, text: str) -> None:
        self.scripttext.insert(self.scripttext.index(ttk.INSERT), f"{text}\n")


class ScriptingGuideCard(ttk.Labelframe):
    def __init__(
        self,
        parent,
        data: Dict[str, str],
        callback: Callable[[Any], Any],
        *args,
        **kwargs,
    ) -> None:
        super().__init__(parent, *args, **kwargs)
        self.data: Dict[str, str] = data
        self.callback: Callable[[Any], Any] = callback

        self.keyword_frame: ttk.Frame = ttk.Frame(self)
        self.keyword_label: ttk.Label = ttk.Label(
            self.keyword_frame,
            font=("QType CondBook", 20),
            text=self.data["keyword"],
        )

        self.info_frame: ttk.Frame = ttk.Frame(self)
        self.arguments_frame: ttk.Frame = ttk.Frame(self.info_frame)
        self.arguments_title: ttk.Label = ttk.Label(
            self.arguments_frame, text=f"Arguments:", font=("Arial", 13, "bold")
        )
        self.arguments_label: ttk.Label = ttk.Label(
            self.arguments_frame, text=self.data["arguments"]
        )

        self.description_frame: ttk.Frame = ttk.Frame(self.info_frame)
        self.description_title: ttk.Label = ttk.Label(
            self.description_frame, text=f"Description:", font=("Arial", 13, "bold")
        )
        self.description_label: ttk.Label = ttk.Label(
            self.description_frame, text=self.data["description"]
        )

        self.example_frame: ttk.Frame = ttk.Frame(self.info_frame)
        self.example_title: ttk.Label = ttk.Label(
            self.example_frame, text=f"Example:", font=("Arial", 13, "bold")
        )
        self.example_label: ttk.Label = ttk.Label(
            self.example_frame, text=self.data["example"]
        )

        self.bind_deep(self, "<Button-1>", self.callback)
        self.bind_deep(self, "<Enter>", self.mark)
        self.bind_deep(self, "<Leave>", self.unmark)

    @staticmethod
    def bind_deep(widget, event, handler) -> None:
        widget.bind(event, handler)
        for child in widget.winfo_children():
            ScriptingGuideCard.bind_deep(child, event, handler)

    @staticmethod
    def deep_mark(widget, style) -> None:
        if isinstance(widget, (ttk.Label, ttk.LabelFrame)):
            widget.configure(bootstyle=style)
        for child in widget.winfo_children():
            ScriptingGuideCard.deep_mark(child, style)

    def unmark(self, event: Any = None) -> None:
        ScriptingGuideCard.deep_mark(self, ttk.DEFAULT)

    def mark(self, event: Any = None) -> None:
        ScriptingGuideCard.deep_mark(self, ttk.PRIMARY)

    def publish(self) -> None:
        self.keyword_frame.pack(padx=10, pady=5, fill=ttk.X)
        self.keyword_label.pack(expand=True, fill=ttk.X, padx=5, pady=5)

        self.info_frame.pack(padx=5, pady=5, fill=ttk.X)
        self.arguments_frame.pack(fill=ttk.X, padx=5, pady=5)
        self.arguments_title.pack(fill=ttk.X, padx=3, pady=3)
        self.arguments_label.pack(fill=ttk.X, padx=3, pady=3)

        self.description_frame.pack(fill=ttk.X, padx=5, pady=5)
        self.description_title.pack(fill=ttk.X, padx=3, pady=3)
        self.description_label.pack(fill=ttk.X, padx=3, pady=3)

        self.example_frame.pack(fill=ttk.X, padx=5, pady=5)
        self.example_title.pack(fill=ttk.X, padx=3, pady=3)
        self.example_label.pack(fill=ttk.X, padx=3, pady=3)


class Sequence(SonicThread):
    def __init__(
        self, sonicamp: SonicAmpAgent, scripttext: str, *args, **kwargs
    ) -> None:
        super().__init__()
        self._scripttext: str = scripttext
        self._sonicamp: SonicAmpAgent = sonicamp
        self._parser: SonicParser = SonicParser()
        self.output_queue: queue.Queue[Dict[str, Any]] = queue.Queue()

    def setup(self) -> None:
        try:
            parsed_script: dict[
                str, Union[tuple[Any, ...], str]
            ] = self._parser.parse_text(self._scripttext)
        except Exception as e:
            self.exceptions_queue.put(sys.exc_info())
        self._commands, self._args_, self._loops, self._comment = parsed_script.values()  # type: ignore
        self._original_loops = copy.deepcopy(self._loops)

        logger.info(f"Comments: {self._comment}")
        logger.info(f"Commands: {self._commands}")
        logger.info(f"Arguments: {self._args_}")
        logger.info(f"Loops: {self._loops}")

        self._current_line: int = 0

    def worker(self) -> None:
        if self.shutdown_request.is_set():
            return
        if self._current_line > len(self._commands) - 1:
            logger.info(f"End of script")
            self.shutdown()
            return

        self.output_queue.put(
            {
                "line": self._current_line,
                "command": self._commands[self._current_line],
                "arguments": self._args_[self._current_line],
                "info": f"{self._commands[self._current_line]} with {self._args_[self._current_line]}",
            }
        )
        try:
            if self._commands[self._current_line] == "startloop":
                self._current_line = self.startloop_response(self._current_line)
            elif self._commands[self._current_line] == "endloop":
                self._current_line = self.endloop_response(self._current_line)
            else:
                self.exec_command(self._current_line)
                self._sonicamp.add_job(Command("-", type_="status"), 0)
                self._sonicamp.add_job(Command("?sens", type_="status"), 0)
                self._current_line += 1
                time.sleep(0.2)
        except Exception as e:
            self.exceptions_queue.put(sys.exc_info())

    def startloop_response(self, line: int) -> int:
        logger.debug(
            f"'startloop' @ {line}; quantifier = {self._loops[line].get('quantifier')}"
        )
        if (
            self._loops[line].get("quantifier")
            and isinstance(self._loops[line].get("quantifier"), int)
            and self._loops[line].get("quantifier") != -1
        ):
            self._loops[line]["quantifier"] -= 1
            return line + 1

        elif self._loops[line].get("quantifier") == -1:
            return line + 1

        else:
            logger.debug(f"Jumping to {self._loops[line]['end'] + 1}; quantifier = 0")
            line = self._loops[line]["end"] + 1
            return line

    def endloop_response(self, line: int) -> int:
        logger.debug(f"'endloop' @ {line}")
        current_loop: dict[str, int] = list(
            filter(lambda x: (x.get("end") == line), self._loops)
        )[0]
        to_be_reseted: tuple[dict[str, int], ...] = copy.deepcopy(
            self._original_loops[current_loop["begin"] + 1 : current_loop["end"] - 1]
        )
        loops: list[dict[str, int]] = list(copy.deepcopy(self._loops))
        loops[current_loop["begin"] + 1 : current_loop["end"] - 1] = to_be_reseted
        self._loops = tuple(loops)

        logger.info(f"Loops reseted: {to_be_reseted}")
        return current_loop["begin"]

    def exec_command(self, index: int) -> None:
        current_argument: Union[int, tuple[Union[int, str], ...]] = self._args_[index]
        current_command: str = self._commands[index]
        logger.info(f"Executing command: '{self._commands[index]}'")

        if current_command == "frequency":
            self._sonicamp.add_job(Command(f"!f={current_argument}", type_="script"), 0)
        elif current_command == "gain":
            self._sonicamp.add_job(Command(f"!g={current_argument}", type_="script"), 0)
        elif current_command == "ramp_freq":
            self.ramp_freq(*current_argument)
        elif current_command == "ramp_gain":
            self.ramp_gain(*current_argument)
        elif current_command in ("!AUTO", "AUTO"):
            self._sonicamp.add_job(Command(f"!AUTO", type_="script"), 0)
        elif current_command == "hold":
            self.hold(None, *current_argument)
        elif current_command == "on":
            self._sonicamp.add_job(Command(f"!ON", type_="script"), 0)
        elif current_command == "off":
            self._sonicamp.add_job(Command(f"!OFF", type_="script"), 0)
        else:
            raise SyntaxError(f"Syntax of the command {current_command} is not known!")

    def shutdown(self) -> None:
        logger.debug("SHUTTING DOWN SEQUENCE THREAD")
        return super().shutdown()

    def ramp_freq(
        self,
        start: int,
        stop: int,
        step: int,
        hold_on_time: int = 10,
        hold_on_timeunit: str = "ms",
        hold_off_time: int = 0,
        hold_off_timeunit: str = "ms",
        *args,
        **kwargs,
    ) -> None:
        return self.ramp(
            type_="frequency",
            start=start,
            stop=stop,
            step=step,
            hold_on_time=hold_on_time,
            hold_on_timeunit=hold_on_timeunit,
            hold_off_time=hold_off_time,
            hold_off_timeunit=hold_off_timeunit,
        )

    def ramp_gain(
        self,
        start: int,
        stop: int,
        step: int,
        hold_on_time: int = 10,
        hold_on_timeunit: str = "ms",
        hold_off_time: int = 0,
        hold_off_timeunit: str = "ms",
        *args,
        **kwargs,
    ) -> None:
        return self.ramp(
            type_="gain",
            start=start,
            stop=stop,
            step=step,
            hold_on_time=hold_on_time,
            hold_on_timeunit=hold_on_timeunit,
            hold_off_time=hold_off_time,
            hold_off_timeunit=hold_off_timeunit,
        )

    def ramp(
        self,
        type_: str,
        start: int,
        stop: int,
        step: int,
        hold_on_time: int = 1,
        hold_on_timeunit: Literal["ms", "s"] = "ms",
        hold_off_time: int = 0,
        hold_off_timeunit: Literal["ms", "s"] = "ms",
    ) -> None:
        self._sonicamp.add_job(Command("!ON", type_="script"), 0)
        if type_ == "frequency":
            to_send: str = "!f="
        else:
            to_send: str = "!g="
        if start > stop:
            step = -step

        values: Iterable[int] = range(start, stop, step)
        for value in values:
            if self.shutdown_request.is_set():
                return
            command = Command(f"{to_send}{value}", type_="script")
            self.output_queue.put(
                {
                    "line": self._current_line,
                    "command": self._commands[self._current_line],
                    "arguments": self._args_[self._current_line],
                    "info": f"Ramp @ {value} {type_}",
                }
            )
            self._sonicamp.add_job(command, 0)
            command.processed.wait()
            command.processed.clear()

            if hold_off_time:
                command = Command(f"!ON", type_="script")
                self._sonicamp.add_job(command, 0)
                command.processed.wait()
                command.processed.clear()

            self.hold(command, hold_on_time, hold_on_timeunit)
            if hold_off_time:
                command = Command(f"!OFF", type_="script")
                self._sonicamp.add_job(Command(f"!OFF", type_="script"), 0)
                command.processed.wait()
                command.processed.clear()

                self.hold(command, hold_off_time, hold_off_timeunit)

            if self.shutdown_request.is_set():
                return

    def hold(
        self,
        command: Optional[Command] = None,
        duration: int = 10,
        unit: str = "ms",
        *args,
        **kwargs,
    ) -> None:
        duration /= 1000.0 if unit == "ms" else 1
        end_time = (command.timestamp if command else time.time()) + duration

        while time.time() < end_time and not self.shutdown_request.is_set():
            time.sleep(0.001)
            remaining_time: int = end_time - time.time()
            remaining_time = remaining_time if remaining_time < 10_000 else 0
            self.output_queue.put(
                {
                    "line": self._current_line,
                    "command": self._commands[self._current_line],
                    "arguments": self._args_[self._current_line],
                    "info": f"{round(remaining_time, 2)} seconds remaining on hold",
                }
            )
            logger.debug(f"Currently remaining {remaining_time})")

            if time.time() > end_time and self.shutdown_request.is_set():
                return

            command = Command("-", type_="status")
            self._sonicamp.add_job(command, 0)
            command.processed.wait()
            command.processed.clear()

            if time.time() > end_time and self.shutdown_request.is_set():
                return

            command = Command("?sens", type_="status")
            self._sonicamp.add_job(command, 0)
            command.processed.wait()
            command.processed.clear()


class SonicParser:
    SUPPORTED_TOKENS: list[str] = [
        "frequency",
        "gain",
        "ramp_freq",
        "ramp_gain",
        "on",
        "off",
        "hold",
        "startloop",
        "endloop",
        # "chirp_ramp_freq",
        # "chirp_ramp_gain",
        "!AUTO",
        "AUTO",
    ]

    def __init__(self) -> None:
        pass

    def parse_text(self, text: str) -> dict[str, Union[tuple[Any, ...], str]]:
        lines: list[str] = list(filter(None, text.rstrip().splitlines()))
        commands, arguments, comment = self.parse_lines(lines)
        loops: tuple[dict[str, int], ...] = self.parse_for_loops(commands, arguments)

        self.check_syntax_acception(loops, commands, arguments)

        return {
            "commands": commands,
            "arguments": arguments,
            "loops": loops,
            "comments": comment,
        }

    def values_correctly_converted(
        self, arg: Union[int, tuple[Union[int, str], ...]]
    ) -> bool:
        return (
            not isinstance(arg, int) and arg.isnumeric()
            if not isinstance(arg, tuple)
            else any(self.values_correctly_converted(value) for value in arg)
        )

    def parse_lines(self, lines: list[str]) -> tuple[Any, ...]:
        commands: list[str] = list()
        arguments: list[Union[str, int]] = list()
        comments: str = str()
        for line in lines:
            if "#" in line:
                comments += f"{line}\n"
                continue

            command, argument = self._parse_line(line)
            commands.append(command)
            arguments.append(argument)

        return (tuple(commands), tuple(arguments), comments)

    def parse_for_loops(
        self, commands: list[str], arguments: list[Union[str, int]]
    ) -> tuple[dict[str, int], ...]:
        loops: list[dict[str, int]] = list()
        for i, command in enumerate(commands):
            if command == "startloop":
                logger.debug(arguments)
                logger.debug(arguments[i])
                quantifier: int = (-1, arguments[i])[
                    arguments[i] is not None
                    and bool(arguments[i])
                    and int(arguments[i]) >= 1
                    and isinstance(arguments[i], int)
                ]
                loops.insert(i, {"begin": i, "quantifier": quantifier})

            elif command == "endloop":
                loops.insert(i, {})
                for loop in reversed(loops):
                    if len(loop) != 2:
                        continue
                    loop.update({"end": i})
                    break

            else:
                loops.insert(i, dict())
        return tuple(loops)

    def _parse_line(self, line: str) -> tuple[Union[str, int], ...]:
        if line is None or line == "":
            return ((), ())

        tmp_line_list: list[Union[str, int, list[Union[str, int]]]] = [
            i.split(",") for i in line.split(" ")
        ]
        line_list: list[Union[str, int]] = list(
            filter(None, [item for sublist in tmp_line_list for item in sublist])
        )

        for i, part in enumerate(line_list):
            if part[-1:] == "s" and part[-2:] != "ms" and part[:-1].isnumeric():
                line_list.insert(i + 1, part[-1:])
                line_list[i] = int(part[:-1])
            elif part[-2:] == "ms" and part[:-2].isnumeric():
                line_list.insert(i + 1, part[-2:])
                line_list[i] = int(part[:-2])
            elif part.isnumeric():
                line_list[i] = int(part)

        command: str = line_list[0]
        line_list.pop(0)
        return (command, line_list[0] if len(line_list) == 1 else tuple(line_list))

    def check_syntax_acception(self, loops, commands, arguments) -> None:
        if any(
            (len(loop) != 3 and loop is not None and len(loop) != 0) for loop in loops
        ):
            raise ValueError(
                "Syntax of loops is invalid. Maybe you forgot to close a loop?"
            )

        elif any(self.values_correctly_converted(arg) for arg in arguments):
            raise ValueError(
                "Argument(s) could not have been correctly converted to  integers,\nplease call for support or try again"
            )

        elif any(command not in self.SUPPORTED_TOKENS for command in commands):
            raise ValueError("One or more commands are illegal or written wrong")
