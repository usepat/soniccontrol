import time
import tkinter as tk
import tkinter.ttk as ttk
from matplotlib.figure import Figure
from  matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import ttkbootstrap as ttkb
from tkinter import font
from tkinter import filedialog
from ttkbootstrap import Style
from PIL.ImageTk import PhotoImage
import serial

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
        self.gain: tk.IntVar = tk.IntVar()
        self.frq_range: tk.StringVar = tk.StringVar()
        self.protocol: tk.StringVar = tk.StringVar()
        
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
        self.serial_monitor: SerialMonitor = SerialMonitor(self)
        
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
            # self.engine()
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
    
    def engine(self) -> None:
        # if not self.serial.serial.is_open:
        #     self.notebook.connectiontab.disconnect()
        
        while self.thread.queue.qsize():
            self.sonicamp.status = self.thread.queue.get(0)
            self.update_idletasks()
            self.attach_data()
        self.after(100, self.engine)
    
    def decide_action(self) -> None:
        self.serial.send_and_get(Command.SET_SERIAL, line=False)
        init_status: Status = Status.construct_from_str(self.serial.send_and_get(Command.GET_STATUS))
        self.frq.set(init_status.frequency)
        self.gain.set(init_status.gain)
        
        type_: str = self.serial.send_and_get(Command.GET_TYPE)
        if type_ == "soniccatch":
            logger.info("Found soniccatch")
            self.serial.send_and_get(Command.SET_MHZ)
            self.frq_range.set('mhz')
            self.sonicamp = SonicCatch(self.serial)
            self.publish_for_catch()
        elif type_ == "sonicwipe":
            logger.info("Found sonicwipe")
            self.sonicamp = SonicWipe(self.serial)
            self.publish_for_wipe()
        
        self.engine()
        
        if self.thread.paused:
            self.thread.resume()
    
    def publish_disconnected(self) -> None:
        """ Publishes children in case there is no connection """
        logger.info("publishing for disconnected")
        self.notebook.publish_disconnected()
        self.status_frame_catch.abolish_data()
        self.mainframe.pack(anchor=tk.W, side=tk.LEFT)
        
        if self.winfo_width() == Root.MAX_WIDTH:
            self.adjust_dimensions()
    
    def publish_for_catch(self) -> None:
        """ Publishes children in case there is a connection to a soniccatch """
        logger.info("publishing for catch")
        self.attach_data()
        self.notebook.publish_for_catch()
        self.status_frame_catch.publish()
        # self.mainframe.grid(row=0, column=0, sticky=tk.NSEW)
        self.mainframe.pack(anchor=tk.W, side=tk.LEFT)
    
    def publish_for_wipe(self) -> None:
        """ Publishes children in case there is a connection to a sonicwipe """
        logger.info("publishing for wipe")
        self.notebook.publish_for_wipe()
        self.status_frame_wipe.publish()
        self.mainframe.pack(anchor=tk.W, side=tk.LEFT)
    
    def publish_sonicmeasure(self) -> None:
        """ Publishes the sonicmeasure frame """
        self.sonic_measure: SonicMeasure = SonicMeasure(self)
    
    def publish_serial_monitor(self) -> None:
        """ Publishes the serial monitor """
        if self.adjust_dimensions():
            self.serial_monitor.pack(anchor=tk.E, side=tk.RIGHT, padx=5, pady=5, expand=True, fill=tk.BOTH)
    
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
        self.enable_children()
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
        self.disable_children(self.connectiontab)
        self.pack(padx=5, pady=5)
        
    def publish_children(self) -> None:
        """ Publishes children """
        for child in self.children.values():
            child.publish()
                
    def disable_children(self, focused_child: ttk.Frame) -> None:
        """ Disables childen and selects connection tab (case: not connected)"""
        for child in self.children.values():
            if child != focused_child:
                self.tab(child, state=tk.DISABLED)
        self.select(focused_child)
    
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
    



