import pathlib
from tkinter import filedialog
from typing import Any, Final, Optional, TypedDict

import attrs
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame, ScrolledText

from soniccontrol.interfaces.ui_component import UIComponent
from soniccontrol.interfaces.view import TabView
from soniccontrol.sonicpackage.interfaces import Scriptable
from soniccontrol.sonicpackage.script.legacy_scripting import LegacyScriptingFacade
from soniccontrol.sonicpackage.script.scripting_facade import ScriptingFacade
from soniccontrol.tkintergui.utils.constants import (events, sizes, tk_const,
                                                     ui_labels)
from soniccontrol.tkintergui.utils.image_loader import ImageLoader
from soniccontrol.tkintergui.widgets.card import Card
from soniccontrol.utils.files import images


@attrs.define
class ScriptFile:
    filename: str = attrs.ib(default = "./script.sonic")
    text: str = attrs.ib(default="")

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
        

class Scripting(UIComponent):
    def __init__(self, parent: UIComponent, device: Scriptable):
        self._device = device
        self._scripting: ScriptingFacade = LegacyScriptingFacade(self._device)
        self._interpreter_worker = None
        self._script: ScriptFile = ScriptFile()
        super().__init__(parent, ScriptingView(parent.view))


    def _on_open_script(self):
        filename: str = filedialog.askopenfilename(
            defaultextension=".sonic", filetypes=(("Text Files", "*.txt"), ("Sonic Script", "*.sonic"))
        )
        if filename == "." or filename == "" or isinstance(filename, (tuple)):
            return
        
        self._script.load_script(filename)
        self.view.script_text = self._script.text


    def _on_save_as_script(self):
        filename: str = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=(("Text Files", "*.txt"),)
        )
        if filename == "." or filename == "" or isinstance(filename, (tuple)):
            return
        
        self._script.text = self._view.script_text
        self._script.save_script(filename)


    def _on_start_script(self):
        pass

    def _on_stop_script(self):
        pass

    def _on_pause_script(self):
        pass

    async def _interpreter_engine(self):
        pass


