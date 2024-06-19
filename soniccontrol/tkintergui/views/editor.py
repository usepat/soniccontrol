import asyncio
import pathlib
from tkinter import filedialog
from typing import Any, Final, Iterable, List, Optional, Tuple, TypedDict

from enum import Enum
import attrs
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame, ScrolledText
from async_tkinter_loop import async_handler

from soniccontrol.interfaces.ui_component import UIComponent
from soniccontrol.interfaces.view import TabView
from soniccontrol.sonicpackage.interfaces import Scriptable
from soniccontrol.sonicpackage.script.legacy_scripting import LegacyScriptingFacade
from soniccontrol.sonicpackage.script.scripting_facade import ScriptingFacade
from soniccontrol.tkintergui.utils.constants import (events, sizes, tk_const,
                                                     ui_labels)
from soniccontrol.tkintergui.utils.image_loader import ImageLoader
from soniccontrol.tkintergui.views.pushbutton import PushButtonView
from soniccontrol.tkintergui.widgets.card import Card
from soniccontrol.utils.files import images


@attrs.define
class ScriptFile:
    filename: str = attrs.field(default="./script.sonic")
    text: str = attrs.field(default="")
    filetypes: List[Tuple[str, str]] = attrs.field(default=[("Text Files", "*.txt"), ("Sonic Script", "*.sonic")])
    default_extension: str = attrs.field(default=".sonic")

    def load_script(self, filename: Optional[str] = None):
        if filename is not None:
            self.filename = filename
        with pathlib.Path(self.filename).open("r") as f:
            self.text = f.read()

    def save_script(self, filename: Optional[str] = None):
        if filename is not None:
            self.filename = filename
        with pathlib.Path(self.filename).open("w") as f:
            f.write(self.text)
        

class InterpreterState:
    READY = 0
    PAUSED = 1
    RUNNING = 2


