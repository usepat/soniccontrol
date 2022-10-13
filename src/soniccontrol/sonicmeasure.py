from __future__ import annotations
from dataclasses import dataclass

import os
import sys
import datetime
import csv
import time
import tkinter as tk
import tkinter.ttk as ttk
import logging
import traceback

from typing import TYPE_CHECKING, Union
from tkinter import messagebox, filedialog
from matplotlib import style
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk, FigureCanvasTkAgg

from sonicpackage import Command, serial, SonicAmp
from soniccontrol.sonicamp import SerialConnection, SerialConnectionGUI
from soniccontrol.helpers import logger

if TYPE_CHECKING:
    from soniccontrol.core import Root

if sys.platform == 'darwin':
    import matplotlib
    matplotlib.use('TkAgg')


class SonicMeasureWindow(tk.Toplevel):
    
    def __init__(self, root: Root, *args, **kwargs):
        super().__init__(master=root, *args, **kwargs)
        
        self.root: Root = root
        self.control_unit: SonicMeasureControlUnit
        self.filehandler: FileHandler
        
        # Data array for plotting
        self.frq_list: list = []
        self.urms_list: list = []
        self.irms_list: list = []
        self.phase_list: list = []
        
        # Tkinter variables
        self.start_frq_tk: tk.IntVar = tk.IntVar(value=1900000)
        self.stop_frq_tk: tk.IntVar = tk.IntVar(value=2100000)
        self.step_frq_tk: tk.IntVar = tk.IntVar(value=1000)
        self.gain_tk: tk.IntVar = tk.IntVar(value=100)
        self.comment_tk: tk.StringVar = tk.StringVar()
        
        # Window configuration
        self.title('Sonic Measure')
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Figure Frame
        self.fig_frame: ttk.Frame = ttk.Frame(self)
        self.fig_canvas: MeasureCanvas = MeasureCanvas(
            self,
            self.start_frq_tk.get(),
            self.stop_frq_tk.get(),
        )
        self.toolbar: NavigationToolbar2Tk = NavigationToolbar2Tk(self.fig_canvas, self.fig_frame)
        
        # Control Frame
        self.control_frame: ttk.Frame = ttk.Frame(self)
        
        # Control Frame - Utility frame
        self.util_ctrl_frame: ttk.Frame = ttk.Frame(self.control_frame)
        self.start_btn: ttk.Button = ttk.Button(
            self.util_ctrl_frame,
            text='Start',
            style='success.TButton',
            image=self.root.PLAY_IMG,
            compound=tk.RIGHT,
            command=self.start,
        )
        
        # Control Frame - Frequency and Gain configuration Frame
        self.frq_frame: ttk.LabelFrame = ttk.LabelFrame(
            self.control_frame, text='Set up Frequency', style='secondary.TLabelframe',
        )
        self.start_frq_label: ttk.Label = ttk.Label(
            self.frq_frame, text='Start frequency [Hz]',
        )
        self.start_frq_entry: ttk.Entry = ttk.Entry(
            self.frq_frame,
            textvariable=self.start_frq_tk,
            style="dark.TEntry",
        )
        self.stop_frq_label: ttk.Label = ttk.Label(
            self.frq_frame, text="Stop frequency [Hz]"
        )
        self.stop_frq_entry: ttk.Entry = ttk.Entry(
            self.frq_frame,
            textvariable=self.stop_frq_tk,
            style="dark.TEntry",
        )
        self.step_frq_label: ttk.Label = ttk.Label(
            self.frq_frame, text="Resolution [Hz]"
        )
        self.step_frq_entry: ttk.Entry = ttk.Entry(
            self.frq_frame, 
            textvariable=self.step_frq_tk, 
            style="dark.TEntry"
        )
        self.gain_label: ttk.Label = ttk.Label(
            self.frq_frame, text='Configure Gain [%]'
        )
        self.gain_entry: ttk.Entry = ttk.Entry(
            self.frq_frame,
            textvariable=self.gain_tk,
            style="dark.TEntry",
        )
        
        # Control Frame - Meta data Frame
        self.meta_data_frame: ttk.LabelFrame = ttk.LabelFrame(
            self.control_frame, text='Comment', style='secondary.TLabelframe',
        )
        self.meta_comment_label: ttk.Label = ttk.Label(
            self.meta_data_frame, text= 'Comment',
        )
        self.meta_comment: tk.Text = tk.Text(
            self.meta_data_frame,
            autoseparators=False,
            background='white',
            setgrid=False,
            width=30,
            height=7,
        )
        self.material_comment_label: ttk.Label = ttk.Label(
            self.meta_data_frame, text= 'Material',
        )
        self.material_comment_entry: ttk.Entry = ttk.Entry(
            self.meta_data_frame, textvariable=self.comment_tk, style='dark.TEntry'
        )
        self.distance_label: ttk.Label = ttk.Label(
            self.meta_data_frame, text= 'Distance',
        )
        self.distance_entry: ttk.Entry = ttk.Entry(
            self.meta_data_frame, textvariable=self.comment_tk, style='dark.TEntry'
        )
        
        self.publish()
        
    def start(self) -> None:
        if self.start_frq_tk.get() < 600000 or self.stop_frq_tk.get() < 600000:
            messagebox.showinfo(
                "Not supported values",
                "Please make sure that your frequency values are between 600000Hz and 6000000Hz",
            )
            self.stop()
        
        make_copy_answer: Union[bool, None] = messagebox.askyesnocancel(
            "Specify save path?", 
            "Do you want to specify a save path for the stored data? \nNote that a copy will be stored under SonicControl/SonicMeasue regardless")
        
        if make_copy_answer is None:
            return None
        
        self.filehandler: FileHandler = FileHandler(self, make_copy_answer)
        self.control_unit: SonicMeasureControlUnit = SonicMeasureControlUnit(
            self, 
            self.root.sonicamp,
        )
        
        self.start_btn.config(
            text='Stop',
            style='danger.TButton',
            image=self.root.PAUSE_IMG,
            command=self.control_unit.stop
        )
        
        for child in self.frq_frame.winfo_children():
            child.config(state=tk.DISABLED)
        
        self.root.serial.send_and_get(Command.SET_SIGNAL_ON)
        self.root.serial.send_and_get(Command.SET_GAIN + self.gain_tk.get())
        
        time.sleep(1)
        
        if not self.root.thread.paused:
            logging.debug("pausing thread")
            self.root.thread.pause()
            
        self.control_unit.start()
    
    def stop(self) -> None:
        self.start_btn.config(
            text="Run",
            style="success.TButton",
            image=self.root.PLAY_IMG,
            command=self.start,
        )

        for child in self.frq_frame.children.values():
            child.config(state=tk.NORMAL)

        # In case the thread was paused, resume. If statement to not resume the thread twice
        if self.root.thread.paused:
            self.root.thread.resume()
    
    def plot_data(self, data: MeasureData) -> None:
        assert isinstance(data, MeasureData)
        
        self.frq_list.append(data.FRQ)
        self.urms_list.append(data.URMS)
        self.irms_list.append(data.IRMS)
        self.phase_list.append(data.PHASE)

        self.fig_canvas.plot_urms.set_data(self.frq_list, self.urms_list)
        self.fig_canvas.plot_irms.set_data(self.frq_list, self.irms_list)
        self.fig_canvas.plot_phase.set_data(self.frq_list, self.phase_list)

        self.fig_canvas.draw()

        self.fig_canvas.ax_urms.set_ylim(
            min(self.urms_list) - min(self.urms_list) * 0.4,
            max(self.urms_list) + max(self.urms_list) * 0.2,
        )
        self.fig_canvas.ax_irms.set_ylim(
            min(self.irms_list) - min(self.irms_list) * 0.4,
            max(self.irms_list) + max(self.irms_list) * 0.2,
        )
        self.fig_canvas.ax_phase.set_ylim(
            min(self.phase_list) - min(self.phase_list) * 0.4,
            max(self.phase_list) + max(self.phase_list) * 0.2,
        )

        self.fig_canvas.flush_events()
        self.root.update()
    
    def publish(self) -> None:
        self.fig_frame.pack(fill=tk.BOTH, expand=True)
        self.fig_canvas._tkcanvas.pack(fill=tk.BOTH, expand=True)
        self.control_frame.pack()

        self.util_ctrl_frame.grid(row=0, column=0, padx=10, pady=10)
        self.frq_frame.grid(row=0, column=1, padx=10, pady=10)
        self.meta_data_frame.grid(row=0, column=2, padx=10, pady=10)

        self.start_btn.pack(expand=True, fill=tk.BOTH, padx=3, pady=3)
        # self.save_btn.pack(expand=True, fill=tk.BOTH, padx=3, pady=3)

        # Frq Frame
        self.start_frq_label.grid(row=0, column=0, padx=3, pady=3)
        self.start_frq_entry.grid(row=0, column=1, padx=3, pady=3)

        self.stop_frq_label.grid(row=1, column=0, padx=3, pady=3)
        self.stop_frq_entry.grid(row=1, column=1, padx=3, pady=3)

        self.step_frq_label.grid(row=2, column=0, padx=3, pady=3)
        self.step_frq_entry.grid(row=2, column=1, padx=3, pady=3)

        self.gain_label.grid(row=3, column=0, padx=3, pady=3)
        self.gain_entry.grid(row=3, column=1, padx=3, pady=3)
        
        # self.meta_comment_label.grid(row=0, column=0, padx=3, pady=3)
        self.meta_comment.grid(row=0, column=1, padx=3, pady=3)
        
    def on_closing(self) -> None:
        self.stop()
        self.destroy()
        
        