class StatusFrameWipe(ttk.Frame):
    
    @property
    def root(self) -> Root:
        return self._root
    
    @property
    def serial(self) -> SerialConnection:
        return self._serial
    
    # @property
    # def sonicamp(self) -> SonicAmp:
    #     return self._sonicamp
    
    def __init__(self, parent: ttk.Frame, root: Root, *args, **kwargs) -> None:
        """
        Statusframe object, that is used in case the GUI is
        connected to a SonicWipe
        """
        super().__init__(parent, *args, **kwargs)
        self._root = root
        self._serial = root.serial
        # self._sonicamp = root.sonicamp
        
        # Is being splittet into two main frames
        self.meter_frame: ttk.Frame = ttk.Frame(self)
        self.overview_frame: ttk.Frame = ttk.Frame(self, style="secondary.TFrame")
        
        # meter frame
        self.frq_meter: ttkb.Meter = ttkb.Meter(
            self.meter_frame,
            bootstyle='dark',
            amounttotal=1200000 / 1000, 
            amountused=0,
            textright='kHz',
            subtext='Current Frequency',
            metersize=150)
        
        self.seperator: ttk.Separator = ttk.Separator(
            self.meter_frame,
            orient=tk.HORIZONTAL,
            style="info.TSeperator",)
        
        self.protocol_status: ttk.Label = ttk.Label(
            self.meter_frame,
            textvariable=self.root.protocol,
            text="Dummy Text",
            style="info.TLabel",
        )
        
        # Overview Frame
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
        pass
    
    def abolish_data(self) -> None:
        """ Function to repeal setted values """
        pass
    
    def attach_data(self) -> None:
        """ Function to configure objects to corresponding data """
        pass       
        


