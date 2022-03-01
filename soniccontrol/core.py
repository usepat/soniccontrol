from cgitb import lookup
import tkinter as tk
import tkinter.ttk as ttk
import ttkbootstrap as ttkb
from tkinter import font
from ttkbootstrap import Style
from PIL.ImageTk import PhotoImage

from sonicpackage import Command, Status, Modules, SonicCatch, SonicWipe, SerialConnection, SonicAmp
from sonicpackage.threads import SonicThread
from soniccontrol.fonts import *
import soniccontrol.pictures as pics
from soniccontrol.gui import HomeTabCatch, ScriptingTab, ConnectionTab, InfoTab
from soniccontrol.helpers import logger

class Root(tk.Tk):
    """
    The class Root defines the whole GUI application named soniccontrol. 
    It composites all the tkinter objects of the window.
    """
    
    MIN_WIDTH: int = 555
    MIN_HEIGHT: int = 900
    MAX_WIDTH: int = 1110
    TITLE: str = "Soniccontrol"
    THEME: str = "sandstone"
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
        self.serial: SerialConnection = SerialConnection()
        self.sonicamp: SonicAmp
        self.port: tk.StringVar = tk.StringVar()
        self.frq: tk.IntVar = tk.IntVar()
        
        # setting up root window, configurations
        self.geometry(f"{Root.MIN_WIDTH}x{Root.MIN_HEIGHT}")
        self.minsize(Root.MIN_WIDTH, Root.MIN_HEIGHT)
        self.maxsize(Root.MAX_WIDTH, Root.MIN_HEIGHT)
        self.wm_title(Root.TITLE)
        style = Style(theme=Root.THEME) 

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
        
        self.qtype30: font.Font = font.Font(
            family="QTypeOT-CondLight",
            size=30,)
        
        self.qtype30b: font.Font = font.Font(
            family="QTypeOT-CondBook",
            size=30,
            weight=tk.font.BOLD)        

        #Defining images
        self.refresh_img: PhotoImage = PhotoImage(pics.refresh_img)
        self.home_img: PhotoImage = PhotoImage(pics.home_img)
        self.script_img: PhotoImage = PhotoImage(pics.script_img)
        self.connection_img: PhotoImage = PhotoImage(pics.connection_img)
        self.info_img: PhotoImage = PhotoImage(pics.info_img)
        self.play_img: PhotoImage = PhotoImage(pics.play_img)
        self.pause_img: PhotoImage = PhotoImage(pics.pause_img)
        self.wave_bg: PhotoImage = PhotoImage(pics.wave_bg)
        self.graph_img: PhotoImage = PhotoImage(pics.graph_img)
        self.led_green_img: PhotoImage = PhotoImage(pics.led_green_img)
        self.led_red_img: PhotoImage = PhotoImage(pics.led_red_img)

        # Children of Root
        self.mainframe: ttk.Frame = ttk.Frame(self)
        self.notebook: NotebookMenu = NotebookMenu(self.mainframe, self)
        self.status_frame_catch: StatusFrameCatch = StatusFrameCatch(self.mainframe, self, style='dark.TFrame')
        self.status_frame_wipe: StatusFrameWipe = StatusFrameWipe(self.mainframe, self, style='dark.TFrame')
        logger.info("initialized children and root")
        
        self.thread: SonicThread = SonicAgent(self)
        self.thread.setDaemon(True)
        self.thread.start()
        
        self.__reinit__()
    
    def __reinit__(self) -> None:
        if self.serial.auto_connect():
            logger.info("autoconnected")
            self.decide_action()
        elif self.port.get()[:3] == ('COM' or '/de'):
            logger.info("manually connected")
            self.decide_action()
        else:
            logger.info("Did not detect connection")
            self.publish_disconnected()
            
    def attach_data(self) -> None:
        if self.sonicamp.amp_type == 'soniccatch':
            self.notebook.attach_data()
            self.status_frame_catch.attach_data()
        elif self.sonicamp.amp_type == 'sonicwipe':
            pass
    
    def decide_action(self) -> None:
        type_: str = self.serial.send_and_get(Command.GET_TYPE)
        if type_ == "soniccatch":
            logger.info("Found soniccatch")
            self.sonicamp = SonicCatch(self.serial)
            self.publish_for_catch()
        elif type_ == "sonicwipe":
            logger.info("Found sonicwipe")
            self.sonicamp = SonicWipe(self.serial)
            self.publish_for_wipe()
    
    def publish_disconnected(self) -> None:
        """ Publishes children in case there is no connection """
        logger.info("publishing for disconnected")
        self.notebook.publish_disconnected()
        self.mainframe.grid(row=0, column=0)
    
    def publish_for_catch(self) -> None:
        """ Publishes children in case there is a connection to a soniccatch """
        logger.info("publishing for catch")
        self.attach_data()
        self.notebook.publish_for_catch()
        self.status_frame_catch.publish()
        self.mainframe.grid(row=0, column=0)
    
    def publish_for_wipe(self) -> None:
        """ Publishes children in case there is a connection to a sonicwipe """
        logger.info("publishing for wipe")
        self.notebook.publish_for_wipe()
        self.status_frame_wipe.publish()
        self.mainframe.grid(row=0, column=0)
    
    def publish_sonicmeasure(self) -> None:
        """ Publishes the sonicmeasure frame """
        if self.adjust_dimensions():
            self.sonicmeasure: SonicMeasure = SonicMeasure(self)
    
    def publish_serial_monitor(self) -> None:
        """ Publishes the serial monitor """
        if self.adjust_dimensions():
            self.serial_monitor: SerialMonitor = SerialMonitor(self)
    
    def adjust_dimensions(self) -> bool:
        """ 
        Adjust heights and widths for the window 
        Returns true, if the window is in smaller width usage mode
        """
        if self.winfo_width() == Root.MIN_WIDTH:
            self.geometry(f"{Root.MAX_WIDTH}x{Root.MIN_HEIGHT}")
            return True
        else:
            self.geometry(f"{Root.MIN_WIDTH}x{Root.MIN_HEIGHT}")
            return False
            