class SonicMeasureControlUnit(object):
    
    @property
    def sonicamp(self) -> SonicAmp:
        return self._sonicamp
    
    @property
    def serial(self) -> SerialConnectionGUI:
        return self._serial
    
    def __init__(self, gui: SonicMeasureWindow, sonicamp: SonicAmp) -> None:
        
        self.gui: SonicMeasureWindow = gui
        self._sonicamp: SonicAmp = sonicamp
        self._serial: SerialConnection = sonicamp.serial
        
        self.collected_data: list = []
        
        self.start_frq: int = self.gui.start_frq_tk.get()
        self.stop_frq: int = self.gui.stop_frq_tk.get()
        
        if self.start_frq > self.stop_frq:
            self.step_frq: int = -abs(self.gui.step_frq_tk.get())
        else:
            self.step_frq: int = self.gui.step_frq_tk.get()
        
        logger.info(f"{self.start_frq}{self.stop_frq}{self.step_frq}")
        
    def get_sens(self) -> MeasureData:
        logger.debug(f"Sonicamp signal: {self.sonicamp.status.signal}")

        data: MeasureData = MeasureData.construct_from_str(
            self.serial.send_and_get(Command.GET_SENS),
            self.sonicamp.status.gain
        )
        self.collected_data.append(data)
        logger.info(data)
        
        return data
        
    def stop(self) -> None:
        if not self.run:
            self.run: bool = False
            
        self.serial.send_and_get(Command.SET_SIGNAL_OFF)
        self.gui.stop()
    
    def sequence(self) -> None:
        
        for frq in range(self.start_frq, self.stop_frq, self.step_frq):
            if self.run:    
                try:  
                    logger.debug(f"At {frq}")
                    self.serial.send_and_get(Command.SET_FRQ + frq)
                    data: MeasureData = self.get_sens()

                    logger.info(data)

                    self.gui.plot_data(data)
                    self.gui.filehandler.register_data(data)

                except AssertionError:
                    logger.warning("Something went wrong ASSERTIONERROR")
                    self.gui.stop()

                except serial.SerialException:
                    self.gui.stop()
                    self.gui.root.__reinit__()
                    break
            
            else:
                break
        
        self.stop()
            
    def start(self):
        # self.sonicamp.status.signal = True
        # self.sonicamp.status.gain = self.gui.gain_tk.get()
        
        self.run: bool = True
        self.sequence()
    
    
