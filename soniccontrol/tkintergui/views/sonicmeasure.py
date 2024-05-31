import matplotlib.figure
import pandas as pd
from soniccontrol.interfaces.view import TabView, View
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame
import matplotlib
matplotlib.use("TkAgg")

from soniccontrol.state_updater.DataProvider import DataProvider
from soniccontrol.tkintergui.utils.constants import sizes, style, ui_labels
from soniccontrol.utils.files import images
from soniccontrol.tkintergui.utils.image_loader import ImageLoader
from soniccontrol.tkintergui.views.plot_view import PlotView, PlotViewModel
from soniccontrol.utils.plotlib.plot_builder import PlotBuilder


class SonicMeasureViewModel:
    def __init__(self, dataProvider: DataProvider):
        self._dataProvider = dataProvider

    @property
    def dataProvider(self):
        return self._dataProvider


class SonicMeasureView(TabView):
    def __init__(self, master: ttk.Window, *args, **kwargs) -> None:
        # TODO pass viewmodel over args
        # TODO remove this, only for testing
        filepath = "./logs/status_log.csv"
        data = pd.read_csv(filepath)
        data["timestamp"] = pd.to_datetime(data["timestamp"])
        self._vm = SonicMeasureViewModel(DataProvider())
        for row in data.itertuples():
            self._vm.dataProvider.add_row(row._asdict())

        super().__init__(master, *args, **kwargs)
        self._vm.dataProvider._eventManager.subscribe_property_listener("data", lambda e: self._timeplot.update_data(e.new_value))
        self._vm.dataProvider._eventManager.subscribe_property_listener("data", lambda e: self._spectralplot.update_data(e.new_value))


    def _initialize_children(self) -> None:
        self._main_frame: ttk.Frame = ttk.Frame(self)
        self._notebook: ttk.Notebook = ttk.Notebook(self._main_frame)

        self._figure = matplotlib.figure.Figure(dpi=100)
        self._subplot = self._figure.add_subplot(1, 1, 1)

        self._timeplot = PlotBuilder.create_timeplot_fuip(self._subplot)
        self._timeplot_frame: PlotView = PlotView(self._main_frame, PlotViewModel(self._timeplot))

        self._spectralplot = PlotBuilder.create_timeplot_fuip(self._subplot) # TODO: change this to spectral plot
        self._spectralplot_frame: PlotView = PlotView(self._main_frame, PlotViewModel(self._spectralplot))


    def _initialize_publish(self) -> None:
        self._main_frame.pack(expand=True, fill=ttk.BOTH)
        self._notebook.pack(expand=True, fill=ttk.BOTH)
        self._notebook.add(self._timeplot_frame, text=ui_labels.LIVE_PLOT)
        self._notebook.add(self._spectralplot_frame, text=ui_labels.SONIC_MEASURE_LABEL)


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