class NotebookMenu(ttk.Notebook):

    @property
    def root(self) -> Root:
        return self._root

    def __init__(self, parent: ttk.Frame, root: Root, *args, **kwargs) -> None:
        """ Notebook object """
        super().__init__(parent, *args, **kwargs)
        self._root: Root = root
        self.config(height=560, width=540)
        self['style'] = 'light.TNotebook'
        
        self.hometab: HomeTabCatch = HomeTabCatch(self, self.root)
        self.scriptingtab: ScriptingTab = ScriptingTab(self, self.root)
        self.connectiontab: ConnectionTab = ConnectionTab(self, self.root)
        self.infotab: InfoTab = InfoTab(self, self.root)
        logger.info("initialized children and object")
        
    def attach_data(self) -> None:
        for child in self.children.values():
            child.attach_data()
        
    def publish_for_catch(self) -> None:
        """ Builds children and displayes menue for a soniccatch """
        self.add(self.hometab, text="Home", image=self.root.home_img, compound=tk.TOP)
        self.add(self.scriptingtab, text="Scripting", image=self.root.script_img, compound=tk.TOP)
        self.add(self.connectiontab, text="Connection", image=self.root.connection_img, compound=tk.TOP)
        self.add(self.infotab, text="Info", image=self.root.info_img, compound=tk.TOP)
        self.select(self.connectiontab)
        self.connectiontab.attach_data()
        self.publish_children()
        self.pack(padx=5, pady=5)
        
    def publish_for_wipe(self) -> None:
        pass
    
    def publish_disconnected(self) -> None:
        self.add(self.hometab, text="Home", image=self.root.home_img, compound=tk.TOP)
        self.add(self.scriptingtab, text="Scripting", image=self.root.script_img, compound=tk.TOP)
        self.add(self.connectiontab, text="Connection", image=self.root.connection_img, compound=tk.TOP)
        self.add(self.infotab, text="Info", image=self.root.info_img, compound=tk.TOP)
        self.select(self.connectiontab)
        self.connectiontab.abolish_data()
        self.publish_children()
        self.disable_children()
        self.pack(padx=5, pady=5)
        
    def publish_children(self) -> None:
        """ Publishes children """
        for child in self.children.values():
            child.publish()
                
    def disable_children(self) -> None:
        """ Disables childen and selects connection tab (case: not connected)"""
        for child in self.children.values():
            if child != self.connectiontab:
                self.tab(child, state=tk.DISABLED)
        self.select(self.connectiontab)
    
    def enable_children(self) -> None:
        """ Enables all children for use """
        for child in self.children.values():
            self.tab(child, state=tk.NORMAL)


