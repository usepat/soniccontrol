# General libraries
import datetime
from os import error
import threading
import time
from PIL import Image, ImageTk
# Tkinter
import tkinter as tk
# import ttkbootstrap as ttk
import tkinter.ttk as ttk
import ttkbootstrap as ttkb
import tkinter.scrolledtext as st
from serial.win32 import CE_FRAME
from ttkbootstrap import Style
from tkinter import font
from tkinter import filedialog
from tkinter import messagebox
from tkinter import *
#PySerial Libraries
import serial
from serial.serialutil import SerialException, Timeout
import serial.tools.list_ports
#
import queue
import pyglet
from sonicfont.connection_thread import Concur


root = tk.Tk()

style = Style(theme='sandstone')

root.geometry("540x900")
root.maxsize(540, 900)
root.minsize(540, 900)
# root.iconbitmap('welle.ico')
root.wm_title('SonicControl')

default_font = tk.font.nametofont("TkDefaultFont")
default_font.configure(family='Arial', size=12) 
root.option_add("*Font", default_font)

pyglet.font.add_file('.//sonicfont//QTypeOT-CondExtraLight.otf')
pyglet.font.add_file('.//sonicfont//QTypeOT-CondLight.otf')
pyglet.font.add_file('.//sonicfont//QTypeOT-CondMedium.otf')
pyglet.font.add_file('.//sonicfont//QTypeOT-CondBook.otf')
pyglet.font.add_file('.//sonicfont//QTypeOT-CondBold.otf')


