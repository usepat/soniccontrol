from __future__ import annotations

import os
import sys
import csv
import time
import tkinter as tk
import tkinter.ttk as ttk
import logging
import traceback
import threading

from datetime import datetime
from typing import TYPE_CHECKING, Union
from tkinter import messagebox, filedialog
from matplotlib import style
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk, FigureCanvasTkAgg

from sonicpackage import (
    Command, 
    serial, 
    SonicInterface, 
    SonicMeasureFileHandler, 
    FileHandler,
    ValueNotSupported
)
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
        self.sonicmeasure: SonicMeasureFrame = SonicMeasureFrame(self, self.root)
        
        self.title('Sonic Measure')
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.sonicmeasure.pack()

        logger.debug("Initialized SonicMeasureWindow")
        
    def __reinit__(self):
        start: int = self.sonicmeasure.start_freq_tk.get()
        stop: int = self.sonicmeasure.stop_freq_tk.get()
        step: int = self.sonicmeasure.step_freq_tk.get()
        gain: int = self.sonicmeasure.gain_tk.get()
        comment: str = self.sonicmeasure.meta_comment.get(1.0, tk.END)
        
        self.sonicmeasure.destroy()
        self.sonicmeasure: SonicMeasureFrame = SonicMeasureFrame(self, self.root)
        
        self.sonicmeasure.start_freq_tk.set(start)
        self.sonicmeasure.stop_freq_tk.set(stop)
        self.sonicmeasure.step_freq_tk.set(step)
        self.sonicmeasure.gain_tk.set(gain)
        self.sonicmeasure.meta_comment.insert(1.0, comment)
        
        self.sonicmeasure.pack()
        self.sonicmeasure.button_starter()
        
    def on_closing(self) -> None:
        self.root.notebook.hometab.sonic_measure_button.config(state=tk.NORMAL)
        self.sonicmeasure.stop()
        self.sonicmeasure.destroy()
        self.destroy()