@dataclass(frozen=True)
class MeasureData(object):
    
    timestamp: int
    signal: bool
    frq: int
    gain: int
    urms: int
    irms: int
    phase: int
    
    @classmethod
    def construct_from_str(cls, data_string: str, gain: int) -> MeasureData:
        assert len(data_string)
        
        timestamp: datetime.datetime = datetime.datetime.now()
        data_list: list = [int(data) for data in data_string.split(" ")]
        
        obj: MeasureData = cls(timestamp, True, data_list[0], gain, data_list[1], data_list[2], data_list[3])
        
        return obj
    
    
class MeasureCanvas(FigureCanvasTkAgg):
    
    def __init__(self, parent: ttk.Frame, start_frq: int, stop_frq: int) -> None:
        self.figure: Figure = Figure()
        style.use("seaborn")

        self.ax_urms = self.figure.add_subplot(111)
        self.figure.subplots_adjust(right=0.8)

        self.ax_irms = self.ax_urms.twinx()
        self.ax_phase = self.ax_urms.twinx()
        self.ax_phase.spines["right"].set_position(("axes", 1.15))

        (self.plot_urms,) = self.ax_urms.plot([], [], "bo-", label="U$_{RMS}$ / mV")
        (self.plot_irms,) = self.ax_irms.plot([], [], "ro-", label="I$_{RMS}$ / mA")
        (self.plot_phase,) = self.ax_phase.plot([], [], "go-", label="Phase / °")

        self.ax_urms.set_xlim(start_frq, stop_frq)
        self.ax_urms.set_xlabel("Frequency / Hz")
        self.ax_urms.set_ylabel("U$_{RMS}$ / mV")
        self.ax_irms.set_ylabel("I$_{RMS}$ / mA")
        self.ax_phase.set_ylabel("Phase / °")

        self.ax_urms.yaxis.label.set_color(self.plot_urms.get_color())
        self.ax_irms.yaxis.label.set_color(self.plot_irms.get_color())
        self.ax_phase.yaxis.label.set_color(self.plot_phase.get_color())

        self.ax_urms.legend(handles=[self.plot_urms, self.plot_irms, self.plot_phase])
        super().__init__(self.figure, parent)

    def update_axes(self, start_frq: int, stop_frq: int) -> None:
        self.ax_urms.set_xlim(start_frq, stop_frq)
        

