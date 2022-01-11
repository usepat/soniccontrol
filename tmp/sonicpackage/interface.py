import tkinter as tk
import tkinter.ttk as ttk
import ttkbootstrap as ttkb
from ttkbootstrap import Style
from ttkbootstrap.constants import *
from tkinter import font
from PIL import ImageTk
import time

from ttkbootstrap.style import Bootstyle

from sonicpackage.gui_parts.home import HomeTab
from sonicpackage.gui_parts.scripting import ScriptingTab
from sonicpackage.gui_parts.connection import ConnectionTab
from sonicpackage.gui_parts.info import InfoTab
from sonicpackage.utils.img import resize_img
from sonicpackage.connection import SonicAmp, SerialConnection
from sonicpackage.sonicthread import SonicAgent


class Root(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        
        # setting up root window
        self.geometry("540x900")
        self.minsize(540, 900)
        self.maxsize(1080,900)
        self.wm_title('SonicControl')
        style = Style(theme="sandstone")        
        
        # Defining and setting font
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family='Arial', size=12) 
        self.option_add("*Font", default_font)

        self.arial12 = font.Font(family='Arial', size=12, weight=font.BOLD)
        self.qtype12 = font.Font(family='QTypeOT-CondMedium', size=12, weight=font.BOLD)
        
        # Defining images
        # Uses custom resize funtion in utils file
        self.refresh_img = ImageTk.PhotoImage(
            resize_img('sonicpackage//pictures//refresh_icon.png', (20, 20)))
        self.home_img = ImageTk.PhotoImage(
            resize_img('sonicpackage//pictures//home_icon.png', (30, 30)))
        self.script_img = ImageTk.PhotoImage(
            resize_img('sonicpackage//pictures//script_icon.png', (30, 30)))
        self.connection_img = ImageTk.PhotoImage(
            resize_img('sonicpackage//pictures//connection_icon.png', (30, 30)))
        self.info_img = ImageTk.PhotoImage(
            resize_img('sonicpackage//pictures//info_icon.png', (30, 30)))
        self.play_img = ImageTk.PhotoImage(
            resize_img('sonicpackage//pictures//play_icon.png', (30, 30)))
        self.pause_img = ImageTk.PhotoImage(
            resize_img('sonicpackage//pictures//pause_icon.png', (30, 30)))
        self.wave_bg = ImageTk.PhotoImage(
            resize_img('sonicpackage//pictures//wave_bg.png', (540,440)))

        # Declaring the sonicamp and serial object for communication and data storage
        # To be found in connection
        self.serial = SerialConnection()
        self.sonicamp = SonicAmp(self.serial)
        # try to auto connect
        self.serial.connect_to_port(auto=True)
        # Getting data into a dictionary 
        self.sonicamp.get_info()
        
        print(self.serial.device_list)
        print(self.sonicamp.info)

        # root variables for gui
        self.port = tk.StringVar(value=f"{self.sonicamp.info['port']}")
        self.wiperuns = tk.StringVar()
        self.frequency = tk.StringVar()
        
        #TODO: KHZ und MHZ synchronisation
        self.frq_mode = 'KHZ'

        # Declaring Agent for automatic status data exchange
        self.status_thread = SonicAgent(self.serial)
        self.status_thread.daemon = True
        self.status_thread.start()
        
        while self.sonicamp.info == None:
            time.sleep(1)
            if self.sonicamp.info:
                break
        
        self.checkout_amp()
        self.build_window()
    
    def checkout_amp(self):
        self.process_incoming()
        if not self.serial.is_connected and self.status_thread.pause == False:
            print("pausing thread")
            self.status_thread.pause()
        elif not self.serial.is_connected and self.status_thread.pause == True:
            self.status_thread.pause_cond.wait()
        self.after(50, self.checkout_amp)


    def process_incoming(self):
        while self.serial.queue.qsize():
            try:
                status = self.serial.queue.get(0)
                self.sonicamp.get_status(status)
                # print(self.sonicamp.info['status']['frequency'])
                print(self.sonicamp.info.get('status').get('frequency'))
                if self.sonicamp.info['status']['error'] == 0:
                    self.window_updater(self.sonicamp.info['status'])
                else:
                    self.serial.is_connected = False

            except:
                pass
    
    
    def window_updater(self, update_dict):
        pass
    

    def build_window(self):
        self.notebook = NotebookMenu(self, self.serial, self.sonicamp)
        self.status_frame = StatusFrame(self, self.serial, self.sonicamp)



