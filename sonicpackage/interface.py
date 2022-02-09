import sys
import tkinter as tk
import tkinter.ttk as ttk
import ttkbootstrap as ttkb
from tkinter import font
from PIL import ImageTk
from ttkbootstrap import Style
from ttkbootstrap.constants import *

sys.path.append('C://Users//Ilja Golovanov//Documents//dev//SonicWipeControl//sonicpackage')
sys.path.append('C://Users//iljag//Documents//sh_doc//WfH//python_gui//new_gui//sonicpackage')

from sonicpackage.gui_parts.home import HomeTab
from sonicpackage.gui_parts.scripting import ScriptingTab
from sonicpackage.gui_parts.connection import ConnectionTab
from sonicpackage.gui_parts.info import InfoTab
from sonicpackage.gui_parts.skeleton import SonicFrame
from sonicpackage.utils.img import resize_img
from sonicpackage.connection import SerialConnection
from sonicpackage.data import SonicAmp, Modules, Status, Command
from sonicpackage.threads import GuiBuilder, SonicAgent


class Root(tk.Tk):

    def __init__(self, *args, **kwargs) -> None:
        tk.Tk.__init__(self, *args, **kwargs)
        
        self.sonic_agent: object
        self.sonicamp: object
        self.serial: object
        
        # root variables for gui
        self.port: str = tk.StringVar()
        self.wiperuns: str  = tk.StringVar()
        self.input_gain: object = tk.IntVar()
        self.output_gain: object = tk.IntVar()
        self.mode: str = "kHz"
        self.prev_status: list = []
        
        #Defining custom fonts
        self.arial12: object = font.Font(
            family="Arial", 
            size=12, 
            weight=font.BOLD)
        
        self.qtype12: object = font.Font(
            family="QTypeOT-CondMedium", 
            size=12, 
            weight=font.BOLD)
        
        # Defining images
        # Uses custom resize funtion in utils file
        self.refresh_img: object = ImageTk.PhotoImage(
            resize_img('sonicpackage//pictures//refresh_icon.png', (20, 20)))
        self.home_img: object = ImageTk.PhotoImage(
            resize_img('sonicpackage//pictures//home_icon.png', (30, 30)))
        self.script_img: object = ImageTk.PhotoImage(
            resize_img('sonicpackage//pictures//script_icon.png', (30, 30)))
        self.connection_img: object = ImageTk.PhotoImage(
            resize_img('sonicpackage//pictures//connection_icon.png', (30, 30)))
        self.info_img: object = ImageTk.PhotoImage(
            resize_img('sonicpackage//pictures//info_icon.png', (30, 30)))
        self.play_img: object = ImageTk.PhotoImage(
            resize_img('sonicpackage//pictures//play_icon.png', (30, 30)))
        self.pause_img: object = ImageTk.PhotoImage(
            resize_img('sonicpackage//pictures//pause_icon.png', (30, 30)))
        self.wave_bg: object = ImageTk.PhotoImage(
            resize_img('sonicpackage//pictures//wave_bg.png', (540,440)))
        self.graph_img: object = ImageTk.PhotoImage(
            resize_img('sonicpackage//pictures//graph.png', (100,100)))
        self.led_green_img: object = ImageTk.PhotoImage(
            resize_img('sonicpackage//pictures//led_green.png', (35,35)))
        self.led_red_img: object = ImageTk.PhotoImage(
            resize_img('sonicpackage//pictures//led_red.png', (35,35)))

        # setting up root window, configurations
        self.geometry("540x900")
        self.minsize(540, 900)
        self.maxsize(1080,900)
        self.wm_title('SonicControl')
        style = Style(theme="sandstone")        
        # default font in GUI
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family='Arial', size=12) 
        self.option_add("*Font", default_font)

        # Defining the sonicamp and serial object for communication and data storage
        
        self.serial = SerialConnection()
        self.serial.auto_connect()
        self.sonicamp = self.serial.initialize_amp()
        
        print(self.serial.device_list)
        print(self.sonicamp)
        
        if self.sonicamp.amp_type == 'soniccatch':
            self.sonicamp.frq_range_start = 600000
            self.sonicamp.frq_range_stop = 6000000
        
        elif self.sonicamp.amp_type == 'sonicwipe':
            self.sonicamp.frq_range_start = 50000
            self.sonicamp.frq_range_stop = 1200000
        
        self.build_window()
        
        # Defining Agent for automatic status data exchange
        self.sonic_agent = SonicAgent(self.serial)
        self.sonic_agent.daemon = True
        self.sonic_agent.start()
        
        self.gui_builder = GuiBuilder(self)
        self.gui_builder.daemon = True
        self.gui_builder.start()
        
        self.checkout_amp()
    
    
    def checkout_amp(self) -> None:
        """Checks out Amp every 100 milliseconds and makes sure that the thread is working correctly"""
        
        self.process_incoming()
        if not self.serial.is_connected and self.sonic_agent.paused == False:
            self.sonic_agent.pause()
            # self.gui_builder.pause()
        if not self.serial.is_connected:
            self.build_for_not_connected()
        self.after(100, self.checkout_amp)


    def process_incoming(self) -> None:
        """Reads the Queue object provided by the thread and configures the sonicamp object accordingly"""
        #! GLASMÜLL BEIM TSCHIKN MITNEHMEN
        while self.sonic_agent.queue.qsize():
            status_str = self.sonic_agent.queue.get(0)
            tmp_status = Status.construct_from_str(status_str)
            print(tmp_status)
            print(self.sonicamp.status)
            if self.serial.is_connected:
                if tmp_status == self.sonicamp.status:
                    print("nichts neues zu ändern")
                    continue
                else:
                    self.sonicamp.status = tmp_status
                    self.children.update()
            else:
                self.build_for_not_connected()
            

    def build_for_not_connected(self):
        print("window updater not connected")
        # setting all values to None
        self.sonicamp.connection = "not connected"
        self.sonicamp.signal = "signal off"
        self.sonicamp.status = Status(0, 0, 0, 0, 0)
        self.status_frame.con_status_label.configure(text=self.sonicamp.connection,
                                                     image=self.led_red_img)
        self.status_frame.sig_status_label.configure(text=self.sonicamp.signal,
                                                     image=self.led_red_img)
        self.status_frame.frq_meter["amountused"] = self.sonicamp.status.frequency / 1000000
        self.status_frame.gain_meter["amountused"] = self.sonicamp.status.gain


    def build_window(self) -> None:
        """Function to build other frames when starting the programm"""
        
        self.notebook: object = NotebookMenu(self, self.serial, self.sonicamp)
        self.status_frame: object = StatusFrame(self, self.serial, self.sonicamp, style='dark.TFrame')