class StatusFrameCatch(ttk.Frame):
    
    @property
    def root(self) -> tk.Tk:
        return self._root
    
    def __init__(self, parent: ttk.Frame, root: Root, *args, **kwargs) -> None:
        """
        Statusframe object, that is used in case the GUI is
        connected to a SonicCatch
        """
        super().__init__(parent, *args, **kwargs)
        self._root = root
        
        # Is being splittet into two main frames
        # Each organizes it's children through grid
        self.meter_frame: ttk.Frame = ttk.Frame(self)
        self.overview_frame: ttk.Frame = ttk.Frame(self, style="secondary.TFrame")
        
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
            self.overview_frame,
            font="QTypeOT-CondBook 15",
            padding=(5,0,5,0),
            justify=tk.CENTER,
            anchor=tk.CENTER,
            compound=tk.LEFT,
            width=15,
            image=self.root.led_red_img,
            bootstyle="inverse-secondary",
            text="not connected")
        
        self.sig_status_label: ttkb.Label = ttkb.Label(
            self.overview_frame,
            font="QTypeOT-CondBook 15",
            padding=(5,0,5,0),
            justify=tk.CENTER,
            anchor=tk.CENTER,
            compound=tk.LEFT,
            width=10,
            image=self.root.led_red_img,
            bootstyle="inverse-secondary",
            text="Signal OFF")
        
        self.err_status_label: ttkb.Label = ttkb.Label(
            self.overview_frame,
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
        self.overview_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=0, pady=0)
        self.pack()
    
    def show_error(self) -> None:
        """ Shows the errormessage in the overview frame"""
        for child in self.overview_frame.children.values():
            child.grid_forget()
        self.overview_frame["style"] = "danger.TFrame"
        self.err_status_label["text"] = None #!Here
        self.err_status_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.CENTER)
    
    def abolish_data(self) -> None:
        """ Function to repeal setted values """
        self.frq_meter["amountused"] = 0
        self.gain_meter["amountused"] = 0
        self.temp_meter["amountused"] = 0
        
        self.con_status_label["image"] = self.root.led_red_img
        self.con_status_label["text"] = "Not Connected"
        
        self.sig_status_label["image"] = self.root.led_red_img
        self.sig_status_label["text"] = "Signal OFF"
        
    
    def attach_data(self) -> None:
        """ Function to configure objects to corresponding data """
        logger.info("attaching data")
        print("geht los")
        self.frq_meter["amountused"] = self.root.sonicamp.status.frequency / 1000
        self.gain_meter["amountused"] = self.root.sonicamp.status.gain
        self.temp_meter["amountused"] = 36 #!Here
        
        self.con_status_label["image"] = self.root.led_green_img
        self.con_status_label["text"] = "connected"
        
        if self.root.sonicamp.status.frequency:
            self.sig_status_label["text"] = "Signal ON"
            self.sig_status_label["image"] = self.root.led_green_img
        else:
            self.sig_status_label["text"] = "Signal OFF"
            self.sig_status_label["image"] = self.root.led_red_img
        print("geschafft")
    



class StatusFrameWipe(ttk.Frame):
    
    def __init__(self, parent: ttk.Frame, root: Root, *args, **kwargs) -> None:
        """
        Statusframe object, that is used in case the GUI is
        connected to a SonicWipe
        """
        super().__init__(parent, *args, **kwargs)
        
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
        


class SerialMonitor(ttk.Frame):
    
    @property
    def root(self) -> Root:
        return self._root
    
    def __init__(self, root: Root, *args, **kwargs) -> None:
        super().__init__(root, *args, **kwargs)
        self._root: Root = root
        


class SonicMeasure(ttk.Frame):
    
    def __init__(self, root: Root, *args, **kwargs) -> None:
        pass



class SonicAgent(SonicThread):
    """
    The SonicAgent sends the Command.GET_STATUS command to get the status data
    from a SonicAmp. It puts that data into the inhereted queue.
    Furthermore it has access to the serial connection through it's parameters
    """
    @property
    def root(self):
        """ The serial communication object """
        return self._root
    
    def __init__(self, root: Root) -> None:
        super().__init__()
        self._root: Root = root
        
    
    def run(self) -> None:
        while True:
            # in case the thread is paused
            with self.pause_cond:
                while self.paused:
                    self.pause_cond.wait()
                
                # thread should not try to do something if paused
                # in case not paused
                if self.root.serial.is_connected:
                    data_str = self.root.serial.send_and_get(Command.GET_STATUS)
                    if len(data_str) > 1:
                        status: Status = Status.construct_from_str(data_str)
                        if status != self.root.sonicamp.status:
                            self.root.sonicamp.status = status
                            self.root.update_idletasks()
                            self.root.attach_data()
                                
                else:
                    self.pause_cond.wait()