class SonicMeasureFrame(ttk.Frame):
    
    @property
    def run(self) -> bool:
        return self._run

    def __init__(self, window: SonicMeasureWindow,root: Root, *args, **kwargs):
        super().__init__(master=window, *args, **kwargs)
        
        self.window: SonicMeasureWindow = window
        self.root: Root = root
        self.filehandler: FileHandler

        self._run: bool = False
        self.logfile: str = None
        
        self._filetypes: list = [
            ("Text", "*.txt"),
            ("Logging files", "*.log"),
            ("CSV files", "*.csv"),
            ("All files", "*"),
        ]
        
        # Data array for plotting
        self.freq_list: list = []
        self.urms_list: list = []
        self.irms_list: list = []
        self.phase_list: list = []
        
        # Tkinter variables
        self.start_freq_tk: tk.IntVar = tk.IntVar(value=1900000)
        self.stop_freq_tk: tk.IntVar = tk.IntVar(value=2100000)
        self.step_freq_tk: tk.IntVar = tk.IntVar(value=1000)
        self.gain_tk: tk.IntVar = tk.IntVar(value=100)
        self.comment_tk: tk.StringVar = tk.StringVar()
        
        # Figure Frame
        self.fig_frame: ttk.Frame = ttk.Frame(self)
        self.fig_canvas: MeasureCanvas = MeasureCanvas(
            self,
            self.start_freq_tk.get(),
            self.stop_freq_tk.get(),
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
            command=self.button_starter,
        )
        self.save_log_btn: ttk.Button = ttk.Button(
            self.util_ctrl_frame,
            text="Specify logfile path",
            style="dark.TButton",
            width=15,
            command=self.open_logfile,
        )
        
        # Control Frame - Frequency and Gain configuration Frame
        self.freq_frame: ttk.LabelFrame = ttk.LabelFrame(
            self.control_frame, text='Set up Frequency', style='secondary.TLabelframe',
        )
        self.start_freq_label: ttk.Label = ttk.Label(
            self.freq_frame, text='Start frequency [Hz]',
        )
        self.start_freq_entry: ttk.Entry = ttk.Entry(
            self.freq_frame,
            textvariable=self.start_freq_tk,
            style="dark.TEntry",
        )
        self.stop_freq_label: ttk.Label = ttk.Label(
            self.freq_frame, text="Stop frequency [Hz]"
        )
        self.stop_freq_entry: ttk.Entry = ttk.Entry(
            self.freq_frame,
            textvariable=self.stop_freq_tk,
            style="dark.TEntry",
        )
        self.step_freq_label: ttk.Label = ttk.Label(
            self.freq_frame, text="Resolution [Hz]"
        )
        self.step_freq_entry: ttk.Entry = ttk.Entry(
            self.freq_frame, 
            textvariable=self.step_freq_tk, 
            style="dark.TEntry"
        )
        self.gain_label: ttk.Label = ttk.Label(
            self.freq_frame, text='Configure Gain [%]'
        )
        self.gain_entry: ttk.Entry = ttk.Entry(
            self.freq_frame,
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

    def open_logfile(self) -> None:
        self.logfile = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=self._filetypes
        )

    def button_starter(self) -> None:
        threading.Thread(target=self.start, daemon=True).start()

    def start(self) -> None:
        start_freq: int = self.start_freq_tk.get()
        stop_freq: int = self.stop_freq_tk.get()
        step_freq: int = self.step_freq_tk.get()

        self._run: bool = True

        self.root.amp_controller.set_gain(self.gain_tk.get())
        self.root.amp_controller.set_signal_on()

        self.root.thread.pause() if not self.root.thread.paused.is_set() else None

        if not self.logfile: 
            time_str: str = datetime.now().strftime("%Y%m%d-%H%M")
            self.logfile: str = f"logs/{time_str}_{self.root.sonicamp.type_}_sonicmeasure.csv"

        self.filehandler: FileHandler = SonicMeasureFileHandler(
            self.logfile,
            self.root.sonicamp.status,
            self.meta_comment.get(1.0, tk.END)
        ).create_datafile()

        self.fig_canvas.update_axes(start_freq, stop_freq)

        self.start_btn.config(
            text='Stop',
            style='danger.TButton',
            image=self.root.PAUSE_IMG,
            command=self.stop
        )

        for child in self.freq_frame.winfo_children():
            child.config(state=tk.DISABLED)
        
        logger.debug(f'trying to start ramp; Conditions run = {self.run}')
        try: self.root.sonicamp.ramp(
            start = start_freq, 
            stop = stop_freq, 
            step = step_freq, 
            delay = 1, 
            worker = self.updater, 
            sequence = self
        )
        
        except ValueNotSupported as ve: 
            messagebox.showerror("Value Error", ve)
            self.stop()
        except Exception as e:
            logger.warning(traceback.format_exc(e))

        self.stop()
        
    def stop(self) -> None:
        if self._run: self._run: bool = False
        self.root.amp_controller.set_signal_off()
        self.root.attach_data()

        self.start_btn.config(
            text="Run",
            style="success.TButton",
            image=self.root.PLAY_IMG,
            command=self.window.__reinit__,
        )

        for child in self.freq_frame.children.values():
            child.config(state=tk.NORMAL)
 
        self.root.thread.resume() if self.root.thread.paused.is_set() else None

    def status_handler(self) -> None:
        self.root.attach_data()
        self.root.update_idletasks()

    def draw(self) -> None:
        self.freq_list.append(self.root.sonicamp.status.frequency)
        self.urms_list.append(self.root.sonicamp.status.urms)
        self.irms_list.append(self.root.sonicamp.status.irms)
        self.phase_list.append(self.root.sonicamp.status.phase)

        self.fig_canvas.plot_urms.set_data(self.freq_list, self.urms_list)
        self.fig_canvas.plot_irms.set_data(self.freq_list, self.irms_list)
        self.fig_canvas.plot_phase.set_data(self.freq_list, self.phase_list)

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

    def updater(self) -> None:
        self.root.sonicamp.update()
        self.filehandler.register_data(self.root.sonicamp.status.__dict__)
        self.draw()
        self.status_handler()

    def publish(self) -> None:
        self.fig_frame.pack(fill=tk.BOTH, expand=True)
        self.fig_canvas._tkcanvas.pack(fill=tk.BOTH, expand=True)
        self.control_frame.pack()

        self.util_ctrl_frame.grid(row=0, column=0, padx=10, pady=10)
        self.freq_frame.grid(row=0, column=1, padx=10, pady=10)
        self.meta_data_frame.grid(row=0, column=2, padx=10, pady=10)

        self.start_btn.pack(expand=True, fill=tk.BOTH, padx=3, pady=3)
        self.save_log_btn.pack(expand=True, fill=tk.BOTH, padx=3, pady=3)

        # Frq Frame
        self.start_freq_label.grid(row=0, column=0, padx=3, pady=3)
        self.start_freq_entry.grid(row=0, column=1, padx=3, pady=3)

        self.stop_freq_label.grid(row=1, column=0, padx=3, pady=3)
        self.stop_freq_entry.grid(row=1, column=1, padx=3, pady=3)

        self.step_freq_label.grid(row=2, column=0, padx=3, pady=3)
        self.step_freq_entry.grid(row=2, column=1, padx=3, pady=3)

        self.gain_label.grid(row=3, column=0, padx=3, pady=3)
        self.gain_entry.grid(row=3, column=1, padx=3, pady=3)

        # self.meta_comment_label.grid(row=0, column=0, padx=3, pady=3)
        self.meta_comment.grid(row=0, column=1, padx=3, pady=3)