class SerialMonitor(ttkb.Frame):
    
    HELPTEXT: str = '''
Welcome to the Help Page for SonicAmp Systems!
There are a variety  of commands to control your SonicAmp
under you liking.  Typically, a  command that sets up the 
SonicAmp System starts with an <!>, whereas commands that
start  with a  <?> ask  the  System  about  something and 
outputs this data.

Here is a list for all commands:

   COMMAND:          DESCRIPTION:
   !SERIAL           Set your SonicAmp to the serial mode
   !f=<Frequency>    Sets the frequency you want to operate on
   !g=<Gain>         Sets the Gain to your liking
   !cur1=<mAmpere>   Sets the current of the 1st Interface
   !cur2=<mAmpere>   Sets the current of the 2nd Interface
   !KHZ              Sets the Frequency range to KHz
   !MHZ              Sets the Frequency range to MHz
   !ON               Starts the output of the signal
   !OFF              Ends the Output of the Signal, Auto 
                     and Wipe
   !WIPE             [WIPE ONLY] Starts the wiping process 
                     with indefinite cycles
   !WIPE=<Cycles>    [WIPE ONLY] Starts the wiping process 
                     with definite cycles
   !prot=<Protocol>  Sets the protocol of your liking
   !rang=<Frequency> Sets the frequency range for protocols
   !step=<Range>     Sets the step range for protocols
   !sing=<Seconds>   Sets the time, the Signal should be 
                     turned
                     on during protocols
   !paus=<Seconds>   Sets the time, the Signal shoudl be 
                     turned off during protocols
   !AUTO             Starts the Auto mode
   !atf1=<Frequency> Sets the Frequency for the 1st protocol
   !atf2=<Frequency> Sets the Frequency for the 2nd protocol
   !atf3=<Frequency> Sets the Frequency for the 3rd protocol
   !tust=<Hertz>     Sets the tuning steps in Hz
   !tutm=<mseconds>  Sets the tuning pause in milliseconds
   !scst=<Hertz>     Sets the scaning steps in Hz    
   
   ?                 Prints information on the progress State
   ?info             Prints information on the software
   ?type             Prints the type of the SonicAmp System
   ?freq             Prints the current frequency
   ?gain             Prints the current gain
   ?temp             Prints the current temperature of the 
                     PT100 element
   ?tpcb             Prints the current temperature in the 
                     case
   ?cur1             Prints the Current of the 1st Interface                     
   ?cur2             Prints the Current of the 2nd Interface
   ?sens             Prints the values of the measurement chip
   ?prot             Lists the current protocol
   ?list             Lists all available protocols
   ?atf1             Prints the frequency of the 1st protocol                     
   ?atf2             Prints the frequency of the 2nd protocol                     
   ?atf3             Prints the frequency of the 3rd protocol
   ?pval             Prints values used for the protocol\n\n'''
    
    @property
    def root(self) -> Root:
        return self._root
    
    def __init__(self, root: Root, *args, **kwargs) -> None:
        super().__init__(root, *args, **kwargs)
        self._root: Root = root
        
        self.command_history: list[str] = []
        self.index_history: int = -1
        
        self.output_frame: ttk.Frame = ttk.LabelFrame(self, text='OUTPUT')
        
        container: ttk.Frame = ttk.Frame(self.output_frame)
        self.canvas: tk.Canvas = tk.Canvas(container)
        scrollbar: ttk.Scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollable_frame: ttk.Frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda x: self.canvas.configure(scrollregion=self.canvas.bbox(tk.ALL)))
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor=tk.NW)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        container.pack(anchor=tk.N, expand=True, fill=tk.BOTH, padx=5, pady=5, side=tk.TOP)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.input_frame: ttk.Frame = ttk.LabelFrame(self, text='INPUT')
        
        self.command_field: ttk.Entry = ttk.Entry(self.input_frame, style='dark.TEntry')
        self.command_field.bind('<Return>', self.send_command)
        self.command_field.bind('<Up>', self.history_up)
        self.command_field.bind('<Down>', self.history_down)
        
        self.send_button: ttk.Button = ttk.Button(self.input_frame, text='Send', command=self.send_command, style='success.TButton')
        self.send_button.bind('<Button-1>', self.send_command)
        
        self.command_field.pack(anchor=tk.S, padx=10, pady=10, fill=tk.X, expand=True, side=tk.LEFT)
        self.send_button.pack(anchor=tk.S, padx=10, pady=10, side=tk.RIGHT)
        
        self.input_frame.pack(anchor=tk.S, fill=tk.X, side=tk.BOTTOM)
        self.output_frame.pack(anchor=tk.N, expand=True, fill=tk.BOTH, pady=10, side=tk.TOP)
        
        # self.text_frame.pack_propagate(False)

        self.insert_text('Type <help> to output the command-cheatsheet!')
        self.insert_text('Type <clear> to clear the screen!')
        self.insert_text(SerialMonitor.HELPTEXT)
        
        self.output_frame.pack_propagate(False)
    
    def send_command(self, event) -> None:
        command: str = self.command_field.get()
        self.command_history.insert(0, command)
        self.insert_text(f">>> {command}")
        
        if command == 'clear':
            for child in self.scrollable_frame.children.values():
                child.destroy()
        elif command == 'help':
            self.insert_text(SerialMonitor.HELPTEXT)
        elif command == 'exit':
            self.destroy()
        else:
            self.root.thread.pause()
            self.root.serial.serial.write(f"{command}\n".encode())
            time.sleep(0.3)
            answer: str = self.root.serial.serial.read(255)
            self.insert_text(answer)
            self.root.thread.resume()
        
        self.canvas.yview_moveto(1)
        self.command_field.delete(0, tk.END)
    
    def insert_text(self, text: str) -> None:
        ttk.Label(self.scrollable_frame, text=text, font=("Consolas", 10)).pack(fill=tk.X, side=tk.TOP, anchor=tk.W)
        self.canvas.update()
    
    def history_up(self, event) -> None:
        if self.index_history != len(self.command_history) - 1:
            self.index_history += 1
            self.command_field.delete(0, tk.END)
            self.command_field.insert(0, self.command_history[self.index_history])
            
    def history_down(self, event) -> None:
        if self.index_history !=  -1:
            self.index_history -= 1
            self.command_field.delete(0, tk.END)
            self.command_field.insert(0, self.command_history[self.index_history])
        else:
            self.command_field.delete(0, tk.END)
            
            


