from soniccontrol.utils.plotlib.plot import Plot

import matplotlib
import pandas as pd
import datetime


class PlotBuilder:
    # creates a timeplot for frequency, urms, irms and phase
    @staticmethod
    def create_timeplot_fuip(subplot: matplotlib.axes.Axes) -> Plot:
        plot = Plot(subplot, "timestamp", "Time")
        plot._plot.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M:%S"))
        plot.add_line(
            "frequency", 
            "Frequency / Hz",
            label="Frequency",
            color="black"
        )
        plot.add_line(
            "phase", 
            "Phase / °",
            label="Phase",
            color="green",
        )
        plot.add_line(
            "urms", 
            "U$_{RMS}$ / mV",
            label="Urms",
            color="blue",
        )
        plot.add_line(
            "irms", 
            "I$_{RMS}$ / mA",
            label="Irms",
            color="red",
        )
        plot.select_axis("frequency")
        plot.update_plot()
        return plot
