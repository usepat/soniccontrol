import datetime
from distutils import command
import logging
import tkinter as tk
from tkinter import filedialog, messagebox
import tkinter.ttk as ttk
import ttkbootstrap as ttkb
from abc import ABC, abstractmethod
import time
from sonicpackage import Command, SerialConnection
from .helpers import logger

class HomeTabCatch(ttk.Frame):
    
    @property
    def root(self) -> tk.Tk:
        return self._root
    
    def __init__(self, parent: ttk.Notebook, root: tk.Tk, *args, **kwargs) -> None:
        """
        The Hometab is a child tab of the Notebook menu and is resonsible
        for handling and updating its children
        
        The frame is, again, splittet up into two main frames that organize
        its children
        """
        super().__init__(parent, *args, **kwargs)
        self._root: tk.Tk = root
        
        self.config(height=200, width=200)
        
        # Here follows the code regarding the TOPFRAME
        self.topframe: ttk.Labelframe = ttk.Labelframe(self, text="Manual control")
        self.control_frame: ttk.Frame = ttk.Frame(self.topframe) 
        
        # Frq frame
        self.frq_frame: ttk.Label = ttk.Label(self.control_frame)
        self.frq_spinbox: ttk.Spinbox = ttk.Spinbox(
            self.frq_frame,
            from_=600000,
            increment=100,
            to=6000000,
            textvariable=self.root.frq, 
            width=16,
            style='dark.TSpinbox',
            command=lambda: self.root.serial.sc_sendget(Command.SET_FRQ + self.root.frq.get(), self.root.thread))
        
        self.scroll_digit: ttk.Spinbox = ttk.Spinbox(
            self.frq_frame,
            from_=1,
            increment=1,
            to=6,
            validate=None,
            width=5,
            style='secondary.TSpinbox',
            command=self.set_scrolldigit)
        
        # Gain Frame
        self.gain_frame: ttk.Frame = ttk.Frame(self.control_frame)
        self.gain_spinbox: ttk.Spinbox = ttk.Spinbox(
            self.gain_frame,
            from_=0,
            increment=10,
            to=150,
            textvariable=self.root.gain,
            width=5,
            style='dark.TSpinbox',
            command=lambda: self.root.serial.sc_sendget(Command.SET_GAIN + int(self.root.gain.get()), self.root.thread))
        
        self.gain_scale: ttk.Scale = ttk.Scale(
            self.gain_frame,
            from_=0,
            to=150,
            name='gainscale',
            length=180,
            orient=tk.HORIZONTAL,
            style="primary.TScale",
            variable=self.root.gain,)
            #command=lambda: self.root.serial.sc_sendget(Command.SET_GAIN + int(self.root.gain.get()), self.root.thread))
        
        # kHz MHz Frame
        self.frq_rng_frame: ttk.Label = ttk.Label(self.control_frame)
        self.khz_button: ttkb.Radiobutton = ttkb.Radiobutton(
            self.frq_rng_frame,
            text='KHz',
            value='khz',
            variable=self.root.frq_range,
            bootstyle='dark-outline-toolbutton',
            width=12,
            command=lambda: self.root.serial.sc_sendget(Command.SET_KHZ, self.root.thread))
        
        self.mhz_button: ttkb.Radiobutton = ttkb.Radiobutton(
            self.frq_rng_frame,
            text='MHz',
            value='mhz',
            variable=self.root.frq_range,
            bootstyle='dark-outline-toolbutton',
            width=12,
            command=lambda: self.root.serial.sc_sendget(Command.SET_MHZ, self.root.thread)) 
        
        # Other children of the control frame
        self.set_val_btn: ttk.Button = ttk.Button(
            self.control_frame,
            text='Set Frequency and Gain',
            command=self.set_val,
            bootstyle='dark.TButton',)
        
        self.sonic_measure_frame: ttk.Frame = ttk.Frame(self.topframe)
        self.sonic_measure_button: ttk.Button = ttk.Button(
            self.sonic_measure_frame,
            text='Sonic measure',
            style='dark.TButton',
            image=self.root.graph_img,
            compound=tk.TOP,
            command=self.root.publish_sonicmeasure)
        
        self.serial_monitor_btn: ttk.Button = ttk.Button(
            self.sonic_measure_frame,
            text='Serial Monitor',
            style='secondary.TButton',
            width=12,
            command=self.root.publish_serial_monitor,)
        
        self.botframe: ttk.Frame = ttk.Frame(self)
        
        self.us_on_button: ttk.Button = ttk.Button(
            self.botframe,
            text='ON',
            style='success.TButton',
            width=10,
            command=lambda: self.root.serial.sc_sendget(Command.SET_SIGNAL_ON, self.root.thread))
        
        self.us_off_button: object = ttk.Button(
            self.botframe,
            text='OFF',
            style='danger.TButton',
            width=10,
            command=lambda: self.root.serial.sc_sendget(Command.SET_SIGNAL_OFF, self.root.thread))
        
        logger.info("Initialized children and object")

    def set_val(self) -> None:
        self.root.serial.sc_sendget(
            [Command.SET_GAIN + int(self.root.gain.get()),
            Command.SET_FRQ + self.root.frq.get(),], 
            self.root.thread)
            
    def attach_data(self) -> None:
        logger.info("Attaching data to Hometab")
        self.frq_spinbox.config(
            from_=self.root.sonicamp.frq_range_start,
            to=self.root.sonicamp.frq_range_stop)
            
    def publish(self) -> None:
        """ Function to build children of this frame """
        logger.info("Publishing hometab")
        self.frq_spinbox.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.scroll_digit.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)
        
        self.gain_spinbox.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.gain_scale.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)
        
        self.khz_button.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.mhz_button.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)
        
        self.frq_frame.pack(side=tk.TOP, expand=True, fill=tk.X)
        self.gain_frame.pack(side=tk.TOP, expand=True, fill=tk.X)
        self.frq_rng_frame.pack(side=tk.TOP, expand=True, fill=tk.X)
        self.set_val_btn.pack(side=tk.TOP, expand=True, fill=tk.X, padx=10, pady=10)
        self.sonic_measure_button.pack(side=tk.TOP, padx=10, pady=10)
        self.serial_monitor_btn.pack(side=tk.TOP, padx=10, pady=5)
        
        self.control_frame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.sonic_measure_frame.grid(row=0, column=1, padx=20, pady=20, sticky=tk.NSEW)

        self.us_on_button.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.us_off_button.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)

        self.topframe.pack(side=tk.TOP, padx=20, pady=20)
        self.botframe.pack(side=tk.TOP)        
            
    def set_scrolldigit(self) -> None:
        """ Function regarding the scroll digit combobox """
        self.frq_spinbox.config(
            increment = str(10 ** (int(self.scroll_digit.get())-1)))
        
        