class FileHandler(object):
    def __init__(self, gui: SonicMeasureWindow, make_copy: bool) -> None:
        
        self.gui: SonicMeasureWindow = gui

        self.save_filepath: str = ""
        self.logfilepath: str = ""
        
        self.preamble: str = f"""
# Datetime: {datetime.datetime.now()}
# Gain: {self.gui.gain_tk.get()} in [%]
# Frequency in [Hz]
# Urms in [mV]
# Irms in [mA]
# Phase in [deg]
#
# Comment:
# {self.insert_text_as_comment()}\n"""

        self._filetypes: list[tuple] = [
            ("Text", "*.txt"),
            ("All files", "*"),
        ]
        self._save_dir: str = "SonicMeasure"

        self.fieldnames: list = [
            "timestamp",
            "frq",
            "gain",
            "urms",
            "irms",
            "phase"
        ]

        if not os.path.exists(self._save_dir):
            os.mkdir(self._save_dir)
        
        self.decide_logfile_name(make_copy)

    def insert_text_as_comment(self) -> str:
        
        text: str = self.gui.meta_comment.get(2.0, tk.END)
        output_text: str = f"{self.gui.meta_comment.get(1.0, '1.end')}\n"
        
        for line in text.splitlines():
            output_text += f"# {line}\n"

        return output_text

    def decide_logfile_name(self, make_copy: bool) -> None:
        tmp_timestamp: str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.logfilepath: str = f"{self._save_dir}//{tmp_timestamp}_{self.gui.root.sonicamp.type_}_SonicMeasure.csv"
        
        if make_copy:
            self.save_filepath: str = filedialog.asksaveasfilename(
                defaultextension='.txt', filetypes=self._filetypes
            )
        
        self._create_datafiles()

    def save_file(self) -> None:
        self.save_filename = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=self._filetypes
        )

    def _create_datafiles(self) -> None:
        """
        Internal method to create the csv status log file
        """
        with open(self.logfilepath, "a", newline="") as logfile:
            logfile.write(self.preamble)
            
            csv_writer: csv.DictWriter = csv.DictWriter(
                logfile, fieldnames=self.fieldnames
            )
            csv_writer.writeheader()
        
        if self.save_filepath:
            with open(self.save_filepath, "a", newline="") as savefile:
                savefile.write(self.preamble)
                
                csv_writer: csv.DictWriter = csv.DictWriter(
                    savefile, fieldnames=self.fieldnames
                )
                csv_writer.writeheader()

    def register_data(self, data: MeasureData) -> None:
        
        data_dict: dict = data.__dict__
        
        with open(self.logfilepath, "a", newline="") as logfile:
            csv_writer: csv.DictWriter = csv.DictWriter(
                logfile, fieldnames=self.fieldnames
            )
            csv_writer.writerow(data_dict)
        
        with open(self.gui.root.statuslog_filepath, "a", newline="") as statuslogfile:
            csv_writer: csv.DictWriter = csv.DictWriter(
                statuslogfile, fieldnames=self.fieldnames
            )
            csv_writer.writerow(data_dict)
        
        if self.save_filepath:
            with open(self.save_filepath, "a", newline="") as savefile:
                csv_writer: csv.DictWriter = csv.DictWriter(
                    savefile, fieldnames=self.fieldnames
                )
                csv_writer.writerow(data_dict)