class MeasureCanvas(FigureCanvasTkAgg):
    
    def __init__(self, parent: ttk.Frame, start_freq: int, stop_freq: int) -> None:
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

        self.ax_urms.set_xlim(start_freq, stop_freq)
        self.ax_urms.set_xlabel("Frequency / Hz")
        self.ax_urms.set_ylabel("U$_{RMS}$ / mV")
        self.ax_irms.set_ylabel("I$_{RMS}$ / mA")
        self.ax_phase.set_ylabel("Phase / °")

        self.ax_urms.yaxis.label.set_color(self.plot_urms.get_color())
        self.ax_irms.yaxis.label.set_color(self.plot_irms.get_color())
        self.ax_phase.yaxis.label.set_color(self.plot_phase.get_color())

        self.ax_urms.legend(handles=[self.plot_urms, self.plot_irms, self.plot_phase])
        super().__init__(self.figure, parent)

    def update_axes(self, start_freq: int, stop_freq: int) -> None:
        self.ax_urms.set_xlim(start_freq, stop_freq)
        
    def remove_plot(self) -> None:
        pass


### Temporary Idea and Issue:
# XXX: Make sonicmeasure a static window extension like the 
# Serial monitor. The Window should plot the current SonicMeasure Data
# while opened, and pause while closed. Futhermore it should be
# configured, if the user wants to see the data in a specific frequency
# range. And possibly if needed be used as simple as the old sonicmeasure
# window.
# class SonicMeasureFrame(ttk.Frame):

#     @property
#     def root(self) -> Root:
#         return self._root

#     @property
#     def serial(self) -> SerialConnection:
#         return self._serial

#     @property
#     def amp_controller(self) -> SonicInterface:
#         return self._amp_controller

#     @property
#     def sonicamp(self) -> SonicAmp:
#         return self._sonicamp

#     def __init__(self, root: Root, *args, **kwargs) -> None:
#         super().__init__(root, *args, **kwargs)

#         self._root: Root = root
#         self._serial: SerialConnection = root.serial
#         self._amp_controller: SonicInterface = root.amp_controller
#         self._sonicamp: SonicAmp = root.sonicamp

#         self._initialize_graph_frame()
#         self._initialize_button_frame()

#         self.publish()

#     def _initialize_graph_frame(self) -> None:
#         self.graph_frame: SonicMeasureGraph

#     def _initialize_button_frame(self) -> None:
#         self.freq_begin_button: ttk.Button()
#         self.freq_end_button: ttk.Button()


#     def set_axes(self) -> None:
#         pass

#     def restore_normal(self) -> None:
#         pass

#     def attach_data(self) -> None:
#         if not self.sonicamp.status.signal: return 
        
#     def unpublish(self) -> None:
#         pass

#     def publish(self) -> None:
#         pass