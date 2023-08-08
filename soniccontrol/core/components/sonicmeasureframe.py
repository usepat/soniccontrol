import logging
from typing import Iterable, Any
import ttkbootstrap as ttk
import pandas as pd
from ttkbootstrap.scrolled import ScrolledText
import matplotlib

matplotlib.use("TkAgg")

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.animation import FuncAnimation

import PIL
from PIL.ImageTk import PhotoImage
import soniccontrol.constants as const
from soniccontrol.interfaces import RootChild, Layout, Connectable, Updatable
from soniccontrol.interfaces.rootchild import RootChildFrame

logger = logging.getLogger(__name__)


class SonicMeasureFrame(RootChildFrame, Connectable, Updatable):
    def __init__(
        self, parent_frame: ttk.Frame, tab_title: str, image: PIL.Image, *args, **kwargs
    ):
        super().__init__(parent_frame, tab_title, image, *args, **kwargs)
        #     self._width_layouts: Iterable[Layout] = ()
        #     self._height_layouts: Iterable[Layout] = ()
        self.configure(width=200)

        self.last_read_line = 0

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

        self.main_frame: ttk.Frame = ttk.Frame(self)
        self.button_frame: ttk.Frame = ttk.Frame(self.main_frame)
        self.pause_resume_button: ttk.Button = ttk.Button(
            self.button_frame,
            text="Pause",
            bootstyle=ttk.DANGER,
            image=self.stop_image,
            compound=ttk.RIGHT,
            command=lambda event: self.event_generate(const.Events.PAUSE_SONICMEASURE),
        )
        self.restart_button: ttk.Button = ttk.Button(
            self.button_frame,
            text="Restart",
            bootstyle="info",
            image=self.restart_image,
            compound=ttk.RIGHT,
            command=self.restart_sonicmeasure,
        )

        self.plot_frame: ttk.Frame = ttk.Frame(self.main_frame)
        self.figure: Figure = Figure(figsize=(4, 3), dpi=100)
        self.figure_canvas: FigureCanvasTkAgg = FigureCanvasTkAgg(
            self.figure, self.plot_frame
        )
        NavigationToolbar2Tk(self.figure_canvas, self.plot_frame)

        self.configuration_frame: ttk.Frame = ttk.Frame(self)
        self.navigation_bar: ttk.Frame = ttk.Frame(self.configuration_frame)
        self.back_button: ttk.Button = ttk.Button(
            self.navigation_bar,
            text="Back",
            bootstyle=ttk.DARK,
            image=self.back_image,
            compound=ttk.LEFT,
            command=self.show_mainframe,
        )
        self.submit_button: ttk.Button = ttk.Button(
            self.navigation_bar,
            text="Start Sonicmeasure",
            bootstyle=ttk.SUCCESS,
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
            bootstyle=ttk.SECONDARY,
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

    def restart_sonicmeasure(self) -> None:
        self.main_frame.pack_forget()
        self.configuration_frame.pack(padx=15)

    def start_sonicmeasure(self) -> None:
        self.sonicmeasure_engine()
        self.show_mainframe()

    def sonicmeasure_engine(self) -> None:
        self.figure.clear()
        self.ax1 = self.figure.add_subplot(1, 1, 1)  # Main axis for frequency
        self.ax2 = self.ax1.twinx()  # Secondary axis for urms
        self.ax3 = self.ax1.twinx()  # Tertiary axis for irms
        self.ax3.spines["right"].set_position(
            ("outward", 60)
        )  # Move tertiary axis to the right

        (self.line1,) = self.ax1.plot([], [], lw=2, label="Frequency")
        (self.line2,) = self.ax2.plot([], [], lw=2, label="Urms", color="red")
        (self.line3,) = self.ax3.plot([], [], lw=2, label="Irms", color="green")

        self.xdata = []
        self.ydata_phase = []
        self.ydata_urms = []
        self.ydata_irms = []

        def init():
            self.line1.set_data([], [])
            self.line2.set_data([], [])
            self.line3.set_data([], [])
            return (
                self.line1,
                self.line2,
                self.line3,
            )

        self.ani = FuncAnimation(
            self.figure, self.update_graph, init_func=init, blit=True, interval=1000
        )  # 100ms interval
        self.figure_canvas.draw()

    def update_graph(self, frame) -> None:
        data = pd.read_csv(
            self.root.status_log_filepath, skiprows=range(1, self.last_read_line)
        )
        # Update last_read_line
        self.last_read_line += len(data)
        data["timestamp"] = pd.to_datetime(data["timestamp"])
        # Append new data to existing data
        self.xdata += data["timestamp"].tolist()
        self.ydata_phase += data["phase"].tolist()
        self.ydata_urms += data["urms"].tolist()
        self.ydata_irms += data["irms"].tolist()

        self.line1.set_data(self.xdata, self.ydata_phase)
        self.line2.set_data(self.xdata, self.ydata_urms)
        self.line3.set_data(self.xdata, self.ydata_irms)

        self.ax1.relim()  # Recalculate limits
        self.ax1.autoscale_view()  # Autoscale
        self.ax2.relim()
        self.ax2.autoscale_view()
        self.ax3.relim()
        self.ax3.autoscale_view()

        return (
            self.line1,
            self.line2,
            self.line3,
        )

    def show_mainframe(self) -> None:
        self.configuration_frame.pack_forget()
        self.main_frame.pack(fill=ttk.BOTH)

    def publish(self) -> None:
        self.main_frame.pack(fill=ttk.BOTH, padx=3, pady=3)

        self.button_frame.pack(fill=ttk.X, padx=3, pady=3)
        self.pause_resume_button.pack(side=ttk.LEFT, padx=3, pady=3)
        self.restart_button.pack(side=ttk.LEFT, padx=3, pady=3)

        self.plot_frame.pack(padx=3, pady=3)
        self.figure_canvas.get_tk_widget().pack(fill=ttk.BOTH)

        self.navigation_bar.pack(pady=5, fill=ttk.X)
        self.back_button.pack(pady=5, side=ttk.LEFT)
        self.submit_button.pack(pady=5, side=ttk.RIGHT)

        self.logfile_specifier_frame.pack(pady=10, fill=ttk.X)
        self.logfile_entry.pack(side=ttk.LEFT, fill=ttk.X, padx=5, pady=5, expand=True)
        self.browse_files_button.pack(side=ttk.RIGHT, fill=ttk.X, padx=5, pady=5)

        self.comment_frame.pack(pady=5)
        self.comment_entry.pack(padx=5, pady=5)