# from __future__ import annotations

# import os
# import sys
# import datetime
# import csv
# import tkinter as tk
# import tkinter.ttk as ttk

# from typing import TYPE_CHECKING
# from tkinter import messagebox
# from matplotlib import style
# from matplotlib.figure import Figure
# from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk, FigureCanvasTkAgg

# from sonicpackage import Command, serial
# from soniccontrol.sonicamp import SerialConnection

# if TYPE_CHECKING:
#     from soniccontrol.core import Root

# if sys.platform == 'darwin':
#     import matplotlib
#     matplotlib.use('TkAgg')

# class SonicMeasure(tk.Toplevel):
#     @property
#     def serial(self) -> SerialConnection:
#         return self._serial

#     def __init__(self, root: Root, *args, **kwargs) -> None:
#         super().__init__(master=root, *args, **kwargs)

#         self._serial: SerialConnection = root.serial
#         self.root: Root = root

#         self._filetypes: list[tuple] = [
#             ("Text", "*.txt"),
#             ("All files", "*"),
#         ]

#         self.title("SonicMeasure")

#         self.start_frq: tk.IntVar = tk.IntVar(value=1900000)
#         self.stop_frq: tk.IntVar = tk.IntVar(value=2100000)
#         self.step_frq: tk.IntVar = tk.IntVar(value=100)

#         self.start_gain: tk.IntVar = tk.IntVar(value=10)
#         self.stop_gain: tk.IntVar = tk.IntVar(value=10)
#         self.step_gain: tk.IntVar = tk.IntVar(value=0)

#         # Figure Frame
#         self.fig_frame: ttk.Frame = ttk.Frame(self)
#         self.figure_canvas: MeasureCanvas = MeasureCanvas(
#             self.fig_frame, self.start_frq.get(), self.stop_frq.get()
#         )
#         self.toolbar = NavigationToolbar2Tk(self.figure_canvas, self.fig_frame)

#         # Utility controls Frame
#         self.control_frame: ttk.Frame = ttk.Frame(self)
#         self.util_ctrl_frame: ttk.Frame = ttk.Frame(self.control_frame)
#         self.start_btn: ttk.Button = ttk.Button(
#             self.util_ctrl_frame,
#             text="Start",
#             style="success.TButton",
#             image=root.PLAY_IMG,
#             compound=tk.RIGHT,
#             command=self.start,
#         )

#         self.save_btn: ttk.Button = ttk.Button(
#             self.util_ctrl_frame,
#             text="Save Plot",
#             style="info.TButton",
#             # image=self.root.save_img, #! Implement image
#             # compound=tk.RIGHT,
#             command=self.save,
#         )

#         # Frquency Frame
#         self.frq_frame: ttk.LabelFrame = ttk.LabelFrame(
#             self.control_frame, text="Set up Frequency", style="secondary.TLabelframe"
#         )
#         self.start_frq_label: ttk.Label = ttk.Label(
#             self.frq_frame, text="Start frequency [Hz]"
#         )

#         self.start_frq_entry: ttk.Entry = ttk.Entry(
#             self.frq_frame,
#             textvariable=self.start_frq,
#             style="dark.TEntry",
#         )

#         self.stop_frq_label: ttk.Label = ttk.Label(
#             self.frq_frame, text="Stop frequency [Hz]"
#         )

#         self.stop_frq_entry: ttk.Entry = ttk.Entry(
#             self.frq_frame,
#             textvariable=self.stop_frq,
#             style="dark.TEntry",
#         )

