import asyncio
import pathlib
from tkinter import filedialog
from typing import Callable, Final, Iterable, List, Optional, Tuple

import attrs
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledText
from ttkbootstrap.dialogs import Messagebox
from async_tkinter_loop import async_handler

from soniccontrol.interfaces.ui_component import UIComponent
from soniccontrol.interfaces.view import TabView
from soniccontrol.sonicpackage.interfaces import Scriptable
from soniccontrol.sonicpackage.script.legacy_scripting import LegacyScriptingFacade
from soniccontrol.sonicpackage.script.scripting_facade import ScriptingFacade
from soniccontrol.tkintergui.utils.constants import (sizes, scripting_cards_data,
                                                     ui_labels)
from soniccontrol.tkintergui.utils.image_loader import ImageLoader
from soniccontrol.tkintergui.widgets.pushbutton import PushButtonView
from soniccontrol.tkintergui.views.scriptingguide import ScriptingGuide
from soniccontrol.utils.files import images


@attrs.define
class ScriptFile:
    filepath: str = attrs.field(default="./script.sonic")
    text: str = attrs.field(default="")
    filetypes: List[Tuple[str, str]] = attrs.field(default=[("Text Files", "*.txt"), ("Sonic Script", "*.sonic")])
    default_extension: str = attrs.field(default=".sonic")

    def load_script(self, filepath: Optional[str] = None):
        if filepath is not None:
            self.filepath = filepath
        with pathlib.Path(self.filepath).open("r") as f:
            self.text = f.read()

    def save_script(self, filepath: Optional[str] = None):
        if filepath is not None:
            self.filepath = filepath
        with pathlib.Path(self.filepath).open("w") as f:
            f.write(self.text)
        

class InterpreterState:
    READY = 0
    PAUSED = 1
    RUNNING = 2


