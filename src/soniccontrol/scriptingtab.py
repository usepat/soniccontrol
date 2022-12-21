from __future__ import annotations

import os
import datetime
import time
import csv
import tkinter as tk
import tkinter.ttk as ttk
import threading

from typing import Union, TYPE_CHECKING
from enum import Enum
from tkinter import messagebox
from tkinter import filedialog

from sonicpackage import (
    SonicInterface,
    SonicWipe40KHZ,
    SonicWipeOld,
    SonicWipeAncient,
    Sequence,
    SerialConnection,
    FileHandler,
    ValueNotSupported
)

from soniccontrol.helpers import logger, ToolTip

if TYPE_CHECKING:
    from soniccontrol.core import Root
    from soniccontrol.notebook import ScNotebook


class ScriptCommand(Enum):

    SET_FRQ: str = "frequency XXXXXXXX\n"
    SET_GAIN: str = "gain XXX\n"
    SET_KHZ: str = "setkHz\n"
    SET_MHZ: str = "setMHz\n"
    SET_SIGNAL_ON: str = "on\n"
    SET_SIGNAL_OFF: str = "off\n"
    SET_AUTO: str = "autotune\n"
    SET_HOLD: str = "hold Xs\n"
    STARTLOOP: str = "startloop X\n"
    ENDLOOP: str = "endloop\n"
    SET_RAMP: str = "ramp XXXXXXX XXXXXXX XXXX XXXms\n"


