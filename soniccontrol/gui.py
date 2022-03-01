from cmath import log
import tkinter as tk
from tkinter import filedialog
import tkinter.ttk as ttk
import ttkbootstrap as ttkb
from abc import ABC, abstractmethod
from sonicpackage import Command
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
        self._input_frq: tk.StringVar = tk.IntVar()
        
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
        self.radiobtn_val: tk.IntVar = tk.IntVar()
        self.khz_button: ttkb.Radiobutton = ttkb.Radiobutton(
            self.frq_rng_frame,
            text='KHz',
            value='khz',
            variable=self.radiobtn_val,
            bootstyle='dark-outline-toolbutton',
            width=12,
            command=lambda: self.root.serial.sc_sendget(Command.SET_KHZ, self.root.thread))
        
        self.mhz_button: ttkb.Radiobutton = ttkb.Radiobutton(
            self.frq_rng_frame,
            text='MHz',
            value='mhz',
            variable=self.radiobtn_val,
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
    
    def __init__(self, parent: ttk.Notebook, root: tk.Tk, *args, **kwargs) -> None:
        """ Declare all children """
        super().__init__(parent, *args, **kwargs)
        self._root = root
        self.script_filepath: str
        self.save_filename: str
        self.logfilename: str
        self.logfilepath: str
        self._filetypes: list[tuple] = [('Text', '*.txt'),('All files', '*'),]
        
        self.config(height=200, width=200)
        
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
            font=None, #!Here
            length=160,
            mode=ttkb.INDETERMINATE,
            orient=ttkb.HORIZONTAL,
            bootstyle=ttkb.DARK,
            text=None) #!here
        
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
            command=None) #!Here

        self.task_frame = ttk.Frame(self)
        self.static_prevtask_label = ttk.Label(
            self.task_frame,
            font=None, #!here
            text='Previous Task:',)
        
        self.prev_task_label = ttk.Label(
            self.task_frame,
            font=None, #!here
            textvariable=None,) #!here
        
        self.static_curtask_label = ttk.Label(
            self.task_frame,
            font=None, #! Here
            text='Current Task:')
        
        self.cur_task_label = ttk.Label(
            self.task_frame,
            font=None, #!here
            textvariable=None) #!heres
        
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
            self.scripttext.delete(1, tk.END)
            self.scripttext.insert(tk.INSERT, f.read())
        logger.info("Loaded file")
    
    def save_file(self) -> None:
        self.save_filename = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=self._filetypes)
        with open(self.save_filename, 'w') as f:
            f.write(self.scripttext.get(1, tk.END))
    
    def open_logfile(self) -> None:
        self.logfilepath = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=self._filetypes)
        
    
    def close_file(self):
        self.start_script_btn.configure(
            text='Run',
            style='success.TButton',
            image=self.root.play_img,
            command=self.read_file)
    
    def read_file(self):
        self.start_script_btn.configure(
            text='Stop',
            style='danger.TButton',
            image=self.root.pause_img,
            command=self.close_file)
    
    def attach_data(self) -> None:
        pass



class ScriptingGuide(tk.Toplevel):
    
    def __init__(self, root: tk.Tk, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass
    


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
            text = 'control',
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