class ScriptingTab(ttk.Frame):
    """ Scripting tab of the GUI """
    
    @property
    def root(self) -> tk.Tk:
        return self._root
    
    @property
    def serial(self) -> SerialConnection:
        return self._serial
    
    def __init__(self, parent: ttk.Notebook, root: tk.Tk, *args, **kwargs) -> None:
        """ Declare all children """
        super().__init__(parent, *args, **kwargs)
        self._root = root
        self._serial: SerialConnection = root.serial
        self.script_filepath: str
        self.save_filename: str
        self.logfilename: str
        self.logfilepath: str
        self.current_task: tk.StringVar = tk.StringVar(value='Idle')
        self.previous_task: tk.StringVar = tk.StringVar(value='Idle')
        
        self._filetypes: list[tuple] = [('Text', '*.txt'),('All files', '*'),]
        
        self.config(height=200, width=200)
        
        self.logger: logging.Logger = logging.getLogger("Scripting")
        self.formatter: logging.Formatter = logging.Formatter('%(asctime)s  %(message)s')
        self.file_handler: logging.FileHandler = logging.FileHandler('sequence.log')
        self.logger.setLevel(logging.DEBUG)
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)
        
        self.button_frame: ttk.Frame = ttk.Frame(self)
        self.start_script_btn = ttk.Button(
            self.button_frame,
            text='Run',
            style='success.TButton',
            width=11,
            image=self.root.play_img,
            compound=tk.RIGHT,
            command=self.read_file,)
        
        self.load_script_btn: ttk.Button = ttk.Button(
            self.button_frame,
            text='Open script file',
            style='dark.TButton',
            width=15,
            command=self.load_file,)
        
        self.save_script_btn: ttk.Button = ttk.Button(
            self.button_frame,
            text='Save script file',
            style='dark.TButton',
            width=15,
            command=self.save_file,)
        
        self.save_log_btn: ttk.Button = ttk.Button(
            self.button_frame,
            text='Specify logfile path',
            style='dark.TButton',
            width=15,
            command=self.open_logfile)
        
        self.sequence_status: ttkb.Floodgauge = ttkb.Floodgauge(
            self.button_frame,
            font=self.root.qtype12,
            length=160,
            mode=ttkb.INDETERMINATE,
            orient=ttkb.HORIZONTAL,
            bootstyle=ttkb.DARK,) 
        
        self.scripting_frame: ttk.Labelframe = ttk.Labelframe(
            self,
            text="Script Editor",
            style="dark.TLabelframe",
            padding=(5,5,5,5),)
        
        self.scripttext: tk.Text = tk.Text(
            self.scripting_frame,
            autoseparators=False,
            background='white',
            setgrid=False,
            width=35,
            padx=5,
            pady=5,
            font=("Consolas", 12))
        
        self.scrollbar: ttk.Scrollbar = ttk.Scrollbar(
            self.scripting_frame,
            orient='vertical',
            command=self.scripttext.yview)  
        
        self.show_log_console: ttk.Button = ttk.Button(
            self.scripting_frame,
            text='Show log console',
            style="secondary.TButton",
            command=self.show_console)
        
        self.script_guide_btn = ttk.Button(
            self.scripting_frame,
            text='Scripting Guide',
            style='dark.TButton',
            command=lambda: ScriptingGuide(self.root, self.scripttext))

        self.task_frame = ttk.Frame(self)
        self.static_prevtask_label = ttk.Label(
            self.task_frame,
            text='Previous Task:',)
        
        self.prev_task_label = ttk.Label(
            self.task_frame,
            textvariable=self.previous_task,)
        
        self.static_curtask_label = ttk.Label(
            self.task_frame,
            text='Current Task:')
        
        self.cur_task_label = ttk.Label(
            self.task_frame,
            textvariable=self.current_task)
        
        logger.info("Initialized scripting tab")

    def publish(self):
        # Button Frame
        logger.info("Publishing scripting tab")
        self.button_frame.pack(anchor=tk.N, side=tk.LEFT, padx=5, pady=5)
        for child in self.button_frame.winfo_children():
            child.pack(side=tk.TOP, padx=5, pady=5)

        #Scripting Frame
        self.scripting_frame.pack(anchor=tk.N ,side=tk.RIGHT ,padx=5, pady=5, expand=True, fill=tk.X)
        self.scripttext.grid(row=0, column=0, columnspan=2)
        self.show_log_console.grid(row=1, column=0, padx=5, pady=5)
        self.script_guide_btn.grid(row=1, column=1, padx=5, pady=5)
        
        #Task Frame
        self.task_frame.pack(side=tk.BOTTOM, padx=10, pady=10)
        self.static_prevtask_label.grid(row=0, column=0)
        self.prev_task_label.grid(row=1, column=0)
        self.static_curtask_label.grid(row=0, column=1)
        self.cur_task_label.grid(row=1, column=1)
    
    def show_console(self):
        pass
    
    def load_file(self) -> None:
        self.script_filepath = filedialog.askopenfilename(defaultextension='.txt', filetypes=self._filetypes)
        with open(self.script_filepath, 'r') as f:
            self.scripttext.delete(0, tk.END)
            self.scripttext.insert(tk.INSERT, f.read())
        logger.info("Loaded file")
    
    def save_file(self) -> None:
        self.save_filename = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=self._filetypes)
        with open(self.save_filename, 'w') as f:
            f.write(self.scripttext.get(0, tk.END))
    
    def open_logfile(self) -> None:
        self.logfilepath = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=self._filetypes)
    
    def close_file(self) -> None:
        self.run: bool = False
        self.start_script_btn.configure(
            text='Run',
            style='success.TButton',
            image=self.root.play_img,
            command=self.read_file)
        
        self.current_task.set('Idle')
        self.previous_task.set('Idle')
        self.root.notebook.enable_children()
        self.scripttext.config(state=tk.NORMAL)
        self.load_script_btn.config(state=tk.NORMAL)
        self.save_script_btn.config(state=tk.NORMAL)
        self.save_log_btn.config(state=tk.NORMAL)
        self.script_guide_btn.config(state=tk.NORMAL)
        self.sequence_status.config(text=None)
        self.serial.send_and_get(Command.SET_SIGNAL_OFF)
    
    def read_file(self):
        self.run: bool = True
        
        self.start_script_btn.configure(
            text='Stop',
            style='danger.TButton',
            image=self.root.pause_img,
            command=self.close_file)

        self.root.notebook.disable_children(self)
        self.scripttext.config(state=tk.DISABLED)
        self.load_script_btn.config(state=tk.DISABLED)
        self.save_script_btn.config(state=tk.DISABLED)
        self.save_log_btn.config(state=tk.DISABLED)
        self.script_guide_btn.config(state=tk.DISABLED)
        self.serial.send_and_get(Command.SET_SIGNAL_ON)
        
        try:
            self.logfilehandler = open(self.logfilepath, 'w')
            self.logfilehandler.write("Timestamp"+"\t"+"Datetime"+"\t"+"Action"+"\n")
            self.logfilehandler.close()
            self.start_sequence()
        except:
            messagebox.showerror("Error", "No logfile is specified. Please specify a file.")
            self.open_logfile()
            if not self.logfilepath:
                self.close_file()
            else:
                self.logfilehandler = open(self.logfilepath, 'w')
                self.logfilehandler.write("Timestamp"+"\t"+"Datetime"+"\t"+"Action"+"\n")
                self.logfilehandler.close()
                self.start_sequence()
    
    def start_sequence(self) -> None:
        self.commands: list[str] = []
        self.args_: list[str] = []
        self.loops: list[list[int]] = [[]]
        self.loop_index: int = 0
        
        line_list: list[str] = self.scripttext.get(1.0, tk.END).splitlines()
        self.parse_commands(line_list)
        
        for i, command in enumerate(self.commands):
            if command == "startloop":
                loopdata = [i, int(self.args_[i][0])]
                self.loops.insert(i, loopdata)
            elif command == "endloop":
                self.loops.insert(i, [])
                for loop in reversed(self.loops):
                    if len(loop) == 2:
                        loop.insert(2, i)
                        break
            elif command == "hold":
                self.loops.insert(i, [])
            elif command == "ramp":
                self.loops.insert(i, [])
                
                start: int = int(self.args_[i][0])
                stop: int = int(self.args_[i][1])
                step: int = int(self.args_[i][2])
                delay: int = int(self.args_[i][3])
                
                if start > stop:
                    frq_list: list = list(range(stop, start, step))
                else:
                    frq_list: list = list(range(start, stop, step))
            else:
                self.loops.insert(i, [])
        
        i = 0
        while i < len(self.commands):
            if self.commands[i] == 'startloop':
                if self.loops[i][1]:
                    self.loops[i][1] =- 1
                    i += 1
                else:
                    i = self.loops[i][2] + 1
            elif self.commands[i] == 'endloop':
                for loop in self.loops:
                    if loop[2] == i:
                        for j in range(self.loops[0]+1, self.loops[2]):
                            if self.loops[j]:
                                self.loops[j][1] = int(self.args_[j][0])
                        i = loop[0]
            else:
                self.exec_command(i)
                i += 1
        self.close_file()
        
    def exec_command(self, counter: int) -> None:
        self.current_task.set(f"{self.commands[counter]} {str(self.args_[counter])}")
        self.root.update()
        if counter > 0:
            self.previous_task.set(f"{self.commands[counter-1]} {self.args_[counter-1]}")
        self.logger.info(f"{str(self.commands[counter])}   {str(self.args_[counter])}  {str(self.root.sonicamp.status.frequency)}")
        if self.commands[counter] == "set_frq":
            self.serial.sc_sendget(Command.SET_FRQ + self.args_[counter], self.root.thread)
        elif self.commands[counter] == "set_gain":
            self.serial.sc_sendget(Command.SET_GAIN + self.args_[counter], self.root.thread)
        elif self.commands[counter] == "ramp":
            self.start_ramp(self.args_[counter])
        elif self.commands[counter] == "hold":
            now = datetime.datetime.now()
            target = now + datetime.timedelta(milliseconds=int(self.args_[counter][0]))
            while now < target:
                time.sleep(0.02)
                now = datetime.datetime.now()
                self.root.update()
        elif self.commands[counter] == "set_signal_on":
            self.serial.sc_sendget(Command.SET_SIGNAL_ON, self.root.thread)
            self.root.update()
        elif self.commands[counter] == "set_signal_off":
            self.serial.sc_sendget(Command.SET_SIGNAL_OFF, self.root.thread)
            self.root.update()
        elif self.commands[counter] == "set_mhz":
            self.serial.sc_sendget(Command.SET_MHZ, self.root.thread)
        elif self.commands[counter] == "set_khz":
            self.serial.sc_sendget(Command.SET_KHZ, self.root.thread)
        elif self.commands[counter] == "set_auto":
            self.serial.sc_sendget(Command.SET_AUTO, self.root.thread)
    
    def start_ramp(self, args_: list) -> None:
        start = int(args_[0])
        stop = int(args_[1])
        step = int(args_[2])
        delay = int(args_[3])
        
        if start > stop:
            for frq in range(start, stop, -step):
                self.current_task.set(f"Ramp is @ {frq/1000}kHz")
                self.logger.info(f"ramp\t{start},{stop},{step}\t{frq}")
                self.root.status_frame_catch.frq_meter["amountused"] = frq
                self.serial.sc_sendget(Command.SET_FRQ + frq, self.root.thread)
        else:
            for frq in range(start, stop, step):
                self.current_task.set(f"Ramp is @ {frq/1000}kHz")
                self.logger.info(f"ramp\t{start},{stop},{step}\t{frq}")
                self.root.status_frame_catch.frq_meter["amountused"] = frq
                self.serial.sc_sendget(Command.SET_FRQ + frq, self.root.thread)
                
    
    def parse_commands(self, line_list: list) -> None:
        for line in line_list:
            if ' ' in line:
                self.commands.append(line.split(' ')[0])
                self.args_.append(line.split(' ')[1].split(','))
            else:
                self.commands.append(line)
                self.args_.append(None)
    
    def attach_data(self) -> None:
        pass



