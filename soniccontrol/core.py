import tkinter as tk
import tkinter.ttk as ttk
import ttkbootstrap as ttkb
from tkinter import font
from ttkbootstrap import Style

from fonts import *
from pictures import *
from gui import HomeTabCatch, ScriptingTab, ConnectionTab, InfoTab

class Root(tk.Tk):
    """
    The class Root defines the whole GUI application named soniccontrol. 
    It composites all the tkinter objects of the window.
    """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(self, *args, **kwargs)

        # setting up root window, configurations
        self.geometry("540x900")
        self.minsize(540, 900)
        self.maxsize(1080,900)
        self.wm_title('SonicControl')
        style = Style(theme="sandstone") 

        # default font in GUI and custom Fonts
        default_font: font.Font = font.nametofont("TkDefaultFont")
        default_font.configure(family='Arial', size=12) 
        self.option_add("*Font", default_font)

        self.arial12: font.Font = font.Font(
            family="Arial", 
            size=12, 
            weight=tk.font.BOLD)
        
        self.qtype12: font.Font = font.Font(
            family="QTypeOT-CondMedium", 
            size=12, 
            weight=tk.font.BOLD)


        # Children of Root
        self.notebook: NotebookMenu = NotebookMenu(self, self.serial, self.sonicamp)
        self.status_frame: StatusFrameCatch = StatusFrameCatch(self, self.serial, self.sonicamp, style='dark.TFrame')




class NotebookMenu(ttk.Notebook):

    def __init__(self) -> None:
        """ Notebook object """
        self.config(height=560, width=540)
        self['style'] = 'light.TNotebook'
        
        self.hometab: HomeTabCatch = HomeTabCatch(self)
        self.scriptingtab: ScriptingTab = ScriptingTab(self)
        self.connectiontab: ConnectionTab = ConnectionTab(self)
        self.infotab: InfoTab = InfoTab(self)
        
    def publish_for_catch(self) -> None:
        """ Builds children and displayes menue for a soniccatch """
        self.add(self.hometab, text="Home")
        self.add(self.scriptingtab, text="Scripting")
        self.add(self.connectiontab, "Connection")
        self.add(self.infotab, "Info")
        self.select(self.connectiontab)
        self.pack(padx=5, pady=5)
        
    def disable_children(self) -> None:
        """ Disables childen and selects connection tab (case: not connected)"""
        for child in self.children.values():
            if child != self.connectiontab:
                self.tab(child, state=tk.DISABLED)
        self.select(self.connectiontab)
    
    def enable_children(self) -> None:
        """ Enables all children """
        for child in self.children.values():
            self.tab(child, state=tk.NORMAL)


class StatusFrameCatch(ttk.Frame):
    
    def __init__(self, *args, **kwargs) -> None:
        """
        Statusframe object, that is used in case the GUI is
        connected to a SonicCatch
        """
        super().__init__(*args, **kwargs)
        
        # Is being splittet into two main frames
        # Each organizes it's children through grid
        self.meter_frame: ttk.Frame = ttk.Frame(self)
        self.overview_frame: ttk.Frame = ttk.Frame(self)
        
        # Meterframe objects
        self.frq_meter: ttkb.Meter = ttkb.Meter(
            self.meter_frame,
            bootstyle='dark',
            amounttotal=6000000 / 1000, 
            amountused=0,
            textright='kHz',
            subtext='Current Frequency',
            metersize=150)
        
        self.gain_meter: ttkb.Meter = ttkb.Meter(
            self.meter_frame,
            bootstyle='success',
            amounttotal=150,
            amountused=0,
            textright='%',
            subtext='Current Gain',
            metersize=150)
        
        self.temp_meter: ttkb.Meter = ttkb.Meter(
            self.meter_frame,
            bootstyle='warning',
            amounttotal=100,
            amountused=0,
            textright='°C',
            subtext='Liquid Temperature',
            metersize=150)
        
        # Overview frame objects
        self.con_status_label: ttkb.Label = ttkb.Label(
            self.stati_frame,
            font="QTypeOT-CondBook 15",
            padding=(5,0,5,0),
            justify=tk.CENTER,
            anchor=tk.CENTER,
            compound=tk.LEFT,
            width=15,
            image=led_red_img,
            bootstyle="inverse-secondary",
            text="not connected")
        
        self.sig_status_label: ttkb.Label = ttkb.Label(
            self.stati_frame,
            font="QTypeOT-CondBook 15",
            padding=(5,0,5,0),
            justify=tk.CENTER,
            anchor=tk.CENTER,
            compound=tk.LEFT,
            width=10,
            image=led_red_img,
            bootstyle="inverse-secondary",
            text="Signal OFF")
        
        self.err_status_label: ttkb.Label = ttkb.Label(
            self.stati_frame,
            font="QTypeOT-CondBook 15",
            padding=(5,5,5,5),
            justify=tk.CENTER,
            anchor=tk.CENTER,
            compound=tk.CENTER,
            relief=tk.RIDGE,
            width=10,
            text=None)
        
    def publish(self) -> None:
        """ Function to build the statusframe """
        self.frq_meter.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.gain_meter.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)
        self.temp_meter.grid(row=0, column=2, padx=10, pady=10, sticky=tk.NSEW)
        
        self.con_status_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.sig_status_label.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)
        
        self.meter_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH, ipadx=10, ipady=10)
        self.stati_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=0, pady=0)
    
    def abolish_data(self) -> None:
        """ Function to repeal setted values """
        self.frq_meter["amountused"] = 0
        self.gain_meter["amountused"] = 0
        self.temp_meter["amountused"] = 0
        
        self.con_status_label["image"] = led_red_img
        self.con_status_label["text"] = "Not Connected"
        
        self.sig_status_label["image"] = led_red_img
        self.sig_status_label["text"] = "Signal OFF"
        
    
    def attach_data(self, sonicamp: object) -> None:
        """ Function to configure objects to corresponding data """
        self.frq_meter["amountused"] = 0
        self.gain_meter["amountused"] = 0
        self.temp_meter["amountused"] = 0
        
        self.con_status_label["image"] = led_red_img
        self.con_status_label["text"] = "Not Connected"
        
        self.sig_status_label["image"] = led_red_img
        self.sig_status_label["text"] = "Signal OFF"
    



class StatusFrameWipe(ttk.Frame):
    
    def __init__(self, *args, **kwargs) -> None:
        """
        Statusframe object, that is used in case the GUI is
        connected to a SonicWipe
        """
        super().__init__(*args, **kwargs)
        
        # Is being splittet into two main frames
        self.meter_frame: ttk.Frame = ttk.Frame(self)
        self.overview_frame: ttk.Frame = ttk.Frame(self)
        
    def publish(self) -> None:
        """ Function to build the statusframe """
        pass
    
    def abolish_data(self) -> None:
        """ Function to repeal setted values """
        pass
    
    def attach_data(self) -> None:
        """ Function to configure objects to corresponding data """
        pass       
        