class ScriptingTab(ttk.Frame):

    @property
    def root(self) -> Root:
        return self._root

    @property
    def serial(self) -> SerialConnection:
        return self._serial

    @property
    def amp_controller(self) -> SonicInterface:
        return self._amp_controller

    def __init__(self, parent: ScNotebook, root: Root, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self.config(height=200, width=200)

        self._root: Root = root
        self._serial: SerialConnection = root.serial
        self._amp_controller: SonicInterface = root.amp_controller
        self._sequence: Sequence
        self._filehandler: FileHandler

        self.logfile: str = None
        self.current_task: tk.StringVar = tk.StringVar(value="Idle")

        self._filetypes: list = [
            ("Text", "*.txt"),
            ("Logging files", "*.log"),
            ("CSV files", "*.csv"),
            ("All files", "*"),
        ]

        self._initialize_button_frame()
        self._initialize_scripting_frame()

    def _initialize_button_frame(self) -> None:
        self.button_frame: ttk.Frame = ttk.Frame(self)
        self.start_script_btn = ttk.Button(
            self.button_frame,
            text="Run",
            style="success.TButton",
            width=11,
            image=self.root.PLAY_IMG,
            compound=tk.RIGHT,
            command=self.button_starter,
        )
        self.load_script_btn: ttk.Button = ttk.Button(
            self.button_frame,
            text="Open script file",
            style="dark.TButton",
            width=15,
            command=self.load_file,
        )
        self.save_script_btn: ttk.Button = ttk.Button(
            self.button_frame,
            text="Save script file",
            style="dark.TButton",
            width=15,
            command=self.save_file,
        )
        self.save_log_btn: ttk.Button = ttk.Button(
            self.button_frame,
            text="Specify logfile path",
            style="dark.TButton",
            width=15,
            command=self.open_logfile,
        )
        self.script_guide_btn = ttk.Button(
            self.button_frame,
            text="Function Helper",
            style="info.TButton",
            width=15,
            command=lambda: ScriptingGuide(self.root, self.scripttext),
        )
        ToolTip(self.script_guide_btn, text="Help regarding the scripting commands")

        logger.debug("Initialzed scriptingtab")

    def _initialize_scripting_frame(self) -> None:
        self.scripting_frame: ttk.Labelframe = ttk.Labelframe(
            self,
            text="Script Editor",
            style="dark.TLabelframe",
            padding=(5, 5, 5, 5),
        )
        self.scripttext: tk.Text = tk.Text(
            self.scripting_frame,
            autoseparators=False,
            background="white",
            setgrid=False,
            width=35,
            padx=5,
            pady=5,
            font=("Consolas", 12),
        )
        self.scrollbar: ttk.Scrollbar = ttk.Scrollbar(
            self.scripting_frame, orient="vertical", command=self.scripttext.yview
        )
        self.cur_task_label = ttk.Label(
            self.scripting_frame,
            justify=tk.CENTER,
            anchor=tk.CENTER,
            style="dark.TLabel",
            textvariable=self.current_task,
        )
        self.sequence_status: ttk.Progressbar = ttk.Progressbar(
            self.scripting_frame,
            length=160,
            mode="indeterminate",
            orient=tk.HORIZONTAL,
            style="dark.TProgressbar",
        )

    def status_handler(self) -> None:
        if isinstance(self.root.sonicamp, SonicWipe40KHZ): return
        self.root.attach_data()
        self.root.update_idletasks()
        if not self.sequence.run: self.end_sequence()

    def highlight_line(self, current_line: int) -> None:
        current_line += 1
        self.scripttext.tag_remove("currentLine", 1.0, "end")
        self.scripttext.tag_add(
            "currentLine", f"{current_line}.0", f"{current_line}.end"
        )
        self.scripttext.tag_configure(
            "currentLine", background="#3e3f3a", foreground="#dfd7ca"
        )

    def button_starter(self):
        thread = threading.Thread(target=self.start_sequence)
        thread.start()

    def start_sequence(self) -> None:
        logger.debug("Started sequence")
        self.sequence: Sequence = GUISequence(self.amp_controller, self, self.logfile)

        if not self.root.thread.paused:
            self.root.thread.pause()

        self.start_script_btn.configure(
            text="Stop",
            style="danger.TButton",
            image=self.root.PAUSE_IMG,
            command=self.sequence.stop,
        )

        self.sequence_status.start()
        self.root.notebook.disable_children(self)
        self.scripttext.config(state=tk.DISABLED)
        self.load_script_btn.config(state=tk.DISABLED)
        self.save_log_btn.config(state=tk.DISABLED)
        self.save_script_btn.config(state=tk.DISABLED)
        self.script_guide_btn.config(state=tk.DISABLED)
        
        logger.debug("trying to start loop")
        try: 
            self.sequence.start(self.scripttext.get(1.0, tk.END))
        except SyntaxError as se:
            messagebox.showerror("Syntax Error", se)
        except ValueNotSupported as ve:
            messagebox.showerror("Value Error", ve)
        except ValueError as vee:
            logger.warning(vee)

    def end_sequence(self) -> None:
        logger.debug("End sequence started")
        if self.sequence._run: self.sequence._run: bool = False
        
        self.logfile: str = None
        self.start_script_btn.configure(
            text="Run",
            style="success.TButton",
            image=self.root.PLAY_IMG,
            command=self.button_starter,
        )

        # Changing GUI elemets so that everything looks different
        self.scripttext.tag_delete("currentLine", 1.0, tk.END)
        self.sequence_status.stop()
        self.current_task.set("Idle")
        self.previous_task = "Idle"
        self.root.notebook.enable_children()
        
        # Changing the state of the Buttons
        self.scripttext.config(state=tk.NORMAL)
        self.load_script_btn.config(state=tk.NORMAL)
        self.save_script_btn.config(state=tk.NORMAL)
        self.save_log_btn.config(state=tk.NORMAL)
        self.script_guide_btn.config(state=tk.NORMAL)
        self.sequence_status.config(text=None)

        self.root.amp_controller.set_signal_off()
        self.root.attach_data()

        if not isinstance(self.root.sonicamp, SonicWipe40KHZ) and self.root.thread.paused:
            self.root.thread.resume()

    def attach_data(self) -> None:
        pass

    def load_file(self) -> None:
        script_filepath: str = filedialog.askopenfilename(
            defaultextension=".txt", filetypes=self._filetypes
        )

        with open(script_filepath, "r") as f:
            self.scripttext.delete(1.0, tk.END)
            self.scripttext.insert(tk.INSERT, f.read())

    def save_file(self) -> None:
        self.save_filename = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=self._filetypes
        )

        with open(self.save_filename, "w") as f:
            f.write(self.scripttext.get(1.0, tk.END))

    def open_logfile(self) -> None:
        self.logfile = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=self._filetypes
        )
        logger.debug(f"The new logfile path is: {self.logfile}")

    def publish(self):
        self.button_frame.pack(anchor=tk.N, side=tk.LEFT, padx=5, pady=5)

        for child in self.button_frame.winfo_children():
            child.pack(side=tk.TOP, padx=5, pady=5)

        self.scripting_frame.pack(anchor=tk.N, side=tk.RIGHT, padx=5, pady=5, expand=True, fill=tk.X)
        self.scripttext.grid(row=0, column=0, columnspan=2)
        self.cur_task_label.grid(row=1, column=0, padx=0, pady=5, sticky=tk.EW, columnspan=2)
        self.sequence_status.grid(row=2, column=0, padx=0, pady=5, sticky=tk.EW, columnspan=2)


