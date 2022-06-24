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
from ttkbootstrap.tooltip import ToolTip

from sonicpackage import Status, Command, SonicCatch, SonicWipeDuty, SonicWipe, SonicWipeOld, SonicCatchOld
from soniccontrol.sonicamp import SerialConnection, SerialConnectionGUI
from soniccontrol.helpers import logger

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
    
    @property
    def root(self) -> Root:
        return self._root
    
    @property
    def serial(self) -> SerialConnectionGUI:
        return self._serial
    
    @property
    def sequence(self) -> Sequence:
        return self._sequence
    
    def __init__(self, parent: ScNotebook, root: Root, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self.config(height=200, width=200)
        
        self._root: Root = root
        self._serial: SerialConnectionGUI = root.serial
        self._sequence: Sequence = Sequence(self)
        
        self._initialize_button_frame()
        self._initialize_scripting_frame()
        
    def _initialize_button_frame(self) -> None:
        self.button_frame: ttk.Frame = ttk.Frame(self)
        
        self.start_script_btn = ttk.Button(
            self.button_frame,
            text='Run',
            style='success.TButton',
            width=11,
            image=self.root.play_img,
            compound=tk.RIGHT,
            command=,
        )
        
        self.load_script_btn: ttk.Button = ttk.Button(
            self.button_frame,
            text='Open script file',
            style='dark.TButton',
            width=15,
            command=
        )
        
        self.save_script_btn: ttk.Button = ttk.Button(
            self.button_frame,
            text='Save script file',
            style='dark.TButton',
            width=15,
            command=
        )
        
        self.save_log_btn: ttk.Button = ttk.Button(
            self.button_frame,
            text='Specify logfile path',
            style='dark.TButton',
            width=15,
            command=
        )
        
        self.script_guide_btn = ttk.Button(
            self.button_frame,
            text='Function Helper',
            style='info.TButton',
            width=15,
            command=
        )
        
        ToolTip(
            self.script_guide_btn, 
            text="Help regarding the scripting commands"
        )
    
    def _initialize_scripting_frame(self) -> None:
        self.scripting_frame: ttk.Labelframe = ttk.Labelframe(
            self,
            text="Script Editor",
            style="dark.TLabelframe",
            padding=(5,5,5,5),
        )
        
        self.scripttext: tk.Text = tk.Text(
            self.scripting_frame,
            autoseparators=False,
            background='white',
            setgrid=False,
            width=35,
            padx=5,
            pady=5,
            font=("Consolas", 12)
        )
        
        self.scrollbar: ttk.Scrollbar = ttk.Scrollbar(
            self.scripting_frame,
            orient='vertical',
            command=self.scripttext.yview
        )  
        
        self.cur_task_label = ttk.Label(
           self.scripting_frame,
           justify=tk.CENTER,
           anchor=tk.CENTER,
           style="dark.TLabel",
           textvariable=self.current_task
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
        self.scripttext.tag_remove('currentLine', 1.0, "end")
        self.scripttext.tag_add('currentLine', f"{current_line}.0", f"{current_line}.end")
        self.scripttext.tag_configure('currentLine', background="#3e3f3a", foreground="#dfd7ca")

    def publish(self):
        """
        Method to publish every component and show the tab visually in the GUI
        """
        # Button Frame
        self.button_frame.pack(anchor=tk.N, side=tk.LEFT, padx=5, pady=5)
        
        for child in self.button_frame.winfo_children():
            child.pack(side=tk.TOP, padx=5, pady=5)

        # Scripting Frame
        self.scripting_frame.pack(anchor=tk.N ,side=tk.RIGHT ,padx=5, pady=5, expand=True, fill=tk.X)
        self.scripttext.grid(row=0, column=0, columnspan=2)
        self.cur_task_label.grid(row=1, column=0, padx=0, pady=5, sticky=tk.EW, columnspan=2)
        self.sequence_status.grid(row=2, column=0, padx=0, pady=5, sticky=tk.EW, columnspan=2)
        


class Sequence(object):
    
    def __init__(self, gui: ScriptingTab) -> None:
        
        self.gui: ScriptingTab = gui
        self.serial: SerialConnectionGUI = gui.serial
        
        self.run: bool = False
        
        self.commands: list = []
        self.args_: list = []
        self.loops: list = []
        
    def start(self) -> None:
        
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
                "It seems you've given commands or arguments in the wrong format"
            )
            
            self.run: bool = False
        
        self.loop()
        
    def loop(self) -> None:
        line: int = 0
        while line < len(self.commands) and self.run:
            self.gui.highlight_line(line)
            
            if self.commands[line] == 'startloop':
                
                logger.debug(f"Found startloop command at {line}, with the quantifier {self.loops[line][1]}")
                if self.loops[line][1] and isinstance(self.loops[line][1], int):
                    self.loops[line][1] -= 1
                    line += 1
                
                elif self.loops[line][1] == 'inf':
                    line += 1
                
                else:
                    logger.debug(f"Jumping to line {self.loops[line][2] + 1}, because quantifier is 0")
                    line: int = self.loops[line][2] + 1
            
            elif self.commands[line] == 'endloop':
                
                logger.debug(f"Found endloop command at {line}")
                for loop in self.loops:
                    
                    if loop and loop[2] == line:
                        
                        for j in range(loop[0]+1, loop[2]):
                            
                            if self.loops[j]:
                                logger.info(f"Found loop to be reseted: {self.loops[j]}")
                                self.loops[j][1] = self.args_[j]
                        
                        line: int = loop[0]
                        
            else:
                logger.info(f"Executing command at\t{line}")
                self.exec_command(line)
                line += 1
    
    def exec_command(self, counter: int) -> None:
        """
        This function manages the execution of functions
        and manages the visualization of the execution

        Args:
            counter (int): The index of the line
        """
        self.gui.highlight_line(counter)

        # For the visual feedback of the sequence
        self.current_task.set(f"{self.commands[counter]} {str(self.args_[counter])}")
        if counter > 0:
            self.previous_task: str = f"{self.commands[counter-1]} {self.args_[counter-1]}"

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
                self.serial.send_and_get(Command.SET_FRQ + argument)
            
            elif self.commands[counter] == "gain":
                self.serial.send_and_get(Command.SET_GAIN + argument)
            
            elif self.commands[counter] == "ramp":
                self.start_ramp(argument)
            
            elif self.commands[counter] == "hold":
                self.hold(argument)
            
            elif self.commands[counter] == "on":
                self.serial.send_and_get(Command.SET_SIGNAL_ON)
            
            elif self.commands[counter] == "off":
                self.serial.send_and_get(Command.SET_SIGNAL_OFF)
                
            else:
                messagebox.showerror("Wrong command", f"the command {self.commands[counter]} is not known, please use the correct commands in the correct syntax")
                self.close_sequence()
        
        self.status_handler()
        self.register_data(self.commands[counter], argument=argument)
        
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
            
            frq_list: list[int] = list(range(stop, start+step, step))
            frq_list.sort(reverse=True)
        
        else:
            
            frq_list: list[int] = list(range(start, stop+step, step))

        # The core of the ramp function
        for frq in frq_list:
            
            if self.run:
                
                if isinstance(self.root.sonicamp, SonicWipeDuty):
                    self.gui.current_task.set(f"Ramp is @ {frq}%")
                    logger.info(f"Ramp is at {frq}%")
                    
                    self.serial.send_and_get(Command.SET_GAIN + frq)
                    self.check_for_duty_wipe(gain=frq)
                
                else:
                    
                    self.current_task.set(f"Ramp is @ {frq/1000}kHz")
                    logger.info(f"Ramp is at {frq/1000}kHz")
                    
                    self.serial.send_and_get(Command.SET_FRQ + frq)
                
                self.status_handler()
                
                self.register_data(command="ramp", argument=args_)
                
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
        
        elif (len(args_) > 1 and args_[1] == 's'):
            # logger.info(f"Scriptingtab\tunit given\t{args_[1] = }\tusing seconds")
            target: datetime.datetime = now + datetime.timedelta(seconds=args_[0])
        
        elif (len(args_) > 1 and args_[1] == 'ms') or (len(args_) == 1):
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
                self.gui.current_task.set(f"Hold: {(target - now).seconds} seconds remaining")
            
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
            line: list = line.rstrip().split(' ')
            
            # Go through each word or number item of that line
            for i, part in enumerate(line):
                
                part = part.rstrip()                    # Clean the part from leading and trailing white-spaces
                
                # If the part is numeric, it should be resembled as an integer, not a string
                if part.isnumeric():
                    line[i] = int(part)
                    
                elif ',' in part:
                    part: list = part.split(',')
                    
                    for j, ramp_part in enumerate(part):
                        if ramp_part.isnumeric():
                            part[j] = int(ramp_part)
                        
                        elif ramp_part[-2:] == 'ms' and ramp_part[0].isdigit():
                            part[j] = int(ramp_part[:-2])
                            part.append(ramp_part[-2:])
                
                        elif ramp_part[-1:] == 's' and ramp_part[-2:] != 'ms' and ramp_part[0].isdigit():
                            part[j] = int(ramp_part[:-1])
                            part.append(ramp_part[-1:])
                    
                    line[i] = part
                
                # If part has no length, it's essentially a empty part, we don't need that
                elif not len(part):
                    line.pop(i)
                
                # In case it's a delay that shows in which time unit it should be executet
                elif part[-2:] == 'ms' and part[0].isdigit():
                    line[i] = int(part[:-2])
                    line.append(part[-2:])
                
                elif part[-1:] == 's' and part[-2:] != 'ms' and part[0].isdigit():
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
                
                if self.args_[i] == 'inf':
                    loopdata: list = [i, 'inf']
                
                elif isinstance(self.args_[i], int):
                    loopdata: list = [i, self.args_[i]]
                
                else:    
                    loopdata: list = [i, 'inf']
                    
                self.loops.insert(i, loopdata)
            
            elif command == "endloop":
                self.loops.insert(i, [])
                for loop in reversed(self.loops):
                
                    if len(loop) == 2:
                        loop.insert(2, i)
                        break
            
            else:
                self.loops.insert(i, [])
        
        logger.info(f"After parsing\tcommands = {self.commands}\targuments = {self.args_}\t loops = {self.loops}")