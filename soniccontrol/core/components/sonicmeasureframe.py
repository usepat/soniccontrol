import logging
from typing import Iterable, Any, Tuple, Optional, Any, Literal
import ttkbootstrap as ttk
import threading
import pandas as pd
from ttkbootstrap.scrolled import ScrolledText, ScrolledFrame
import matplotlib

matplotlib.use("TkAgg")

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.animation import FuncAnimation
import matplotlib.dates as mdates
import functools
import datetime

from PIL.ImageTk import PhotoImage
import soniccontrol.constants as const
from soniccontrol.interfaces import RootChild, Layout, Connectable, Updatable, Root
from soniccontrol.interfaces.rootchild import RootChildFrame
from soniccontrol.interfaces.horizontal_scrolled import HorizontalScrolledFrame
from soniccontrol.sonicamp import Command
from sonicpackage import SonicThread
import time
import csv

logger = logging.getLogger(__name__)


class SonicMeasureFrame(RootChildFrame, Connectable, Updatable):
    def __init__(
        self, parent_frame: Root, tab_title: str, image: PhotoImage, *args, **kwargs
    ):
        super().__init__(parent_frame, tab_title, image, *args, **kwargs)
        #     self._width_layouts: Iterable[Layout] = ()
        #     self._height_layouts: Iterable[Layout] = ()
        self.configure(width=200)

        self.sonicmeasure: Optional[SonicMeasure] = None
        self._paused: threading.Event = threading.Event()
        self.last_read_line = 0

        self.urms_visible: ttk.BooleanVar = ttk.BooleanVar(value=True)
        self.irms_visible: ttk.BooleanVar = ttk.BooleanVar(value=True)
        self.phase_visible: ttk.BooleanVar = ttk.BooleanVar(value=True)
        self.frequency_visible: ttk.BooleanVar = ttk.BooleanVar(value=True)

        self.start_image: PhotoImage = const.Images.get_image(
            const.Images.PLAY_IMG_WHITE, const.Images.BUTTON_ICON_SIZE
        )
        self.stop_image: PhotoImage = const.Images.get_image(
            const.Images.PAUSE_IMG_WHITE, const.Images.BUTTON_ICON_SIZE
        )
        self.restart_image: PhotoImage = const.Images.get_image(
            const.Images.REFRESH_IMG_WHITE, const.Images.BUTTON_ICON_SIZE
        )
        self.back_image: PhotoImage = const.Images.get_image(
            const.Images.BACK_IMG_WHITE, const.Images.BUTTON_ICON_SIZE
        )
        self.forward_image: PhotoImage = const.Images.get_image(
            const.Images.FORWARDS_IMG_WHITE, const.Images.BUTTON_ICON_SIZE
        )

        self.main_frame: ScrolledFrame = ScrolledFrame(self, autohide=True)
        self.button_frame: ttk.Frame = ttk.Frame(self)
        self.start_stop_button: ttk.Button = ttk.Button(
            self.button_frame,
            text="Start",
            style=ttk.SUCCESS,
            image=self.start_image,
            compound=ttk.RIGHT,
            command=self.start_sonicmeasure,
        )
        self.spectrum_button: ttk.Button = ttk.Button(
            self.button_frame,
            text="Open SonicMeasure Graph",
            style=ttk.DARK,
            command=self.open_spectrum_measure,
        )

        self.toggle_button_frame: ttk.Frame = ttk.Frame(self.main_frame)
        self.toggle_urms_button = ttk.Checkbutton(
            self.toggle_button_frame,
            text="Urms",
            style="dark-square-toggle",
            variable=self.urms_visible,
            command=self.toggle_urms,
        )
        self.toggle_frequency_button = ttk.Checkbutton(
            self.toggle_button_frame,
            text="Frequency",
            style="dark-square-toggle",
            variable=self.frequency_visible,
            command=self.toggle_frequency,
        )
        self.toggle_irms_button = ttk.Checkbutton(
            self.toggle_button_frame,
            text="Irms",
            style="dark-square-toggle",
            variable=self.irms_visible,
            command=self.toggle_irms,
        )
        self.toggle_phase_button = ttk.Checkbutton(
            self.toggle_button_frame,
            text="Phase",
            style="dark-square-toggle",
            variable=self.phase_visible,
            command=self.toggle_phase,
        )

        self.plot_frame: ttk.Frame = ttk.Frame(self.main_frame)
        self.figure: Figure = Figure(dpi=100)
        self.figure_canvas: FigureCanvasTkAgg = FigureCanvasTkAgg(
            self.figure, self.plot_frame
        )
        NavigationToolbar2Tk(self.figure_canvas, self.plot_frame)

        self.configuration_frame: ttk.Frame = ttk.Frame(self)
        self.navigation_bar: ttk.Frame = ttk.Frame(self.configuration_frame)
        self.back_button: ttk.Button = ttk.Button(
            self.navigation_bar,
            text="Back",
            style=ttk.DARK,
            image=self.back_image,
            compound=ttk.LEFT,
            command=self.show_mainframe,
        )
        self.submit_button: ttk.Button = ttk.Button(
            self.navigation_bar,
            text="Start Sonicmeasure",
            style=ttk.SUCCESS,
            image=self.forward_image,
            compound=ttk.RIGHT,
            command=self.start_sonicmeasure,
        )

        self.logfile_specifier_frame: ttk.Labelframe = ttk.Labelframe(
            self.configuration_frame, text="Specify the filepath for the data storage"
        )
        self.logfile_entry: ttk.Entry = ttk.Entry(self.logfile_specifier_frame)
        self.browse_files_button: ttk.Button = ttk.Button(
            self.logfile_specifier_frame,
            text="Browse files...",
            style=ttk.SECONDARY,
            command=self.open_log_file,
        )
        self.comment_frame: ttk.Labelframe = ttk.Labelframe(
            self.configuration_frame, text="Make a comment on your data"
        )
        self.comment_entry: ttk.ScrolledText = ttk.ScrolledText(self.comment_frame)
        self.bind_events()

    def on_connect(self, event=None) -> None:
        return self.publish()

    def on_update(self, event: Any = None) -> None:
        pass

    def on_frequency_change(self, event: Any = None) -> None:
        pass

    def on_gain_change(self, event: Any = None) -> None:
        pass

    def on_temperature_change(self, event: Any = None) -> None:
        pass

    def on_urms_change(self, event: Any = None) -> None:
        pass

    def on_irms_change(self, event: Any = None) -> None:
        pass

    def on_phase_change(self, event: Any = None) -> None:
        pass

    def on_mode_change(self, event: Any = None) -> None:
        pass

    def on_signal_change(self, event: Any = None, *args, **kwargs) -> None:
        pass

    def open_log_file(self, event=None) -> None:
        pass

    def on_wipe_mode_change(self, event: Any = None) -> None:
        pass

    def resume_sonicmeasure(self) -> None:
        # self._paused.clear()
        self.ani.resume()
        self.start_stop_button.configure(
            text="Pause",
            image=self.stop_image,
            bootstyle=ttk.DANGER,
            command=self.pause_sonicmeasure,
        )

    def pause_sonicmeasure(self) -> None:
        # self._paused.set()
        self.ani.pause()
        self.start_stop_button.configure(
            text="Resume",
            image=self.start_image,
            bootstyle=ttk.SUCCESS,
            command=self.resume_sonicmeasure,
        )

    def open_spectrum_measure(self) -> None:
        self.spectrum_button.configure(state=ttk.DISABLED)
        self.sonicmeasure = SonicMeasure(self.root, self)

    def restart_sonicmeasure(self) -> None:
        self.main_frame.pack_forget()
        self.configuration_frame.pack(padx=15)

    def start_sonicmeasure(self) -> None:
        self.start_stop_button.configure(
            bootstyle=ttk.DANGER,
            text="Stop",
            image=self.stop_image,
            command=self.stop_sonicmeasure,
        )
        self.sonicmeasure_engine()
        self.show_mainframe()

    def stop_sonicmeasure(self) -> None:
        self.start_stop_button.configure(
            bootstyle=ttk.SUCCESS,
            text="Start",
            image=self.start_image,
            command=self.start_sonicmeasure,
        )
        self.figure.clear(keep_observers=False)
        self.ani = None

    def sonicmeasure_engine(self) -> None:
        self.figure.clear()
        self.figure_canvas.get_tk_widget().destroy()
        # del self.figure_canvas
        self.figure_canvas = FigureCanvasTkAgg(
            self.figure, master=self.plot_frame
        )  # Adjust master if needed
        self.figure_canvas.draw()
        self.figure_canvas.get_tk_widget().pack(fill=ttk.BOTH, expand=True)

        self.ax1_frequency = self.figure.add_subplot(1, 1, 1)  # Main axis for frequency
        self.ax1_frequency.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
        self.ax1_frequency.tick_params(axis="x", rotation=45)

        self.ax2_urms = self.ax1_frequency.twinx()  # Secondary axis for urms
        self.ax3_irms = self.ax1_frequency.twinx()  # Tertiary axis for irms
        self.ax3_irms.spines["right"].set_position(
            ("outward", 60)
        )  # Move tertiary axis to the right
        self.ax4_phase = self.ax1_frequency.twinx()
        self.figure.subplots_adjust(right=0.8)

        (self.line_frequency,) = self.ax1_frequency.plot(
            [],
            [],
            lw=2,
            marker="o",
            markersize=4,
            linestyle="-",
            label="Frequency",
            color="black",
        )
        (self.line_urms,) = self.ax2_urms.plot(
            [],
            [],
            lw=2,
            marker="o",
            markersize=4,
            linestyle="-",
            label="Urms",
            color="blue",
        )
        (self.line_irms,) = self.ax3_irms.plot(
            [],
            [],
            lw=2,
            marker="o",
            markersize=4,
            linestyle="-",
            label="Irms",
            color="red",
        )
        (self.line_phase,) = self.ax4_phase.plot(
            [],
            [],
            lw=2,
            marker="o",
            markersize=4,
            linestyle="-",
            label="Phase",
            color="green",
        )

        self.ax1_frequency.set_xlabel("Time")
        self.ax1_frequency.set_ylabel("Frequency / Hz")
        self.ax2_urms.set_ylabel("U$_{RMS}$ / mV")
        self.ax3_irms.set_ylabel("I$_{RMS}$ / mA")
        self.ax4_phase.set_ylabel("Phase / °")

        self.time_data = []
        self.frequency_data = []
        self.phase_data = []
        self.urms_data = []
        self.irms_data = []

        self.figure.canvas.mpl_connect("draw_event", self.sync_axes)
        self.ax1_frequency.legend(
            loc="upper left",
            handles=[
                self.line_frequency,
                self.line_irms,
                self.line_urms,
                self.line_phase,
            ],
        )

        def init():
            self.line_frequency.set_data([], [])
            self.line_urms.set_data([], [])
            self.line_irms.set_data([], [])
            self.line_phase.set_data([], [])
            return self.line_frequency, self.line_urms, self.line_irms, self.line_phase

        self.ani = FuncAnimation(
            self.figure, self.update_graph, init_func=init, interval=100
        )  # 100ms interval
        self.figure_canvas.draw()

    def sync_axes(self, event) -> None:
        self.ax2_urms.set_yticks(self.ax1_frequency.get_yticks())
        self.ax3_irms.set_yticks(self.ax1_frequency.get_yticks())
        self.ax4_phase.set_yticks(self.ax4_phase.get_yticks())

    @functools.cache
    def update_graph(self, frame) -> Tuple[Any, ...]:
        data = pd.read_csv(
            self.root.status_log_filepath, skiprows=range(1, self.last_read_line)
        )
        self.last_read_line += len(data)
        data["timestamp"] = pd.to_datetime(data["timestamp"])

        self.time_data += data["timestamp"].tolist()
        self.frequency_data += data["frequency"].tolist()
        self.phase_data += data["phase"].tolist()
        self.urms_data += data["urms"].tolist()
        self.irms_data += data["irms"].tolist()

        self.line_frequency.set_data(
            self.time_data[-50:], self.frequency_data[-50:]
        )  # only plot last 100 points
        self.line_urms.set_data(self.time_data[-50:], self.urms_data[-50:])
        self.line_irms.set_data(self.time_data[-50:], self.irms_data[-50:])
        self.line_phase.set_data(self.time_data[-50:], self.phase_data[-50:])

        self.ax1_frequency.relim()
        self.ax1_frequency.autoscale_view()
        self.ax2_urms.relim()
        self.ax2_urms.autoscale_view()
        self.ax3_irms.relim()
        self.ax3_irms.autoscale_view()
        self.ax4_phase.relim()
        self.ax4_phase.autoscale_view()

        return self.line_frequency, self.line_urms, self.line_irms, self.line_phase

    def toggle_frequency(self) -> None:
        self.toggle_data(
            self.frequency_visible, self.line_frequency, self.ax1_frequency
        )

    def toggle_urms(self) -> None:
        self.toggle_data(self.urms_visible, self.line_urms, self.ax2_urms)

    def toggle_irms(self) -> None:
        self.toggle_data(self.irms_visible, self.line_irms, self.ax3_irms)

    def toggle_phase(self) -> None:
        self.toggle_data(self.phase_visible, self.line_phase, self.ax4_phase)

    def toggle_data(self, tk_var: ttk.Variable, line, axis) -> None:
        is_visible = tk_var.get()
        line.set_visible(is_visible)

    def show_mainframe(self) -> None:
        self.configuration_frame.pack_forget()
        self.main_frame.pack(fill=ttk.BOTH, expand=True, padx=3, pady=3)

    def publish(self) -> None:
        self.button_frame.pack(fill=ttk.X, padx=3, pady=3)
        self.start_stop_button.pack(side=ttk.LEFT, padx=3, pady=3)
        # self.restart_button.pack(side=ttk.LEFT, padx=3, pady=3)
        self.spectrum_button.pack(side=ttk.LEFT, padx=3, pady=3)

        self.main_frame.pack(expand=True, fill=ttk.BOTH, padx=3, pady=3)

        self.toggle_button_frame.pack(fill=ttk.X, padx=3, pady=3)
        self.toggle_frequency_button.pack(side=ttk.LEFT, padx=3, pady=3)
        self.toggle_urms_button.pack(side=ttk.LEFT, padx=3, pady=3)
        self.toggle_irms_button.pack(side=ttk.LEFT, padx=3, pady=3)
        self.toggle_phase_button.pack(side=ttk.LEFT, padx=3, pady=3)

        self.plot_frame.pack(padx=3, pady=3)
        self.figure_canvas.get_tk_widget().pack(fill=ttk.BOTH, expand=True)

        self.navigation_bar.pack(pady=5, fill=ttk.X)
        self.back_button.pack(pady=5, side=ttk.LEFT)
        self.submit_button.pack(pady=5, side=ttk.RIGHT)

        self.logfile_specifier_frame.pack(pady=10, fill=ttk.X)
        self.logfile_entry.pack(side=ttk.LEFT, fill=ttk.X, padx=5, pady=5, expand=True)
        self.browse_files_button.pack(side=ttk.RIGHT, fill=ttk.X, padx=5, pady=5)

        self.comment_frame.pack(pady=5)
        self.comment_entry.pack(padx=5, pady=5)