class Editor(UIComponent):
    def __init__(self, parent: UIComponent, device: Scriptable):
        self._device = device
        self._scripting: ScriptingFacade = LegacyScriptingFacade(self._device)
        self._interpreter_worker = None
        self._script: ScriptFile = ScriptFile()
        self._interpreter_iter: Iterable = iter([])
        self._interpreter_state = InterpreterState.READY
        super().__init__(parent, EditorView(parent.view))
        self._set_interpreter_state(self._interpreter_state)

    def _set_interpreter_state(self, interpreter_state: InterpreterState):
        self._interpreter_state = interpreter_state
        match interpreter_state:
            case InterpreterState.READY:
                self.view.start_pause_continue_button.configure(
                    label=ui_labels.START_LABEL,
                    image=(images.PLAY_ICON_WHITE, sizes.BUTTON_ICON_SIZE),
                    command=lambda: self._on_start_script(single_instruction=False),
                    enabled=True
                )
                self.view.single_step_button.configure(
                    label=ui_labels.SINGLE_STEP_LABEL,
                    image=(images.FORWARDS_ICON_WHITE, sizes.BUTTON_ICON_SIZE),
                    command=lambda: self._on_start_script(single_instruction=True),
                    enabled=False
                )
                self.view.stop_button.configure(
                    label=ui_labels.STOP_LABEL,
                    image=(images.END_ICON_WHITE, sizes.BUTTON_ICON_SIZE),
                    command=lambda: self._on_stop_script(),
                    enabled=False
                )
                self.view.editor_enabled = True
                self.view.current_task = "Idle"
                self.view.highlight_line(None)

            case InterpreterState.RUNNING:
                self.view.start_pause_continue_button.configure(
                    label=ui_labels.PAUSE_LABEL,
                    image=(images.PAUSE_ICON_WHITE, sizes.BUTTON_ICON_SIZE),
                    command=lambda: self._on_pause_script(),
                    enabled=True
                )
                self.view.single_step_button.configure(
                    enabled=False
                )
                self.view.stop_button.configure(
                    enabled=True
                )
                self.view.editor_enabled = False

            case InterpreterState.PAUSED:
                self.view.start_pause_continue_button.configure(
                    label=ui_labels.RESUME_LABEL,
                    image=(images.PLAY_ICON_WHITE, sizes.BUTTON_ICON_SIZE),
                    command=lambda: self._on_continue_script(),
                    enabled=True
                )
                self.view.single_step_button.configure(
                    enabled=True
                )
                self.view.stop_button.configure(
                    enabled=True
                )
                self.view.editor_enabled = False

    def _on_open_script(self):
        # TODO: move stuff like filedialog later into an abstract factory for the whole tkinter fronted
        filename: str = filedialog.askopenfilename(
            defaultextension=self._script.default_extension, 
            filetypes=self._script.filetypes
        )
        if filename == "." or filename == "" or isinstance(filename, (tuple)):
            return
        
        self._script.load_script(filename)
        self.view.editor_text = self._script.text

    def _on_save_as_script(self):
        filename: str = filedialog.asksaveasfilename(
            defaultextension=self._script.default_extension, 
            filetypes=self._script.filetypes
        )
        if filename == "." or filename == "" or isinstance(filename, (tuple)):
            return
        
        self._script.text = self._view.editor_text
        self._script.save_script(filename)

    def _on_save_script(self):
        self._script.text = self._view.editor_text
        self._script.save_script()

    @async_handler
    async def _on_start_script(self, single_instruction: bool = False):
        if self._interpreter_state == InterpreterState.READY:
            interpreter = self._scripting.parse_script(self._script.text)
            self._interpreter_iter = await iter(interpreter)

        self._interpreter_worker = asyncio.create_task(self._interpreter_engine(), single_instruction=single_instruction)
        self._set_interpreter_state(InterpreterState.RUNNING)

    @async_handler
    async def _on_stop_script(self):
        if self._interpreter_worker and not self._interpreter_worker.done() and not self._interpreter_worker.cancelled():
            self._interpreter_worker.cancel()
            await self._interpreter_worker
        
        self._set_interpreter_state(InterpreterState.READY)

    @async_handler
    def _on_continue_script(self):
        self._interpreter_worker = asyncio.create_task(self._interpreter_engine())
        self._set_interpreter_state(InterpreterState.RUNNING)

    @async_handler
    async def _on_pause_script(self):
        if self._interpreter_worker and not self._interpreter_worker.done() and not self._interpreter_worker.cancelled():
            self._interpreter_worker.cancel()
            await self._interpreter_worker
        
        self._set_interpreter_state(InterpreterState.PAUSED)

    async def _interpreter_engine(self, single_instruction: bool = False):
        try:
            async for line_index, task in self._interpreter_iter:
                self.view.highlight_line(line_index)
                self.view.current_task = task
                if single_instruction:
                    break
        except asyncio.CancelledError:
            return
        except Exception as e:
            self._show_err_msg(e)   
            self._set_interpreter_state(InterpreterState.PAUSED)
            return
        self._set_interpreter_state(InterpreterState.PAUSED if single_instruction else InterpreterState.READY)

    def _show_err_msg(self, e: Exception):
        pass


