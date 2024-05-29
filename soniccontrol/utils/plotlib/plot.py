import matplotlib
import pandas as pd

from typing import Dict, Optional

from soniccontrol.tkintergui.utils.events import Event, EventManager, PropertyChangeEvent


class Plot:
    def __init__(self, subplot: matplotlib.axes.Axes, dataAttrNameXAxis: str, xlabel: str):
        super()
        self._plot: matplotlib.axes.Axes = subplot
        self._plot.set_xlabel(xlabel)
        self._dataAttrNameXAxis = dataAttrNameXAxis
        self._lines: Dict[str, matplotlib.lines.Line2D] = {}
        self._axes: Dict[str, matplotlib.axes.Axes] = {}
        self._plot.legend(
            loc="upper left",
            handles=[]
        )
        self._selectedAxis: Optional[matplotlib.axes.Axes] = None
        self._eventManager = EventManager()
        self._lineDefaultStyle: dict = {
            "lw": 2,
            "marker": "o",
            "markersize": 4,
            "linestyle": "-",
            "color": "blue"
        }

    @property
    def plot(self) -> matplotlib.axes.Axes:
        return self._plot
    
    @property
    def lines(self) -> matplotlib.lines.Line2D:
        return self._lines
    
    @property
    def eventManager(self) -> EventManager:
        return self._eventManager

    @property
    def lineDefaultStyle(self) -> dict:
        return self._lineDefaultStyle
    
    @lineDefaultStyle.setter
    def lineDefaultStyle(self, value) -> None:
        self._lineDefaultStyle = value


    def add_line(self, dataAttrName: str, ylabel: str, **kwargs):
        if dataAttrName in self._lines:
            raise KeyError("There already exists a line for this attribute")
        
        ax = self._plot.twinx()
        ax.set_ylabel(ylabel)
        ax.get_yaxis().set_visible(False)
        ax.spines['right'].set_color('none')
        
        linekwargs = self.lineDefaultStyle.copy()
        linekwargs.update(**kwargs)
        (line, ) = ax.plot([], [], **linekwargs)

        self._axes[dataAttrName] = ax
        self._lines[dataAttrName] = line
        handles, _ = ax.get_legend_handles_labels()
        handles.append(line)
        self._plot.legend(handles=handles)


    def toggle_line(self, dataAttrName: str, isVisible: bool):
        self._lines[dataAttrName].set_visible(isVisible)
        self.eventManager.emit(PropertyChangeEvent("plot", self._plot, self._plot))


    def select_axis(self, dataAttrName: str):
        if dataAttrName not in self._lines:
            raise KeyError("There exists no line for this data attribute")
        
        self._selectedAxis = self._axes[dataAttrName]
        self.eventManager.emit(PropertyChangeEvent("plot", self._plot, self._plot))


    def update_plot(self):
        for _, axis in self._axes.items():
            axis.relim()
            axis.autoscale_view()

        if self._selectedAxis:
            self._plot.set_ylabel(self._selectedAxis.get_ylabel())
            self._plot.set_yticks(self._selectedAxis.get_yticks())
        else:
            self._plot.set_ylabel("")
           

    def update_data(self, data: pd.DataFrame):
        for attrName, line in self._lines.items():
            line.set_data(data[self._dataAttrNameXAxis], data[attrName])
        self.update_plot()
        self.eventManager.emit(PropertyChangeEvent("plot", self._plot, self._plot))