class App:
    
    def __init__(self, master):
        
        self.master = master
        
        self.arial12 = font.Font(family='Arial', size=12, weight=font.BOLD)
        self.qtype12 = font.Font(family='QTypeOT-CondMedium', size=12, weight=font.BOLD)

        self.var_port = tk.StringVar()
        self.device_list = []
        self.firmware_text = tk.StringVar()
        self.connection_status = ""
        self.sonicamp = ""
        
        self.serial_running = False
        self.queue = queue.Queue()
        self.status_thread = threading.Thread(target=self.statusworker_thread)
        self.serial_state = threading.Condition()
        self.connection_lock = self.serial_state.acquire()
        self.serial_state.wait()
        self.status_thread.start()
        
        self.modules = []
        self.signal = False
        self.frequency = 0
        self.gain = 0
        self.protocol = ""
        self.protocol_options = ""
        
        self.get_ports()
        self.auto_connect(True)
        
        self.sonic_control = ttk.Frame(self.master)
        self.notebook = ttkb.Notebook(self.sonic_control, bootstyle="primary")
        self.statusframe = ttk.Frame(self.sonic_control)

        self.home_tab_builder()
        self.script_tab_builder()
        self.connection_tab_builder()
        self.info_tab_builder()
        self.status_builder()
                
        self.notebook.select(self.tab_connection)
        
        self.sonic_control.config(borderwidth=0, height=900, width=540)
        self.sonic_control.pack(side=TOP)
        
        
    def script_tab_builder(self):    
        self.tab_script = ttk.Frame(self.notebook)
        self.script_button = ttk.Button(self.tab_script, text="SCRIPT")
        self.script_button.pack()
        self.tab_script.pack(side=TOP)
        self.notebook.add(self.tab_script, text='Scripting')
        
    def home_tab_builder(self):
        self.tab_manual = ttk.Frame(self.notebook)
        self.manual_button = ttk.Button(self.tab_manual, text="MANUAL")
        self.manual_button.pack()
        self.tab_manual.pack(side=TOP)
        self.notebook.add(self.tab_manual, padding=0, state=NORMAL, sticky=NSEW, text='Manual')
        
        
    def connection_tab_builder(self):    
        
        self.tab_connection = ttk.Frame(self.notebook)
        
        topframe = ttk.Frame(self.tab_connection)
        headframe = ttk.Frame(topframe)
        connectionframe = ttk.Frame(topframe, style="secondary.TFrame", border=5)
        
        botframe = ttk.Frame(self.tab_connection)
                
        self.connection_label = ttk.Label(headframe, text=self.connection_status, font="QTypeOT-CondBook 30 bold", padding=10, anchor=W)
        
        self.comports_box = ttk.OptionMenu(connectionframe, self.var_port, self.device_list[0], *self.device_list, style="primary.TOption")
        self.connect_button = ttk.Button(connectionframe, text='Connect', command=self.auto_connect, style="success.TButton" ,width=10)
        self.refresh_button = ttk.Button(connectionframe, text='Refresh', command=self.get_ports, style="outline.TButton")
        self.disconnect_button = ttk.Button(connectionframe, text='Disconnect', command=self.disconnect, style="danger.TButton", width=10)

        self.firmwareframe = ttkb.Labelframe(botframe, height='200', text=f'Firmware Info', width='200', style="primary.TLabelframe")#, font="QTypeOT-CondBook 10 bold")
        self.firmwarelabel = ttk.Label(self.firmwareframe, text='No SonicAmp connected', textvariable=self.firmware_text, font="Consolas")

        self.connection_label.pack(anchor=CENTER, side=TOP, padx=15, pady=15)

        self.comports_box.grid(sticky=NSEW, column=0, row=0, padx=5, pady=5)
        self.connect_button.grid(sticky=tk.N, column=1, row=0, padx=5, pady=5)
        self.refresh_button.grid(sticky=tk.W, column=0, row=1, padx=5, pady=5)
        self.disconnect_button.grid(sticky=tk.E, column=1, row=1, padx=5, pady=5)

        self.firmwarelabel.pack(padx='10', pady='10', side='top')
        self.firmwareframe.pack(pady='30', side='top')
        self.firmwareframe.pack_propagate(0)

        # self.comports_box.pack(anchor=CENTER, side=LEFT, padx=5, pady=5)
        # self.connect_button.pack(anchor=tk.N, side=LEFT, padx=5, pady=10)
        # self.refresh_button.pack(anchor=tk.W, side=LEFT, padx=40, pady=5)
        # self.disconnect_button.pack(anchor=tk.E, side=tk.RIGHT, padx=40, pady=5)

        topframe.pack(anchor=N, side=TOP)
        headframe.pack(anchor=CENTER, side=TOP)
        connectionframe.pack(anchor=CENTER, side=BOTTOM, expand=True)
        botframe.pack(anchor=CENTER, side=TOP)
        # primary_frame.pack(anchor=CENTER, side=TOP, expand=True)
        # secondary_frame.pack(anchor=CENTER, side=BOTTOM, expand=True)
        
        self.tab_connection.pack(side=TOP)
        self.notebook.add(self.tab_connection, text='Connection')
        
        
    def info_tab_builder(self):
        self.tab_info = ttk.Frame(self.notebook)
        self.info_button = ttk.Button(self.tab_info, text="INFO")
        self.info_button.pack()
        self.tab_info.pack(side=TOP)
        self.notebook.add(self.tab_info, text='Info')
        self.notebook.config(height=680, width=530)
        self.notebook.pack(expand=True, fill=BOTH, side=TOP)


    def status_builder(self):
        # self.frequency_meter = ttk.Meter(self.statusframe, style="primary.", subtextstyle="info")
        # self.frequency_meter.pack()
        self.statusframe.pack(side=BOTTOM)