class EditorView(TabView):
    def __init__(self, master: ttk.Window, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)

    @property
    def image(self) -> ttk.ImageTk.PhotoImage:
        return ImageLoader.load_image(images.SCRIPT_ICON_BLACK, sizes.TAB_ICON_SIZE)

    @property
    def tab_title(self) -> str:
        return ui_labels.SCRIPTING_LABEL

    def _initialize_children(self) -> None:
        self._main_frame: ttk.Frame = ttk.Frame(self)

        SCRIPTING_PADDING: Final[tuple[int, int, int, int]] = (6, 1, 6, 7)
        self._scripting_frame: ttk.Labelframe = ttk.Labelframe(
            self._main_frame,
            text=ui_labels.SCRIPT_EDITOR_LABEL,
            padding=SCRIPTING_PADDING,
        )
        self._editor_text: ScrolledText = ScrolledText(
            self._scripting_frame, autohide=True
        )

        self._script_status_frame: ttk.Frame = ttk.Frame(self)
        self._current_task_var = ttk.StringVar(value="")
        self._current_task_label: ttk.Label = ttk.Label(
            self._script_status_frame, textvariable=self._current_task_var, justify=ttk.CENTER, style=ttk.DARK
        )
        # self._progressbar: ttk.Progressbar = ttk.Progressbar(
        #     self._script_status_frame,
        #     mode=ttk.INDETERMINATE,
        #     orient=ttk.HORIZONTAL,
        #     style=ttk.DARK,
        # )
        # self._scripting_guide: ScriptingGuide = ScriptingGuide(self._editor_text)
        self._navigation_button_frame: ttk.Frame = ttk.Frame(self)
        self._start_pause_continue_button = PushButtonView(
            self._navigation_button_frame,
            compound=ttk.LEFT
        )
        self._single_step_button = PushButtonView(
            self._navigation_button_frame,
            compound=ttk.LEFT
        )
        self._stop_button = PushButtonView(
            self._navigation_button_frame,
            compound=ttk.LEFT
        )
        # self._scripting_guide_button: ttk.Button = ttk.Button(
        #     self._navigation_button_frame,
        #     text=ui_labels.GUIDE_LABEL,
        #     style=ttk.INFO,
        #     image=ImageLoader.load_image(images.INFO_ICON_WHITE, (13, 13)),
        #     compound=ttk.LEFT,
        #     command=self._scripting_guide.publish,
        # )
        self._menue: ttk.Menu = ttk.Menu(self._navigation_button_frame)
        self._menue_button: ttk.Menubutton = ttk.Menubutton(
            self._navigation_button_frame,
            menu=self._menue,
            style=ttk.DARK,
            image=ImageLoader.load_image(images.MENUE_ICON_WHITE, (13, 13)),
            compound=ttk.LEFT,
        )
        # self._menue.add_command(label=ui_labels.SAVE_LABEL, command=self.save_script)
        # self._menue.add_command(label=ui_labels.LOAD_LABEL, command=self.load_script)
        # self._menue.add_command(
        #     label=ui_labels.SPECIFY_PATH_LABEL, command=self.specify_datalog_path
        # )


    def _initialize_publish(self) -> None:
        self.columnconfigure(0, weight=sizes.EXPAND)
        self.rowconfigure(0, weight=sizes.DONT_EXPAND, minsize=20)
        self.rowconfigure(1, weight=sizes.EXPAND)
        self.rowconfigure(2, weight=sizes.DONT_EXPAND, minsize=20)
        self._navigation_button_frame.grid(
            row=0,
            column=0,
            sticky=ttk.EW,
            padx=sizes.LARGE_PADDING,
            pady=sizes.LARGE_PADDING,
        )
        self._start_pause_continue_button._button.grid(
            row=0,
            column=0,
            padx=sizes.MEDIUM_PADDING,
            sticky=ttk.W,
        )
        self._single_step_button._button.grid(
            row=0,
            column=1,
            padx=sizes.MEDIUM_PADDING,
            sticky=ttk.W,
        )
        self._stop_button._button.grid(
            row=0,
            column=2,
            padx=sizes.MEDIUM_PADDING,
            sticky=ttk.W,
        )
        # self._scripting_guide_button.grid(
        #     row=0,
        #     column=2,
        #     padx=sizes.MEDIUM_PADDING,
        #     sticky=ttk.W,
        # )
        self._navigation_button_frame.columnconfigure(3, weight=sizes.EXPAND)
        self._menue_button.grid(
            row=0, column=3, sticky=ttk.E, padx=sizes.MEDIUM_PADDING
        )

        self._main_frame.grid(row=1, column=0, sticky=ttk.NSEW)
        self._scripting_frame.pack(
            expand=True,
            fill=ttk.BOTH,
            padx=sizes.SIDE_PADDING,
            pady=sizes.MEDIUM_PADDING,
        )
        self._editor_text.pack(expand=True, fill=ttk.BOTH)

        self._script_status_frame.grid(
            row=2,
            column=0,
            sticky=ttk.EW,
            padx=sizes.SIDE_PADDING,
            pady=sizes.MEDIUM_PADDING,
        )
        self._script_status_frame.columnconfigure(0, weight=3)
        self._script_status_frame.columnconfigure(1, weight=sizes.EXPAND)
        self._current_task_label.grid(row=0, column=0, columnspan=2, sticky=ttk.EW)
        # self._progressbar.grid(row=0, column=1, sticky=ttk.EW)

    @property
    def editor_text(self) -> str:
        return self._editor_text.get(1.0, ttk.END)
    
    @editor_text.setter
    def editor_text(self, value: str) -> None:
        self._editor_text.delete(1.0, ttk.END)
        self._editor_text.insert(ttk.INSERT, value)

    @property
    def current_task(self) -> str:
        return self._current_task_var.get()
    
    @current_task.setter
    def current_task(self, value: str) -> None:
        self._current_task_var.set(value)

    @property
    def editor_enabled(self) -> bool:
        pass

    @editor_enabled.setter 
    def editor_enabled(self, enabled: bool) -> None:
        self._editor_text.configure(state=ttk.NORMAL if enabled else ttk.DISABLED)

    @property
    def start_pause_continue_button(self) -> PushButtonView:
        return self._start_pause_continue_button
    
    @property
    def single_step_button(self) -> PushButtonView:
        return self._single_step_button

    @property
    def stop_button(self) -> PushButtonView:
        return self._stop_button

    def highlight_line(self, line_idx: Optional[int]) -> None:
        current_line_tag = "currentLine"
        self._scripttext.tag_remove(current_line_tag, 1.0, "end")

        if line_idx:
            line_idx += 1
            self._scripttext.tag_add(current_line_tag, f"{line_idx}.0", f"{line_idx}.end")
            self._scripttext.tag_configure(
                current_line_tag, background="#3e3f3a", foreground="#dfd7ca"
            )


