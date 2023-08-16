import logging
from typing import Iterable, Any, Tuple
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

from PIL.ImageTk import PhotoImage
import soniccontrol.constants as const
from soniccontrol.interfaces import RootChild, Layout, Connectable, Updatable, Root
from soniccontrol.interfaces.rootchild import RootChildFrame

logger = logging.getLogger(__name__)


class SonicMeasureFrame(RootChildFrame, Connectable, Updatable):
    def __init__(
        self, parent_frame: Root, tab_title: str, image: PhotoImage, *args, **kwargs
    ):
        super().__init__(parent_frame, tab_title, image, *args, **kwargs)
        #     self._width_layouts: Iterable[Layout] = ()
        #     self._height_layouts: Iterable[Layout] = ()
        self.configure(width=200)

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
        self.pause_resume_button: ttk.Button = ttk.Button(
            self.button_frame,
            text="Pause",
            style=ttk.DANGER,
            image=self.stop_image,
            compound=ttk.RIGHT,
            command=self.pause_sonicmeasure,
        )
        self.restart_button: ttk.Button = ttk.Button(
            self.button_frame,
            text="Restart",
            style="info",
            image=self.restart_image,
            compound=ttk.RIGHT,
            command=self.restart_sonicmeasure,
        )
        self.popup_sonicmeasure_button: ttk.Button(
            self.button_frame,
            text="PopUp",
            style=ttk.DARK,
            command=self.popup_sonicmeasure,
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
        self.pause_resume_button.configure(
            text="Pause",
            image=self.stop_image,
            bootstyle=ttk.DANGER,
            command=self.pause_sonicmeasure,
        )

    def pause_sonicmeasure(self) -> None:
        # self._paused.set()
        self.ani.pause()
        self.pause_resume_button.configure(
            text="Resume",
            image=self.start_image,
            bootstyle=ttk.SUCCESS,
            command=self.resume_sonicmeasure,
        )
        
    def popup_sonicmeasure(self) -> None:
        pass

    def restart_sonicmeasure(self) -> None:
        self.main_frame.pack_forget()
        self.configuration_frame.pack(padx=15)

    def start_sonicmeasure(self) -> None:
        self.sonicmeasure_engine()
        self.show_mainframe()

    def sonicmeasure_engine(self) -> None:
        self.figure.clear()

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
        self.pause_resume_button.pack(side=ttk.LEFT, padx=3, pady=3)
        self.restart_button.pack(side=ttk.LEFT, padx=3, pady=3)

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
    def __init__(self) -> None:
        pass
    