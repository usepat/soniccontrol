from __future__ import annotations

import os
import datetime
import time
import csv
import tkinter as tk
import tkinter.ttk as ttk

from typing import Union, TYPE_CHECKING
from enum import Enum
from tkinter import messagebox
from tkinter import filedialog

from sonicpackage import (
    Status,
    Command,
    SonicAmp,
    SonicCatch,
    SonicWipeDuty,
    SonicWipe,
    SonicWipeOld,
    SonicCatchOld,
    SonicCatchAncient,
    SonicWipeAncient,
    KhzMode,
    MhzMode,
    CatchMode,
    WipeMode,
    ValueNotSupported,
)
from soniccontrol.sonicamp import SerialConnectionGUI
from soniccontrol.helpers import logger, ToolTip

if TYPE_CHECKING:
    from soniccontrol.core import Root
    from soniccontrol._notebook import ScNotebook


class ScriptCommand(Enum):
    """
    The ScriptCommand class is an enumaration class
    that has it's builtin constants of strings, those
    are being used for the function helper to insert
    scripting commands into the scripting text frame

    Inheritance:
        Enum (enum.Enum): the python enumaration class
    """

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
    """
    The Scriptingtab is an element of the GUI with that
    the user can control an SonicAmp through running a 
    simple script in a very light weight syntax.
    
    The logic of the Scripitng Tab is splitted up into 3 
    classes. Firstly the ScriptingTab class, that handles 
    everything regarding the GUI. Every visual aspect of the 
    Scripting tab are being managed here.
    
    Secondly the Sequence class, that handles the conrete logic
    to control an sonicamp
    
    Thirdly, the FileHandler. Given the name, that class handles
    filepaths and log files
    
    Inheritance:
        ttk (ttk.Frame): inherets from the ttk.Frame object in 
        the Tkinter library
    """
    @property
    def root(self) -> Root:
        return self._root

    @property
    def serial(self) -> SerialConnectionGUI:
        return self._serial

    def __init__(self, parent: ScNotebook, root: Root, *args, **kwargs) -> None:
        """
        When initialized, the composit elements of the ScriptingTab 
        are initialized. Mainly the sequence and filehandler objects

        Furhtermore, the creation of the GUI children is being held 
        in the internal initialize methods

        Args:
            parent (ScNotebook): The tkinter parent of the ScriptingTab
            root (Root): The root instance
        """
        super().__init__(parent, *args, **kwargs)
        self.config(height=200, width=200)

        self._root: Root = root
        self._serial: SerialConnectionGUI = root.serial
        self.sequence: Sequence
        self.file_handler: FileHandler = FileHandler(self)

        self.current_task: tk.StringVar = tk.StringVar(value="Idle")

        self._initialize_button_frame()
        self._initialize_scripting_frame()

    def _initialize_button_frame(self) -> None:
        """
        Given the name, this method create GUI children
        for the button frame
        """
        self.button_frame: ttk.Frame = ttk.Frame(self)

        self.start_script_btn = ttk.Button(
            self.button_frame,
            text="Run",
            style="success.TButton",
            width=11,
            image=self.root.PLAY_IMG,
            compound=tk.RIGHT,
            command=self.start_sequence,
        )

        self.load_script_btn: ttk.Button = ttk.Button(
            self.button_frame,
            text="Open script file",
            style="dark.TButton",
            width=15,
            command=self.file_handler.load_file,
        )

        self.save_script_btn: ttk.Button = ttk.Button(
            self.button_frame,
            text="Save script file",
            style="dark.TButton",
            width=15,
            command=self.file_handler.save_file,
        )

        self.save_log_btn: ttk.Button = ttk.Button(
            self.button_frame,
            text="Specify logfile path",
            style="dark.TButton",
            width=15,
            command=self.file_handler.open_logfile,
        )

        self.script_guide_btn = ttk.Button(
            self.button_frame,
            text="Function Helper",
            style="info.TButton",
            width=15,
            command=lambda: ScriptingGuide(self.root, self.scripttext),
        )

        ToolTip(self.script_guide_btn, text="Help regarding the scripting commands")

    def _initialize_scripting_frame(self) -> None:
        """
        Given the name, this method creates the composit children
        regarding the scripting frame
        """
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

    def highlight_line(self, current_line: int) -> None:
        """
        Function that highlights the current line of the sequence in the script editor
        The argument current_line

        Args:
            current_line (int): current line in the script, that need to be highlighted
        """
        current_line += 1
        self.scripttext.tag_remove("currentLine", 1.0, "end")
        self.scripttext.tag_add(
            "currentLine", f"{current_line}.0", f"{current_line}.end"
        )
        self.scripttext.tag_configure(
            "currentLine", background="#3e3f3a", foreground="#dfd7ca"
        )

    def start_sequence(self) -> None:
        """
        This method configures everything in the GUI so that 
        a new sequence can be initialized. A new Sequence instance
        is being created
        
        A log file for this sequence is being created
        
        The SonicAgent Thread is paused so that the Scripting tab
        is now responsible for updating the GUI to the new state 
        of the sonicamp
        """
        self.sequence: Sequence = Sequence(self)
        self.file_handler.decide_logfile_name()

        if not self.root.thread.paused:
            self.root.thread.pause()

        # GUI children to manage the appearance
        self.start_script_btn.configure(
            text="Stop",
            style="danger.TButton",
            image=self.root.PAUSE_IMG,
            command=self.end,
        )

        self.sequence_status.start()
        self.root.notebook.disable_children(self)
        self.scripttext.config(state=tk.DISABLED)
        self.load_script_btn.config(state=tk.DISABLED)
        self.save_log_btn.config(state=tk.DISABLED)
        self.save_script_btn.config(state=tk.DISABLED)
        self.script_guide_btn.config(state=tk.DISABLED)

        self.sequence.start()

    def end(self) -> None:
        """
        Similar to the start_sequence method, this method
        ends the sequence with configuring everything for 
        normal usage again.
        """
        if not self.sequence.run:
            self.sequence.run: bool = False
        
        self.file_handler.logfilepath: str = None
        self.start_script_btn.configure(
            text="Run",
            style="success.TButton",
            image=self.root.PLAY_IMG,
            command=self.start_sequence,
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

        self.serial.send_and_get(Command.SET_SIGNAL_OFF)
        self.root.attach_data()

        if not isinstance(self.root.sonicamp, SonicWipeDuty) and self.root.thread.paused:
            self.root.thread.resume()

    def status_handler(self, command: str, argument: int) -> None:
        """
        The builtin status handler method of the ScriptingTab class
        It baisically resembles the engine method of Root

        Args:
            command (str): The command, that currently is being executed
            argument (int): The argument for that command
        """
        if not isinstance(self.root.sonicamp, SonicWipeDuty):
            self.root.sonicamp.status: Status = self.root.sonicamp.get_status()
            self.root.attach_data()
            self.root.register_status_data(data=self.root.sonicamp.status)
            self.file_handler.register_data(
                command=command, argument=argument, status=self.root.sonicamp.status
            )
            self.root.update_idletasks()

    def attach_data(self) -> None:
        pass

    def publish(self):
        """
        Method to publish every component and show the tab visually in the GUI
        """
        # Button Frame
        self.button_frame.pack(anchor=tk.N, side=tk.LEFT, padx=5, pady=5)

        for child in self.button_frame.winfo_children():
            child.pack(side=tk.TOP, padx=5, pady=5)

        # Scripting Frame
        self.scripting_frame.pack(
            anchor=tk.N, side=tk.RIGHT, padx=5, pady=5, expand=True, fill=tk.X
        )
        self.scripttext.grid(row=0, column=0, columnspan=2)
        self.cur_task_label.grid(
            row=1, column=0, padx=0, pady=5, sticky=tk.EW, columnspan=2
        )
        self.sequence_status.grid(
            row=2, column=0, padx=0, pady=5, sticky=tk.EW, columnspan=2
        )


class Sequence:
    """
    The Sequecne class is the core logic of the Scripting tab.
    This class is responsible for controlling the sonicamp based
    on the commands and arguments that were passed into the scripttext
    from the ScriptingTab
    
    The main attributes of the sequence class are:
        self.commands (list) -> List of string commands from the scripttext
        self.args_ (list) -> list of arguments for commands from the scripttext
        self.loops (list) -> list of lists where one can find data, that describes
            a loop block.
            
        The above lists have the same lenght, so that the index information can 
        be used to identify the command for the concrete argument
        
        Element of the self.loops list:
        [
            <index of the startloop command for the concrete block>,
            <quantifier for the loop block (how often should this block be run)>,
            <index of the endloop command for the concrete block>
        ]
        
        Example for an self.loops list:
        [[],[],[2, 5, 6],[3, 3, 5], [], [], []]
        
        This list tells the programm, that on line 3 there is a startloop 5 with an
        endloop command on line 7. Furthermore, there is a nested loop with an 
        startloop 3 on line 4 and a endloop command on line 6

    """
    def __init__(self, gui: ScriptingTab) -> None:
        """
        Every attribute is being initialized.
        The main attributes are the commands, args_ and loops
        
        Furthermore there is self.run, that is being used
        for indicating if the sequence is currently running

        Args:
            gui (ScriptingTab): the ScriptingTab class from above
        """
        self.gui: ScriptingTab = gui
        self.serial: SerialConnectionGUI = gui.serial
        self.sonicamp: SonicAmp = gui.root.sonicamp

        self.run: bool = False

        self.commands: list = []
        self.args_: list = []
        self.loops: list = []

    def start(self) -> None:
        """
        This method uses
        """

        self.run: bool = True

        self.commands.clear()
        self.args_.clear()
        self.loops.clear()

        try:
            self.parse_commands(self.gui.scripttext.get(1.0, tk.END))

        except Exception as e:
            logger.warning(f"Error while trying to parse: {e}")

            messagebox.showerror(
                "Error in formatting",
                "It seems you've given commands or arguments in the wrong format",
            )

            self.run: bool = False

        self.loop()

    def loop(self) -> None:
        line: int = 0
        while line < len(self.commands) and self.run:
            self.gui.highlight_line(line)

            if self.commands[line] == "startloop":

                logger.debug(
                    f"Found startloop command at {line}, with the quantifier {self.loops[line][1]}"
                )
                if self.loops[line][1] and isinstance(self.loops[line][1], int):
                    self.loops[line][1] -= 1
                    line += 1

                elif self.loops[line][1] == "inf":
                    line += 1

                else:
                    logger.debug(
                        f"Jumping to line {self.loops[line][2] + 1}, because quantifier is 0"
                    )
                    line: int = self.loops[line][2] + 1

            elif self.commands[line] == "endloop":

                logger.debug(f"Found endloop command at {line}")
                for loop in self.loops:

                    if loop and loop[2] == line:

                        for j in range(loop[0] + 1, loop[2]):

                            if self.loops[j]:
                                logger.info(
                                    f"Found loop to be reseted: {self.loops[j]}"
                                )
                                self.loops[j][1] = self.args_[j]

                        line: int = loop[0]

            else:
                logger.info(f"Executing command at\t{line}")
                self.exec_command(line)
                line += 1
                
        self.gui.end()

    def exec_command(self, counter: int) -> None:
        """
        This function manages the execution of functions
        and manages the visualization of the execution

        Args:
            counter (int): The index of the line
        """
        self.gui.highlight_line(counter)
        self.gui.current_task.set(
            f"{self.commands[counter]} {str(self.args_[counter])}"
        )

        # Just for managing purposes
        if isinstance(self.args_[counter], list):

            if len(self.args_[counter]) == 1:
                argument: int = self.args_[counter][0]
            else:
                argument: list = self.args_[counter]

        else:
            argument: int = self.args_[counter]

        if self.run:

            logger.info(f"Executing command: {self.commands[counter]}")

            if self.commands[counter] == "frequency":
                self.set_frq(argument)

            elif self.commands[counter] == "gain":
                self.set_gain(argument)

            elif self.commands[counter] == "ramp":
                self.start_ramp(argument)

            elif self.commands[counter] == "hold":
                self.hold(argument)

            elif self.commands[counter] == "on":
                self.serial.send_and_get(Command.SET_SIGNAL_ON)
                
                if isinstance(self.sonicamp, SonicWipeDuty):
                    self.gui.root.status_frame.signal_on()

            elif self.commands[counter] == "off":
                self.serial.send_and_get(Command.SET_SIGNAL_OFF)
                
                if isinstance(self.sonicamp, SonicWipeDuty):
                    self.gui.root.status_frame.signal_off()

            else:
                messagebox.showerror(
                    "Wrong command",
                    f"the command {self.commands[counter]} is not known, please use the correct commands in the correct syntax",
                )
                self.close_sequence()

        self.gui.status_handler(self.commands[counter], argument=argument)

    def set_frq(self, frq: int) -> None:
        if not self.sonicamp.values_possible(frq=frq) or not (
            self.sonicamp.values_supported(frq=frq) or self.manage_relay()
        ):
            messagebox.showerror(
                "Wrong frequency value",
                "The frequency value, you wanted to set, is not possible. Please take a look at the syntax again",
            )
            self.close_sequence()

        self.sonicamp.set_frq(frq=frq)

    def set_gain(self, gain: int) -> None:

        if not self.sonicamp.values_possible(gain=gain) or not (
            self.sonicamp.values_supported(gain=gain) or self.manage_relay()
        ):
            messagebox.showerror(
                "Wrong frequency value",
                "The Gain value, you wanted to set, is not possible. Please take a look at the syntax again",
            )
            self.close_sequence()

        self.sonicamp.set_gain(gain=gain)
        
        if isinstance(self.sonicamp, SonicWipeDuty):
            self.gui.root.status_frame.change_values(gain=gain)

    def manage_relay(self) -> bool:

        if isinstance(self.sonicamp, SonicCatchOld) or isinstance(
            self.sonicamp, SonicCatchAncient
        ):
            if self.sonicamp.mode == KhzMode():
                self.sonicamp.set_mode(MhzMode())
            else:
                self.sonicamp.set_mode(KhzMode())

            return True

        elif isinstance(self.sonicamp, SonicCatch):
            if self.sonicamp.mode == WipeMode():
                self.sonicamp.set_mode(CatchMode())
            else:
                self.sonicamp.set_mode(WipeMode())

            return True

        else:
            return False

    def start_ramp(self, args_: list) -> None:
        """
        Starts the ramp process, and ramps up the frequency from a
        start value to a stop value. The resolution (step size) is also given
        from the passed argument. Additionally, a delay and the unit of that
        delay are also passed down.

        Args:
            args_ (list): [start, stop, step, delay, unit]
            example:
            [1200000, 1900000, 10000, 100, 'ms']
        """
        logger.info("Starting ramp")

        # declaring variables for easier use
        start: int = args_[0]
        stop: int = args_[1]
        step: int = args_[2]
        delay: int = args_[3]

        # Constructing an argument for the delay
        if len(args_) > 4:
            hold_argument: list = [delay, args_[4]]

        else:
            hold_argument: list = [delay]

        # in case the ramp should be decreasing
        if start > stop:

            frq_list: list[int] = list(range(stop, start, step))
            frq_list.sort(reverse=True)

        else:

            frq_list: list[int] = list(range(start, stop, step))

        # The core of the ramp function
        for frq in frq_list:

            if self.run:

                if isinstance(self.sonicamp, SonicWipeDuty):
                    self.gui.current_task.set(f"Ramp is @ {frq}%")
                    logger.info(f"Ramp is at {frq}%")
                    self.set_gain(frq)

                else:

                    self.gui.current_task.set(f"Ramp is @ {frq/1000}kHz")
                    logger.info(f"Ramp is at {frq/1000}kHz")

                    self.set_frq(frq)

                self.gui.status_handler(command="ramp", argument=args_)
                self.hold(hold_argument, ramp_mode=True)

            else:
                break

    def hold(self, args_: Union[list, int], ramp_mode: bool = False) -> None:
        """
        Holds the time during sequence, that was passed as an argument
        The user has the ability to control in which time unit the delay should
        be executed. More concretly:
            trailing 's' -> seconds
            trailing 'ms' -> milliseconds

        Args:
            args_ (list[Union[str, int]]): _description_
        """
        now: datetime.datetime = datetime.datetime.now()
        # Let us find out, what unit the delay should be in
        if isinstance(args_, int):
            # logger.info(f"Scriptingtab\tNo unit given\tusing seconds")
            target: datetime.datetime = now + datetime.timedelta(milliseconds=args_)

        elif len(args_) > 1 and args_[1] == "s":
            # logger.info(f"Scriptingtab\tunit given\t{args_[1] = }\tusing seconds")
            target: datetime.datetime = now + datetime.timedelta(seconds=args_[0])

        elif (len(args_) > 1 and args_[1] == "ms") or (len(args_) == 1):
            # logger.info(f"Scriptingtab\tunit given\t{args_[1] = }\tusing milliseconds")
            target: datetime.datetime = now + datetime.timedelta(milliseconds=args_[0])

        else:
            # logger.info(f"Scriptingtab\tno unit given\tusing seconds (else condition)")
            target: datetime.datetime = now + datetime.timedelta(milliseconds=args_[0])

        # The actual execute of the delay
        while now < target and self.run:

            time.sleep(0.02)
            now = datetime.datetime.now()

            if not ramp_mode:
                self.gui.current_task.set(
                    f"Hold: {(target - now).seconds} seconds remaining"
                )

            self.gui.root.update()

    def parse_commands(self, text: str) -> None:
        """
        Parse a string and split it into data parts
        Conretely into:
            self.commands -> a list of strings indicating which action to execute
            self.args_ -> a list of numbers and values for the commands
            self.loops -> data about index of loops, index of the end of loops and arguments

        Every list has the same length, indicating the line numbers

        Args:
            text (str): a str of text
        """
        # The string becomes a list of strings, in which each item resembles a line
        line_list: list[str] = text.rstrip().splitlines()

        for line in line_list:
            # Clean the line and split it where a white-space is
            line: list = line.rstrip().split(" ")

            # Go through each word or number item of that line
            for i, part in enumerate(line):

                part = (
                    part.rstrip()
                )  # Clean the part from leading and trailing white-spaces

                # If the part is numeric, it should be resembled as an integer, not a string
                if part.isnumeric():
                    line[i] = int(part)

                elif "," in part:
                    part: list = part.split(",")

                    for j, ramp_part in enumerate(part):
                        if ramp_part.isnumeric():
                            part[j] = int(ramp_part)

                        elif ramp_part[-2:] == "ms" and ramp_part[0].isdigit():
                            part[j] = int(ramp_part[:-2])
                            part.append(ramp_part[-2:])

                        elif (
                            ramp_part[-1:] == "s"
                            and ramp_part[-2:] != "ms"
                            and ramp_part[0].isdigit()
                        ):
                            part[j] = int(ramp_part[:-1])
                            part.append(ramp_part[-1:])

                    line[i] = part

                # If part has no length, it's essentially a empty part, we don't need that
                elif not len(part):
                    line.pop(i)

                # In case it's a delay that shows in which time unit it should be executet
                elif part[-2:] == "ms" and part[0].isdigit():
                    line[i] = int(part[:-2])
                    line.append(part[-2:])

                elif part[-1:] == "s" and part[-2:] != "ms" and part[0].isdigit():
                    line[i] = int(part[:-1])
                    line.append(part[-1:])

            # In case it"s a list with one element len() == 1
            self.commands.append(line[0])
            line.pop(0)

            if len(line) == 1:
                self.args_.append(line[0])

            else:
                self.args_.append(line)

        # We go through each command to look for loops
        for i, command in enumerate(self.commands):

            if command == "startloop":

                if self.args_[i] == "inf":
                    loopdata: list = [i, "inf"]

                elif isinstance(self.args_[i], int):
                    loopdata: list = [i, self.args_[i]]

                else:
                    loopdata: list = [i, "inf"]

                self.loops.insert(i, loopdata)

            elif command == "endloop":
                self.loops.insert(i, [])
                for loop in reversed(self.loops):

                    if len(loop) == 2:
                        loop.insert(2, i)
                        break

            else:
                self.loops.insert(i, [])

        logger.info(
            f"After parsing\tcommands = {self.commands}\targuments = {self.args_}\t loops = {self.loops}"
        )

    def close_sequence(self) -> None:

        if not self.run:
            self.run: bool = False

        self.gui.end()


class FileHandler(object):
    def __init__(self, gui: ScriptingTab) -> None:
        self.gui: ScriptingTab = gui

        self.script_filepath: str
        self.save_filename: str
        self.logfilename: str
        self.logfilepath: str = None

        self._filetypes: list[tuple] = [
            ("Text", "*.txt"),
            ("All files", "*"),
        ]
        self._sequence_dir: str = "ScriptingSequence"

        self.fieldnames: list = [
            "timestamp",
            "command",
            "argument",
            "signal",
            "frequency",
            "gain",
            "urms",
            "irms",
            "phase"
        ]

        if not os.path.exists(self._sequence_dir):
            os.mkdir(self._sequence_dir)

    def decide_logfile_name(self) -> None:
        tmp_timestamp: str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.logfilepath: str = f"{self._sequence_dir}//{tmp_timestamp}_{self.gui.root.sonicamp.type_}_sequence.csv"

        self._create_statuslog()

    def load_file(self) -> None:
        self.script_filepath: str = filedialog.askopenfilename(
            defaultextension=".txt", filetypes=self._filetypes
        )

        with open(self.script_filepath, "r") as f:
            self.gui.scripttext.delete(1.0, tk.END)
            self.gui.scripttext.insert(tk.INSERT, f.read())

    def save_file(self) -> None:
        self.save_filename = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=self._filetypes
        )

        with open(self.save_filename, "w") as f:
            f.write(self.gui.scripttext.get(1.0, tk.END))

    def open_logfile(self) -> None:
        self.logfilepath = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=self._filetypes
        )

    def _create_statuslog(self) -> None:
        """
        Internal method to create the csv status log file
        """
        if not isinstance(self.gui.root.sonicamp, SonicWipeDuty):
            with open(self.logfilepath, "a") as statuslog:
                csv_writer: csv.DictWriter = csv.DictWriter(
                    statuslog, fieldnames=self.fieldnames
                )
                csv_writer.writeheader()

    def register_data(
        self, command: str, argument: Union[int, list], status: Status
    ) -> None:
        
        if not isinstance(self.gui.root.sonicamp, SonicWipeDuty):
            data_dict: dict = {
                "timestamp": datetime.datetime.now(),
                "command": command,
                "argument": argument,
                "signal": status.signal,
                "frequency": status.frequency,
                "gain": status.gain,
                "urms": status.urms,
                "irms": status.irms,
                "phase": status.phase
            }

            with open(self.logfilepath, "a", newline="") as logfile:
                csv_writer: csv.DictWriter = csv.DictWriter(
                    logfile, fieldnames=self.fieldnames
                )
                csv_writer.writerow(data_dict)


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

        self.frq_btn: ScriptingGuideRow = ScriptingGuideRow(
            self,
            btn_text="frequency",
            arg_text="[50.000-6.000.000] in [Hz]",
            desc_text=None,
            command=lambda: self.insert_command(ScriptCommand.SET_FRQ),
        )

        ToolTip(self.frq_btn, text="Change to the indicated frequency in Hz")

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

        if not isinstance(self.root.sonicamp, SonicWipeOld) or isinstance(
            self.root.sonicamp, SonicWipeAncient
        ):
            self.gain_btn.pack(side=tk.TOP, padx=5, pady=5, anchor=tk.W)

        elif not isinstance(self.root.sonicamp, SonicWipeDuty):
            self.frq_btn.pack(side=tk.TOP, padx=5, pady=5, anchor=tk.W)

        self.disclaimer_label.pack(side=tk.TOP, expand=True, fill=tk.X, padx=5, pady=5)