class SonicMeasure(tk.Toplevel):
    
    @property
    def root(self) -> Root:
        return self._root
    
    @property
    def serial(self) -> SerialConnection:
        return self._serial
    
    def __init__(self, root: Root, *args, **kwargs) -> None:
        super().__init__(root, *args, **kwargs)
        self._root: Root = root
        self._serial: SerialConnection = root.serial
        self._filetypes: list[tuple] = [('Text', '*.txt'),('All files', '*'),]
        
        self.title('SonicMeasure')
        
        self.start_frq: tk.IntVar = tk.IntVar(value=1900000)
        self.stop_frq: tk.IntVar = tk.IntVar(value=2100000)
        self.resolution: tk.IntVar = tk.IntVar(value=100)
        self.gain: tk.IntVar = tk.IntVar(value=10)
        
        self.mainframe: ttk.Frame = ttk.Frame(self)
        self.fig_frame: ttk.Frame = ttk.Frame(self.mainframe, height=450, width=700)
        self.fig_frame.pack(anchor=tk.N, expand=True, fill=tk.X, padx=3, pady=3, side=tk.TOP)
        
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.fig.subplots_adjust(right=0.8)
        
        self.twin1 = self.ax.twinx()
        self.twin2 = self.ax.twinx()
        
        self.twin2.spines['right'].set_position(("axes", 1.15))
        
        self.p1, = self.ax.plot([], [], "bo-", label="U$_{RMS}$ / mV")
        self.p2, = self.twin1.plot([], [], "ro-", label="I$_{RMS}$ / mA")
        self.p3, = self.twin2.plot([], [], "go-", label="Phase / °")
        
        self.ax.set_xlim(int(self.start_frq.get()), int(self.stop_frq.get()))
        
        self.ax.set_xlabel("Frequency / Hz")
        self.ax.set_ylabel("U$_{RMS}$ / mV")
        self.twin1.set_ylabel("I$_{RMS}$ / mA")
        self.twin2.set_ylabel("Phase / °")
        
        self.ax.yaxis.label.set_color(self.p1.get_color())
        self.twin1.yaxis.label.set_color(self.p2.get_color())
        self.twin2.yaxis.label.set_color(self.p3.get_color())
        
        tkw = dict(size=4, width=1.5)
        self.ax.tick_params(axis='y', colors=self.p1.get_color(), **tkw)
        self.twin1.tick_params(axis='y', colors=self.p2.get_color(), **tkw)
        self.twin2.tick_params(axis='y', colors=self.p3.get_color(), **tkw)
        self.ax.tick_params(axis='x', **tkw)
        
        self.ax.legend(handles=[self.p1, self.p2, self.p3])


        self.canvas = FigureCanvasTkAgg(self.fig, self.fig_frame)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.fig_frame)

        self.canvas._tkcanvas.pack(fill=tk.BOTH, expand=1)
        
        self.button_frame = ttk.Frame(self.mainframe)
        
        self.start_frq_label = ttk.Label(self.button_frame, text='Start Freq. [Hz]')
        self.start_frq_label.pack(side=tk.LEFT)
        
        self.start_frq_entry = ttk.Entry(self.button_frame, 
                                         width=8, 
                                         textvariable=self.start_frq)
        self.start_frq_entry.pack(padx=10, side=tk.LEFT)
        
        self.stop_frq_label = ttk.Label(self.button_frame, text='Stop Freq. [Hz]')
        self.stop_frq_label.pack(ipadx=2, side=tk.LEFT)
        
        self.stop_frq_entry = ttk.Entry(self.button_frame, width=8, textvariable=self.stop_frq)
        self.stop_frq_entry.pack(padx=10, side=tk.LEFT)
        
        self.res_label = ttk.Label(self.button_frame, text='Res. [Hz]')
        self.res_label.pack(ipadx=2, side=tk.LEFT)
        
        self.res_entry = ttk.Entry(self.button_frame, width=5, textvariable=self.resolution)
        self.res_entry.pack(padx=10, side=tk.LEFT)
        
        self.gain_label = ttk.Label(self.button_frame, text='Gain [%]')
        self.gain_label.pack(ipadx=2, side=tk.LEFT)
        
        self.gain_entry = ttk.Entry(self.button_frame, width=3, textvariable = self.gain)
        self.gain_entry.pack(padx=10, side=tk.LEFT)
        
        self.logging = ttk.Button(self.button_frame, text='Save', command=self.save_spectrum)
        self.logging.pack(side=tk.RIGHT)
        
        self.stop_measure_btn = ttk.Button(self.button_frame, text='Stop', command=self.stop_measure)
        self.stop_measure_btn.pack(side=tk.BOTTOM)
        
        self.start_measure_btn = ttk.Button(self.button_frame, text='Start', command=self.start_measure)
        self.start_measure_btn.pack(side=tk.BOTTOM)
        # self.button_frame.config(height='200', width='600')
        self.button_frame.pack(expand=True, fill=tk.X, padx=3, pady=3, side=tk.TOP)
        # self.mainframe.config(height='500', width='600')
        self.mainframe.pack(side=tk.TOP)
    
    def start_measure(self) -> None:
        self.root.thread.pause()
        self.run: bool = True
        
        start: int = self.start_frq.get()
        stop: int = self.stop_frq.get()
        step: int = self.resolution.get()
        
        self.frequencies: list[int] = []
        self.u_rms: list[int] = []
        self.i_rms: list[int] = []
        self.phase: list[int] = []
        
        self.ax.set_xlim(int(start), int(stop))
        self.serial.send_and_get(Command.SET_GAIN + self.gain.get())
        self.serial.send_and_get(Command.SET_SIGNAL_ON)
        self.serial.send_and_get(Command.SET_FLOW + f"{start};{stop};{step}")
        
        while self.run and self.serial.is_connected:
            data_str: str = self.serial.get_answer()
            if data_str == '':
                continue
            else:
                data: list[int] = [int(val) for val in data_str.split(' ')]
            print(data)
            self.frequencies.append(data[0])
            self.u_rms.append(data[1])
            self.i_rms.append(data[2])
            self.phase.append(data[3])
            
            self.p1.set_data(self.frequencies, self.u_rms)
            self.p2.set_data(self.frequencies, self.i_rms)
            self.p3.set_data(self.frequencies, self.phase)
            self.fig.canvas.draw()
            self.ax.set_ylim(
                min(self.u_rms) - min(self.u_rms) * 0.4,
                max(self.u_rms) + max(self.u_rms) * 0.2,)
            self.twin1.set_ylim(
                min(self.i_rms) - min(self.i_rms) * 0.4,
                max(self.i_rms) + max(self.i_rms) * 0.2,)
            self.twin2.set_ylim(
                min(self.phase) - min(self.phase) * 0.4,
                max(self.phase) + max(self.phase) * 0.2,)
            self.fig.canvas.flush_events()
            self.root.update()
            time.sleep(0.1)     
        
        self.serial.send_and_get(Command.SET_SIGNAL_OFF)
        self.root.thread.resume()
        
    def stop_measure(self) -> None:
        self.run: bool = False   
    
    def save_spectrum(self):
        self.filename = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=self._filetypes)
        f = open(self.filename, 'w')
        f.write("I-V-Phase Spectrum @ Gain: "+ self.gain.get() +" %\n")
        f.write("Measurement time: "+self.measurementtime.isoformat()+"\n")
        f.write("Frequency [Hz]"+"\t"+"Urms [V]"+"\t"+"Irms [mA]"+"\t"+"Phase [°]"+"\n")
        for i in range(0, len(self.frequencies)):
            f.write("{0}\t{1}\t{2}\t{3}\n".format(self.frequencies[i],self.u_rms[i], self.i_rms[i], self.phase[i]))
        f.close()