class NotebookMenu(ttk.Notebook):
    
    @property
    def root(self):
        return self._root
    
    @property
    def sonicamp(self):
        return self._sonicamp
    
    @property
    def serial(self):
        return self._serial
    
    def __init__(self, root, serial, sonicamp, *args, **kwargs):
        ttk.Notebook.__init__(self, root, *args, **kwargs)
        self._root = root
        self._sonicamp = sonicamp
        self._serial = serial
        
        self.config(height=560, width=540)
        self['style'] = 'light.TNotebook'
        
        self.home_tab = HomeTab(self, self.root, self.serial, self.sonicamp)
        self.script_tab = ScriptingTab(self, self.serial, self.sonicamp)
        self.connection_tab = ConnectionTab(self, self.root, self.serial, self.sonicamp)
        self.info_tab = InfoTab(self)
        
        if not serial.is_connected:
            for child in self.children.values():
                if child != self.connection_tab:
                    self.tab(child, state=tk.DISABLED)
        
        self.select(self.connection_tab)
        
        self.publish()


    def publish(self):
        self.pack()#grid(row=0, column=0, padx=2.5, pady=2.5)


class StatusFrame(ttk.Frame):
    
    @property
    def root(self):
        return self._root
    
    @property
    def sonicamp(self):
        return self._sonicamp
    
    @property
    def serial(self):
        return self._serial
    
    def __init__(self, root, serial, sonicamp, *args, **kwargs):
        ttk.Frame.__init__(self, root, *args, **kwargs)
        
        self._root = root
        self._serial = serial
        self._sonicamp = sonicamp
        
        self.canvas = tk.Canvas(self, width=540, height=440)
        self.canvas.pack()
        
        self.bg = self.canvas.create_image(0, 0, image=self.root.wave_bg)
        
        self.frq_meter = self.add(ttkb.Meter(
            self,
            bootstyle='primary',
            amounttotal=1200000,
            amountused=self.sonicamp.info.get('status').get('frequency'),
            textright='Hz',
            subtext='Current Frequency',
            metersize=150,
        ), 10, 10)
        self.frq_meter.pack(side=tk.LEFT)
        
        self.gain_meter = self.add(ttkb.Meter(
            self,
            bootstyle='success',
            amounttotal=150,
            amountused=self.sonicamp.info.get('status').get('gain'),
            textright='%',
            subtext='Current Gain',
            metersize=150
        ), 50, 10)
        #self.gain_meter.pack(side=tk.LEFT)
        
        self.temp_meter = self.add(ttkb.Meter(
            self,
            bootstyle='warning',
            amounttotal=150,
            amountused=self.sonicamp.info.get('status').get('gain'),
            textright='°C',
            subtext='Inner Temperature',
            metersize=150
        ), 100, 10)
        #self.temp_meter.pack(side=tk.LEFT)
        
        self.sep = self.add(ttkb.Separator(
            master=self,
            orient=ttkb.VERTICAL,
            style='primary',
        ), 150, 10)
        self.sep.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        self.pack(padx=10, pady=10, fill=tk.BOTH)

    
    def add(self, widget, x, y):
        canvas_window = self.canvas.create_window(x, y, anchor=tk.NW, window=widget)
        return widget

if __name__ == "__main__":
    gui = Root()
    gui.mainloop()
    gui.sonicamp.is_connected = False

        

    