#*********************** METHODS FOR SERIAL INTERFACE ***************************************************


    def get_ports(self):
        """Loops through the possible serial connections, except the internal serial connection port of the pc and returns said list

        Returns:
            list:   Possible serial connection addresses in a string object
        """
        
        comports = []
        for self.index, self.port in enumerate(serial.tools.list_ports.comports(), start=0):
            if self.port.device != 'COM1':
                comports.append(self.port.device)
            
        self.device_list = comports
    
    
    def auto_connect(self, auto=False):
        """This function connects to an sonicamp system via the serial interface.

        Args:
            auto (bool, optional): When passed True, the function automatically 
            searches for an amp system and connects if only one is connected. 
            This is used during the initialization of the program, 
            due to conventional reasons. Defaults to False.
        """
        
        #TODO Make auto mode of this function available for linux und mac
        if len(self.device_list) == 1:
                self.connect_to_port(self.device_list[0]) 
            
        elif len(self.device_list) > 1:
            
            if auto:
                pass
            
            else:
                
                try:
                    self.connect_to_port(self.var_port.get())
                except Exception:
                    self.error_message('serial_port')
        
        
    def connect_to_port(self, port):
        """Connects to the given serial port and initializes the sonic amp system to communicate via the serial connection

        Args:
            port (string): The serial address of the sonic amp system
        """
        
        try:
            self.serial_connection = serial.Serial(port, 115200, timeout=0.3)
            time.sleep(5)
            self.connection_status = "connected"
            # self.connect_button.configure(text='Disconnect', command=self.disconnect)
            self.send_message('!SERIAL', read_line=False, flush = True, delay=0.5)
            # time.sleep(1)
            self.firmware_text.set(self.send_message('?info', read_line=False, flush = True))
            self.sonicamp = self.send_message("?type")
            print(self.sonicamp)
            self.modules = self.send_message('=')#.split('=')
            self.get_modules(self.modules)
            self.serial_running = True
            self.serial_state.notify()
            self.periodic_call()
            
        except SerialException:
            pass
    
    
    def disconnect(self):
        self.connection_status = 'not connected'
        self.serial_running = False
        self.firmware_text.set('')
        self.serial_connection.close()
        # self.canvas.itemconfig(self.LEDAmp, fill=self.red)
        # self.notebook_1.tab(self.tabManual, state='disabled')
        # self.notebook_1.tab(self.tabScripting, state='disabled')
    
    
    def send_message(self, message, read_line=True, flush=False, delay=0.05, wait=0.1):
        """Takes a string, decodes it and finally sends said string to a sonicamp system.
        Further, receives the answer from the sonicamp, decodes it and returns the data as
        a string.

        Args:
            message (string): The string to be send to a sonicamp system
            read_line (bool, optional): Reads the answer in lines, if False, reads in 255 Bytes. Defaults to True.
            flush (bool, optional): Flushes the register if set to True. Defaults to False.
            delay (float, optional): Delay between sending and reading data. Defaults to 0.05.

        Returns:
            string: The answer from the sonicamp system
        """
        
        if self.serial_connection.is_open:
            if flush:
                self.serial_connection.flushInput()
                
            self.serial_connection.write(f"{message}\n".encode())
            time.sleep(delay)

            if read_line == True:
                return self.serial_connection.readline().rstrip().decode()
            
            elif read_line == False:
                return self.serial_connection.read(255).rstrip().decode('cp1252')
            
            time.sleep(wait)

        else:
            self.error_message('connection')
            return False


#*********************** METHODS FOR THE STATUS THREAD (Communication Protocol) ***************************************************

    
    def periodic_call(self):
        
        self.process_incoming()
        
        if self.serial_running:
            self.connection_status = "connected"
            # self.connect_button.config(text='Disconnect', command=self.disconnect)#, style="danger")
        else:
            self.disconnect()
            
        self.master.after(200, self.periodic_call)
        
    
    def statusworker_thread(self):

        while self.serial_running:
            time.sleep(0.1)
            status = self.send_message('-')
            self.queue.put(status)
        
        with self.serial_state:
            self.serial_state.wait()
    

    def process_incoming(self):
        
        while self.queue.qsize():
            
            try:
                status = self.queue.get(0)
                print(status)
            
            except queue.Empty:
                pass
    
    
    def get_modules(self, module_list):
        print(module_list)
         

#*********************** METHODS FOR UTILITIES ***************************************************


    def error_message(self, category):
        
        if category == 'connection':
            messagebox.showerror("Error", "No connection is established, please recheck all connections and try to reconnect in the Connection Tab. Make sure the instrument is in Serial Mode.")
        
        elif category == 'serial_port':
            messagebox.showerror("Error", "No Serial port is selected. Please select the correct Serial port and reconnect.") 
                
            

if __name__ == '__main__':
    app = App(root)
    root.mainloop()
    app.disconnect()
    app.serial_running = False