class ScriptingGuideRow(ttk.Frame):
    def __init__(
        self,
        parent: ScriptingGuide,
        btn_text: str,
        arg_text: str,
        desc_text: str,
        command,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(parent, *args, **kwargs)

        self.command_btn: ttk.Button = ttk.Button(
            self, width=15, style="dark.TButton", text=btn_text, command=command
        )

        self.command_btn.grid(row=0, column=0, padx=5, pady=5, sticky=tk.NSEW)

        if arg_text:

            self.arg_label: ttk.Label = ttk.Label(
                self, style="inverse.info.TLabel", text=arg_text
            )

            self.arg_label.grid(row=0, column=2, padx=5, pady=5, sticky=tk.NSEW)

        if desc_text:

            self.desc_label: ttk.Label = ttk.Label(
                self, text=desc_text, style="inverse.primary.TLabel"
            )

            self.desc_label.grid(row=0, column=3, padx=5, pady=5, sticky=tk.NSEW)


# from __future__ import annotations

# import os
# import datetime
# import time
# import csv
# import tkinter as tk
# import tkinter.ttk as ttk

# from typing import Union, TYPE_CHECKING
# from enum import Enum
# from tkinter import messagebox
# from tkinter import filedialog
# from ttkbootstrap.tooltip import ToolTip

# from sonicpackage import Status, Command, SonicCatch, SonicWipeDuty, SonicWipe, SonicWipeOld, SonicCatchOld, SonicCatchAncient
# from soniccontrol.sonicamp import SerialConnection
# from soniccontrol.helpers import logger

# if TYPE_CHECKING:
#     from soniccontrol.core import Root
#     from soniccontrol._notebook import ScNotebook


# class ScriptCommand(Enum):
#     """
#     The ScriptCommand class is an enumaration class
#     that has it's builtin constants of strings, those
#     are being used for the function helper to insert
#     scripting commands into the scripting text frame

#     Inheritance:
#         Enum (enum.Enum): the python enumaration class
#     """
#     SET_FRQ: str = "frequency XXXXXXXX\n"
#     SET_GAIN: str = "gain XXX\n"
#     SET_KHZ: str = "setkHz\n"
#     SET_MHZ: str = "setMHz\n"
#     SET_SIGNAL_ON: str = "on\n"
#     SET_SIGNAL_OFF: str = "off\n"
#     SET_AUTO: str = "autotune\n"
#     SET_HOLD: str = "hold Xs\n"
#     STARTLOOP: str = "startloop X\n"
#     ENDLOOP: str = "endloop\n"
#     SET_RAMP: str = "ramp XXXXXXX XXXXXXX XXXX XXXms\n"


# class ScriptingTab(ttk.Frame):

#     @property
#     def root(self) -> Root:
#         return self._root

#     @property
#     def serial(self) -> SerialConnection:
#         return self._serial

#     def __init__(self, parent: ScNotebook, root: Root, *args, **kwargs) -> None:
#         super().__init__(parent, *args, **kwargs)

#         self._root: Root = root
#         self._serial: SerialConnection = root.serial

#         self.run: bool = False

#         self.script_filepath: str
#         self.save_filename: str
#         self.logfilename: str
#         self.logfilepath: str = None
#         self.current_task: tk.StringVar = tk.StringVar(value='Idle')
#         self.status: Status = Status()
#         self.previous_task: str = "Idle"

#         self._filetypes: list[tuple] = [('Text', '*.txt'),('All files', '*'),]

#         # Variables and functionality for the status_log of the scripting tab
#         self._sequence_dir: str = 'ScriptingSequence'
#         self.fieldnames: list = ['timestamp','command', 'argument', 'signal', 'frequency', 'gain']

#         if not os.path.exists(self._sequence_dir):
#             os.mkdir(self._sequence_dir)

#         # Building the tkinter GUI for the Tab
#         self.config(height=200, width=200)

#         self.button_frame: ttk.Frame = ttk.Frame(self)

#         self.start_script_btn = ttk.Button(
#             self.button_frame,
#             text='Run',
#             style='success.TButton',
#             width=11,
#             image=self.root.PLAY_IMG,
#             compound=tk.RIGHT,
#             command=self.configure_for_sequence,)

#         self.load_script_btn: ttk.Button = ttk.Button(
#             self.button_frame,
#             text='Open script file',
#             style='dark.TButton',
#             width=15,
#             command=self.load_file,)

#         self.save_script_btn: ttk.Button = ttk.Button(
#             self.button_frame,
#             text='Save script file',
#             style='dark.TButton',
#             width=15,
#             command=self.save_file,)

#         self.save_log_btn: ttk.Button = ttk.Button(
#             self.button_frame,
#             text='Specify logfile path',
#             style='dark.TButton',
#             width=15,
#             command=self.open_logfile)

#         self.script_guide_btn = ttk.Button(
#             self.button_frame,
#             text='Function Helper',
#             style='info.TButton',
#             width=15,
#             command=lambda: ScriptingGuide(self.root, self.scripttext))

#         ToolTip(self.script_guide_btn, text="Help regarding the scripting commands")

#         self.scripting_frame: ttk.Labelframe = ttk.Labelframe(
#             self,
#             text="Script Editor",
#             style="dark.TLabelframe",
#             padding=(5,5,5,5),)

#         self.scripttext: tk.Text = tk.Text(
#             self.scripting_frame,
#             autoseparators=False,
#             background='white',
#             setgrid=False,
#             width=35,
#             padx=5,
#             pady=5,
#             font=("Consolas", 12))

#         self.scrollbar: ttk.Scrollbar = ttk.Scrollbar(
#             self.scripting_frame,
#             orient='vertical',
#             command=self.scripttext.yview)

#         self.cur_task_label = ttk.Label(
#            self.scripting_frame,
#            justify=tk.CENTER,
#            anchor=tk.CENTER,
#            style="dark.TLabel",
#            textvariable=self.current_task)

#         self.sequence_status: ttk.Progressbar = ttk.Progressbar(
#             self.scripting_frame,
#             length=160,
#             mode="indeterminate",
#             orient=tk.HORIZONTAL,
#             style="dark.TProgressbar",)

#     def publish(self):
#         """
#         Method to publish every component and show the tab visually in the GUI
#         """
#         # Button Frame
#         self.button_frame.pack(anchor=tk.N, side=tk.LEFT, padx=5, pady=5)

#         for child in self.button_frame.winfo_children():
#             child.pack(side=tk.TOP, padx=5, pady=5)

#         # Scripting Frame
#         self.scripting_frame.pack(anchor=tk.N ,side=tk.RIGHT ,padx=5, pady=5, expand=True, fill=tk.X)
#         self.scripttext.grid(row=0, column=0, columnspan=2)
#         self.cur_task_label.grid(row=1, column=0, padx=0, pady=5, sticky=tk.EW, columnspan=2)
#         self.sequence_status.grid(row=2, column=0, padx=0, pady=5, sticky=tk.EW, columnspan=2)

#     def load_file(self) -> None:
#         """
#         Method to load a already existing script to the text frame
#         """
#         self.script_filepath = filedialog.askopenfilename(defaultextension='.txt', filetypes=self._filetypes)

#         with open(self.script_filepath, 'r') as f:
#             self.scripttext.delete(0, tk.END)
#             self.scripttext.insert(tk.INSERT, f.read())

#     def save_file(self) -> None:
#         """
#         Method to save the written script in the text frame to a txt file
#         """
#         self.save_filename = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=self._filetypes)

#         with open(self.save_filename, 'w') as f:
#             f.write(self.scripttext.get(0, tk.END))

#     def open_logfile(self) -> None:
#         """
#         Method to change the saving location of the logfile
#         """
#         self.logfilepath = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=self._filetypes)

#     def close_sequence(self) -> None:
#         """
#         Function that closes the scripting sequence

#         Direclty stops the sequence and changes the appearence
#         of the GUI. The start button now directs to the
#         self.start_sequence method of the scripting tab
#         """
#         self.run: bool = False

#         self.logfilepath: str = None

#         self.start_script_btn.configure(
#             text='Run',
#             style='success.TButton',
#             image=self.root.PLAY_IMG,
#             command=self.configure_for_sequence)

#         # Changing GUI elemets so that everything looks different
#         self.scripttext.tag_delete("currentLine", 1.0, tk.END)
#         self.sequence_status.stop()
#         self.current_task.set("Idle")
#         self.previous_task = "Idle"
#         self.root.notebook.enable_children()
#         # Changing the state of the Buttons
#         self.scripttext.config(state=tk.NORMAL)
#         self.load_script_btn.config(state=tk.NORMAL)
#         self.save_script_btn.config(state=tk.NORMAL)
#         self.save_log_btn.config(state=tk.NORMAL)
#         self.script_guide_btn.config(state=tk.NORMAL)
#         self.sequence_status.config(text=None)

#         self.serial.send_and_get(Command.SET_SIGNAL_OFF)

#         self.root.attach_data()

#         if not isinstance(self.root.sonicamp, SonicWipeDuty):
#             self.root.thread.resume()

#     def _create_statuslog(self) -> None:
#         """
#         Internal method to create the csv status log file
#         """
#         with open(self.logfilepath, "a") as statuslog:
#             csv_writer: csv.DictWriter = csv.DictWriter(
#                 statuslog, fieldnames=self.fieldnames)
#             csv_writer.writeheader()

#     def configure_for_sequence(self) -> None:
#         """
#         Method that starts the scripting sequence

#         Gets the tab into a loop that checks if the self.run attribute
#         is set to true or false. True being further try to run the
#         sequence and false being stop the sequence. The stop button
#         is being configured so that it can stop the sequence immediatley
#         through the self.close_sequence method
#         """
#         self.run: bool = True

#         if not self.logfilepath:
#             tmp_timestamp: str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#             self.logfilepath: str = f"{self._sequence_dir}//{tmp_timestamp}_{self.root.sonicamp.type_}_sequence.csv"

#         with open(self.logfilepath, "a", newline="") as logfile:
#             csv_writer: csv.DictWriter = csv.DictWriter(
#                 logfile, fieldnames=self.fieldnames)
#             csv_writer.writeheader()

#         if not self.root.thread.paused:
#             self.root.thread.pause()

#         self.start_script_btn.configure(
#             text='Stop',
#             style='danger.TButton',
#             image=self.root.PAUSE_IMG,
#             command=self.close_sequence)

#         self.sequence_status.start()
#         self.root.notebook.disable_children(self)
#         self.scripttext.config(state=tk.DISABLED)
#         self.load_script_btn.config(state=tk.DISABLED)
#         self.save_log_btn.config(state=tk.DISABLED)
#         self.save_script_btn.config(state=tk.DISABLED)
#         self.script_guide_btn.config(state=tk.DISABLED)

#         self.serial.send_and_get(Command.SET_SIGNAL_ON)

#         self.status_handler()
#         self.start_sequence()

#     def set_run(self, state: bool) -> None:
#         """
#         The sequence checks the run flag constantly, so this function
#         acts as a setter of that variable

#         Args:
#             state (bool): The to be setted state
#         """
#         self.run: bool = state

#     def highlight_line(self, current_line: int) -> None:
#         """
#         Function that highlights the current line of the sequence in the script editor
#         The argument current_line

#         Args:
#             current_line (int): current line in the script, that need to be highlighted
#         """
#         current_line += 1
#         self.scripttext.tag_remove('currentLine', 1.0, "end")
#         self.scripttext.tag_add('currentLine', f"{current_line}.0", f"{current_line}.end")
#         self.scripttext.tag_configure('currentLine', background="#3e3f3a", foreground="#dfd7ca")

#     def start_sequence(self) -> None:
#         """
#         Method that has the main loop of the sequence

#         Here everything is being managed. Every method that needs to be
#         run, is being launched accordingly in the while loop.

#         Before the loop has started the scripting text is being parsed
#         and saved to lists of commands, arguments and loops (startloop, endloop commands)
#         """
#         self.commands: list[str] = []
#         self.args_: list[str] = []
#         self.loops: list[list[int]] = [[]]
#         self.loop_index: int = 0

#         # Try to parse the string from the textfield and get the data into ordered arrays
#         # If it fails, the formatting supposedely is false, so an error is shown
#         try:
#             self.parse_commands(self.scripttext.get(1.0, tk.END))

#         except Exception as e:
#             logger.warning(f"Error while trying to parse: {e}")
#             messagebox.showerror("Error in formatting", "It seems you've given commands or arguments in the wrong format")
#             self.run: bool = False

#         line: int = 0
#         while line < len(self.commands) and self.run:
#             self.highlight_line(line)

#             if self.commands[line] == 'startloop':

#                 logger.debug(f"Found startloop command at {line}, with the quantifier {self.loops[line][1]}")
#                 if self.loops[line][1] and isinstance(self.loops[line][1], int):
#                     self.loops[line][1] -= 1
#                     line += 1

#                 elif self.loops[line][1] == 'inf':
#                     line += 1

#                 else:
#                     logger.debug(f"Jumping to line {self.loops[line][2] + 1}, because quantifier is 0")
#                     line: int = self.loops[line][2] + 1

#             elif self.commands[line] == 'endloop':

#                 logger.debug(f"Found endloop command at {line}")
#                 for loop in self.loops:

#                     if loop and loop[2] == line:

#                         for j in range(loop[0]+1, loop[2]):

#                             if self.loops[j]:
#                                 logger.info(f"Found loop to be reseted: {self.loops[j]}")
#                                 self.loops[j][1] = self.args_[j]

#                         line: int = loop[0]

#             else:
#                 logger.info(f"Executing command at\t{line}")
#                 self.exec_command(line)
#                 line += 1

#         # So that the close_sequence function doesn't get called two times
#         if not self.run:
#             return

#         else:
#             self.close_sequence()


#     def status_handler(self) -> None:
#         """
#         Update the Root Window at the status frame to display the current data from the sequence
#         """
#         try:

#             if not isinstance(self.root.sonicamp, SonicWipeDuty):
#                 self.status: Status = self.root.sonicamp.get_status()

#             else:
#                 self.status.frequency = 40000

#             logger.info(f"Got status: {self.status}")

#         except ValueError:
#             pass

#         if isinstance(self.root.sonicamp, SonicCatch) or isinstance(self.root.sonicamp, SonicCatchOld):

#             self.root.status_frame.gain_meter["amountused"] = self.status.gain
#             self.root.status_frame.frq_meter["amountused"] = self.status.frequency / 1000

#             if self.status.signal:
#                 self.root.status_frame.sig_status_label["text"] = "Signal ON"
#                 self.root.status_frame.sig_status_label["image"] = self.root.led_green_img

#             else:
#                 self.root.status_frame.sig_status_label["text"] = "Signal OFF"
#                 self.root.status_frame.sig_status_label["image"] = self.root.led_red_img

#         elif isinstance(self.root.sonicamp, SonicWipe) or isinstance(self.root.sonicamp, SonicWipeOld):

#             self.root.status_frame.frq_meter["amountused"] = self.status.frequency / 1000

#             if self.status.signal:
#                 self.root.status_frame.sig_status_label["text"] = "Signal ON"
#                 self.root.status_frame.sig_status_label["image"] = self.root.led_green_img

#             else:
#                 self.root.status_frame.sig_status_label["text"] = "Signal OFF"
#                 self.root.status_frame.sig_status_label["image"] = self.root.led_red_img

#         self.root.update()

#     def exec_command(self, counter: int) -> None:
#         """
#         This function manages the execution of functions
#         and manages the visualization of the execution

#         Args:
#             counter (int): The index of the line
#         """
#         self.highlight_line(counter)

#         # For the visual feedback of the sequence
#         self.current_task.set(f"{self.commands[counter]} {str(self.args_[counter])}")
#         if counter > 0:
#             self.previous_task: str = f"{self.commands[counter-1]} {self.args_[counter-1]}"

#         # Just for managing purposes
#         if isinstance(self.args_[counter], list):

#             if len(self.args_[counter]) == 1:
#                 argument: int = self.args_[counter][0]
#             else:
#                 argument: list = self.args_[counter]

#         else:

#             argument: int = self.args_[counter]


#         if self.run:

#             logger.info(f"Executing command: {self.commands[counter]}")

#             if self.commands[counter] == "frequency":
#                 self.check_relay(frq=argument)
#                 self.check_for_duty_wipe(frq=argument)
#                 self.serial.send_and_get(Command.SET_FRQ + argument)

#             elif self.commands[counter] == "gain":
#                 self.check_relay(gain=argument)
#                 self.check_for_duty_wipe(gain=argument)
#                 self.serial.send_and_get(Command.SET_GAIN + argument)

#             elif self.commands[counter] == "ramp":
#                 self.start_ramp(argument)

#             elif self.commands[counter] == "hold":
#                 self.hold(argument)

#             elif self.commands[counter] == "on":
#                 self.check_for_duty_wipe(on=True)
#                 self.serial.send_and_get(Command.SET_SIGNAL_ON)

#             elif self.commands[counter] == "off":
#                 self.check_for_duty_wipe(off=True)
#                 self.serial.send_and_get(Command.SET_SIGNAL_OFF)

#             else:
#                 messagebox.showerror("Wrong command", f"the command {self.commands[counter]} is not known, please use the correct commands in the correct syntax")
#                 self.close_sequence()

#         self.status_handler()
#         self.register_data(self.commands[counter], argument=argument)

#     def register_data(self, command: str, argument: Union[int, list]) -> None:

#         data_dict: dict = {
#             "timestamp": datetime.datetime.now(),
#             "command": command,
#             "argument": argument,
#             "signal": self.status.signal,
#             "frequency": self.status.frequency,
#             "gain": self.status.gain,
#         }

#         with open(self.logfilepath, "a", newline="") as logfile:
#             csv_writer: csv.DictWriter = csv.DictWriter(
#                 logfile, fieldnames=self.fieldnames)
#             csv_writer.writerow(data_dict)

#     def hold(self, args_: Union[list, int], ramp_mode: bool = False) -> None:
#         """
#         Holds the time during sequence, that was passed as an argument
#         The user has the ability to control in which time unit the delay should
#         be executed. More concretly:
#             trailing 's' -> seconds
#             trailing 'ms' -> milliseconds

#         Args:
#             args_ (list[Union[str, int]]): _description_
#         """
#         now: datetime.datetime = datetime.datetime.now()
#         # Let us find out, what unit the delay should be in
#         if isinstance(args_, int):
#             # logger.info(f"Scriptingtab\tNo unit given\tusing seconds")
#             target: datetime.datetime = now + datetime.timedelta(milliseconds=args_)

#         elif (len(args_) > 1 and args_[1] == 's'):
#             # logger.info(f"Scriptingtab\tunit given\t{args_[1] = }\tusing seconds")
#             target: datetime.datetime = now + datetime.timedelta(seconds=args_[0])

#         elif (len(args_) > 1 and args_[1] == 'ms') or (len(args_) == 1):
#             # logger.info(f"Scriptingtab\tunit given\t{args_[1] = }\tusing milliseconds")
#             target: datetime.datetime = now + datetime.timedelta(milliseconds=args_[0])

#         else:
#             # logger.info(f"Scriptingtab\tno unit given\tusing seconds (else condition)")
#             target: datetime.datetime = now + datetime.timedelta(milliseconds=args_[0])

#         # The actual execute of the delay
#         while now < target and self.run:

#             time.sleep(0.02)
#             now = datetime.datetime.now()

#             if not ramp_mode:
#                 self.current_task.set(f"Hold: {(target - now).seconds} seconds remaining")

#             self.root.update()

#     def check_relay(self, frq: int = 0, gain: int = 0) -> None:
#         """
#         Function that checks the current relay setting in a soniccatch and changes
#         the relay accordingly, so that the frequency set would be possible

#         Args:
#             frq (int):  The frequency that should be set
#             gain (int): The gain that should be setted, if needed
#         """
#         running_soniccatch: bool = self.run and (isinstance(self.root.sonicamp, SonicCatchOld) or isinstance(self.root.sonicamp, SonicCatchAncient))

#         if (running_soniccatch and frq >= 1000000 and self.status.frequency < 1000000) or (running_soniccatch and gain and self.status.frequency >= 1000000):

#             logger.info(f"Checking relay -> Setting to MHz")
#             self.serial.send_and_get(Command.SET_MHZ)
#             self.serial.send_and_get(Command.SET_SIGNAL_ON)

#         elif running_soniccatch and  frq < 1000000 and self.status.frequency >= 1000000:

#             logger.info(f"Checking relay -> Setting to kHz")
#             self.serial.send_and_get(Command.SET_KHZ)
#             self.serial.send_and_get(Command.SET_SIGNAL_ON)

#         elif running_soniccatch and gain and self.status.frequency < 1000000:

#             self.close_sequence()
#             messagebox.showerror("Semantic error", "Gain setting is not supported for frequencies under 1MHz. Please make sure that the frequency is over 1MHz when setting the gain")

#     def check_for_duty_wipe(self, frq: int = 0, gain: int = 0, on: bool = None, off: bool = None) -> None:

#         is_duty_wipe: bool = isinstance(self.root.sonicamp, SonicWipeDuty)

#         if is_duty_wipe and frq:
#             messagebox.showerror("Not supported", "You cannot set frequency with this device")

#         elif is_duty_wipe and gain:

#             self.status.gain = gain
#             self.root.status_frame.gain_meter["amountused"] = gain

#         elif is_duty_wipe and on and not off:

#             self.status.signal = True
#             self.root.status_frame.sig_status_label["text"] = "Signal ON"
#             self.root.status_frame.sig_status_label["image"] = self.root.led_green_img

#         elif is_duty_wipe and not on and off:

#             self.status.signal = False
#             self.root.status_frame.sig_status_label["text"] = "Signal OFF"
#             self.root.status_frame.sig_status_label["image"] = self.root.led_red_img


#     def start_ramp(self, args_: list) -> None:
#         """
#         Starts the ramp process, and ramps up the frequency from a
#         start value to a stop value. The resolution (step size) is also given
#         from the passed argument. Additionally, a delay and the unit of that
#         delay are also passed down.

#         Args:
#             args_ (list): [start, stop, step, delay, unit]
#             example:
#             [1200000, 1900000, 10000, 100, 'ms']
#         """
#         logger.info("Starting ramp")

#         # declaring variables for easier use
#         start: int = args_[0]
#         stop: int = args_[1]
#         step: int = args_[2]
#         delay: int = args_[3]

#         # Constructing an argument for the delay
#         if len(args_) > 4:
#             hold_argument: list = [delay, args_[4]]

#         else:
#             hold_argument: list = [delay]

#         # in case the ramp should be decreasing
#         if start > stop:

#             frq_list: list[int] = list(range(stop, start+step, step))
#             frq_list.sort(reverse=True)

#         else:

#             frq_list: list[int] = list(range(start, stop+step, step))

#         # The core of the ramp function
#         for frq in frq_list:

#             if self.run:

#                 self.check_relay(frq)

#                 if isinstance(self.root.sonicamp, SonicWipeDuty):
#                     self.current_task.set(f"Ramp is @ {frq}%")
#                     logger.info(f"Ramp is at {frq}%")

#                     self.serial.send_and_get(Command.SET_GAIN + frq)
#                     self.check_for_duty_wipe(gain=frq)

#                 else:

#                     self.current_task.set(f"Ramp is @ {frq/1000}kHz")
#                     logger.info(f"Ramp is at {frq/1000}kHz")

#                     self.serial.send_and_get(Command.SET_FRQ + frq)

#                 self.status_handler()

#                 self.register_data(command="ramp", argument=args_)

#                 self.hold(hold_argument, ramp_mode=True)

#             else:
#                 break

#     def parse_commands(self, text: str) -> None:
#         """
#         Parse a string and split it into data parts
#         Conretely into:
#             self.commands -> a list of strings indicating which action to execute
#             self.args_ -> a list of numbers and values for the commands
#             self.loops -> data about index of loops, index of the end of loops and arguments

#         Every list has the same length, indicating the line numbers

#         Args:
#             text (str): a str of text
#         """
#         # The string becomes a list of strings, in which each item resembles a line
#         line_list: list[str] = text.rstrip().splitlines()

#         for line in line_list:
#             # Clean the line and split it where a white-space is
#             line: list = line.rstrip().split(' ')

#             # Go through each word or number item of that line
#             for i, part in enumerate(line):

#                 part = part.rstrip()                    # Clean the part from leading and trailing white-spaces

#                 # If the part is numeric, it should be resembled as an integer, not a string
#                 if part.isnumeric():
#                     line[i] = int(part)

#                 elif ',' in part:
#                     part: list = part.split(',')

#                     for j, ramp_part in enumerate(part):
#                         if ramp_part.isnumeric():
#                             part[j] = int(ramp_part)

#                         elif ramp_part[-2:] == 'ms' and ramp_part[0].isdigit():
#                             part[j] = int(ramp_part[:-2])
#                             part.append(ramp_part[-2:])

#                         elif ramp_part[-1:] == 's' and ramp_part[-2:] != 'ms' and ramp_part[0].isdigit():
#                             part[j] = int(ramp_part[:-1])
#                             part.append(ramp_part[-1:])

#                     line[i] = part

#                 # If part has no length, it's essentially a empty part, we don't need that
#                 elif not len(part):
#                     line.pop(i)

#                 # In case it's a delay that shows in which time unit it should be executet
#                 elif part[-2:] == 'ms' and part[0].isdigit():
#                     line[i] = int(part[:-2])
#                     line.append(part[-2:])

#                 elif part[-1:] == 's' and part[-2:] != 'ms' and part[0].isdigit():
#                     line[i] = int(part[:-1])
#                     line.append(part[-1:])

#             # In case it"s a list with one element len() == 1
#             self.commands.append(line[0])
#             line.pop(0)

#             if len(line) == 1:
#                 self.args_.append(line[0])

#             else:
#                 self.args_.append(line)

#         # We go through each command to look for loops
#         for i, command in enumerate(self.commands):

#             if command == "startloop":

#                 if self.args_[i] == 'inf':
#                     loopdata: list = [i, 'inf']

#                 elif isinstance(self.args_[i], int):
#                     loopdata: list = [i, self.args_[i]]

#                 else:
#                     loopdata: list = [i, 'inf']

#                 self.loops.insert(i, loopdata)

#             elif command == "endloop":
#                 self.loops.insert(i, [])
#                 for loop in reversed(self.loops):

#                     if len(loop) == 2:
#                         loop.insert(2, i)
#                         break

#             else:
#                 self.loops.insert(i, [])

#         logger.info(f"After parsing\tcommands = {self.commands}\targuments = {self.args_}\t loops = {self.loops}")

#     def attach_data(self) -> None:
#         pass


# class ScriptingGuide(tk.Toplevel):

#     def __init__(self, root: Root, scripttext: tk.Text, *args, **kwargs) -> None:
#         super().__init__(root, *args, **kwargs)
#         self.title('Function Helper')

#         self.root: Root = root
#         self.scripttext: tk.Text = scripttext

#         self.heading_frame: ttk.Frame = ttk.Frame(self)

#         self.heading_command = ttk.Label(
#             self.heading_frame,
#             anchor=tk.W,
#             justify=tk.CENTER,
#             text='Command',
#             width=15,
#             style="dark.TLabel",
#             font="QTypeOT-CondMedium 15 bold",)

#         self.heading_arg = ttk.Label(
#             self.heading_frame,
#             anchor=tk.W,
#             justify=tk.CENTER,
#             width=15,
#             style="info.TLabel",
#             text='Arguments',
#             font="QTypeOT-CondMedium 15 bold",)

#         self.hold_btn: ScriptingGuideRow = ScriptingGuideRow(
#             self,
#             btn_text="hold",
#             arg_text="[1-10^6] in [seconds/ milliseconds] (depending on what you write e.g: 100ms, 5s, nothing defaults to milliseconds)",
#             desc_text=None,
#             command=lambda: self.insert_command(ScriptCommand.SET_HOLD),)

#         ToolTip(self.hold_btn, text="Hold the last state for X seconds/ milliseconds, depending on what unit you have given")

#         self.frq_btn: ScriptingGuideRow = ScriptingGuideRow(
#             self,
#             btn_text='frequency',
#             arg_text='[50.000-6.000.000] in [Hz]',
#             desc_text=None,
#             command = lambda: self.insert_command(ScriptCommand.SET_FRQ))

#         ToolTip(self.frq_btn, text='Change to the indicated frequency in Hz')

#         self.gain_btn: ScriptingGuideRow = ScriptingGuideRow(
#             self,
#             btn_text='gain',
#             arg_text='[1-150] in [%]',
#             desc_text=None,
#             command = lambda: self.insert_command(ScriptCommand.SET_GAIN))

#         ToolTip(self.gain_btn, text='Change to the selected gain in %')

#         self.on_btn: ScriptingGuideRow = ScriptingGuideRow(
#             self,
#             btn_text='on',
#             arg_text=None,
#             desc_text=None,
#             command = lambda: self.insert_command(ScriptCommand.SET_SIGNAL_ON))

#         ToolTip(self.on_btn, text='Activate US emission')

#         self.off_btn: ScriptingGuideRow = ScriptingGuideRow(
#             self,
#             btn_text='off',
#             arg_text=None,
#             desc_text=None,
#             command = lambda: self.insert_command(ScriptCommand.SET_SIGNAL_OFF))

#         ToolTip(self.off_btn, text='Deactivate US emission')

#         self.startloop_btn: ScriptingGuideRow = ScriptingGuideRow(
#             self,
#             btn_text='startloop',
#             arg_text='[2-10.000] as an [integer]',
#             desc_text=None,
#             command = lambda: self.insert_command(ScriptCommand.STARTLOOP))

#         ToolTip(self.startloop_btn, text='Start a loop for X times')

#         self.endloop_btn: ScriptingGuideRow = ScriptingGuideRow(
#             self,
#             btn_text='endloop',
#             arg_text=None,
#             desc_text=None,
#             command = lambda: self.insert_command(ScriptCommand.ENDLOOP))

#         ToolTip(self.endloop_btn, text='End the loop here')

#         self.ramp_btn: ScriptingGuideRow = ScriptingGuideRow(
#             self,
#             btn_text='ramp',
#             arg_text='<start f [Hz]> <stop f [Hz]> <step size [Hz]> <delay [ms / s]><unit of time> \nThe delay should be written like a hold (e.g: 100ms, 5s, nothing defaults to milliseconds)',
#             desc_text=None,
#             command = lambda: self.insert_command(ScriptCommand.SET_RAMP))

#         ToolTip(self.ramp_btn, text='Create a frequency ramp with a start frequency, a stop frequency,\n a step size and a delay between steps\nExpamle: ramp 50000 1200000 1000 100ms')

#         self.disclaimer_label: ttk.Label = ttk.Label(
#             self,
#             text='To insert a function at the cursor position, click on the respective button',
#             font=('TkDefaultFont', 11, 'bold'))

#         self.publish()

#     def insert_command(self, command: ScriptCommand) -> None:
#         self.scripttext.insert(self.scripttext.index(tk.INSERT), command.value)

#     def publish(self) -> None:
#         self.heading_command.grid(row=0, column=0, padx=5, pady=5, sticky=tk.NSEW)
#         self.heading_arg.grid(row=0, column=1, padx=5, pady=5, sticky=tk.NSEW)
#         self.heading_frame.pack(side=tk.TOP, padx=5, pady=5, anchor=tk.W, expand=True, fill=tk.X)
#         self.hold_btn.pack(side=tk.TOP, padx=5, pady=5, anchor=tk.W)
#         self.on_btn.pack(side=tk.TOP, padx=5, pady=5, anchor=tk.W)
#         self.off_btn.pack(side=tk.TOP, padx=5, pady=5, anchor=tk.W)
#         self.startloop_btn.pack(side=tk.TOP, padx=5, pady=5, anchor=tk.W)
#         self.endloop_btn.pack(side=tk.TOP, padx=5, pady=5, anchor=tk.W)
#         self.ramp_btn.pack(side=tk.TOP, padx=5, pady=5, anchor=tk.W)

#         if self.root.sonicamp.type_ == 'soniccatch' or isinstance(self.root.sonicamp, SonicWipeDuty):
#             self.gain_btn.pack(side=tk.TOP, padx=5, pady=5, anchor=tk.W)

#         elif not isinstance(self.root.sonicamp, SonicWipeDuty):
#             self.frq_btn.pack(side=tk.TOP, padx=5, pady=5, anchor=tk.W)

#         self.disclaimer_label.pack(side=tk.TOP, expand=True, fill=tk.X, padx=5, pady=5)


# class ScriptingGuideRow(ttk.Frame):

#     def __init__(self, parent: ScriptingGuide, btn_text: str, arg_text: str, desc_text: str, command, *args, **kwargs) -> None:
#         super().__init__(parent, *args, **kwargs)

#         self.command_btn: ttk.Button = ttk.Button(
#             self,
#             width=15,
#             style="dark.TButton",
#             text=btn_text,
#             command=command)

#         self.command_btn.grid(row=0, column=0, padx=5, pady=5, sticky=tk.NSEW)

#         if arg_text:

#             self.arg_label: ttk.Label = ttk.Label(
#                 self,
#                 style='inverse.info.TLabel',
#                 text=arg_text)

#             self.arg_label.grid(row=0, column=2, padx=5, pady=5, sticky=tk.NSEW)

#         if desc_text:

#             self.desc_label: ttk.Label = ttk.Label(
#                 self,
#                 text=desc_text,
#                 style='inverse.primary.TLabel')

#             self.desc_label.grid(row=0, column=3, padx=5, pady=5, sticky=tk.NSEW)
