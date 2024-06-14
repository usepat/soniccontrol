from soniccontrol.interfaces.mvc_command import MvcCommand
from soniccontrol.interfaces.ui_component import UIComponent
from soniccontrol.interfaces.view import View

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from typing import Callable, Dict

from soniccontrol.tkintergui.utils.constants import _Style, _UIStringsEN, sizes, ui_labels
from soniccontrol.tkintergui.utils.events import PropertyChangeEvent
from soniccontrol.utils.plotlib.plot import Plot



class SavePlotCommand(MvcCommand):
    def __init__(self, target, source = None):
        super().__init__(target, source)

    def can_execute(self) -> bool:
        return isinstance(self.target,  Figure)

    async def execute(self) -> None:
        filetypes = [("PNG File", "*.png")]
        fileHandle = tk.filedialog.asksaveasfilename(
            defaultextension=".png", filetypes=filetypes
        )
        if fileHandle:
            self.target.savefig(fileHandle)


class Plotting(UIComponent):
    def __init__(self, parent: UIComponent, plot: Plot):
        self._plot = plot
        self._figure: Figure = plot.plot.get_figure()
        self._saveCommand = SavePlotCommand(self._figure)
        super().__init__(parent, PlottingView(parent.view, self._figure))

        for (attrName, line) in self._plot.lines.items():
            self.view.add_line(attrName, line.get_label(), self.create_toggle_line_callback(attrName))
        self.view.on_plot_changed()
        
        self.view.set_save_button_command(self._saveCommand)

        self._plot.subscribe_property_listener("plot", lambda _: self.view.on_plot_changed())

    def create_toggle_line_callback(self, attrName: str):
            def toggle_line():
                is_visible = self.view.get_line_visibility(attrName)
                self._plot.toggle_line(attrName, is_visible)
            return toggle_line


class PlottingView(View):
    def __init__(self, master: tk.Widget, _figure: Figure, *args, **kwargs) -> None:
        self._figure = _figure
        super().__init__(master, *args, **kwargs)


    def _initialize_children(self) -> None:
        

        self._main_frame: ScrolledFrame = ScrolledFrame(self, autohide=True)
        self._plot_frame: ttk.Frame = ttk.Frame(self._main_frame)
        self._figure_canvas: FigureCanvasTkAgg = FigureCanvasTkAgg(
            self._figure, self._plot_frame
        )
        self._toggle_button_frame: ttk.Frame = ttk.Frame(self)
        self._line_toggle_buttons: Dict[str, ttk.Button] = {}
        self._line_visibilities: Dict[str, tk.BooleanVar] = {}
        self._save_button: ttk.Button = ttk.Button(
            self._toggle_button_frame, 
            text=ui_labels.SAVE_PLOT_LABEL, 
        )
        
        self._figure_canvas.draw()


    def _initialize_publish(self) -> None:
        self._main_frame.pack(expand=True, fill=ttk.BOTH, padx=3, pady=3)
        self._plot_frame.pack(padx=3, pady=3)
        self._figure_canvas.get_tk_widget().pack(fill=ttk.BOTH, expand=True)

        self._toggle_button_frame.pack(fill=ttk.X, padx=3, pady=3)
        for (i, toggle_button) in enumerate(self._line_toggle_buttons.values()):
            toggle_button.grid(row=0, column=i, padx=sizes.SMALL_PADDING)
        self._save_button.grid(row=0, column=len(self._line_toggle_buttons), padx=sizes.SMALL_PADDING)


    def on_plot_changed(self):
        self._figure_canvas.draw()
        self._figure_canvas.flush_events()

    def get_line_visiblity(self, attrName: str) -> bool:
        return self._line_visibilities[attrName].get()

    def add_line(self, attrName: str, line_label: str, toggle_command: Callable[[None], None]) -> None:
        self._line_visibilities[attrName] = tk.BooleanVar(value=True)
        toggle_button = ttk.Checkbutton(
            self._toggle_button_frame, 
            text=line_label, 
            variable=self._line_visibilities[attrName],
            command=toggle_command
        )
        self._line_toggle_buttons[attrName] = toggle_button

    def set_save_button_command(self, command: Callable[[None], None]) -> None:
        self._save_button.configure(command=command)