class Editor(UIComponent):
    def __init__(self, parent: UIComponent, root, device: Scriptable):
        self._root = root
        self._device = device
        self._scripting: ScriptingFacade = LegacyScriptingFacade(self._device)
        self._interpreter_worker = None
        self._script: ScriptFile = ScriptFile()
        self._interpreter: Iterable = iter([])
        self._interpreter_state = InterpreterState.READY

        super().__init__(parent, EditorView(parent.view))

        self.view.add_menu_command(ui_labels.LOAD_LABEL, self._on_load_script)
        self.view.add_menu_command(ui_labels.SAVE_LABEL, self._on_save_script)
        self.view.add_menu_command(ui_labels.SAVE_AS_LABEL, self._on_save_as_script)
        self.view.set_scripting_guide_button_command(self._on_open_scriping_guide)
        self._set_interpreter_state(self._interpreter_state)

    def _set_interpreter_state(self, interpreter_state: InterpreterState):
        self._interpreter_state = interpreter_state
        match interpreter_state:
            case InterpreterState.READY:
                self.view.start_pause_continue_button.configure(
                    label=ui_labels.START_LABEL,
                    image=(images.PLAY_ICON_WHITE, sizes.BUTTON_ICON_SIZE),
                    command=lambda: self._on_start_script(False),
                    enabled=True
                )
                self.view.single_step_button.configure(
                    label=ui_labels.SINGLE_STEP_LABEL,
                    image=(images.FORWARDS_ICON_WHITE, sizes.BUTTON_ICON_SIZE),
                    command=lambda: self._on_start_script(True),
                    enabled=True
                )
                self.view.stop_button.configure(
                    label=ui_labels.STOP_LABEL,
                    image=(images.END_ICON_WHITE, sizes.BUTTON_ICON_SIZE),
                    command=self._on_stop_script,
                    enabled=False
                )
                self.view.editor_enabled = True
                self.view.current_task = "Idle"
                self.view.highlight_line(None)

            case InterpreterState.RUNNING:
                self.view.start_pause_continue_button.configure(
                    label=ui_labels.PAUSE_LABEL,
                    image=(images.PAUSE_ICON_WHITE, sizes.BUTTON_ICON_SIZE),
                    command=self._on_pause_script,
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
                    command=self._on_continue_script,
                    enabled=True
                )
                self.view.single_step_button.configure(
                    enabled=True
                )
                self.view.stop_button.configure(
                    enabled=True
                )
                self.view.editor_enabled = False

    def _on_load_script(self):
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
        if pathlib.Path(self._script.filepath).exists():
            self._script.text = self._view.editor_text
            self._script.save_script()
        else:
            self._on_save_as_script()

    def _on_open_scriping_guide(self):
        ScriptingGuide(self._root, self.view.editor_text_view, scripting_cards_data)


    @async_handler
    async def _on_start_script(self, single_instruction: bool):
        self._script.text = self.view.editor_text
        if self._interpreter_state == InterpreterState.READY:
            try:
                self._interpreter = self._scripting.parse_script(self._script.text)
            except Exception as e:
                self._show_err_msg(e)
                return

        self._set_interpreter_state(InterpreterState.RUNNING)
        self._interpreter_worker = asyncio.create_task(self._interpreter_engine(single_instruction=single_instruction))

    @async_handler
    async def _on_stop_script(self):
        if self._interpreter_worker and not self._interpreter_worker.done() and not self._interpreter_worker.cancelled():
            self._interpreter_worker.cancel()
            await self._interpreter_worker
        
        self._set_interpreter_state(InterpreterState.READY)

    @async_handler
    async def _on_continue_script(self):
        self._set_interpreter_state(InterpreterState.RUNNING)
        self._interpreter_worker = asyncio.create_task(self._interpreter_engine())

    @async_handler
    async def _on_pause_script(self):
        if self._interpreter_worker and not self._interpreter_worker.done() and not self._interpreter_worker.cancelled():
            self._interpreter_worker.cancel()
            await self._interpreter_worker
        
        self._set_interpreter_state(InterpreterState.PAUSED)

    async def _interpreter_engine(self, single_instruction: bool = False):
        try:
            async for line_index, task in self._interpreter:
                self.view.highlight_line(line_index)
                self.view.current_task = task
                if single_instruction and line_index != 0:
                    break
        except asyncio.CancelledError:
            return
        except Exception as e:
            self._show_err_msg(e)   
            self._set_interpreter_state(InterpreterState.PAUSED)
            return
        self._set_interpreter_state(InterpreterState.PAUSED if single_instruction and not self._interpreter.is_finished else InterpreterState.READY)

    def _show_err_msg(self, e: Exception):
        Messagebox.show_error(f"{e.__class__.__name__}: {str(e)}")


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
        self._scripting_guide_button: ttk.Button = ttk.Button(
            self._navigation_button_frame,
            text=ui_labels.GUIDE_LABEL,
            style=ttk.INFO,
            image=ImageLoader.load_image(images.INFO_ICON_WHITE, (13, 13)),
            compound=ttk.LEFT, 
        )
        self._menue: ttk.Menu = ttk.Menu(self._navigation_button_frame)
        self._menue_button: ttk.Menubutton = ttk.Menubutton(
            self._navigation_button_frame,
            menu=self._menue,
            style=ttk.DARK,
            image=ImageLoader.load_image(images.MENUE_ICON_WHITE, (13, 13)),
            compound=ttk.LEFT,
        )


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
        self._scripting_guide_button.grid(
            row=0,
            column=3,
            padx=sizes.MEDIUM_PADDING,
            sticky=ttk.W,
        )
        self._navigation_button_frame.columnconfigure(3, weight=sizes.EXPAND)
        self._menue_button.grid(
            row=0, column=4, sticky=ttk.E, padx=sizes.MEDIUM_PADDING
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

    def add_menu_command(self, label: str, command: Callable[[None], None]) -> None:
        self._menue.add_command(label=label, command=command)

    @property 
    def editor_text_view(self) -> ttk.ScrolledText:
        return self._editor_text
    
    def set_scripting_guide_button_command(self, command: Callable[[None], None]) -> None:
        self._scripting_guide_button.configure(command=command)

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
        pass

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
        self._editor_text.tag_remove(current_line_tag, 1.0, "end")

        if line_idx:
            line_idx += 1
            self._editor_text.tag_add(current_line_tag, f"{line_idx}.0", f"{line_idx}.end")
            self._editor_text.tag_configure(
                current_line_tag, background="#3e3f3a", foreground="#dfd7ca"
            )