# class SonicMeasure(tk.Toplevel):
    
#     @property
#     def root(self) -> Root:
#         return self._root
    
#     @property
#     def serial(self) -> SerialConnection:
#         return self._serial
    
#     def __init__(self, root: Root, *args, **kwargs) -> None:
#         super().__init__(root, *args, **kwargs)
#         self._root: Root = root
#         self._serial: SerialConnection = root.serial
#         self._filetypes: list[tuple] = [('Text', '*.txt'),('All files', '*'),]
        
#         self.title('SonicMeasure')
        
#         self.start_frq: tk.IntVar = tk.IntVar(value=1900000)
#         self.stop_frq: tk.IntVar = tk.IntVar(value=2100000)
#         self.resolution: tk.IntVar = tk.IntVar(value=100)
#         self.gain: tk.IntVar = tk.IntVar(value=10)



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
                    try:
                        data_str = self.root.serial.send_and_get(Command.GET_STATUS)
                        if len(data_str) > 1:
                            status: Status = Status.construct_from_str(data_str)
                            if status != self.root.sonicamp.status:
                                self.queue.put(status)
                    except ValueError:
                        logger.info(f"ValueError: Received {data_str}")
                    except serial.SerialException:
                        self.root.notebook.connectiontab.disconnect()
                else:
                    self.pause_cond.wait()