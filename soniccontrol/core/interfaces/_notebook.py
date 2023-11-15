from soniccontrol.core.interfaces.gui_interfaces import Resizable
import ttkbootstrap as ttk


class RootNotebook(ttk.Noebook, Resizable):
    def __init__(self) -> None:
        super().__init__()
