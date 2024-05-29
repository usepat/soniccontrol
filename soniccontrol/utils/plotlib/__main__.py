import matplotlib.figure
from soniccontrol.tkintergui.views.plot_view import PlotView, PlotViewModel
from soniccontrol.utils.plotlib.plot import Plot
from soniccontrol.utils.plotlib.plot_builder import PlotBuilder 

import pandas as pd
import tkinter as tk
import matplotlib
import threading

from soniccontrol.utils.plotlib.plotly_server import DataProvider, LiveTableFactory, PlotlyServer
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def main():    
    figure = matplotlib.figure.Figure(dpi=100)
    subplot = figure.add_subplot(1, 1, 1)
    plot = PlotBuilder.create_timeplot_fuip(subplot)

    filepath = "./logs/status_log.csv"
    data = pd.read_csv(filepath)
    data["timestamp"] = pd.to_datetime(data["timestamp"])
    plot.update_data(data)

    root = tk.Tk()
    plotViewModel = PlotViewModel(plot)
    plotView = PlotView(root, plotViewModel)
    plotView.grid()
    root.mainloop()


def main_plotly():
    filepath = "./logs/status_log.csv"
    data = pd.read_csv(filepath)
    data["timestamp"] = pd.to_datetime(data["timestamp"])
    dataProvider = DataProvider()
    dataProvider.data = data

    server = PlotlyServer()
    server.add_page("/table", LiveTableFactory(dataProvider))

    server_thread = threading.Thread(target=lambda: server.run())
    server_thread.daemon = True
    server_thread.start()
    
    root = tk.Tk()
    
    root.mainloop()


if __name__ == "__main__":
    main_plotly()
