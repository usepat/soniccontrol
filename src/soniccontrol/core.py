from __future__ import annotations
import time

import traceback
import tkinter as tk
import tkinter.ttk as ttk
import ttkbootstrap as ttkb
import csv
import datetime
import os
import serial

from PIL.ImageTk import PhotoImage
from tkinter import font
from tkinter import messagebox

from sonicpackage import (
    SonicAmp,
    SonicThread,
    Status,
    SonicAmpBuilder,
    SonicWipeDuty,
    SonicCatch,
    SonicCatchOld,
    SonicWipe,
    SonicWipeOld,
    SonicCatchAncient,
    SonicWipeAncient,
    Command,
    Transducer
)
from soniccontrol.sonicamp import SerialConnectionGUI, SerialConnection
from soniccontrol.statusframe import (
    StatusFrameCatch,
    StatusFrameDutyWipe,
    StatusFrameWipe,
    StatusFrame,
)
from soniccontrol.serialmonitor import(
    SerialMonitor, 
    SerialMonitor40KHZ, 
    SerialMonitorCatch, 
    SerialMonitorWipe
)
from soniccontrol._notebook import ScNotebook
from soniccontrol.helpers import logger, read_json

import soniccontrol.constants as const


class Root(tk.Tk):
    """
    The Root class is the main class of the Tkinter GUI.
    Through this class every other compository object can get
    information about another object. When initializing, it
    creates the attribute self.thread that represents the
    main SonicThread that asks the sonicamp about its status.

    This thread then is passed into the customized SerialConnection
    class for the GUI. So that the method SerialConnection.send_and_get()
    pauses and resumes the thread automatically, so that none
    information interwienes with one another

    The data that the thread gets is then being passed into the
    queue object of the thread and processed in the engine method

    Antother useful method is the self.attach_data method, that
    passes the newly arrived data to all tkinter compository
    objects, so that the GUI adapts itself as a whole to the
    new status.

    Inheritance:
        tk (tk.Tk): The main root class of tkinter, that the Root
        class inherets from
    """

    # GUI specific constants
    MIN_WIDTH: int = 555
    MIN_HEIGHT: int = 900
    MAX_WIDTH: int = 1110
    TITLE: str = "Soniccontrol"
    THEME: str = "sandstone"

    def __init__(self, *args, **kwargs) -> None:
        """
        Here the Root class is being constructed and
        every needed child is being initialized, for instance
        the self.thread object that the Root class is inherently
        depended on. Further information above or in the Thread
        itself.
        
        Furthermore, the serial instance is being initialized
        this object is used to exchange data with an sonicamp
        """
        super().__init__(*args, **kwargs)

        self.serial: SerialConnection
        self.sonicamp: SonicAmp
        self.thread: SonicThread

        # Tkinter children of Root
        self.mainframe: ttk.Frame
        self.notebook: ScNotebook
        self.status_frame: StatusFrame
        self.serial_monitor: SerialMonitor

        self.port: tk.StringVar = tk.StringVar(value=None)
        self.frq: tk.IntVar = tk.IntVar(value=0)
        self.gain: tk.IntVar = tk.IntVar(value=0)
        self.frq_range: tk.StringVar = tk.StringVar(value="khz")
        self.wipe_mode: tk.IntVar = tk.IntVar(value=0)
        self.protocol: tk.StringVar = tk.StringVar(value=0)

        # Status Log configuration
        self.fieldnames: list = ["timestamp", "signal", "frequency", "gain"]
        self.status_log_dir: str = "logs"
        self.statuslog_filepath: str

        if not os.path.exists(self.status_log_dir):
            os.mkdir(self.status_log_dir)
            
        self.config_file_algorithm()

        # setting up root window, configurations
        self.geometry(f"{Root.MIN_WIDTH}x{Root.MIN_HEIGHT}")
        self.minsize(Root.MIN_WIDTH, Root.MIN_HEIGHT)
        self.maxsize(Root.MAX_WIDTH, Root.MIN_HEIGHT)
        self.wm_title(Root.TITLE)
        ttkb.Style(theme=Root.THEME)

        if os.sys.platform == 'Windows':
            self.iconbitmap("src//soniccontrol//pictures//welle.ico")

        # default font in GUI and custom Fonts
        default_font: font.Font = font.nametofont("TkDefaultFont")
        default_font.configure(family="Arial", size=12)
        self.option_add("*Font", default_font)

        self.arial12: font.Font = font.Font(
            family="Arial", size=12, weight=tk.font.BOLD
        )

        self.qtype12: font.Font = font.Font(
            family="QTypeOT-CondMedium", size=12, weight=tk.font.BOLD
        )

        self.qtype30: font.Font = font.Font(
            family="QTypeOT-CondLight",
            size=30,
        )

        self.qtype30b: font.Font = font.Font(
            family="QTypeOT-CondBook", size=30, weight=tk.font.BOLD
        )

        # Defining images
        self.REFRESH_IMG: PhotoImage = PhotoImage(const.REFRESH_RAW_IMG)
        self.HOME_IMG: PhotoImage = PhotoImage(const.HOME_RAW_IMG)
        self.SCRIPT_IMG: PhotoImage = PhotoImage(const.SCRIPT_RAW_IMG)
        self.CONNECTION_IMG: PhotoImage = PhotoImage(const.CONNECTION_RAW_IMG)
        self.INFO_IMG: PhotoImage = PhotoImage(const.INFO_RAW_IMG)
        self.PLAY_IMG: PhotoImage = PhotoImage(const.PLAY_RAW_IMG)
        self.PAUSE_IMG: PhotoImage = PhotoImage(const.PAUSE_RAW_IMG)
        self.WAVE_IMG: PhotoImage = PhotoImage(const.WAVE_RAW_IMG)
        self.GRAPH_IMG: PhotoImage = PhotoImage(const.GRAPH_RAW_IMG)
        self.LED_GREEN_IMG: PhotoImage = PhotoImage(const.LED_GREEN_RAW_IMG)
        self.LED_RED_IMG: PhotoImage = PhotoImage(const.LED_RED_RAW_IMG)

        # Building the thread and serialconnection
        # First: initializing the thread
        self.thread: SonicThread = SonicAgent(self)
        self.thread.setDaemon(True)

        # Second: initializing the serial interface, with the information about the thread
        self.serial: SerialConnectionGUI = SerialConnectionGUI(self.thread)

        self.thread.start()
        self.thread.pause()

        # Starting the main parts of the GUI
        self.mainframe: ttk.Frame = ttk.Frame(self)
        self.notebook: ScNotebook = ScNotebook(self.mainframe, self)
        self.status_frame: ttk.Frame = ttk.Frame(self.mainframe)
        self.serial_monitor: ttk.Frame = ttk.Frame(self.mainframe)

        self.__reinit__()

    def __reinit__(self) -> None:
        """
        Method to reinitialize the main composites of Root. Based
        on the fact, if a connection was successfully established
        python decides what exactly to do further in the
        self.decide_action() method.
        
        If no connection was established, or there was an error
        during the connection, the self.publish_disconnected()
        method is being called, which brings the GUI to the
        appearance of a to-be-connected state
        """
        self.serial.get_ports()

        try:

            if self.serial.connect_to_port(self.port.get()):
                logger.info(f"Getting connected to {self.port.get()}")
                self.decide_action()

            else:
                logger.info(f"No connection publishing for not connected")
                self.publish_disconnected()

        except Exception as e:
            traceback.print_tb(e)
            logger.warning(f"{e}")
            messagebox.showerror("Error", "Connection error")
            self.publish_disconnected()

    def decide_action(self) -> None:
        """
        This method is being called when a succesfull connection
        was being made. Through this method, a sonicamp object
        is being created, narrowing the information and methods
        to use with the device.

        Then this information is being setted to the tkinter variables
        and further more the whole GUI is being published accordingly
        """
        try:
            self.sonicamp: SonicAmp = SonicAmpBuilder.build_amp(self.serial)
        except Exception as e:
            logger.warning(f"{e}")

        logger.info(f"Built sonicamp {self.sonicamp}")

        if isinstance(self.sonicamp, SonicCatchOld) or isinstance(
            self.sonicamp, SonicCatchAncient
        ):
            self.publish_for_old_catch()

        elif isinstance(self.sonicamp, SonicWipeAncient) or isinstance(
            self.sonicamp, SonicWipeOld
        ):
            self.publish_for_old_wipe()

        elif isinstance(self.sonicamp, SonicWipeDuty):
            self.publish_for_duty_wipe()

        elif isinstance(self.sonicamp, SonicCatch):
            self.publish_for_catch()

        elif isinstance(self.sonicamp, SonicWipe):
            self.publish_for_wipe()

        else:
            messagebox.showerror("Error", "Either your device is not set for external control or your device was not implemented. Please check if your device is in 'External Control Mode' or 'Serial Mode'")
            print(self.sonicamp)
            self.serial.disconnect()

        self.initialize_amp_data()

        # Due to the Fact, that the 40kHz SonicWipe does not need a data exchange
        # in form of a thread. The sonicamp instance is checked
        if not isinstance(self.sonicamp, SonicWipeDuty):
            self.engine()

            if self.thread.paused:
                self.thread.resume()

    def initialize_amp_data(self) -> None:
        """
        Makes sure that data from the config file is being read and
        updated. So that one can just reset the connection to update
        the data
        
        Method to get the data from the sonicamp to the Root tkinter
        variables, so the all objects can adapt to it
        
        Furthermore the method creates the needed statuslog for this
        instance of usage
        
        Every new connection creates a needed logfile
        """
        self.config_file_algorithm()
        
        self.frq.set(self.sonicamp.status.frequency)
        self.gain.set(self.sonicamp.status.gain)
        self.wipe_mode.set(self.sonicamp.status.wipe_mode)
        self.protocol.set(self.serial.send_and_get(Command.GET_PROTOCOL))
        
        if len(self.transducer) == 1:
            self.set_atf(list(self.transducer.keys())[0])

        tmp_timestamp: str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.statuslog_filepath: str = f"{self.status_log_dir}//statuslog_{self.sonicamp.type_}_{tmp_timestamp}.csv"
        self._create_statuslog()

    def engine(self) -> None:
        """
        The engine method is automatically being
        called every 100ms to look for new data, that
        the thread received. If the new data arrived,
        the whole GUI adapts to it through this said
        method
        
        Furthermore, the register_status_data() method
        is being called to register the current frequency
        and gain to a logfile
        """
        while self.thread.queue.qsize():

            status: Status = self.thread.queue.get(0)
            logger.info(f"Got status {status}")

            self.sonicamp.status = status
            self.register_status_data(data=status)

            self.update_idletasks()
            self.attach_data()

        self.after(100, self.engine)

    def attach_data(self) -> None:
        """
        The attach data method passes the newly
        arrived information about the sonicamp to all
        children of root.
        """
        logger.info(f"attaching data for {self.sonicamp}")
        self.notebook.attach_data()
        self.status_frame.attach_data()

    def publish_disconnected(self) -> None:
        """
        This method publishes the GUI for the case that
        there is no connection with a sonicamp.
        
        Due to the fact, that this method can also be called
        when a connection was lost, the method checks if a 
        sonicmeasure and serialmonitor window exists. If that's
        the case, the windows are closed
        """
        logger.info(f"publshing for disconnected soniccontrol")
        self.notebook.publish_disconnected()
        self.status_frame.destroy()
        self.mainframe.pack(anchor=tk.W, side=tk.LEFT)

        # Check if Serial Monitor is open
        if self.winfo_width() == Root.MAX_WIDTH:
            self.adjust_dimensions()

        try:
        
        # Check if a sonicmeasure window exists
            if tk.Toplevel.winfo_exists(self.notebook.hometab.sonicmeasure):
                self.notebook.hometab.sonicmeasure.destroy()

                if self.thread.paused:
                    self.thread.resume()

        # Undefind behaivour, nooby code
        except AttributeError as e:
            logger.warning(f"{e}")

    def publish_for_old_catch(self) -> None:
        """
        This method published the GUI for the case that there
        is a connection with a SonicCatch. 
        
        Specifically for all SonicCatches that were developed
        pre Revision 2.1 (firmware 1.0)
        """
        self.serial_monitor.destroy()
        self.serial_monitor: SerialMonitor = SerialMonitorCatch(self)
        
        self.status_frame.destroy()
        self.status_frame: StatusFrame = StatusFrameCatch(self.mainframe, self)

        self.attach_data()
        self.notebook.publish_for_old_catch()
        self.status_frame.publish()
        self.mainframe.pack(anchor=tk.W, side=tk.LEFT)

    def publish_for_old_wipe(self) -> None:
        """
        This method published the GUI for the case that there
        is a connection with a SonicWipe
        
        Specifically for all SonicWipes that were developed
        pre Revision 2.1 (firmware 1.0)
        """
        self.serial_monitor.destroy()
        self.serial_monitor: SerialMonitor = SerialMonitorWipe(self)
        
        self.status_frame.destroy()
        self.status_frame: StatusFrame = StatusFrameWipe(self.mainframe, self)

        self.attach_data()
        self.notebook.publish_for_old_wipe()
        self.status_frame.publish()
        self.mainframe.pack(anchor=tk.W, side=tk.LEFT)

    def publish_for_duty_wipe(self) -> None:
        """
        This method published the GUI for the case that there
        is a connection with a SonicWipe 40kHz DutyCycle Amp
        
        Due to the fact, that the sonicwipe dutycycle amp does not
        rely on the SonicAgent thread, there is a if case to pause it
        """
        if not self.thread.paused:
            self.thread.pause()
            
        self.serial_monitor.destroy()
        self.serial_monitor: SerialMonitor = SerialMonitor40KHZ(self)

        self.status_frame.destroy()
        self.status_frame: StatusFrame = StatusFrameDutyWipe(self.mainframe, self)

        self.notebook.publish_for_dutywipe()
        self.status_frame.publish()
        self.status_frame.connection_on()
        self.mainframe.pack(anchor=tk.W, side=tk.LEFT)

    def publish_for_catch(self) -> None:
        """
        Method that publishes everything for the SonicCatch
        Revision 2.1 (firmware 1.0)
        """
        self.serial_monitor.destroy()
        self.serial_monitor: SerialMonitor = SerialMonitorCatch(self)
        
        self.status_frame.destroy()
        self.status_frame: StatusFrame = StatusFrameCatch(self.mainframe, self)

        self.attach_data()
        self.notebook.publish_for_catch()
        self.status_frame.publish()
        self.mainframe.pack(anchor=tk.W, side=tk.LEFT)

    def publish_for_wipe(self) -> None:
        """
        Method that publishes everything for the SonicWipe
        Revision 2.1 (firmware 1.0)
        """
        self.serial_monitor.destroy()
        self.serial_monitor: SerialMonitor = SerialMonitorWipe(self)
        
        self.status_frame.destroy()
        self.status_frame: StatusFrame = StatusFrameCatch(self.mainframe, self)

        self.attach_data()
        self.notebook.publish_for_wipe()
        self.status_frame.publish()
        self.mainframe.pack(anchor=tk.W, side=tk.LEFT)

    def publish_serial_monitor(self) -> None:
        """
        Method to publish the the serial monitor of the tkinter GUI
        """
        if self.adjust_dimensions():
            self.serial_monitor.pack(
                anchor=tk.E, side=tk.RIGHT, padx=5, pady=5, expand=True, fill=tk.BOTH
            )

    def adjust_dimensions(self) -> bool:
        """A method to adjust the dimensions of the GUI
        so that a serialmonitor can be viewed or not.

        Returns:
            bool: Returns True if the GUI is in a stated, where the
            maximum width is being held
        """
        if self.winfo_width() == Root.MIN_WIDTH:

            self.geometry(f"{Root.MAX_WIDTH}x{Root.MIN_HEIGHT}")
            return True

        else:

            self.geometry(f"{Root.MIN_WIDTH}x{Root.MIN_HEIGHT}")
            return False

    def _create_statuslog(self) -> None:
        """
        Internal method to create the csv status log file
        """
        if not isinstance(self.sonicamp, SonicWipeDuty):
            with open(self.statuslog_filepath, "a", newline="") as statuslog:

                csv_writer: csv.DictWriter = csv.DictWriter(
                    statuslog, fieldnames=self.fieldnames
                )
                csv_writer.writeheader()

    def register_status_data(self, data: Status) -> None:
        """
        Method to register the current state of a sonicamp in a
        csv log file. Takes in the Status object, that is normally
        passed from the engine method

        Args:
            data (Status): the Status object containing the data
        """
        if not isinstance(self.sonicamp, SonicWipeDuty):
            data_dict: dict = {
                "timestamp": datetime.datetime.now(),
                "signal": data.signal,
                "frequency": data.frequency,
                "gain": data.gain,
            }

            with open(self.statuslog_filepath, "a", newline="") as statuslog:
                csv_writer: csv.DictWriter = csv.DictWriter(
                    statuslog, fieldnames=self.fieldnames
                )
                csv_writer.writerow(data_dict)
                
    def config_file_algorithm(self) -> None:
        
        self.config_data: dict = read_json()
        
        if self.config_data:
            self.transducer: dict = self.config_data["transducer"]
        else:
            self.transducer: dict = {}
            
                
    def set_atf(self, transducer_name: str) -> None:
        
        transducer: dict = self.transducer[transducer_name]
        
        for atf in transducer:
            self.serial.send_and_get(f"!{atf}={transducer[atf]}")
        
        self.notebook.connectiontab.transducer_menuebutton['text'] = transducer_name
        self.notebook.connectiontab.transducer_preview_label['text'] = self.notebook.connectiontab.config_file_str()


class SonicAgent(SonicThread):
    """
    The SonicAgent sends the Command.GET_STATUS command to get the status data
    from a SonicAmp. It puts that data into the inhereted queue.
    Furthermore it has access to the serial connection through it's parameters

    It is also the source of a connection Interrupt. If that case arrives,
    the __reinit__ method of root is being called so that the
    """

    @property
    def root(self):
        return self._root

    def __init__(self, root: Root) -> None:
        super().__init__()
        self._root: Root = root

    def worker(self) -> None:
        """
        This is the core of the SonicThread, the worker method
        that does the actual work during the phase that the 
        thread is not paused
        """
        
        # This is the case when the thread is resumed
        try:
            
            if self.root.serial.is_connected:
                status: Status = self.root.sonicamp.get_status()
                
                if (
                    not isinstance(status, bool)
                    and status != self.root.sonicamp.status
                ):
                    self.queue.put(status)
        
        # Case when a connection interrupt is happening
        except serial.SerialException:
            self.root.__reinit__()
        
        # Undefined behaviour of the thread, so that the
        # Thread is generally a bit "softer"
        except Exception as e:
            logger.warning(f"{e}")