class ScriptingView(TabView):
    def __init__(self, master: ttk.Window, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)

    @property
    def image(self) -> ttk.ImageTk.PhotoImage:
        return ImageLoader.load_image(images.SCRIPT_ICON_BLACK, sizes.TAB_ICON_SIZE)

    @property
    def tab_title(self) -> str:
        return ui_labels.SCRIPTING_LABEL

    @property
    def start_button(self) -> ttk.Button:
        return self._start_button

    @property
    def script_text(self) -> str:
        return self._script_text.get(1.0, ttk.END)
    
    @script_text.setter
    def script_text(self, value: str) -> None:
        self._script_text.delete(1.0, ttk.END)
        self._script_text.insert(ttk.INSERT, value)

    def _initialize_children(self) -> None:
        self._main_frame: ttk.Frame = ttk.Frame(self)

        SCRIPTING_PADDING: Final[tuple[int, int, int, int]] = (6, 1, 6, 7)
        self._scripting_frame: ttk.Labelframe = ttk.Labelframe(
            self._main_frame,
            text=ui_labels.SCRIPT_EDITOR_LABEL,
            padding=SCRIPTING_PADDING,
        )
        self._script_text: ScrolledText = ScrolledText(
            self._scripting_frame, autohide=True
        )

        self._script_status_frame: ttk.Frame = ttk.Frame(self)
        self._current_task_label: ttk.Label = ttk.Label(
            self._script_status_frame, justify=ttk.CENTER, style=ttk.DARK
        )
        self._progressbar: ttk.Progressbar = ttk.Progressbar(
            self._script_status_frame,
            mode=ttk.INDETERMINATE,
            orient=ttk.HORIZONTAL,
            style=ttk.DARK,
        )
        self._scripting_guide: ScriptingGuide = ScriptingGuide(self._script_text)
        self._navigation_button_frame: ttk.Frame = ttk.Frame(self)
        self._start_button: ttk.Button = ttk.Button(
            self._navigation_button_frame,
            text=ui_labels.START_LABEL,
            style=ttk.SUCCESS,
            image=ImageLoader.load_image(images.PLAY_ICON_WHITE, (13, 13)),
            compound=ttk.LEFT,
            command=lambda: self.event_generate(events.SCRIPT_START_EVENT),
        )
        self._end_button: ttk.Button = ttk.Button(
            self._navigation_button_frame,
            # text=const.ui.END_LABEL,
            style=ttk.DANGER,
            compound=ttk.LEFT,
            command=lambda: self.event_generate(events.SCRIPT_STOP_EVENT),
            image=ImageLoader.load_image(images.END_ICON_WHITE, sizes.BUTTON_ICON_SIZE),
        )
        self._scripting_guide_button: ttk.Button = ttk.Button(
            self._navigation_button_frame,
            text=ui_labels.GUIDE_LABEL,
            style=ttk.INFO,
            image=ImageLoader.load_image(images.INFO_ICON_WHITE, (13, 13)),
            compound=ttk.LEFT,
            command=self._scripting_guide.publish,
        )
        self._menue: ttk.Menu = ttk.Menu(self._navigation_button_frame)
        self._menue_button: ttk.Menubutton = ttk.Menubutton(
            self._navigation_button_frame,
            menu=self._menue,
            style=ttk.DARK,
            image=ImageLoader.load_image(images.MENUE_ICON_WHITE, (13, 13)),
            compound=ttk.LEFT,
        )
        self._menue.add_command(label=ui_labels.SAVE_LABEL, command=self.save_script)
        self._menue.add_command(label=ui_labels.LOAD_LABEL, command=self.load_script)
        self._menue.add_command(
            label=ui_labels.SPECIFY_PATH_LABEL, command=self.specify_datalog_path
        )

        self.bind_all(events.SCRIPT_STOP_EVENT, self.on_script_stop)
        self.bind_all(events.SCRIPT_START_EVENT, self.on_script_start)
        self.bind_all(events.SCRIPT_PAUSE_EVENT, self.on_script_pause)

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
        self._start_button.grid(
            row=0,
            column=0,
            padx=sizes.MEDIUM_PADDING,
            sticky=ttk.W,
        )
        self._end_button.grid(
            row=0,
            column=1,
            padx=sizes.MEDIUM_PADDING,
            sticky=ttk.W,
        )
        self._end_button.grid_remove()
        self._scripting_guide_button.grid(
            row=0,
            column=2,
            padx=sizes.MEDIUM_PADDING,
            sticky=ttk.W,
        )
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
        self._script_text.pack(expand=True, fill=ttk.BOTH)

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
        self._progressbar.grid(row=0, column=1, sticky=ttk.EW)

    def publish(self) -> None:
        ...

    def on_script_start(self, event: Any, *args, **kwargs) -> None:
        self._start_button.configure(
            text=ui_labels.PAUSE_LABEL,
            bootstyle=ttk.DANGER,
            image=ImageLoader.load_image(
                images.PAUSE_ICON_WHITE, sizes.BUTTON_ICON_SIZE
            ),
            command=lambda: self.event_generate(events.SCRIPT_PAUSE_EVENT),
        )
        self._end_button.grid()
        self._progressbar.configure(mode=ttk.DETERMINATE)
        self._progressbar.step()

    def on_script_stop(self, event: Any, *args, **kwargs) -> None:
        self.start_button.configure(
            text=ui_labels.START_LABEL,
            bootstyle=ttk.SUCCESS,
            command=lambda: self.event_generate(events.SCRIPT_START_EVENT),
            image=ImageLoader.load_image(
                images.PLAY_ICON_WHITE, sizes.BUTTON_ICON_SIZE
            ),
        )
        self._end_button.grid_remove()
        self._progressbar.stop()

    def on_script_pause(self, event: Any, *args, **kwargs) -> None:
        self.start_button.configure(
            text=ui_labels.RESUME_LABEL,
            bootstyle=ttk.SUCCESS,
            command=lambda: self.event_generate(events.SCRIPT_START_EVENT),
            image=ImageLoader.load_image(
                images.PLAY_ICON_WHITE, sizes.BUTTON_ICON_SIZE
            ),
        )
        self._progressbar.stop()

    def hightlight_line(self, line_idx: int) -> None:
        ...

    def specify_datalog_path(self) -> None:
        ...


class ScriptingGuideCardDataDict(TypedDict):
    keyword: str
    arguments: str
    description: str
    example: str


class ScriptingGuide(ttk.Toplevel):
    def __init__(self, script_text: ScrolledText, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._script_text: ScrolledText = script_text
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
        self._script_text.insert(self._script_text.index(ttk.INSERT), f"{text}\n")
