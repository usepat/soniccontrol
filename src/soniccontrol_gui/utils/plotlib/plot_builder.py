from soniccontrol_gui.utils.plotlib.plot import Plot

import matplotlib
import pandas as pd
import datetime


class PlotBuilder:
    # creates a timeplot for frequency, urms, irms and phase
    @staticmethod
    def create_timeplot_fuip(subplot: matplotlib.axes.Axes) -> Plot:
        plot = Plot(subplot, "timestamp", "Time")
        plot._plot.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M:%S"))
        
        plot.add_axis("frequency_axis", "Frequency / Hz")
        plot.add_axis("phase_axis", "Phase / °")
        plot.add_axis("urms_axis", "U$_{RMS}$ / mV")
        plot.add_axis("irms_axis", "I$_{RMS}$ / mA")
        
        plot.add_line(
            "frequency", 
            "frequency_axis",
            label="Frequency",
            color="black"
        )
        plot.add_line(
            "phase", 
            "phase_axis",
            label="Phase",
            color="green",
        )
        plot.add_line(
            "urms", 
            "urms_axis",
            label="Urms",
            color="blue",
        )
        plot.add_line(
            "irms", 
            "irms_axis",
            label="Irms",
            color="red",
        )

        plot.update_plot()
        plot.tight_layout()

        return plot

    # creates a spectralplot for urms, irms and phase
    @staticmethod
    def create_spectralplot_uip(subplot: matplotlib.axes.Axes) -> Plot:
        plot = Plot(subplot, "frequency", "Frequency / Hz")
        
        plot.add_axis("phase_axis", "Phase / °")
        plot.add_axis("urms_axis", "U$_{RMS}$ / mV")
        plot.add_axis("irms_axis", "I$_{RMS}$ / mA")
        
        plot.add_line(
            "phase", 
            "phase_axis",
            label="Phase",
            color="green",
        )
        plot.add_line(
            "urms", 
            "urms_axis",
            label="Urms",
            color="blue",
        )
        plot.add_line(
            "irms", 
            "irms_axis",
            label="Irms",
            color="red",
        )

        plot.update_plot()
        plot.tight_layout()

        return plot
