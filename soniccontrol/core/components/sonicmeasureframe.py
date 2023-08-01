import logging
from typing import Iterable
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledText
import matplotlib

matplotlib.use('TkAgg')

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)


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
        self.start_image: PhotoImage = PhotoImage(const.PLAY_RAW_IMG)
        self.stop_image: PhotoImage = PhotoImage(const.PAUSE_RAW_IMG)
        self.restart_image: PhotoImage = PhotoImage(const.REFRESH_RAW_IMG)
        
        self.main_frame: ttk.Frame = ttk.Frame(self)
        self.button_frame: ttk.Frame = ttk.Frame(self.main_frame)
        self.pause_resume_button: ttk.Button = ttk.Button(
            self.button_frame,
            text='Pause',
            bootstyle=ttk.DANGER,
            image=self.stop_image,
            compound=ttk.RIGHT,
            command=lambda event: self.event_generate(const.Events.PAUSE_SONICMEASURE)
        )
        self.restart_button: ttk.Button = ttk.Button(
            self.button_frame,
            text='Restart',
            bootstyle='info',
            image=self.restart_image,
            compound=ttk.RIGHT,
            command=self.restart_sonicmeasure
        )
        
        self.plot_frame: ttk.Frame = ttk.Frame(self.main_frame)
        self.figure: Figure = Figure(figsize=(6,4), dpi=100)
        self.figure_canvas: FigureCanvasTkAgg = FigureCanvasTkAgg(self.figure, self.plot_frame)
        NavigationToolbar2Tk(self.figure_canvas, self.plot_frame)
        
        self.configuration_frame: ttk.Frame = ttk.Frame(self)
        self.navigation_bar: ttk.Frame = ttk.Frame(self.configuration_frame)
        self.back_button: ttk.Button = ttk.Button(
            self.navigation_bar,
            text='Back',
            bootstyle=ttk.DARK,
            command=self.show_mainframe,
        )
        self.submit_button: ttk.Button = ttk.Button(
            self.navigation_bar,
            text='Start Sonicmeasure',
            bootstyle=ttk.SUCCESS,
            command=self.start_sonicmeasure,
        )
        
        self.logfile_specifier_frame: ttk.Labelframe = ttk.Labelframe(self.configuration_frame, text='Specify the filepath for the data storage')
        self.logfile_entry: ttk.Entry = ttk.Entry(self.logfile_specifier_frame)
        self.browse_files_button: ttk.Button = ttk.Button(
            self.logfile_specifier_frame,
            text='Browse files...',
            bootstyle=ttk.SECONDARY,
            command=self.open_log_file,
        )
        self.comment_frame: ttk.Labelframe = ttk.Labelframe(self.configuration_frame, text='Make a comment on your data')
        self.comment_entry: ttk.ScrolledText = ttk.ScrolledText(self.comment_frame)
        
        self.bind_events()    
    
    def on_connect(self, event=None) -> None:
        return self.publish()
    
    def on_update(self, event=None) -> None:
        pass
    
    def open_log_file(self, event=None) -> None:
        pass
    
    def restart_sonicmeasure(self) -> None:
        self.main_frame.pack_forget()
        self.configuration_frame.pack(expand=True, padx=15)
        
    def start_sonicmeasure(self) -> None:
        self.show_mainframe()
        
    def show_mainframe(self) -> None:
        self.configuration_frame.pack_forget()
        self.main_frame.pack(expand=True, fill=ttk.BOTH)
    
    def publish(self) -> None:
        self.main_frame.pack(expand=True, fill=ttk.BOTH, padx=3, pady=3)
        
        self.button_frame.pack(fill=ttk.X, padx=3, pady=3)
        self.pause_resume_button.pack(side=ttk.LEFT, padx=3, pady=3)
        self.restart_button.pack(side=ttk.LEFT, padx=3, pady=3)
        
        self.plot_frame.pack(expand=True, fill=ttk.BOTH, padx=3, pady=3)
        self.figure_canvas.get_tk_widget().pack(expand=True, fill=ttk.BOTH)
        
        self.navigation_bar.pack(pady=5, fill=ttk.X)
        self.back_button.pack( pady=5, side=ttk.LEFT)
        self.submit_button.pack( pady=5, side=ttk.RIGHT)
        
        self.logfile_specifier_frame.pack(pady=10, fill=ttk.X)
        self.logfile_entry.pack(side=ttk.LEFT, fill=ttk.X, padx=5, pady=5)
        self.browse_files_button.pack(side=ttk.RIGHT, fill=ttk.X, padx=5, pady=5)
        
        self.comment_frame.pack(pady=5)
        self.comment_entry.pack(padx=5, pady=5)
        