#         self.step_frq_label: ttk.Label = ttk.Label(
#             self.frq_frame, text="Resolution [Hz]"
#         )

#         self.step_frq_entry: ttk.Entry = ttk.Entry(
#             self.frq_frame, textvariable=self.step_frq, style="dark.TEntry"
#         )

#         # Gain Frame
#         self.gain_frame: ttk.LabelFrame = ttk.LabelFrame(
#             self.control_frame, text="Set up Gain", style="secondary.TLabelframe"
#         )
#         self.start_gain_label: ttk.Label = ttk.Label(
#             self.gain_frame, text="Start gain [%]"
#         )

#         self.start_gain_entry: ttk.Entry = ttk.Entry(
#             self.gain_frame,
#             textvariable=self.start_gain,
#             style="dark.TEntry",
#         )

#         self.stop_gain_label: ttk.Label = ttk.Label(
#             self.gain_frame, text="Stop gain [%]"
#         )

#         self.stop_gain_entry: ttk.Entry = ttk.Entry(
#             self.gain_frame,
#             textvariable=self.stop_gain,
#             style="dark.TEntry",
#         )

#         self.step_gain_label: ttk.Label = ttk.Label(
#             self.gain_frame, text="Resolution [%]"
#         )

#         self.step_gain_entry: ttk.Entry = ttk.Entry(
#             self.gain_frame, textvariable=self.step_gain, style="dark.TEntry"
#         )

#         #! EHRER
#         self._spectra_dir: str = "SonicMeasure"
#         self.fieldnames: list = ["timestamp", "frequency", "urms", "irms", "phase"]

#         if not os.path.exists(self._spectra_dir):
#             os.mkdir(self._spectra_dir)

#         self.publish()

#     def on_closing(self) -> None:
#         """Function that will be executed if window closes"""
#         self.stop()
#         self.destroy()

#     def start(self) -> None:
#         """WHat happens if the start button is being pressed"""
#         # logger.info(f"SonicMeasure\tstarting measure")

#         self.run: bool = True
#         # Change the appearence of the start button -> to a stop button
#         self.start_btn.config(
#             text="Stop",
#             style="danger.TButton",
#             image=self.root.PAUSE_IMG,
#             command=self.stop,
#         )

#         self.save_btn.config(state=tk.DISABLED)

#         for child in self.frq_frame.children.values():
#             child.config(state=tk.DISABLED)

#         timestamp: str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#         self.spectra_file: str = f"sonicmeasure_{timestamp}.csv"
#         self._create_csv()

#         self.root.thread.pause()
#         self.serial.send_and_get(Command.SET_MHZ)
#         self.serial.send_and_get(Command.SET_SIGNAL_ON)
#         self.serial.send_and_get(Command.SET_GAIN + self.start_gain.get())
#         self.start_sequence()

#     def stop(self) -> None:
#         """Code tha will be executed if the Measure sequence is stopped"""
#         self.start_btn.config(
#             text="Run",
#             style="success.TButton",
#             image=self.root.PLAY_IMG,
#             command=self.start,
#         )
#         self.save_btn.config(state=tk.NORMAL)

#         for child in self.frq_frame.children.values():
#             child.config(state=tk.NORMAL)

#         self.serial.send_and_get(Command.SET_SIGNAL_OFF)

#         # In case the thread was paused, resume. If statement to not resume the thread twice
#         if self.root.thread.paused:
#             self.root.thread.resume()

#     def _create_csv(self) -> None:
#         """Create a csv for the current measurement"""
#         with open(f"{self._spectra_dir}//{self.spectra_file}", "a", newline="") as f:
#             f.write(
#                 f"{datetime.datetime.now()}\ngain = {self.root.sonicamp.status.gain}\ndate[Y-m-d]\ntime[H:m:s.ms]\nurms[mV]\nirms[mA]\nphase[degree]\n\n"
#             )
#             csv_writer: csv.DictWriter = csv.DictWriter(f, fieldnames=self.fieldnames)
#             csv_writer.writeheader()

#     def start_sequence(self) -> None:
#         """Starts the sequence and the measurement"""
#         start: int = self.start_frq.get()
#         stop: int = self.stop_frq.get()
#         step: int = self.step_frq.get()

#         self.figure_canvas.update_axes(start, stop)

