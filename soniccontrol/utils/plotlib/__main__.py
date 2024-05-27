import matplotlib.figure
from soniccontrol.utils.plotlib.plot import Plot
from soniccontrol.utils.plotlib.plot_builder import PlotBuilder 

import pandas as pd
import tkinter as tk
import matplotlib
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
    plot.update_plot()

    root = tk.Tk()
    tkagg_canvas = FigureCanvasTkAgg(figure, master=root)
    tkagg_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    tkagg_canvas.draw()
    root.mainloop()


if __name__ == "__main__":
    main()
