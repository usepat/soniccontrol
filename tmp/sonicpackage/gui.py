import tkinter as tk
from tkinter.constants import DISABLED
from tkinter.font import NORMAL
import tkinter.ttk as ttk
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from ttkbootstrap.style import style

class NotebookMenu():

    def __init__(self, root):
        self.root = root
        self.notebook = ttkb.Notebook(self.root, bootstyle=PRIMARY)
        # self.home_tab = HomeTab(self.notebook)
        # self.scripting_tab = ScriptingTab(self.notebook)
        # self.connection_tab = ConnectionTab(self.notebook)
        # self.info_tab = InfoTab(self.notebook)
        self.publish()


    def publish(self):
        self.notebook.grid(row=0, column=0)
        


class HomeTab():
    def __init__(self, root):
        self.root = root
        self.frame = tk.Frame(self.root['notebook'])
        self.root.notebook.add(self.frame, state=DISABLED, text='Home')

class ScriptingTab():
    def __init__(self, root):
        self.root = root
        self.frame = tk.Frame(self.root['notebook'])
        self.root.add(self.frame, state=DISABLED, text='Scripting')

class ConnectionTab():
    def __init__(self, notebook):
        self.notebook = notebook
        self.frame = tk.Frame(self.notebook)
        
        self.topframe = tk.Frame(self.frame)
        self.heading_frame = tk.Frame(self.topframe)
        self.subtitle = tk.Label(self.heading_frame, text="You are connected to:")
        self.heading = tk.Label(
            self.heading_frame, 
            text=self.notebook.root.sonicamp.info['type'],
            font="QTypeOT-CondBook 30 bold",
        )
        self.control_frame = tk.Frame(self.topframe)
        self.ports_menue = tk.OptionMenu(
            self.control_frame,
            variable = self.notebook.root.port,
            value=self.notebook.root.sonicamp.device_list[0],
            values=self.notebook.root.sonicamp.device_list,
            style="primary.TOption"
        )
        self.connect_button = tk.Button(
            self.control_frame, 
            text='Connect', 
            command=self.auto_connect, 
            style="success.TButton",
            width=10
        )
        self.refresh_button = tk.Button(
            self.control_frame, 
            text='Refresh', 
            command=self.get_ports, 
            style="outline.TButton"
        )
        self.disconnect_button = tk.Button(self.control_frame, text='Disconnect', command=self.disconnect, style="danger.TButton", width=10)
        self.botframe = tk.Frame(self.frame)

        if self.notebook.root.sonicamp.is_connected:
            self.connected()
        else:
            self.not_connected()
            
        self.notebook.add(self.frame, state=NORMAL, text='Connection')

    def not_connected(self):
        pass

    def connected(self):
        pass


class InfoTab():
    def __init__(self, notebook):
        self.frame = tk.Frame(notebook)
        notebook.add(self.frame, state=DISABLED, text='Info')
        




        