class ScriptingGuide(tk.Toplevel):
    
    def __init__(self, root: tk.Tk, scripttext: tk.Text, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.title('Function Helper')
        x = root.winfo_x()
        dx = root.winfo_width()
        # dy = root.winfo_height()
        y = root.winfo_y()
        self.geometry("%dx%d+%d+%d" % (850, 500, x + dx, y))
        self.scriptText = scripttext
        # tk.Toplevel.__init__(self, master, **kw)
        self.HelperFrame = ttk.Frame(self)
        self.label_1 = ttk.Label(self.HelperFrame)
        self.label_1.config(anchor='w', font='{Bahnschrift} 12 {}', justify='center', text='Command')
        self.label_1.grid(column='0', columnspan='1', padx='20', pady='0', row='1')
        self.label_2 = ttk.Label(self.HelperFrame)
        self.label_2.config(font='{Bahnschrift} 12 {}', text='Arguments')
        self.label_2.grid(column='1', padx='20', row='1')
        self.label_3 = ttk.Label(self.HelperFrame)
        self.label_3.config(font='{Bahnschrift} 12 {}', text='Description')
        self.label_3.grid(column='2', padx='20', row='1')
        self.HoldButton = ttk.Button(self.HelperFrame)
        self.HoldButton.config(state='normal', text='hold', command = self.insertHold)
        self.HoldButton.grid(column='0', ipady='0', pady='5', row='2')
        self.label_4 = ttk.Label(self.HelperFrame)
        self.label_4.config(text='[1-100.000] in [seconds]')
        self.label_4.grid(column='1', padx='10', row='2')
        self.label_5 = ttk.Label(self.HelperFrame)
        self.label_5.config(text='Hold the last state for X seconds')
        self.label_5.grid(column='2', padx='10', row='2')
        self.FreqButton = ttk.Button(self.HelperFrame)
        self.FreqButton.config(text='frequency', command = self.insertFrequency)
        self.FreqButton.grid(column='0', pady='5', row='3')
        self.GainButton = ttk.Button(self.HelperFrame)
        self.GainButton.config(text='gain', command = self.insertGain)
        self.GainButton.grid(column='0', pady='5', row='4')
        self.kHzButton = ttk.Button(self.HelperFrame)
        self.kHzButton.config(text='setkHz', command = self.insertSetkHz)
        self.kHzButton.grid(column='0', pady='5', row='5')
        self.MHzButton = ttk.Button(self.HelperFrame)
        self.MHzButton.config(text='setMHz', command = self.insertSetMHz)
        self.MHzButton.grid(column='0', pady='5', row='6')
        self.OnButton = ttk.Button(self.HelperFrame)
        self.OnButton.config(text='on', command = self.insertOn)
        self.OnButton.grid(column='0', pady='5', row='7')
        self.OffButton = ttk.Button(self.HelperFrame)
        self.OffButton.config(text='off', command = self.insertOff)
        self.OffButton.grid(column='0', pady='5', row='8')
        self.StartLoopButton = ttk.Button(self.HelperFrame)
        self.StartLoopButton.config(text='startloop', command = self.insertStartloop)
        self.StartLoopButton.grid(column='0', pady='5', row='9')
        self.EndLoopButton = ttk.Button(self.HelperFrame)
        self.EndLoopButton.config(text='endloop', command = self.insertEndloop)
        self.EndLoopButton.grid(column='0', pady='5', row='10')
        self.RampButton = ttk.Button(self.HelperFrame)
        self.RampButton.config(text='ramp', command = self.insertRamp)
        self.RampButton.grid(column='0', pady='5', row='11')
        self.AutotuneButton = ttk.Button(self.HelperFrame)
        self.AutotuneButton.config(text='autotune', command = self.insertAutotune)
        self.AutotuneButton.grid(column='0', pady='5', row='12')
        self.label_6 = ttk.Label(self.HelperFrame)
        self.label_6.config(text='[50.000-1.200.000] for kHz in [Hz]\n [600.000-6.000.000] for MHz in [Hz]')
        self.label_6.grid(column='1', row='3')
        self.label_7 = ttk.Label(self.HelperFrame)
        self.label_7.config(text='Change to the indicated frequency in Hz')
        self.label_7.grid(column='2', padx='5', row='3')
        self.label_8 = ttk.Label(self.HelperFrame)
        self.label_8.config(text='[1-150] in [%]')
        self.label_8.grid(column='1', row='4')
        self.label_9 = ttk.Label(self.HelperFrame)
        self.label_9.config(text='Change to the selected gain in %')
        self.label_9.grid(column='2', row='4')
        self.label_10 = ttk.Label(self.HelperFrame)
        self.label_10.config(text='None')
        self.label_10.grid(column='1', row='5')
        self.label_11 = ttk.Label(self.HelperFrame)
        self.label_11.config(text='Change to the kHz range amplifier')
        self.label_11.grid(column='2', row='5')
        self.label_12 = ttk.Label(self.HelperFrame)
        self.label_12.config(text='None')
        self.label_12.grid(column='1', row='6')
        self.label_13 = ttk.Label(self.HelperFrame)
        self.label_13.config(text='Change to the MHz range amplifier')
        self.label_13.grid(column='2', row='6')
        self.label_14 = ttk.Label(self.HelperFrame)
        self.label_14.config(text='None')
        self.label_14.grid(column='1', row='7')
        self.label_15 = ttk.Label(self.HelperFrame)
        self.label_15.config(text='Activate US emission')
        self.label_15.grid(column='2', row='7')
        self.label_16 = ttk.Label(self.HelperFrame)
        self.label_16.config(text='None')
        self.label_16.grid(column='1', row='8')
        self.label_17 = ttk.Label(self.HelperFrame)
        self.label_17.config(text='Deactivate US emission')
        self.label_17.grid(column='2', row='8')
        self.label_18 = ttk.Label(self.HelperFrame)
        self.label_18.config(text='[2-10.000] as an [integer]')
        self.label_18.grid(column='1', row='9')
        self.label_19 = ttk.Label(self.HelperFrame)
        self.label_19.config(text='Start a loop for X times')
        self.label_19.grid(column='2', row='9')
        self.label_20 = ttk.Label(self.HelperFrame)
        self.label_20.config(text='None')
        self.label_20.grid(column='1', row='10')
        self.label_21 = ttk.Label(self.HelperFrame)
        self.label_21.config(text='End the loop here')
        self.label_21.grid(column='2', row='10')
        self.label_24 = ttk.Label(self.HelperFrame)
        self.label_24.config(text='start f [Hz], stop f [Hz], step size [Hz], delay [s]')
        self.label_24.grid(column='1', row='11')
        self.label_23 = ttk.Label(self.HelperFrame)
        self.label_23.config(text='Create a frequency ramp with a start frequency, a stop frequency,\n a step size and a delay between steps')
        self.label_23.grid(column='2', row='11')
        self.label_26 = ttk.Label(self.HelperFrame)
        self.label_26.config(text='None')
        self.label_26.grid(column='1', row='12')
        self.label_25 = ttk.Label(self.HelperFrame)
        self.label_25.config(text='Start the autotune protocol. This should be followed by "hold"\n commands, otherwise the function will be stopped.')
        self.label_25.grid(column='2', row='12')
        self.label_22 = ttk.Label(self.HelperFrame)
        self.label_22.config(text='To insert a function at the cursor position, click on the respective button', font=('TkDefaultFont', 11, 'bold'))
        self.label_22.grid(column='0', columnspan='3', padx='5', pady='5', row='13')
        self.HelperFrame.config(height='250', width='400')
        self.HelperFrame.pack(side='top')

    def insertHold(self):
        self.scriptText.insert(self.scriptText.index(tk.INSERT), 'hold X\n')
        
    def insertFrequency(self):
        self.scriptText.insert(self.scriptText.index(tk.INSERT), 'frequency XXXXXXXX\n')
        
    def insertGain(self):
        self.scriptText.insert(self.scriptText.index(tk.INSERT), 'gain XXX\n')
        
    def insertSetkHz(self):
        self.scriptText.insert(self.scriptText.index(tk.INSERT), 'setkHz\n')
        
    def insertSetMHz(self):
        self.scriptText.insert(self.scriptText.index(tk.INSERT), 'setMHz\n')
        
    def insertOn(self):
        self.scriptText.insert(self.scriptText.index(tk.INSERT), 'on\n')
        
    def insertOff(self):
        self.scriptText.insert(self.scriptText.index(tk.INSERT), 'off\n')
        
    def insertStartloop(self):
        self.scriptText.insert(self.scriptText.index(tk.INSERT), 'startloop X\n')
        
    def insertEndloop(self):
        self.scriptText.insert(self.scriptText.index(tk.INSERT), 'endloop\n')
        
    def insertRamp(self):
        self.scriptText.insert(self.scriptText.index(tk.INSERT), 'ramp XXXXXXX,XXXXXXX,XXXX,XX\n')
    
    def insertAutotune(self):
        self.scriptText.insert(self.scriptText.index(tk.INSERT), 'autotune\n')
    


class ConnectionTab(ttk.Frame):
    
    @property
    def root(self) -> tk.Tk:
        return self._root
    
    def __init__(self, parent: ttk.Notebook, root: tk.Tk, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._root = root
        
        self.topframe: ttk.Frame = ttk.Frame(self, padding=(10, 10, 10, 10))
        self.heading_frame: ttk.Frame = ttk.Frame(self.topframe)
        
        self.subtitle: ttk.Label = ttk.Label(self.heading_frame, padding=(0, 10, 0, 0))
        
        self.heading1 = ttk.Label(
            self.heading_frame, 
            padding=(10,0,0,10),
            font = self.root.qtype30)
        
        self.heading2 = ttk.Label(
            self.heading_frame,
            padding=(0,0,10,10),
            font = self.root.qtype30b)
        
        self.control_frame = ttk.Frame(self.topframe)
        
        self.connect_button = ttkb.Button(
            self.control_frame, 
            width = 10,
            style="success.TButton")
        
        self.ports_menue = ttk.Combobox(
            master=self.control_frame,
            textvariable=self.root.port,
            values=None,
            width=7,
            style = "dark.TCombobox",
            state=tk.READABLE)
        
        self.refresh_button = ttkb.Button(
            self.control_frame, 
            bootstyle="secondary-outline",
            image=self.root.refresh_img, 
            command = self.refresh)
        
        self.botframe: ttk.Frame = ttk.Frame(self)
        
        logger.info("Initialized children and object connectiontab")
    
    def attach_data(self) -> None:
        logger.info("attaching data")
        self.subtitle["text"] = "You are connected to"
        self.heading1["text"] = self.root.sonicamp.amp_type[:5]
        self.heading2["text"] = self.root.sonicamp.amp_type[5:]
        self.connect_button.config(
            bootstyle="danger",
            text="Disconnect",
            command=self.disconnect,)
        self.ports_menue.config(
            textvariable=self.root.port,
            values=self.root.serial.device_list,)
        
    def abolish_data(self) -> None:
        logger.info("abolishing data")
        self.subtitle["text"] = "Please connect to a SonicAmp system"
        self.heading1["text"] = "not"
        self.heading2["text"] = "connected"
        self.connect_button.config(
            bootstyle="success",
            text="Connect",
            command=self.root.__reinit__,)
        self.ports_menue.config(
            textvariable=self.root.port,
            values=self.root.serial.device_list,)

    def refresh(self) -> None:
        self.ports_menue['values'] = self.root.serial.get_ports()
    
    def disconnect(self) -> None:
        pass
    
    def publish(self) -> None:
        logger.info("Publishing connectiontab")
        for child in self.children.values():
            child.pack()
        
        self.subtitle.grid(row=0, column=0, columnspan=2, sticky=tk.S)
        self.heading1.grid(row=1, column=0, columnspan=1, sticky=tk.E)
        self.heading2.grid(row=1, column=1, columnspan=1, sticky=tk.W)
        self.heading_frame.pack(padx=10, pady=20, expand=True)

        self.ports_menue.grid(row=0, column=0, columnspan=2, pady=10, padx=5, sticky=tk.NSEW)        
        self.connect_button.grid(row=0, column=2,columnspan=1, pady=10, padx=5, sticky=tk.NSEW)
        self.refresh_button.grid(row=0, column=3 ,columnspan=1,  pady=10, padx=5, sticky=tk.NSEW)
        self.control_frame.pack(padx=10, pady=20, expand=True)
    



class InfoTab(ttk.Frame):
    
    INFOTEXT = (
        "Welcome to soniccontrol, a light-weight application to\n" 
        "control sonicamp systems over the serial interface. \n"
        "For help, click the \"Manual\" button below\n"
        "\n"
        "(c) usePAT G.m.b.H\n")
    
    @property
    def root(self) -> tk.Tk:
        return self._root
    
    def __init__(self, parent: ttk.Notebook, root: tk.Tk, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self._root = root
        self.soniccontrol_logo_frame: ttk.Frame = ttk.Frame(self)
        self.soniccontrol_logo1 = ttk.Label(
            self.soniccontrol_logo_frame,
            text = "sonic",
            padding=(10,0,0,10),
            font = "QTypeOT-CondLight 30")
        
        self.soniccontrol_logo2 = ttk.Label(
            self.soniccontrol_logo_frame,
            text = 'crash',
            padding=(0,0,0,10),
            font = "QTypeOT-CondBook 30 bold")
        
        self.info_label = ttk.Label(self, text=InfoTab.INFOTEXT)
        
        self.controlframe = ttk.Frame(self)
        self.manual_btn = ttk.Button(
            self.controlframe,
            text='Manual',
            command=self.open_manual)
        
        self.dev_btn = ttk.Button(
            self.controlframe,
            text='I\'m a developer...',
            command=self.root.publish_serial_monitor,
            style='outline.dark.TButton')
        
        logger.info("Initialized children and object infotab")
        
    def publish(self) -> None:
        logger.info("publishing infotab")
        self.soniccontrol_logo1.grid(row=0, column=0)
        self.soniccontrol_logo2.grid(row=0, column=1)
        self.soniccontrol_logo_frame.pack(padx=20, pady=20)
        self.info_label.pack()
        self.manual_btn.grid(row=0, column=0, padx=5, pady=10)
        self.dev_btn.grid(row=0, column=1, padx=5, pady=10)
        self.controlframe.pack()
    
    def open_manual(self) -> None:
        pass
    
    def attach_data(self) -> None:
        pass


class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")