#         self.frq_list: list = []
#         self.urms_list: list = []
#         self.irms_list: list = []
#         self.phase_list: list = []

#         if start < 600000 or stop < 600000:
#             messagebox.showinfo(
#                 "Not supported values",
#                 "Please make sure that your frequency values are between 600000Hz and 6000000Hz",
#             )
#             self.stop()

#         # In case start value is higher than stop value and the sequence should be run decreasingly
#         elif start > stop:
#             step = -abs(step)

#         for frq in range(start, stop, step):

#             try:
#                 data: dict = self.get_data(frq)
#                 self.protocol(
#                     "WM_DELETE_WINDOW", self.on_closing
#                 )  # tkinter protocol function to -> What function should be called when event (Window closes) happens
#                 print(data)
#                 self.plot_data(data)
#                 self.register_data(data)

#             # What should be done, if connection suddelny disappears
#             except serial.SerialException:
#                 self.root.__reinit__()
#                 break

#         self.stop()

    # def plot_data(self, data: dict) -> None:
    #     """Append the data to the plotted list and update
    #     the plot accordingly

    #     Args:
    #         data (dict): The data that needs to be plotted, specifically with the dict keys:
    #             -> "frequency" (int)    : the current frequency
    #             -> "urms" (int)         : the current Urms (Voltage)
    #             -> "irms" (int)         : the current Irms (Amperage)
    #             -> "phase" (int)        : the current phase (Degree)
    #     """
    #     # logger.info(f"SonicMeasure\tPlotting data\t{data = }")

    #     self.frq_list.append(data["frequency"])
    #     self.urms_list.append(data["urms"])
    #     self.irms_list.append(data["irms"])
    #     self.phase_list.append(data["phase"])

    #     self.figure_canvas.plot_urms.set_data(self.frq_list, self.urms_list)
    #     self.figure_canvas.plot_irms.set_data(self.frq_list, self.irms_list)
    #     self.figure_canvas.plot_phase.set_data(self.frq_list, self.phase_list)

    #     self.figure_canvas.draw()

    #     self.figure_canvas.ax_urms.set_ylim(
    #         min(self.urms_list) - min(self.urms_list) * 0.4,
    #         max(self.urms_list) + max(self.urms_list) * 0.2,
    #     )
    #     self.figure_canvas.ax_irms.set_ylim(
    #         min(self.irms_list) - min(self.irms_list) * 0.4,
    #         max(self.irms_list) + max(self.irms_list) * 0.2,
    #     )
    #     self.figure_canvas.ax_phase.set_ylim(
    #         min(self.phase_list) - min(self.phase_list) * 0.4,
    #         max(self.phase_list) + max(self.phase_list) * 0.2,
    #     )

    #     self.figure_canvas.flush_events()
    #     self.root.update()

#     def register_data(self, data: dict) -> None:
#         """Register the measured data in a csv file"""
#         # logger.info(f"SonicMeasrue\tRegistering data in a csv file\t{data = }")

#         with open(f"{self._spectra_dir}//{self.spectra_file}", "a", newline="") as f:
#             csv_writer: csv.DictWriter = csv.DictWriter(f, fieldnames=self.fieldnames)
#             print(data)
#             csv_writer.writerow(data)

#     def get_data(self, frq: int) -> dict:
#         """Sets the passed freqeuency and gets the new data from the change
#         of state

#         Args:
#             frq (int): The frequency to be setted

#         Returns:
#             dict: The data with URMS, IRMS and PHASE
#         """
#         # logger.info(f"SonicMeasrue\tGetting data for\t{frq = }")

#         self.serial.send_and_get(Command.SET_FRQ + frq)
#         data_list: list = self._get_sens()
#         data_dict: dict = self._list_to_dict(data_list)

#         # logger.info(f"SonicMeasure\tGot data\t{data_dict = }")
#         return data_dict

#     def _list_to_dict(self, data_list: list) -> dict:
#         """Converts a list from the SonSens Module through the command ?sens
#         to a dictionary

#         Args:
#             data_list (list): The data in a list

#         Returns:
#             dict: The data in a dictionary with the following keywords:
#         """
#         data_dict: dict = {
#             "timestamp": datetime.datetime.now(),
#             "frequency": data_list[0],
#             "urms": data_list[1],
#             "irms": data_list[2],
#             "phase": data_list[3],
#         }

