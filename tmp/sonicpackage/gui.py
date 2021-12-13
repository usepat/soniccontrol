import tkinter as tk
from tkinter import font
from tkinter.constants import DISABLED
from tkinter.font import NORMAL
import tkinter.ttk as ttk
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from ttkbootstrap import style

class NotebookMenu(ttk.Notebook):
    
    @property
    def root(self):
        return self._root
    
    def __init__(self, root, *args, **kwargs):
        ttk.Notebook.__init__(self, root, *args, **kwargs)
        self._root = root
        
        self.home_tab = HomeTab(self)
        self.script_tab = ScriptingTab(self)
        self.connection_tab = ConnectionTab(self)
        self.publish()


    def publish(self):
        self.grid(row=0, column=0)
        
        

class HomeTab(ttk.Frame):
    
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        
        self.topframe = ttk.Frame(self)
        self.botframe = ttk.Frame(self)
        
        self.utilframe = ttk.Labelframe(self.topframe)
        
        self.wipe_runs_spinbox = ttk.Spinbox(
            self.utilframe,
            from_ = 10,
            increment = 5,
            justify = tk.LEFT,
            to = 100,
            textvariable = parent.root.wiperuns,
            validate = None,
            width = 5,
            style = 'primary.TButton'   
        )
        
        self.wipemode_button = ttk.Button(
            self.utilframe,
            text='Infinite Cycles',
            command=self.set_wipemode
        )
        
        self.wipe_progressbar = ttk.Progressbar(
            self.utilframe,
            orient=tk.HORIZONTAL,
            length=50,
            mode='indeterminate',
            style=''
        )
        
        self.start_wiping_button = ttk.Button(
            self.utilframe,
            text='WIPE',
            command=self.start_wiping,
            style=''
        )
        
        self.freq_frame = ttk.Labelframe(self.topframe)
        self.frq_spinbox = ttk.Spinbox(
            self.freq_frame,
            from_=50000,
            increment=100,
            to=1200000,
            textvariable=parent.root.frequency,
            width=10,
            style='primary.TSpinbox',
            command=self.set_frequency
        )
        
        self.scroll_digit = ttk.Spinbox(
            self.freq_frame,
            from_=1,
            increment=1,
            to=6,
            validate=None,
            width=5,
            style='secondary.TSpinbox',
            command=self.set_scrolldigit
        )
        
        self.set_frq_button = ttk.Button(
            self.freq_frame,
            text='Set Frequency',
            command=self.set_frequency,
            style='',
        )
    
        self.us_on_button = ttk.Button(
            self.freq_frame,
            text='ON',
            style='success.TButton',
            command=self.turn_us_on
        )
        
        self.us_off_button = ttk.Button(
            self.botframe,
            text='OFF',
            style='danger.TButton',
            width=10,
            command=self.turn_us_off
        )
        
        self.config(height=200, width=200)
        parent.add(self, text='Home')
        
        
    def start_wiping(self):
        pass
    
    
    def set_wipemode(self):
        pass
    
    
    def set_frequency(self):
        pass
    
    
    def set_scrolldigit(self):
        pass
    
    
    def turn_us_on(self):
        pass
    
    def turn_us_off(self):
        pass
        


class ScriptingTab(ttk.Frame):
    
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        
        self.prev_task = tk.StringVar().set('Idle')
        self.current_task = tk.StringVar().set('Idle')
        
        self.button_frame = ttk.Frame(self)
        self.load_script_btn = ttk.Button(
            self.button_frame,
            text='Load script file',
            style='',
            command=self.load_file,
        )
        
        self.save_script_btn = ttk.Button(
            self.button_frame,
            text='Save script file',
            style='',
            command=self.save_file
        )
        
        self.save_log_btn = ttk.Button(
            self.button_frame,
            text='Save log file to',
            style='',
            command=self.open_logfile
        )
        
        self.script_guide_btn = ttk.Button(
            self.button_frame,
            text='Scripting Guide',
            style='',
            command=lambda e: ScriptingGuide(parent.root, self.scripttext)
        )

        self.stop_script_btn = ttk.Button(
            self.button_frame,
            text='Stop Script',
            style='',
            command=self.close_file
        )
        
        self.start_script_btn = ttk.Button(
            self.button_frame,
            text='Start Script',
            style='',
            command=self.read_file
        )
        
        self.scripting_frame = ttk.Labelframe(
            self,
            height=200,
            width=200,
            text='Script Editor'
        )
        
        self.scripttext = tk.Text(
            self.scripting_frame,
            autoseparators=False,
            background='white',
            setgrid=False,
            width=30,
        )
        _text = '''Enter Tasks here...'''
        self.scripttext.insert(0.0, _text)
        
        self.scrollbar = ttk.Scrollbar(
            self.scripting_frame,
            orient='vertical',
            command=self.scripttext.yview
        )
        
        self.scripttext.configure(yscrollcommand=self.scrollbar.set)
        
        self.task_frame = ttk.Frame(self)
        self.static_prevtask_label = ttk.Label(
            self.task_frame,
            font=parent.root.arial12,
            text='Previous Task:'
        )
        
        self.prev_task_label = ttk.Label(
            self.task_frame,
            font=parent.root.arial12,
            textvariable=self.prev_task,
        )
        
        
        self.static_curtask_label = ttk.Label(
            self.task_frame,
            font=parent.root.arial12,
            text='Current Task:'
        )
        
        self.cur_task_label = ttk.Label(
            self.task_frame,
            font=parent.root.arial12,
            textvariable=self.current_task
        )
        
        
        self.script_progressbar = ttk.Progressbar(
            self,
            orient='horizontal',
            mode='indeterminate'
        )
        
        self.config(height=200, width=200)
        parent.add(self, text='Scripting')
        
    
    def load_file(self):
        pass
    
    def save_file(self):
        pass
    
    def open_logfile(self):
        pass
    
    def close_file(self):
        pass
    
    def read_file(self):
        pass
    

class ConnectionTab(ttk.Frame):
    
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        
        self.topframe = ttk.Frame(self)
        self.heading_frame = ttk.Frame(self.topframe)
        self.subtitle = ttk.Label(self.heading_frame, text="You are connected to:")
        
        self.heading = ttk.Label(
            self.heading_frame, 
            text = parent.root.sonicamp.info['type'],
            font = "QTypeOT-CondBook 30 bold",
        )
        
        self.control_frame = ttk.Frame(self.topframe)
        self.ports_menue = ttk.OptionMenu(
            self.control_frame,
            parent.root.port,
            parent.root.sonicamp.device_list[0],
            parent.root.sonicamp.device_list,
            style = "primary.TOption"
        )
        
        self.connect_button = ttk.Button(
            self.control_frame, 
            text = 'Connect', 
            command = parent.root.sonicamp.connect_to_port, 
            style = "success.TButton",
            width = 10
        )
        
        self.refresh_button = ttk.Button(
            self.control_frame, 
            text = 'Refresh', 
            command = parent.root.sonicamp.get_ports, 
            style = "outline.TButton"
        )
        
        self.disconnect_button = ttk.Button(self.control_frame, text='Disconnect', command=parent.root.sonicamp.disconnect, style="danger.TButton", width=10)
        self.botframe = ttk.Frame(self)

        if parent.root.sonicamp.is_connected:
            self.connected()
        else:
            self.not_connected()
            
        parent.add(self, state=NORMAL, text='Connection')
        


    def not_connected(self):
        pass


    def connected(self):
        for child in self.children.values():
            child.pack()
            for grandchild in child.children.values():
                grandchild.pack()
                for gandgrandchild in grandchild.children.values():
                    gandgrandchild.pack()



        