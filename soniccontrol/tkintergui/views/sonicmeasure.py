from typing import Dict, Optional
import matplotlib.figure
import pandas as pd
from soniccontrol.interfaces.ui_component import UIComponent
from soniccontrol.interfaces.view import TabView, View
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame
import matplotlib

from soniccontrol.sonicpackage.amp_data import Status
from soniccontrol.state_updater.capture import Capture
from soniccontrol.state_updater.updater import Updater
from soniccontrol.tkintergui.utils.events import EventManager
from soniccontrol.tkintergui.views.csv_table import CsvTable
matplotlib.use("TkAgg")

from soniccontrol.state_updater.data_provider import DataProvider
from soniccontrol.tkintergui.utils.constants import sizes, style, ui_labels
from soniccontrol.utils.files import images
from soniccontrol.tkintergui.utils.image_loader import ImageLoader
from soniccontrol.tkintergui.views.plotting import Plotting
from soniccontrol.utils.plotlib.plot_builder import PlotBuilder


class SonicMeasure(UIComponent):
    def __init__(self, parent: Optional[UIComponent]):
        self._capture = Capture()
        super().__init__(parent, SonicMeasureView(parent.view))

        self._figure = matplotlib.figure.Figure(dpi=100)
        self._subplot = self._figure.add_subplot(1, 1, 1)
        self._timeplot = PlotBuilder.create_timeplot_fuip(self._subplot)
        self._timeplottab = Plotting(self, self._timeplot)
        self._spectralplot = PlotBuilder.create_timeplot_fuip(self._subplot) # TODO: change this to spectral plot
        self._spectralplottab = Plotting(self, self._spectralplot)
        self._csv_table = CsvTable(self)

        self.view.set_capture_button_command(lambda: self._on_toogle_capture)
        self.view.add_tabs({
            ui_labels.LIVE_PLOT: self._timeplottab.view, 
            ui_labels.SONIC_MEASURE_LABEL: self._spectralplottab.view, 
            ui_labels.CSV_TAB_TITLE: self._csv_table.view
        })

        self._capture.data_provider.subscribe_property_listener("data", lambda e: self._timeplot.update_data(e.new_value))
        # self._capture.data_provider.subscribe_property_listener("data", lambda e: self._spectralplot.update_data(e.new_value))
        self._capture.data_provider.subscribe_property_listener("data", lambda e: self._csv_table.on_update_data(e))


        # TODO remove this, only for testing
        filepath = "./logs/status_log.csv"
        data = pd.read_csv(filepath)
        data["timestamp"] = pd.to_datetime(data["timestamp"])
        for row in data.itertuples():
            self._capture.data_provider.add_row(row._asdict())


    def on_status_update(self, status: Status):
        self._capture.on_update(status)

    def _on_toggle_capture(self):
        if self._capture.is_capturing:
            self._capture.end_capture()
            self._view.set_capture_button_label(ui_labels.START_CAPTURE)
        else:
            self._capture.start_capture()
            self._view.set_capture_button_label(ui_labels.END_CAPTURE)


class SonicMeasureView(TabView):
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
        return ImageLoader.load_image(images.LINECHART_ICON_BLACK, sizes.TAB_ICON_SIZE)
    
    @property
    def tab_title(self) -> str:
        return ui_labels.SONIC_MEASURE_LABEL


def main():    
    root = tk.Tk()
    measureView = SonicMeasureView(root)
    measureView.grid()
    root.mainloop()

if __name__ == "__main__":
    main()