#         return data_dict

#     def _get_sens(self) -> list:
#         """Gets the current sensor data via the ?sens command

#         Returns:
#             list: The from the sonicamp returned sensor data
#         """
#         data_str = self.serial.send_and_get(Command.GET_SENS, delay=0.5)

#         if not len(data_str):
#             return self._get_sens()

#         data_list: list = [
#             int(data) for data in data_str.split(" ") if data != None or data != ""
#         ]

#         # if the data wasn't fetched correctly, repeat until it works
#         if len(data_list) < 3:
#             return self._get_sens()

#         return data_list

#     def save(self) -> None:
#         pass

#     def publish(self) -> None:
#         self.fig_frame.pack(fill=tk.BOTH, expand=True)
#         self.figure_canvas._tkcanvas.pack(fill=tk.BOTH, expand=True)
#         self.control_frame.pack()

#         self.util_ctrl_frame.grid(row=0, column=0, padx=5, pady=5)
#         self.frq_frame.grid(row=0, column=1, padx=5, pady=5)
#         self.gain_frame.grid(row=0, column=2, padx=5, pady=5)

#         self.start_btn.pack(expand=True, fill=tk.BOTH, padx=3, pady=3)
#         # self.save_btn.pack(expand=True, fill=tk.BOTH, padx=3, pady=3)

#         # Frq Frame
#         self.start_frq_label.grid(row=0, column=0, padx=3, pady=3)
#         self.start_frq_entry.grid(row=0, column=1, padx=3, pady=3)

#         self.stop_frq_label.grid(row=1, column=0, padx=3, pady=3)
#         self.stop_frq_entry.grid(row=1, column=1, padx=3, pady=3)

#         self.step_frq_label.grid(row=2, column=0, padx=3, pady=3)
#         self.step_frq_entry.grid(row=2, column=1, padx=3, pady=3)

#         # Gain Frame
#         self.start_gain_label.grid(row=0, column=0, padx=3, pady=3)
#         self.start_gain_entry.grid(row=0, column=1, padx=3, pady=3)

#         # self.stop_gain_label.grid(row=1, column=0, padx=3, pady=3)
#         # self.stop_gain_entry.grid(row=1, column=1, padx=3, pady=3)

#         # self.step_gain_label.grid(row=2, column=0, padx=3, pady=3)
#         # self.step_gain_entry.grid(row=2, column=1, padx=3, pady=3)


# class MeasureCanvas(FigureCanvasTkAgg):
#     def __init__(self, parent: ttk.Frame, start_frq: int, stop_frq: int) -> None:
#         self.figure: Figure = Figure()
#         style.use("seaborn")

#         self.ax_urms = self.figure.add_subplot(111)
#         self.figure.subplots_adjust(right=0.8)

#         self.ax_irms = self.ax_urms.twinx()
#         self.ax_phase = self.ax_urms.twinx()
#         self.ax_phase.spines["right"].set_position(("axes", 1.15))

#         (self.plot_urms,) = self.ax_urms.plot([], [], "bo-", label="U$_{RMS}$ / mV")
#         (self.plot_irms,) = self.ax_irms.plot([], [], "ro-", label="I$_{RMS}$ / mA")
#         (self.plot_phase,) = self.ax_phase.plot([], [], "go-", label="Phase / °")

#         self.ax_urms.set_xlim(start_frq, stop_frq)
#         self.ax_urms.set_xlabel("Frequency / Hz")
#         self.ax_urms.set_ylabel("U$_{RMS}$ / mV")
#         self.ax_irms.set_ylabel("I$_{RMS}$ / mA")
#         self.ax_phase.set_ylabel("Phase / °")

#         self.ax_urms.yaxis.label.set_color(self.plot_urms.get_color())
#         self.ax_irms.yaxis.label.set_color(self.plot_irms.get_color())
#         self.ax_phase.yaxis.label.set_color(self.plot_phase.get_color())

#         self.ax_urms.legend(handles=[self.plot_urms, self.plot_irms, self.plot_phase])
#         super().__init__(self.figure, parent)

#     def update_axes(self, start_frq: int, stop_frq: int) -> None:
#         self.ax_urms.set_xlim(start_frq, stop_frq)
