from __future__ import annotations

import pyglet
import tkinter as tk
import tkinter.ttk as ttk
import ttkbootstrap as ttkb
import csv
import datetime
import os
import json

from PIL import Image
from PIL.ImageTk import PhotoImage
from tkinter import font
from tkinter import messagebox

from sonicpackage import (
    SonicAmp,
    SonicThread,
    serial,
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
from soniccontrol.helpers import logger


##########################################################################
##### General functions and variables for the gui - Fonts and Images #####
##########################################################################

pyglet.font.add_file("QTypeOT-CondExtraLight.otf")
pyglet.font.add_file("QTypeOT-CondLight.otf")
pyglet.font.add_file("QTypeOT-CondMedium.otf")
pyglet.font.add_file("QTypeOT-CondBook.otf")
pyglet.font.add_file("QTypeOT-CondBold.otf")


def resize_img(image_path: str, maxsize: tuple) -> Image:
    image = Image.open(image_path)
    r1 = image.size[0] / maxsize[0]  # width ratio
    r2 = image.size[1] / maxsize[1]  # height ratio
    ratio = max(r1, r2)
    newsize = (int(image.size[0] / ratio), int(image.size[1] / ratio))
    image = image.resize(newsize, Image.ANTIALIAS)
    return image


# Defining images
# Uses custom resize funtion in helpers file
refresh_img: Image = resize_img("refresh_icon.png", (20, 20))
home_img: Image = resize_img("home_icon.png", (30, 30))
script_img: Image = resize_img("script_icon.png", (30, 30))
connection_img: Image = resize_img("connection_icon.png", (30, 30))
info_img: Image = resize_img("info_icon.png", (30, 30))
play_img: Image = resize_img("play_icon.png", (30, 30))
pause_img: Image = resize_img("pause_icon.png", (30, 30))
wave_bg: Image = resize_img("wave_bg.png", (540, 440))
graph_img: Image = resize_img("graph.png", (100, 100))
led_green_img: Image = resize_img("led_green.png", (35, 35))
led_red_img: Image = resize_img("led_red.png", (35, 35))



#############################################################
#### The main GUI object itself - Root object from tk.Tk ####
#############################################################

class Root(tk.Tk):
    """The Root class is the main class of the Tkinter GUI.
    Through this class every other compository object can get
    information about another object. When initializing, it
    creates the attribute self.thread that represents the
    main SonicThread that asks the sonicamp about its status.

    This thread then passed into the customized SerialConnection
    class for the GUI. So that the method SerialConnection.send_get()
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

    MIN_WIDTH: int = 555
    MIN_HEIGHT: int = 900
    MAX_WIDTH: int = 1110
    VERSION: int = 1.054
    TITLE: str = "Soniccontrol"
    THEME: str = "sandstone"

    def __init__(self, *args, **kwargs) -> None:
        """Here the Root class is being constructed and
        every needed child is being initialized, for instance
        the self.thread object that the Root class is inherently
        depended on. Further information above or in the Thread
        itself
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
        self.status_log_dir: str = "Status_Logs"
        self.statuslog_filepath: str

        if not os.path.exists(self.status_log_dir):
            os.mkdir(self.status_log_dir)

        # setting up root window, configurations
        self.geometry(f"{Root.MIN_WIDTH}x{Root.MIN_HEIGHT}")
        self.minsize(Root.MIN_WIDTH, Root.MIN_HEIGHT)
        self.maxsize(Root.MAX_WIDTH, Root.MIN_HEIGHT)
        self.wm_title(Root.TITLE)
        self.iconbitmap("welle.ico")
        style: ttkb.Style = ttkb.Style(theme=Root.THEME)

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
        self.refresh_img: PhotoImage = PhotoImage(refresh_img)
        self.home_img: PhotoImage = PhotoImage(home_img)
        self.script_img: PhotoImage = PhotoImage(script_img)
        self.connection_img: PhotoImage = PhotoImage(connection_img)
        self.info_img: PhotoImage = PhotoImage(info_img)
        self.play_img: PhotoImage = PhotoImage(play_img)
        self.pause_img: PhotoImage = PhotoImage(pause_img)
        self.wave_bg: PhotoImage = PhotoImage(wave_bg)
        self.graph_img: PhotoImage = PhotoImage(graph_img)
        self.led_green_img: PhotoImage = PhotoImage(led_green_img)
        self.led_red_img: PhotoImage = PhotoImage(led_red_img)

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

        self.__reinit__()

    def __reinit__(self) -> None:
        """Method that initializes that collects that data what to do next as
        a GUI, this is the beginnig node of everything. When a connection is
        being made, aswell as just publishing a GUI for making a potential
        connection.

        The thread directs the root object to go to this node if a connection
        suddenly interrupts

        In the Connection tab, the disconnect/ connect button directs to root
        object to go to this node to reinitialize itself

        Of course when initializing the GUI itself and starting the application
        for the first time it is being directed here
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
            messagebox.showerror("Error", "Not implemented the device")

        self.initialize_amp_data()

        if not isinstance(self.sonicamp, SonicWipeDuty):
            self.engine()

            if self.thread.paused:
                self.thread.resume()

    def initialize_amp_data(self) -> None:
        """
        Method to get the data from the sonicamp to the Root tkinter
        variables, so the all objects can adapt to it
        """
        self.frq.set(self.sonicamp.status.frequency)
        self.gain.set(self.sonicamp.status.gain)
        self.wipe_mode.set(self.sonicamp.status.wipe_mode)
        self.protocol.set(self.serial.send_and_get(Command.GET_PROTOCOL))

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
        """
        logger.info(f"publshing for disconnected soniccontrol")
        self.notebook.publish_disconnected()
        self.status_frame.destroy()
        self.mainframe.pack(anchor=tk.W, side=tk.LEFT)

        if self.winfo_width() == Root.MAX_WIDTH:
            self.adjust_dimensions()

        try:

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
        is a connection with a SonicCatch
        """
        self.serial_monitor: SerialMonitor = SerialMonitorCatch(self)
        
        self.status_frame.destroy()
        self.status_frame: StatusFrame = StatusFrameCatch(self.mainframe, self)

        self.attach_data()
        self.notebook.publish_for_catch()
        self.status_frame.publish()
        self.mainframe.pack(anchor=tk.W, side=tk.LEFT)

    def publish_for_old_wipe(self) -> None:
        """
        This method published the GUI for the case that there
        is a connection with a SonicWipe
        """
        self.serial_monitor: SerialMonitor = SerialMonitorWipe(self)
        
        self.status_frame.destroy()
        self.status_frame: StatusFrame = StatusFrameWipe(self.mainframe, self)

        self.attach_data()
        self.notebook.publish_for_wipe()
        self.status_frame.publish()
        self.mainframe.pack(anchor=tk.W, side=tk.LEFT)

    def publish_for_duty_wipe(self) -> None:
        """
        This method published the GUI for the case that there
        is a connection with a SonicWipe 40kHz DutyCycle Amp
        """
        if not self.thread.paused:
            self.thread.pause()
            
        self.serial_monitor: SerialMonitor = SerialMonitor40KHZ(self)

        self.status_frame.destroy()
        self.status_frame: StatusFrame = StatusFrameDutyWipe(self.mainframe, self)

        self.notebook.publish_for_dutywipe()
        self.status_frame.publish()
        self.status_frame.connection_on()
        self.mainframe.pack(anchor=tk.W, side=tk.LEFT)

    def publish_for_catch(self) -> None:
        pass

    def publish_for_wipe(self) -> None:
        pass

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


#####################################################################################
#### The threading.Thread SonicThread object that handles the data communication ####
#####################################################################################


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
