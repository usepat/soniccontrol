from typing import Callable
from soniccontrol_gui.ui_component import UIComponent
from soniccontrol_gui.view import View
import ttkbootstrap as ttk

class SonicMeasure(UIComponent):
    def __init__(self, parent: UIComponent, parent_view: View):
        pass


class SonicMeasureView(View):
    def __init__(self, master: View, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)

    def _initialize_children(self) -> None:
        pass

    def _initialize_publish(self) -> None:
        pass

    @property
    def ramp_frame(self) -> ttk.Frame:
        raise NotImplementedError()
    
    def set_start_button_command(self, command: Callable[[], None]) -> None:
        pass

    def set_stop_button_command(self, command: Callable[[], None]) -> None:
        pass

    def enable_start_button_command(self, enabled: bool) -> None:
        pass

    def enable_stop_button_command(self, enabled: bool) -> None:
        pass
