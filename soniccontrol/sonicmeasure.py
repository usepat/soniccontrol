from __future__ import annotations

import os
import datetime
import csv
import tkinter as tk
import tkinter.ttk as ttk

from typing import Union, TYPE_CHECKING
from tkinter import messagebox
from matplotlib import style
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk, FigureCanvasTkAgg

from sonicpackage import Command, serial
from soniccontrol.sonicamp import SerialConnection

if TYPE_CHECKING:
    from soniccontrol.core import Root


class SonicMeasure(tk.Toplevel):
    @property
    def serial(self) -> SerialConnection:
        return self._serial

    def __init__(self, root: Root, *args, **kwargs) -> None:
        super().__init__(master=root, *args, **kwargs)

        self._serial: SerialConnection = root.serial
        self.root: Root = root

        self._filetypes: list[tuple] = [
            ("Text", "*.txt"),
            ("All files", "*"),
        ]

        self.title("SonicMeasure")

        self.start_frq: tk.IntVar = tk.IntVar(value=1900000)
        self.stop_frq: tk.IntVar = tk.IntVar(value=2100000)
        self.step_frq: tk.IntVar = tk.IntVar(value=100)

        self.start_gain: tk.IntVar = tk.IntVar(value=10)
        self.stop_gain: tk.IntVar = tk.IntVar(value=10)
        self.step_gain: tk.IntVar = tk.IntVar(value=0)

        # Figure Frame
        self.fig_frame: ttk.Frame = ttk.Frame(self)
        self.figure_canvas: MeasureCanvas = MeasureCanvas(
            self.fig_frame, self.start_frq.get(), self.stop_frq.get()
        )
        self.toolbar = NavigationToolbar2Tk(self.figure_canvas, self.fig_frame)

        # Utility controls Frame
        self.control_frame: ttk.Frame = ttk.Frame(self)
        self.util_ctrl_frame: ttk.Frame = ttk.Frame(self.control_frame)
        self.start_btn: ttk.Button = ttk.Button(
            self.util_ctrl_frame,
            text="Start",
            style="success.TButton",
            image=root.play_img,
            compound=tk.RIGHT,
            command=self.start,
        )

        self.save_btn: ttk.Button = ttk.Button(
            self.util_ctrl_frame,
            text="Save Plot",
            style="info.TButton",
            # image=self.root.save_img, #! Implement image
            # compound=tk.RIGHT,
            command=self.save,
        )

        # Frquency Frame
        self.frq_frame: ttk.LabelFrame = ttk.LabelFrame(
            self.control_frame, text="Set up Frequency", style="secondary.TLabelframe"
        )
        self.start_frq_label: ttk.Label = ttk.Label(
            self.frq_frame, text="Start frequency [Hz]"
        )

        self.start_frq_entry: ttk.Entry = ttk.Entry(
            self.frq_frame,
            textvariable=self.start_frq,
            style="dark.TEntry",
        )

        self.stop_frq_label: ttk.Label = ttk.Label(
            self.frq_frame, text="Stop frequency [Hz]"
        )

        self.stop_frq_entry: ttk.Entry = ttk.Entry(
            self.frq_frame,
            textvariable=self.stop_frq,
            style="dark.TEntry",
        )

        self.step_frq_label: ttk.Label = ttk.Label(
            self.frq_frame, text="Resolution [Hz]"
        )

        self.step_frq_entry: ttk.Entry = ttk.Entry(
            self.frq_frame, textvariable=self.step_frq, style="dark.TEntry"
        )

        # Gain Frame
        self.gain_frame: ttk.LabelFrame = ttk.LabelFrame(
            self.control_frame, text="Set up Gain", style="secondary.TLabelframe"
        )
        self.start_gain_label: ttk.Label = ttk.Label(
            self.gain_frame, text="Start gain [%]"
        )

        self.start_gain_entry: ttk.Entry = ttk.Entry(
            self.gain_frame,
            textvariable=self.start_gain,
            style="dark.TEntry",
        )

        self.stop_gain_label: ttk.Label = ttk.Label(
            self.gain_frame, text="Stop gain [%]"
        )

        self.stop_gain_entry: ttk.Entry = ttk.Entry(
            self.gain_frame,
            textvariable=self.stop_gain,
            style="dark.TEntry",
        )

        self.step_gain_label: ttk.Label = ttk.Label(
            self.gain_frame, text="Resolution [%]"
        )

        self.step_gain_entry: ttk.Entry = ttk.Entry(
            self.gain_frame, textvariable=self.step_gain, style="dark.TEntry"
        )

        #! EHRER
        self._spectra_dir: str = "SonicMeasure"
        self.fieldnames: list = ["timestamp", "frequency", "urms", "irms", "phase"]

        if not os.path.exists(self._spectra_dir):
            os.mkdir(self._spectra_dir)

        self.publish()

    def on_closing(self) -> None:
        """Function that will be executed if window closes"""
        self.stop()
        self.destroy()

    def start(self) -> None:
        """WHat happens if the start button is being pressed"""
        # logger.info(f"SonicMeasure\tstarting measure")

        self.run: bool = True
        # Change the appearence of the start button -> to a stop button
        self.start_btn.config(
            text="Stop",
            style="danger.TButton",
            image=self.root.pause_img,
            command=self.stop,
        )

        self.save_btn.config(state=tk.DISABLED)

        for child in self.frq_frame.children.values():
            child.config(state=tk.DISABLED)

        timestamp: str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.spectra_file: str = f"sonicmeasure_{timestamp}.csv"
        self._create_csv()

        self.root.thread.pause()
        self.serial.send_and_get(Command.SET_MHZ)
        self.serial.send_and_get(Command.SET_SIGNAL_ON)
        self.serial.send_and_get(Command.SET_GAIN + self.start_gain.get())
        self.start_sequence()

    def stop(self) -> None:
        """Code tha will be executed if the Measure sequence is stopped"""
        self.start_btn.config(
            text="Run",
            style="success.TButton",
            image=self.root.play_img,
            command=self.start,
        )
        self.save_btn.config(state=tk.NORMAL)

        for child in self.frq_frame.children.values():
            child.config(state=tk.NORMAL)

        self.serial.send_and_get(Command.SET_SIGNAL_OFF)

        # In case the thread was paused, resume. If statement to not resume the thread twice
        if self.root.thread.paused:
            self.root.thread.resume()

    def _create_csv(self) -> None:
        """Create a csv for the current measurement"""
        with open(f"{self._spectra_dir}//{self.spectra_file}", "a", newline="") as f:
            f.write(
                f"{datetime.datetime.now()}\ngain = {self.root.sonicamp.status.gain}\ndate[Y-m-d]\ntime[H:m:s.ms]\nurms[mV]\nirms[mA]\nphase[degree]\n\n"
            )
            csv_writer: csv.DictWriter = csv.DictWriter(f, fieldnames=self.fieldnames)
            csv_writer.writeheader()

    def start_sequence(self) -> None:
        """Starts the sequence and the measurement"""
        start: int = self.start_frq.get()
        stop: int = self.stop_frq.get()
        step: int = self.step_frq.get()

        self.figure_canvas.update_axes(start, stop)

        self.frq_list: list = []
        self.urms_list: list = []
        self.irms_list: list = []
        self.phase_list: list = []

        if start < 600000 or stop < 600000:
            messagebox.showinfo(
                "Not supported values",
                "Please make sure that your frequency values are between 600000Hz and 6000000Hz",
            )
            self.stop()

        # In case start value is higher than stop value and the sequence should be run decreasingly
        elif start > stop:
            step = -abs(step)

        for frq in range(start, stop, step):

            try:
                data: dict = self.get_data(frq)
                self.protocol(
                    "WM_DELETE_WINDOW", self.on_closing
                )  # tkinter protocol function to -> What function should be called when event (Window closes) happens
                print(data)
                self.plot_data(data)
                self.register_data(data)

            # What should be done, if connection suddelny disappears
            except serial.SerialException:
                self.root.__reinit__()
                break

        self.stop()

    def plot_data(self, data: dict) -> None:
        """Append the data to the plotted list and update
        the plot accordingly

        Args:
            data (dict): The data that needs to be plotted, specifically with the dict keys:
                -> "frequency" (int)    : the current frequency
                -> "urms" (int)         : the current Urms (Voltage)
                -> "irms" (int)         : the current Irms (Amperage)
                -> "phase" (int)        : the current phase (Degree)
        """
        # logger.info(f"SonicMeasure\tPlotting data\t{data = }")

        self.frq_list.append(data["frequency"])
        self.urms_list.append(data["urms"])
        self.irms_list.append(data["irms"])
        self.phase_list.append(data["phase"])

        self.figure_canvas.plot_urms.set_data(self.frq_list, self.urms_list)
        self.figure_canvas.plot_irms.set_data(self.frq_list, self.irms_list)
        self.figure_canvas.plot_phase.set_data(self.frq_list, self.phase_list)

        self.figure_canvas.draw()

        self.figure_canvas.ax_urms.set_ylim(
            min(self.urms_list) - min(self.urms_list) * 0.4,
            max(self.urms_list) + max(self.urms_list) * 0.2,
        )
        self.figure_canvas.ax_irms.set_ylim(
            min(self.irms_list) - min(self.irms_list) * 0.4,
            max(self.irms_list) + max(self.irms_list) * 0.2,
        )
        self.figure_canvas.ax_phase.set_ylim(
            min(self.phase_list) - min(self.phase_list) * 0.4,
            max(self.phase_list) + max(self.phase_list) * 0.2,
        )

        self.figure_canvas.flush_events()
        self.root.update()

    def register_data(self, data: dict) -> None:
        """Register the measured data in a csv file"""
        # logger.info(f"SonicMeasrue\tRegistering data in a csv file\t{data = }")

        with open(f"{self._spectra_dir}//{self.spectra_file}", "a", newline="") as f:
            csv_writer: csv.DictWriter = csv.DictWriter(f, fieldnames=self.fieldnames)
            print(data)
            csv_writer.writerow(data)

    def get_data(self, frq: int) -> dict:
        """Sets the passed freqeuency and gets the new data from the change
        of state

        Args:
            frq (int): The frequency to be setted

        Returns:
            dict: The data with URMS, IRMS and PHASE
        """
        # logger.info(f"SonicMeasrue\tGetting data for\t{frq = }")

        self.serial.send_and_get(Command.SET_FRQ + frq)
        data_list: list = self._get_sens()
        data_dict: dict = self._list_to_dict(data_list)

        # logger.info(f"SonicMeasure\tGot data\t{data_dict = }")
        return data_dict

    def _list_to_dict(self, data_list: list) -> dict:
        """Converts a list from the SonSens Module through the command ?sens
        to a dictionary

        Args:
            data_list (list): The data in a list

        Returns:
            dict: The data in a dictionary with the following keywords:
        """
        data_dict: dict = {
            "timestamp": datetime.datetime.now(),
            "frequency": data_list[0],
            "urms": data_list[1],
            "irms": data_list[2],
            "phase": data_list[3],
        }

        return data_dict

    def _get_sens(self) -> list:
        """Gets the current sensor data via the ?sens command

        Returns:
            list: The from the sonicamp returned sensor data
        """
        data_str = self.serial.send_and_get(Command.GET_SENS, delay=0.5)

        if not len(data_str):
            return self._get_sens()

        data_list: list = [
            int(data) for data in data_str.split(" ") if data != None or data != ""
        ]

        # if the data wasn't fetched correctly, repeat until it works
        if len(data_list) < 3:
            return self._get_sens()

        return data_list

    def save(self) -> None:
        pass

    def publish(self) -> None:
        self.fig_frame.pack(fill=tk.BOTH, expand=True)
        self.figure_canvas._tkcanvas.pack(fill=tk.BOTH, expand=True)
        self.control_frame.pack()

        self.util_ctrl_frame.grid(row=0, column=0, padx=5, pady=5)
        self.frq_frame.grid(row=0, column=1, padx=5, pady=5)
        self.gain_frame.grid(row=0, column=2, padx=5, pady=5)

        self.start_btn.pack(expand=True, fill=tk.BOTH, padx=3, pady=3)
        # self.save_btn.pack(expand=True, fill=tk.BOTH, padx=3, pady=3)

        # Frq Frame
        self.start_frq_label.grid(row=0, column=0, padx=3, pady=3)
        self.start_frq_entry.grid(row=0, column=1, padx=3, pady=3)

        self.stop_frq_label.grid(row=1, column=0, padx=3, pady=3)
        self.stop_frq_entry.grid(row=1, column=1, padx=3, pady=3)

        self.step_frq_label.grid(row=2, column=0, padx=3, pady=3)
        self.step_frq_entry.grid(row=2, column=1, padx=3, pady=3)

        # Gain Frame
        self.start_gain_label.grid(row=0, column=0, padx=3, pady=3)
        self.start_gain_entry.grid(row=0, column=1, padx=3, pady=3)

        # self.stop_gain_label.grid(row=1, column=0, padx=3, pady=3)
        # self.stop_gain_entry.grid(row=1, column=1, padx=3, pady=3)

        # self.step_gain_label.grid(row=2, column=0, padx=3, pady=3)
        # self.step_gain_entry.grid(row=2, column=1, padx=3, pady=3)


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