class GUISequence(Sequence):

    @property
    def gui(self) -> ScriptingTab:
        return self._gui
    
    def __init__(self, amp_controller: SonicInterface, gui: ScriptingTab, logfile: str = None) -> None:
        super().__init__(amp_controller, logfile)
        self._gui: ScriptingTab = gui

    def stop(self) -> None:
        if self.run: self._run: bool = False
        self.gui.end_sequence()

    def updater(self, command: str, argument: str) -> None:
        if not self.run: return
        if isinstance(self.sonicamp, SonicWipe40KHZ): return 
        self.amp_controller.update()
        self.gui.status_handler()

        data_dict: dict = self.sonicamp.status.__dict__
        data_dict["command"] = command
        data_dict["argument"] = argument
        
        self.file_handler.register_data(data_dict)

    def exec_command(self, index: int) -> None:
        if not self.run: return
        self.gui.highlight_line(index+len(self.comment))
        
        if isinstance(self.args_[index], list) and len(self.args_[index]) == 1:
            argument: int = self.args_[index][0]            
        else: 
            argument: int = self.args_[index]

        logger.info(f"Executing command: '{self.commands[index]}'")
        self.current_task: str = f"Command: {self.commands[index]} Args: {argument}"
        if self.commands[index] == "frequency":
            self.sonicamp.set_freq(argument)
        
        elif self.commands[index] == "gain":
            self.sonicamp.set_gain(argument)
        
        elif self.commands[index] == "ramp":
            self.ramp(argument)
        
        elif self.commands[index] == "hold":
            self.hold(argument)
        
        elif self.commands[index] == "on":
            self.sonicamp.set_signal_on()
        
        elif self.commands[index] == "off":
            self.sonicamp.set_signal_off()
        
        else:
            raise SyntaxError(f"Syntax of the command {self.commands[index]} is not known!")
            self.stop()
        
        if not self.run: return
        self.updater(self.commands[index], argument)

    def hold(self, args_: Union[list, int], ramp_mode: bool = False) -> None:
        if not self.run: return
        now: datetime.datetime = datetime.datetime.now()
        if isinstance(args_, int):
            target = now + datetime.timedelta(milliseconds=args_)
        elif len(args_) > 1 and args_[1] == "s":
            target = now + datetime.timedelta(seconds=args_[0])
        elif (len(args_) > 1 and args_[1] == "ms") or (len(args_) == 1):
            target = now + datetime.timedelta(milliseconds=args_[0])
        else: 
            target = now + datetime.timedelta(milliseconds=args_[0])

        while now < target and self.run:
            time.sleep(0.02)
            now = datetime.datetime.now()
            if ramp_mode: continue
            self.gui.current_task.set(
                f"Hold: {(target - now).seconds} seconds remaining"
            )
            self.updater("hold", args_)

    def ramp(self, args_: list) -> None:
        if not self.run: return
        logger.info("Starting ramp")
        start, stop, step, delay = args_
        if len(args_) > 4: hold_argument: list = [delay, args_[4]]
        else: hold_argument: list = [delay]

        frq_list: list = list(range(start, stop, step))
        if start > stop: frq_list.sort(reverse=True)

        for frq in frq_list:
            if not self.run: return
            if isinstance(self.sonicamp, SonicWipe40KHZ):
                self.gui.current_task.set(f"Ramp is @ {frq}%")
                logger.info(f"Ramp is at {frq}%")
                self.sonicamp.set_gain(frq)

            else:
                self.gui.current_task.set(f"Ramp is @ {frq/1000}kHz")
                logger.info(f"Ramp is at {frq/1000}kHz")
                self.sonicamp.set_freq(frq)

            if not self.run: return 
            self.updater("ramp", args_)
            self.hold(hold_argument, ramp_mode=True) 



