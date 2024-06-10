import ttkbootstrap as ttk
import tkinter as tk

from soniccontrol.interfaces.ui_component import UIComponent
from soniccontrol.sonicpackage.sonicamp_ import SonicAmp


class DeviceWindow(UIComponent):
    def __init__(self, device: SonicAmp, root):
        self._device = device
        self._view = DeviceWindowView(root)
        super().__init__(None, self._view)


class DeviceWindowView(tk.Toplevel):
    def __init__(self, root, *args, **kwargs) -> None:
        super().__init__(root, *args, **kwargs)
        self.title("Device Window")
        self.geometry('450x550')
        self.minsize(450, 400)