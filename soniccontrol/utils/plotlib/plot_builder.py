from soniccontrol.utils.plotlib.plot import Plot

import matplotlib

class PlotBuilder:
    # creates a timeplot for frequency, urms, irms and phase
    def create_timeplot_fuip(subplot: matplotlib.axes.Axes) -> Plot:
        plot = Plot(subplot, "timestamp", "Time")
        plot._plot.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M:%S"))
        plot.add_line(
            "frequency", 
            "Frequency / Hz",
            lw=2,
            marker="o",
            markersize=4,
            linestyle="-",
            label="Frequency",
            color="black"
        )
        plot.add_line(
            "phase", 
            "Phase / °",
            lw=2,
            marker="o",
            markersize=4,
            linestyle="-",
            label="Phase",
            color="green",
        )
        plot.add_line(
            "urms", 
            "U$_{RMS}$ / mV",
            lw=2,
            marker="o",
            markersize=4,
            linestyle="-",
            label="Urms",
            color="blue",
        )
        plot.add_line(
            "irms", 
            "I$_{RMS}$ / mA",
            lw=2,
            marker="o",
            markersize=4,
            linestyle="-",
            label="Irms",
            color="red",
        )
        plot.select_axis("frequency")
        plot.update_plot()
        return plot
