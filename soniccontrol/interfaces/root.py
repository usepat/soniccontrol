from typing import Any, Optional, Iterable, Set
import tkinter as tk
import ttkbootstrap as ttk
import abc
import logging
import soniccontrol.constants as const
from soniccontrol.interfaces.gui_interfaces import Resizable, Updatable
from soniccontrol.interfaces.resizer import Resizer
from soniccontrol.interfaces.layout import Layout

logger = logging.getLogger(__name__)


class Root(tk.Tk, Resizable, Updatable):
    def __init__(self) -> None:
        super().__init__()
        self._width_layouts: Optional[Iterable[Layout]] = None
        self._height_layouts: Optional[Iterable[Layout]] = None
        self._resizer: Resizer = Resizer(self)

        # (glabal read) tkinter variables
        self.frequency: ttk.IntVar = ttk.IntVar(value=1000)
        self.frequency_text: ttk.StringVar = ttk.StringVar()
        self.frequency.trace(ttk.W, self.on_frequency_change)

        self.gain: ttk.IntVar = ttk.IntVar(value=100)
        self.gain_text: ttk.StringVar = ttk.StringVar()
        self.gain.trace(ttk.W, self.on_gain_change)

        self.temperature: ttk.IntVar = ttk.IntVar(value=23.5)
        self.temperature_text: ttk.IntVar = ttk.StringVar()
        self.temperature.trace(ttk.W, self.on_temperature_change)

        self.urms: ttk.IntVar = ttk.IntVar(value=1003)
        self.urms_text: ttk.IntVar = ttk.StringVar()
        self.urms.trace(ttk.W, self.on_urms_change)

        self.irms: ttk.IntVar = ttk.IntVar(value=134)
        self.irms_text: ttk.IntVar = ttk.StringVar()
        self.irms.trace(ttk.W, self.on_irms_change)

        self.phase: ttk.IntVar = ttk.IntVar(value=75)
        self.phase_text: ttk.IntVar = ttk.StringVar()
        self.phase.trace(ttk.W, self.on_phase_change)

        self.mode: ttk.StringVar = ttk.StringVar(value="Catch")
        self.soniccontrol_state: ttk.StringVar = ttk.StringVar(value="Manual")
        self.port: ttk.StringVar = ttk.StringVar()
        self.connection_status: ttk.StringVar = ttk.StringVar()

        logger.debug("initialized Root")

    @property
    def resizer(self) -> Resizer:
        return self._resizer

    @property
    def width_layouts(self) -> Iterable[Layout]:
        return self._width_layouts

    @property
    def height_layouts(self) -> Iterable[Layout]:
        return self._height_layouts

    def bind_events(self) -> None:
        self.bind(const.Events.RESIZING, self.on_resizing)

    def on_resizing(self, event: Any, *args, **kwargs) -> None:
        return self.resizer.resize(event=event)

    def on_update(self, event: Any = None, *args, **kwargs) -> None:
        pass

    def on_frequency_change(self, event: Any = None, *args, **kwargs) -> None:
        self.frequency_text.set(f"Freq.: {self.frequency.get()} kHz")

    def on_gain_change(self, event: Any = None, *args, **kwargs) -> None:
        self.gain_text.set(f"Gain: {self.gain.get()} %")

    def on_temperature_change(self, event: Any = None, *args, **kwargs) -> None:
        self.temperature_text.set(f"Temp.: {self.temperature.get()} °C")

    def on_urms_change(self, event: Any = None, *args, **kwargs) -> None:
        self.urms_text.set(f"Urms: {self.urms.get()} mV")

    def on_irms_change(self, event: Any = None, *args, **kwargs) -> None:
        self.irms_text.set(f"Irms: {self.irms.get()} mA")

    def on_phase_change(self, event: Any = None, *args, **kwargs) -> None:
        self.phase_text.set(f"Phase: {self.phase.get()} °")

    def on_mode_change(self, event: Any = None, *args, **kwargs) -> None:
        pass