class ScriptingGuide(tk.Toplevel):
    def __init__(self, root: Root, scripttext: tk.Text, *args, **kwargs) -> None:
        super().__init__(root, *args, **kwargs)
        self.title("Function Helper")

        self.root: Root = root
        self.scripttext: tk.Text = scripttext

        self._initialize_frame()
        self.publish()

    def _initialize_frame(self) -> None:
        self.heading_frame: ttk.Frame = ttk.Frame(self)
        self.heading_command = ttk.Label(
            self.heading_frame,
            anchor=tk.W,
            justify=tk.CENTER,
            text="Command",
            width=15,
            style="dark.TLabel",
            font="QTypeOT-CondMedium 15 bold",
        )
        self.heading_arg = ttk.Label(
            self.heading_frame,
            anchor=tk.W,
            justify=tk.CENTER,
            width=15,
            style="info.TLabel",
            text="Arguments",
            font="QTypeOT-CondMedium 15 bold",
        )
        self.hold_btn: ScriptingGuideRow = ScriptingGuideRow(
            self,
            btn_text="hold",
            arg_text="[1-10^6] in [seconds/ milliseconds] (depending on what you write e.g: 100ms, 5s, nothing defaults to milliseconds)",
            desc_text=None,
            command=lambda: self.insert_command(ScriptCommand.SET_HOLD),
        )
        ToolTip(
            self.hold_btn,
            text="Hold the last state for X seconds/ milliseconds, depending on what unit you have given",
        )
        self.freq_btn: ScriptingGuideRow = ScriptingGuideRow(
            self,
            btn_text="frequency",
            arg_text="[50.000-6.000.000] in [Hz]",
            desc_text=None,
            command=lambda: self.insert_command(ScriptCommand.SET_FRQ),
        )
        ToolTip(self.freq_btn, text="Change to the indicated frequency in Hz")
        self.gain_btn: ScriptingGuideRow = ScriptingGuideRow(
            self,
            btn_text="gain",
            arg_text="[1-150] in [%]",
            desc_text=None,
            command=lambda: self.insert_command(ScriptCommand.SET_GAIN),
        )
        ToolTip(self.gain_btn, text="Change to the selected gain in %")
        self.on_btn: ScriptingGuideRow = ScriptingGuideRow(
            self,
            btn_text="on",
            arg_text=None,
            desc_text=None,
            command=lambda: self.insert_command(ScriptCommand.SET_SIGNAL_ON),
        )
        ToolTip(self.on_btn, text="Activate US emission")
        self.off_btn: ScriptingGuideRow = ScriptingGuideRow(
            self,
            btn_text="off",
            arg_text=None,
            desc_text=None,
            command=lambda: self.insert_command(ScriptCommand.SET_SIGNAL_OFF),
        )
        ToolTip(self.off_btn, text="Deactivate US emission")
        self.startloop_btn: ScriptingGuideRow = ScriptingGuideRow(
            self,
            btn_text="startloop",
            arg_text="[2-10.000] as an [integer]",
            desc_text=None,
            command=lambda: self.insert_command(ScriptCommand.STARTLOOP),
        )
        ToolTip(self.startloop_btn, text="Start a loop for X times")
        self.endloop_btn: ScriptingGuideRow = ScriptingGuideRow(
            self,
            btn_text="endloop",
            arg_text=None,
            desc_text=None,
            command=lambda: self.insert_command(ScriptCommand.ENDLOOP),
        )
        ToolTip(self.endloop_btn, text="End the loop here")
        self.ramp_btn: ScriptingGuideRow = ScriptingGuideRow(
            self,
            btn_text="ramp",
            arg_text="<start f [Hz]> <stop f [Hz]> <step size [Hz]> <delay [ms / s]><unit of time> \nThe delay should be written like a hold (e.g: 100ms, 5s, nothing defaults to milliseconds)",
            desc_text=None,
            command=lambda: self.insert_command(ScriptCommand.SET_RAMP),
        )
        ToolTip(
            self.ramp_btn,
            text="Create a frequency ramp with a start frequency, a stop frequency,\n a step size and a delay between steps\nExpamle: ramp 50000 1200000 1000 100ms",
        )
        self.disclaimer_label: ttk.Label = ttk.Label(
            self,
            text="To insert a function at the cursor position, click on the respective button",
            font=("TkDefaultFont", 11, "bold"),
        )

    def insert_command(self, command: ScriptCommand) -> None:
        self.scripttext.insert(self.scripttext.index(tk.INSERT), command.value)

    def publish(self) -> None:
        self.heading_command.grid(row=0, column=0, padx=5, pady=5, sticky=tk.NSEW)
        self.heading_arg.grid(row=0, column=1, padx=5, pady=5, sticky=tk.NSEW)
        self.heading_frame.pack(
            side=tk.TOP, padx=5, pady=5, anchor=tk.W, expand=True, fill=tk.X
        )
        self.hold_btn.pack(side=tk.TOP, padx=5, pady=5, anchor=tk.W)
        self.on_btn.pack(side=tk.TOP, padx=5, pady=5, anchor=tk.W)
        self.off_btn.pack(side=tk.TOP, padx=5, pady=5, anchor=tk.W)
        self.startloop_btn.pack(side=tk.TOP, padx=5, pady=5, anchor=tk.W)
        self.endloop_btn.pack(side=tk.TOP, padx=5, pady=5, anchor=tk.W)
        self.ramp_btn.pack(side=tk.TOP, padx=5, pady=5, anchor=tk.W)

        if (
            not isinstance(self.root.sonicamp, SonicWipeOld) or 
            isinstance(self.root.sonicamp, SonicWipeAncient
        )):
            self.gain_btn.pack(side=tk.TOP, padx=5, pady=5, anchor=tk.W)

        if not isinstance(self.root.sonicamp, SonicWipe40KHZ):
            self.freq_btn.pack(side=tk.TOP, padx=5, pady=5, anchor=tk.W)

        self.disclaimer_label.pack(side=tk.TOP, expand=True, fill=tk.X, padx=5, pady=5)


class ScriptingGuideRow(ttk.Frame):
    def __init__(
        self, parent: ScriptingGuide, btn_text: str, arg_text: str, desc_text: str, command, *args, **kwargs,
    ) -> None:
        super().__init__(parent, *args, **kwargs)

        self.command_btn: ttk.Button = ttk.Button(self, width=15, style="dark.TButton", text=btn_text, command=command)
        self.command_btn.grid(row=0, column=0, padx=5, pady=5, sticky=tk.NSEW)

        if arg_text:
            self.arg_label: ttk.Label = ttk.Label(self, style="inverse.info.TLabel", text=arg_text)
            self.arg_label.grid(row=0, column=2, padx=5, pady=5, sticky=tk.NSEW)

        if desc_text:
            self.desc_label: ttk.Label = ttk.Label(self, text=desc_text, style="inverse.primary.TLabel")
            self.desc_label.grid(row=0, column=3, padx=5, pady=5, sticky=tk.NSEW)
    