class ScriptingGuideCardDataDict(TypedDict):
    keyword: str
    arguments: str
    description: str
    example: str


class ScriptingGuide(ttk.Toplevel):
    def __init__(self, editor_text: ScrolledText, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._editor_text: ScrolledText = editor_text
        self._scrolled_frame: ScrolledFrame = ScrolledFrame(self)
        self._cards_data: tuple[dict[str, str], ...] = (
            {
                "keyword": "startloop",
                "arguments": "times: optional uint",
                "description": "Starts a loop and loops until an endloop was found. \nIf no argument was passed, \nthen the loop turns to a 'While True loop'",
                "example": "startloop 5",
            },
            {
                "keyword": "endloop",
                "arguments": "None",
                "description": "Ends the last started loop",
                "example": "endloop",
            },
            {
                "keyword": "on",
                "arguments": "None",
                "description": "Sets the signal to ON",
                "example": "on",
            },
            {
                "keyword": "off",
                "arguments": "None",
                "description": "Set the signal to OFF",
                "example": "off",
            },
            {
                "keyword": "auto",
                "arguments": "None",
                "description": "Turns the auto mode on.\nIt is important to hold after that \ncommand to stay in auto mode.\nIn the following example the \nauto mode is turned on for 5 seconds",
                "example": "auto\nhold 5s",
            },
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
        )

        KEYWORD = "keyword"
        EXAMPLE = "example"
        for data in self._cards_data:
            card: Card = Card(
                self._scrolled_frame,
                heading=data[KEYWORD],
                data=dict(list(data.items())[1:]),
                command=lambda _, text=data[EXAMPLE]: self.insert_text(text),
            )
            card.pack(side=ttk.TOP, fill=ttk.X, padx=15, pady=15)
        self._scrolled_frame.pack(side=ttk.TOP, fill=ttk.BOTH, expand=True)
        self.protocol(tk_const.DELETE_WINDOW, self.withdraw)
        self.withdraw()

    def publish(self) -> None:
        self.wm_deiconify()

    def insert_text(self, text: str) -> None:
        self._editor_text.insert(self._editor_text.index(ttk.INSERT), f"{text}\n")