class NotebookMenu(SonicFrame, ttk.Notebook):
    
    def __init__(self, root: object, serial: object, sonicamp: object, *args, **kwargs) -> None:
        SonicFrame.__init__(self, root, root, serial, sonicamp)
        ttk.Notebook.__init__(self, root, *args, **kwargs)
        
        self.config(height=560, width=540)
        self['style'] = 'light.TNotebook'
        
        self.home_tab: object = HomeTab(self, self.root, self.serial, self.sonicamp)
        self.script_tab: object = ScriptingTab(self, self.serial, self.sonicamp)
        self.connection_tab: object = ConnectionTab(self, self.root, self.serial, self.sonicamp)
        self.info_tab: object = InfoTab(self, self.root, self.serial, self.sonicamp)
         
        if not serial.is_connected:
            for child in self.children.values():
                if child != self.connection_tab:
                    self.tab(child, state=tk.DISABLED)
        
        self.select(self.connection_tab)
        
        self.publish()


    def publish(self) -> None:
        self.pack(padx=5, pady=5)#grid(row=0, column=0, padx=2.5, pady=2.5)
    
    def build_for_catch(self) -> None:
        pass
    
    def build_for_wipe(self) -> None:
        pass


class StatusFrame(SonicFrame, ttkb.Frame):
    
    def __init__(self, root: object, serial: object, sonicamp: object, *args, **kwargs) -> None:
        SonicFrame.__init__(self, root, root, serial, sonicamp)
        ttkb.Frame.__init__(self, root, *args, **kwargs)
        
        self.meter_frame: object = ttk.Frame(self)
        self.stati_frame: object = ttk.Frame(self, style='secondary.TFrame')
        
        self.frq_meter: object = ttkb.Meter(
            self.meter_frame,
            bootstyle='dark',
            amounttotal=self.sonicamp.frq_range_stop / 1000000,
            amountused=0,
            textright='MHz',
            subtext='Current Frequency',
            metersize=150)
        
        self.gain_meter: object = ttkb.Meter(
            self.meter_frame,
            bootstyle='success',
            amounttotal=150,
            amountused=0,
            textright='%',
            subtext='Current Gain',
            metersize=150)
        
        self.temp_meter: object = ttkb.Meter(
            self.meter_frame,
            bootstyle='warning',
            amounttotal=100,
            amountused=0,
            textright='°C',
            subtext='Liquid Temperature',
            metersize=150)
        
        self.con_status_label: object = ttkb.Label(
            self.stati_frame,
            font="QTypeOT-CondBook 15",
            padding=(5,0,5,0),
            justify=tk.CENTER,
            anchor=tk.CENTER,
            compound=tk.LEFT,
            width=15,
            image=self.root.led_green_img,
            bootstyle="inverse-secondary",
            text="not connected")
        
        self.sig_status_label: object = ttkb.Label(
            self.stati_frame,
            font="QTypeOT-CondBook 15",
            padding=(5,0,5,0),
            justify=tk.CENTER,
            anchor=tk.CENTER,
            compound=tk.LEFT,
            width=10,
            image=self.root.led_red_img,
            bootstyle="inverse-secondary",
            text=self.sonicamp.signal)
        
        self.err_status_label: object = ttkb.Label(
            self.stati_frame,
            font="QTypeOT-CondBook 15",
            padding=(5,5,5,5),
            justify=tk.CENTER,
            anchor=tk.CENTER,
            compound=tk.CENTER,
            relief=tk.RIDGE,
            width=10,
            text=self.sonicamp.error)
        
        self.sep: object = ttkb.Separator(
            master=self,
            orient=ttkb.VERTICAL,
            style='dark')
        
        self.build4catch()
        self.pack(padx=10, pady=10, fill=tk.BOTH)

    def build4catch(self):
        self.frq_meter.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.gain_meter.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)
        self.temp_meter.grid(row=0, column=2, padx=10, pady=10, sticky=tk.NSEW)
        
        self.con_status_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.sig_status_label.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)
        
        self.meter_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH, ipadx=10, ipady=10)
        self.stati_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=0, pady=0)
    
    def build4wipe(self):
        pass
        
    def build_for_catch(self) -> None:
        pass
    
    def build_for_wipe(self) -> None:
        pass
        


if __name__ == "__main__":
    gui = Root()
    gui.mainloop()
    gui.sonicamp.is_connected = False

        

    
