import logging
from typing import Dict, Optional
import matplotlib.figure
import pandas as pd
from soniccontrol_gui.ui_component import UIComponent
from soniccontrol_gui.view import TabView, View
import tkinter as tk
import ttkbootstrap as ttk
import matplotlib

from sonicpackage.amp_data import Status
from soniccontrol_gui.state_fetching.capture import Capture
from soniccontrol_gui.views.measure.csv_table import CsvTable
matplotlib.use("TkAgg")

from soniccontrol_gui.constants import sizes, ui_labels
from soniccontrol_gui.resources import images
from soniccontrol_gui.utils.image_loader import ImageLoader
from soniccontrol_gui.views.measure.plotting import Plotting
from soniccontrol_gui.utils.plotlib.plot_builder import PlotBuilder


class Measuring(UIComponent):
    def __init__(self, parent: UIComponent):
        self._logger = logging.getLogger(parent.logger.name + "." + Measuring.__name__)

        self._logger.debug("Create SonicMeasure")
        self._capture = Capture(self._logger) # TODO: move this to device window
        self._view = MeasuringView(parent.view)
        super().__init__(parent, self._view, self._logger)

        self._time_figure = matplotlib.figure.Figure(dpi=100)
        self._time_subplot = self._time_figure.add_subplot(1, 1, 1)
        self._timeplot = PlotBuilder.create_timeplot_fuip(self._time_subplot)
        self._timeplottab = Plotting(self, self._timeplot)

        self._spectral_figure = matplotlib.figure.Figure(dpi=100)
        self._spectral_subplot = self._spectral_figure.add_subplot(1, 1, 1)
        self._spectralplot = PlotBuilder.create_spectralplot_uip(self._spectral_subplot)
        self._spectralplottab = Plotting(self, self._spectralplot)
        
        self._csv_table = CsvTable(self)

        self._view.set_capture_button_command(lambda: self._on_toggle_capture())
        self._view.set_capture_button_label(ui_labels.START_CAPTURE)
        self._view.add_tabs({
            ui_labels.LIVE_PLOT: self._timeplottab.view, 
            ui_labels.SONIC_MEASURE_LABEL: self._spectralplottab.view, 
            ui_labels.CSV_TAB_TITLE: self._csv_table.view
        })

        self._capture.data_provider.subscribe_property_listener("data", lambda e: self._timeplot.update_data(e.new_value))
        self._capture.data_provider.subscribe_property_listener("data", lambda e: self._spectralplot.update_data(e.new_value))
        self._capture.data_provider.subscribe_property_listener("data", lambda e: self._csv_table.on_update_data(e))

    def on_status_update(self, status: Status):
        self._capture.on_update(status)

    def _on_toggle_capture(self):
        if self._capture.is_capturing:
            self._capture.end_capture()
            self._view.set_capture_button_label(ui_labels.START_CAPTURE)
        else:
            self._capture.start_capture()
            self._view.set_capture_button_label(ui_labels.END_CAPTURE)


class MeasuringView(TabView):
    def __init__(self, master: ttk.Window, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)

    def _initialize_children(self) -> None:
        self._main_frame: ttk.Frame = ttk.Frame(self)
        
        self._capture_frame: ttk.Frame = ttk.Frame(self._main_frame)
        self._capture_btn_text = tk.StringVar()
        self._capture_btn: ttk.Button = ttk.Button(
            self._capture_frame,
            textvariable=self._capture_btn_text
        )

        self._notebook: ttk.Notebook = ttk.Notebook(self._main_frame)

    def _initialize_publish(self) -> None:
        self._main_frame.pack(expand=True, fill=ttk.BOTH)
        
        self._capture_frame.pack(fill=ttk.X, padx=3, pady=3)
        self._capture_btn.grid(row=0, column=0, padx=sizes.SMALL_PADDING)

        self._notebook.pack(expand=True, fill=ttk.BOTH)

    def add_tabs(self, tabs: Dict[str, View]) -> None:
        for (title, tabview) in tabs.items():
            self._notebook.add(tabview, text=title)

    def set_capture_button_label(self, label: str):
        self._capture_btn_text.set(label)

    def set_capture_button_command(self, command):
        self._capture_btn.configure(command=command)

    @property
    def image(self) -> ttk.ImageTk.PhotoImage:
        return ImageLoader.load_image_resource(images.LINECHART_ICON_BLACK, sizes.TAB_ICON_SIZE)
    
    @property
    def tab_title(self) -> str:
        return ui_labels.SONIC_MEASURE_LABEL


def main():    
    root = tk.Tk()
    measureView = MeasuringView(root) #type: ignore
    measureView.grid()
    root.mainloop()

if __name__ == "__main__":
    main()