class SonicMeasure(ttk.Toplevel):
    def __init__(self, root: Root, parent: SonicMeasureFrame, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self.root = root
        self.parent = parent
        self._last_read_line = 0

        self.ramp_thread: Optional[SonicThread] = None

        self.time_units: Tuple[str] = ("ms", "s")

        self.start_image: PhotoImage = const.Images.get_image(
            const.Images.PLAY_IMG_WHITE, const.Images.BUTTON_ICON_SIZE
        )
        self.stop_image: PhotoImage = const.Images.get_image(
            const.Images.PAUSE_IMG_WHITE, const.Images.BUTTON_ICON_SIZE
        )
        self.back_image: PhotoImage = const.Images.get_image(
            const.Images.BACK_IMG_WHITE, const.Images.BUTTON_ICON_SIZE
        )
        self.forward_image: PhotoImage = const.Images.get_image(
            const.Images.FORWARDS_IMG_WHITE, const.Images.BUTTON_ICON_SIZE
        )

        # Ramp variables
        self.ramp_mode: ttk.StringVar = ttk.StringVar(value="ramp_freq")
        self.start_var: ttk.IntVar = ttk.IntVar(value=1000000)
        self.stop_var: ttk.IntVar = ttk.IntVar(value=2000000)
        self.step_var: ttk.IntVar = ttk.IntVar(value=10000)
        self.hold_on_time_var: ttk.DoubleVar = ttk.DoubleVar(value=100)
        self.hold_on_time_unit_var: ttk.StringVar = ttk.StringVar(value="ms")
        self.hold_off_time_var: ttk.DoubleVar = ttk.DoubleVar(value=0)
        self.hold_off_time_unit_var: ttk.StringVar = ttk.StringVar(value="ms")
        self.times_to_repeat_var: ttk.IntVar = ttk.IntVar(value=0)

        self.body_frame: ScrolledFrame = ScrolledFrame(self, autohide=True)

        self.main_frame: ttk.Frame = ttk.Frame(self.body_frame)
        self.button_frame: ttk.Frame = ttk.Frame(self.main_frame)
        self.start_stop_button: ttk.Button = ttk.Button(
            self.button_frame,
            style=ttk.SUCCESS,
            text="Start",
            image=self.start_image,
            compound=ttk.RIGHT,
            command=self.start_sonicmeasure,
        )
        self.pause_resume_button: ttk.Button = ttk.Button(
            self.button_frame,
            style=ttk.DANGER,
            text="Pause",
            state=ttk.DISABLED,
            image=self.stop_image,
            compound=ttk.RIGHT,
            command=self.pause_sonicmeasure,
        )
        self.plot_frame: ttk.Frame = ttk.Frame(self.main_frame)
        self.figure: Figure = Figure(dpi=100)
        self.figure_canvas: FigureCanvasTkAgg = FigureCanvasTkAgg(
            self.figure, self.plot_frame
        )
        NavigationToolbar2Tk(self.figure_canvas, self.plot_frame)

        self.configuration_frame: ttk.Frame = ttk.Frame(self.body_frame)
        self.navigation_bar: ttk.Frame = ttk.Frame(self.configuration_frame)
        self.back_button: ttk.Button = ttk.Button(
            self.navigation_bar,
            text="Back",
            style=ttk.DARK,
            state=ttk.DISABLED,
            image=self.back_image,
            compound=ttk.LEFT,
            command=self.show_mainframe,
        )
        self.submit_button: ttk.Button = ttk.Button(
            self.navigation_bar,
            text="Start Sonicmeasure",
            style=ttk.SUCCESS,
            image=self.forward_image,
            compound=ttk.RIGHT,
            command=self.start_sonicmeasure_process,
        )

        self.ramp_program_frame: HorizontalScrolledFrame = HorizontalScrolledFrame(
            self.configuration_frame, autohide=True, height=80
        )
        # ramp mode frame setter
        self.ramp_modes: Tuple[str] = ("ramp_freq", "ramp_gain")
        self.ramp_mode_frame: ttk.LabelFrame = ttk.Labelframe(
            self.ramp_program_frame, text="Ramp Mode"
        )
        self.ramp_mode_entry: ttk.Combobox = ttk.Combobox(
            self.ramp_mode_frame,
            textvariable=self.ramp_mode,
            values=self.ramp_modes,
            width=8,
        )

        # start var frame setter
        self.start_var_frame: ttk.LabelFrame = ttk.Labelframe(
            self.ramp_program_frame, text="Start [Hz]"
        )
        self.start_var_entry: ttk.Spinbox = ttk.Spinbox(
            self.start_var_frame,
            width=8,
            textvariable=self.start_var,
            from_=0,
            to=10_000_000,
        )

        # stop_var frame setter
        self.stop_var_frame: ttk.LabelFrame = ttk.Labelframe(
            self.ramp_program_frame, text="Stop [Hz]"
        )
        self.stop_var_entry: ttk.Spinbox = ttk.Spinbox(
            self.stop_var_frame,
            width=8,
            textvariable=self.stop_var,
            from_=0,
            to=10_000_000,
        )

        # step var frame setter
        self.step_var_frame: ttk.LabelFrame = ttk.Labelframe(
            self.ramp_program_frame, text="Step [Hz]"
        )
        self.step_var_entry: ttk.Spinbox = ttk.Spinbox(
            self.step_var_frame,
            width=8,
            textvariable=self.step_var,
            from_=0,
            to=1_000_000,
        )

        # hold on frame setter
        self.hold_on_time_var_frame: ttk.LabelFrame = ttk.Labelframe(
            self.ramp_program_frame, text="Hold on time"
        )
        self.hold_on_time_var_entry: ttk.Spinbox = ttk.Spinbox(
            self.hold_on_time_var_frame,
            textvariable=self.hold_on_time_var,
            from_=0,
            width=5,
            to=10_000_000,
        )

        # hold on unit frame setter
        self.hold_on_time_unit_var_frame: ttk.LabelFrame = ttk.Labelframe(
            self.ramp_program_frame, text="Hold on time unit"
        )
        self.hold_on_time_unit_var_entry: ttk.Combobox = ttk.Combobox(
            self.hold_on_time_unit_var_frame,
            textvariable=self.hold_on_time_unit_var,
            width=3,
            values=self.time_units,
        )

        # hold off frame setter
        self.hold_off_time_var_frame: ttk.LabelFrame = ttk.Labelframe(
            self.ramp_program_frame, text="Hold off time"
        )
        self.hold_off_time_var_entry: ttk.Spinbox = ttk.Spinbox(
            self.hold_off_time_var_frame,
            textvariable=self.hold_off_time_var,
            width=5,
            from_=0,
            to=10_000_000,
        )

        # hold off unit frame setter
        self.hold_off_time_unit_var_frame: ttk.LabelFrame = ttk.Labelframe(
            self.ramp_program_frame, text="Hold off time unit"
        )
        self.hold_off_time_unit_var_entry: ttk.Combobox = ttk.Combobox(
            self.hold_off_time_unit_var_frame,
            width=3,
            textvariable=self.hold_off_time_unit_var,
            values=self.time_units,
        )

        self.static_values_frame: ttk.Labelframe = ttk.Labelframe(
            self.configuration_frame,
            text="Set up values, that are set before the ramp algorithm",
        )
        self.gain_frame: ttk.Labelframe = ttk.Labelframe(
            self.static_values_frame, text="Gain"
        )
        self.gain_entry: ttk.Spinbox = ttk.Spinbox(
            self.gain_frame,
            width=8,
            textvariable=self.root._gain,
            from_=0,
            to=150,
        )

        self.freq_frame: ttk.Labelframe = ttk.Labelframe(
            self.static_values_frame, text="Frequency"
        )
        self.freq_entry: ttk.Spinbox = ttk.Spinbox(
            self.freq_frame,
            width=8,
            textvariable=self.root._freq,
            from_=0,
            to=10_000_000,
        )

        self.logfile_specifier_frame: ttk.Labelframe = ttk.Labelframe(
            self.configuration_frame, text="Specify the filepath for the data storage"
        )
        self.logfile_entry: ttk.Entry = ttk.Entry(
            self.logfile_specifier_frame, textvariable=self.root.sonicmeasure_log_var
        )
        self.browse_files_button: ttk.Button = ttk.Button(
            self.logfile_specifier_frame,
            text="Browse files...",
            style=ttk.SECONDARY,
            command=self.open_log_file,
        )
        self.comment_frame: ttk.Labelframe = ttk.Labelframe(
            self.configuration_frame, text="Make a comment on your data"
        )
        self.comment_entry: ttk.ScrolledText = ttk.ScrolledText(self.comment_frame)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.publish()
        self.start_sonicmeasure()

    def open_log_file(self, event=None) -> None:
        self.log_file_path_var.set(
            ttk.filedialog.asksaveasfilename(
                defaultextension=".txt", filetypes=self._filetypes
            )
        )
        logger.debug(f"The new logfile path is: {self.logfile}")

    def on_closing(self) -> None:
        if self.ramp_thread is not None:
            self.ramp_thread.running.clear()
        self.parent.spectrum_button.configure(state=ttk.NORMAL)
        self.destroy()

    def resume_sonicmeasure(self) -> None:
        self.pause_resume_button.configure(
            text="Pause",
            image=self.stop_image,
            bootstyle=ttk.DANGER,
            command=self.pause_sonicmeasure,
        )
        self.ramp_thread.pause()
        self.ani.resume()

    def pause_sonicmeasure(self) -> None:
        self.pause_resume_button.configure(
            text="Resume",
            image=self.start_image,
            bootstyle=ttk.SUCCESS,
            command=self.resume_sonicmeasure,
        )
        self.ramp_thread.pause()
        self.ani.pause()

    def start_sonicmeasure(self) -> None:
        self.main_frame.pack_forget()
        self.configuration_frame.pack(padx=15, fill=ttk.BOTH, expand=True)
        self.root.sonicmeasure_log_var.set(
            f"logs//sonicmeasure_{str(datetime.datetime.now()).replace(' ', '_').replace(':', '-')}.csv"
        )

    def start_sonicmeasure_process(self) -> None:
        self.back_button.configure(state=ttk.NORMAL)
        self.start_stop_button.configure(
            text="Stop",
            bootstyle=ttk.DANGER,
            image=self.stop_image,
            compound=ttk.RIGHT,
            command=self.stop_sonicmeasure,
        )
        self.pause_resume_button.configure(
            text="Pause",
            bootstyle=ttk.DANGER,
            image=self.stop_image,
            compound=ttk.RIGHT,
            state=ttk.NORMAL,
            command=self.pause_sonicmeasure,
        )
        self.show_mainframe()
        self.sonicmeasure_engine()

    def sonicmeasure_engine(self) -> None:
        self.sonicmeasure_setup()
        self.graph_engine()

    def graph_engine(self) -> None:
        self.figure.clear()
        self.figure_canvas.get_tk_widget().destroy()
        self.figure_canvas = FigureCanvasTkAgg(
            self.figure, master=self.plot_frame
        )  # Adjust master if needed
        self.figure_canvas.draw()
        self.figure_canvas.get_tk_widget().pack(fill=ttk.BOTH, expand=True)

        self.ax_urms = self.figure.add_subplot(111)
        self.figure.subplots_adjust(right=0.8)

        self.ax_irms = self.ax_urms.twinx()
        self.ax_phase = self.ax_urms.twinx()
        self.ax_phase.spines["right"].set_position(("axes", 1.15))

        (self.line_urms,) = self.ax_urms.plot(
            [], [], "bo-", label="U$_{RMS}$ / mV", markersize=4, lw=2
        )
        (self.line_irms,) = self.ax_irms.plot(
            [], [], "ro-", label="I$_{RMS}$ / mA", markersize=4, lw=2
        )
        (self.line_phase,) = self.ax_phase.plot(
            [], [], "go-", label="Phase / °", markersize=4, lw=2
        )

        self.ax_urms.set_xlim(self.start_var.get(), self.stop_var.get())
        self.ax_urms.set_xlabel("Frequency / Hz")
        self.ax_urms.set_ylabel("U$_{RMS}$ / mV")
        self.ax_irms.set_ylabel("I$_{RMS}$ / mA")
        self.ax_phase.set_ylabel("Phase / °")

        self.ax_urms.yaxis.label.set_color(self.line_urms.get_color())
        self.ax_irms.yaxis.label.set_color(self.line_irms.get_color())
        self.ax_phase.yaxis.label.set_color(self.line_phase.get_color())

        self.ax_urms.legend(handles=[self.line_urms, self.line_irms, self.line_phase])

        self.time_data = []
        self.frequency_data = []
        self.phase_data = []
        self.urms_data = []
        self.irms_data = []

        def init():
            self.line_urms.set_data([], [])
            self.line_irms.set_data([], [])
            self.line_phase.set_data([], [])
            return self.line_urms, self.line_irms, self.line_phase

        self.ani = FuncAnimation(
            self.figure, self.update_graph, init_func=init, interval=100
        )
        self.figure_canvas.draw()

    @functools.cache
    def update_graph(self, frame):
        data = pd.read_csv(
            self.root.sonicmeasure_log, skiprows=range(1, self._last_read_line)
        )
        self._last_read_line += len(data)

        self.frequency_data += data["frequency"].tolist()
        self.urms_data += data["urms"].tolist()
        self.irms_data += data["irms"].tolist()
        self.phase_data += data["phase"].tolist()

        self.line_urms.set_data(self.frequency_data, self.urms_data)
        self.line_irms.set_data(self.frequency_data, self.irms_data)
        self.line_phase.set_data(self.frequency_data, self.phase_data)

        self.ax_urms.relim()
        self.ax_urms.autoscale_view()
        self.ax_irms.relim()
        self.ax_irms.autoscale_view()
        self.ax_phase.relim()
        self.ax_phase.autoscale_view()

        return self.line_urms, self.line_irms, self.line_phase

    def sonicmeasure_setup(self) -> None:
        with self.root.sonicmeasure_log.open("a", newline="") as file:
            # string = (
            #     f"# SonicMeasure Data Collection on {datetime.datetime.now()}",
            #     f"# Ramping Script of type {self.ramp_mode.get()}",
            #     f"# from start value {self.start_var.get()}",
            #     f"# from stop value {self.stop_var.get()}",
            #     f"# from step value {self.step_var.get()}",
            #     f"# Holding during SIGNAL ON for {self.hold_on_time_var.get()}{self.hold_on_time_unit_var.get()}",
            #     f"# Holding during SIGNAL OFF for {self.hold_off_time_var.get()}{self.hold_off_time_unit_var.get()}\n",
            # )
            # file.write("\n".join(string))
            writer = csv.DictWriter(
                file, fieldnames=self.root.fieldnames, extrasaction="ignore"
            )
            writer.writeheader()

        try:
            self.root.sonicamp.add_job(Command(f"!f={self.root._freq.get()}"), 0)
            self.root.sonicamp.add_job(Command(f"!g={self.root._gain.get()}"), 0)
        except Exception as e:
            logger.warning(e)

        self.root.sonicmeasure_running.set()
        self.ramp_thread = SonicMeasureRamp(
            self,
            self.start_var.get(),
            self.stop_var.get(),
            self.step_var.get(),
            self.hold_on_time_var.get(),
            self.hold_on_time_unit_var.get(),
            self.hold_off_time_var.get(),
            self.hold_off_time_unit_var.get(),
            type_="frequency" if self.ramp_mode.get() == "ramp_freq" else "gain",
            event=self.root.sonicmeasure_running,
        )
        self.ramp_thread.daemon = True
        self.ramp_thread.start()
        self.ramp_thread.resume()

    def stop_sonicmeasure(self) -> None:
        self.root.sonicmeasure_running.clear()
        if self.ramp_thread is not None:
            self.ramp_thread.shutdown()

        self._last_read_line = 1
        self.frequency_data.clear()
        self.urms_data.clear()
        self.irms_data.clear()
        self.phase_data.clear()

        self.ani.pause()
        self.ani.event_source.stop()
        del self.ani

        self.root.sonicamp.add_job(Command("-", type_="status"), 0)
        self.start_stop_button.configure(
            bootstyle=ttk.SUCCESS,
            text="Start",
            image=self.start_image,
            command=self.start_sonicmeasure,
        )
        self.pause_resume_button.configure(
            state=ttk.DISABLED,
            command=self.resume_sonicmeasure,
        )

    def show_mainframe(self) -> None:
        self.configuration_frame.pack_forget()
        self.main_frame.pack(fill=ttk.BOTH, expand=True, padx=3, pady=3)

    def publish(self) -> None:
        self.body_frame.pack(fill=ttk.BOTH, expand=True)
        self.main_frame.pack(expand=True, fill=ttk.BOTH, padx=3, pady=3)

        self.button_frame.pack(fill=ttk.X, padx=3, pady=3)
        self.start_stop_button.pack(side=ttk.LEFT, padx=3, pady=3)
        # self.pause_resume_button.pack(side=ttk.LEFT, padx=3, pady=3)

        self.plot_frame.pack(padx=3, pady=3)
        self.figure_canvas.get_tk_widget().pack(fill=ttk.BOTH, expand=True)

        self.navigation_bar.pack(pady=5, fill=ttk.X)
        self.back_button.pack(pady=5, side=ttk.LEFT)
        self.submit_button.pack(pady=5, side=ttk.RIGHT)

        self.static_values_frame.pack(padx=3, pady=3, fill=ttk.X, expand=True)
        self.gain_frame.pack(side=ttk.LEFT, expand=True, padx=3, pady=3)
        self.gain_entry.pack(fill=ttk.BOTH, padx=2, pady=2)
        self.freq_frame.pack(side=ttk.LEFT, expand=True, padx=3, pady=3)
        self.freq_entry.pack(fill=ttk.BOTH, padx=2, pady=2)

        self.ramp_program_frame.pack(padx=3, pady=3, fill=ttk.X, expand=True)
        self.ramp_mode_frame.pack(
            side=ttk.LEFT, fill=ttk.X, expand=True, padx=3, pady=3
        )
        self.start_var_frame.pack(
            side=ttk.LEFT, fill=ttk.X, expand=True, padx=3, pady=3
        )
        self.stop_var_frame.pack(side=ttk.LEFT, fill=ttk.X, expand=True, padx=3, pady=3)
        self.step_var_frame.pack(side=ttk.LEFT, fill=ttk.X, expand=True, padx=3, pady=3)
        self.hold_on_time_var_frame.pack(
            side=ttk.LEFT, fill=ttk.X, expand=True, padx=3, pady=3
        )
        self.hold_on_time_unit_var_frame.pack(
            side=ttk.LEFT, fill=ttk.X, expand=True, padx=3, pady=3
        )
        self.hold_off_time_var_frame.pack(
            side=ttk.LEFT, fill=ttk.X, expand=True, padx=3, pady=3
        )
        self.hold_off_time_unit_var_frame.pack(
            side=ttk.LEFT, fill=ttk.X, padx=3, pady=3
        )

        self.ramp_mode_entry.pack(fill=ttk.BOTH, expand=True, padx=2, pady=2)
        self.start_var_entry.pack(fill=ttk.BOTH, expand=True, padx=2, pady=2)
        self.stop_var_entry.pack(fill=ttk.BOTH, expand=True, padx=2, pady=2)
        self.step_var_entry.pack(fill=ttk.BOTH, expand=True, padx=2, pady=2)
        self.hold_on_time_var_entry.pack(fill=ttk.BOTH, expand=True, padx=2, pady=2)
        self.hold_on_time_unit_var_entry.pack(
            fill=ttk.BOTH, expand=True, padx=2, pady=2
        )
        self.hold_off_time_var_entry.pack(fill=ttk.BOTH, expand=True, padx=2, pady=2)
        self.hold_off_time_unit_var_entry.pack(
            fill=ttk.BOTH, expand=True, padx=2, pady=2
        )

        self.logfile_specifier_frame.pack(pady=10, fill=ttk.X)
        self.logfile_entry.pack(side=ttk.LEFT, fill=ttk.X, padx=5, pady=5, expand=True)
        self.browse_files_button.pack(side=ttk.RIGHT, fill=ttk.X, padx=5, pady=5)

        # self.comment_frame.pack(pady=5)
        self.comment_entry.pack(padx=5, pady=5)


class SonicMeasureRamp(SonicThread):
    def __init__(
        self,
        parent: SonicMeasure,
        start: int,
        stop: int,
        step: int,
        hold_on_time: float = 1,
        hold_on_time_unit: Literal["ms", "s"] = "ms",
        hold_off_time: float = 0,
        hold_off_time_unit: Literal["ms", "s"] = "ms",
        type_: Literal["gain", "frequency"] = "frequency",
        event: threading.Event = threading.Event(),
    ) -> None:
        super().__init__()
        self.measure_frame = parent
        self._sonicamp = self.measure_frame.root.sonicamp

        self.running: threading.Event = event
        self.to_send: str = "!f=" if type_ == "frequency" else "!g="

        self.start_value: int = start
        self.stop_value: int = stop
        self.step_value: int = abs(step) if start < stop else -abs(step)
        self.values: Iterable[int] = range(start, stop + step, step)

        self.current_value: int = 0

        self.hold_on_time: float = hold_on_time
        self.hold_on_time_unit: Literal["ms", "s"] = hold_on_time_unit
        self.hold_off_time: float = hold_off_time
        self.hold_off_time_unit: Literal["ms", "s"] = hold_off_time_unit

    def setup(self) -> None:
        self._sonicamp.add_job(Command("!ON", type_="sonicmeasure"), 0)

    def can_run(self) -> bool:
        return self.running.is_set() and not self.shutdown_request.is_set()

    def worker(self) -> None:
        for value in self.values:
            if not self.can_run():
                return

            command = Command(f"{self.to_send}{value}", type_="")
            self._sonicamp.add_job(command, 0)
            command.processed.wait()

            if not self.can_run():
                return

            if self.hold_off_time:
                command = Command(f"!ON", type_="")
                self._sonicamp.add_job(command, 0)
                command.processed.wait()

            if not self.can_run():
                return

            command = Command("?sens", type_="sonicmeasure")
            self._sonicamp.add_job(command, 0)
            command.processed.wait()

            if not self.can_run():
                return

            self.hold(command, self.hold_on_time, self.hold_on_time_unit)

            if not self.can_run():
                return

            if self.hold_off_time:
                command = Command(f"!OFF", type_="")
                self._sonicamp.add_job(Command(f"!OFF", type_=""), 0)
                command.processed.wait()

                if not self.can_run():
                    return

                command = Command("?sens", type_="sonicmeasure")
                self._sonicamp.add_job(command, 0)
                command.processed.wait()

                if not self.can_run():
                    return

                self.hold(command, self.hold_off_time, self.hold_off_time_unit)

            if not self.can_run():
                return

    def hold(
        self,
        command: Optional[Command] = None,
        duration: float = 10.0,
        unit: str = "ms",
        *args,
        **kwargs,
    ) -> None:
        duration /= 1000.0 if unit == "ms" else 1.0
        end_time = (command.timestamp if command else time.time()) + duration

        while time.time() < end_time and self.can_run():
            time.sleep(0.001)
            remaining_time: float = end_time - time.time()
            remaining_time = remaining_time if remaining_time < 10_000 else 0

            if time.time() > end_time or not self.can_run():
                return

            # self.measure_frame.root.update_sonicamp(0, "sonicmeasure")
            command = Command("?sens", type_="sonicmeasure")
            self._sonicamp.add_job(command, 0)
            command.processed.wait()
            command.processed.clear()

            if time.time() > end_time or not self.can_run():
                return
