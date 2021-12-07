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
        
        
    def start_wiping(self):
        pass
    
    
    def set_wipemode(self):
        pass
    
    
    def set_frequency(self):
        pass
    
    
    def set_scrolldigit(self):
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



        