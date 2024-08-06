from pathlib import Path
from typing import Callable, Optional, Tuple
import ttkbootstrap as ttk
from enum import Enum

from soniccontrol.gui.view import View
from soniccontrol.gui.utils.image_loader import ImageLoader

class ButtonStyle(Enum):
    SUCCESS = "success.TButton"
    DANGER = "danger.TButton"

"""
    PushButtonView is only used, so that the presenter can directly change the style of the view,
    without touching the underlying gui framework (tkinter) directly. 
    So it is just a layer of abstraction. Will later come into a AbstractGuiFactory.
"""
class PushButtonView:
    def __init__(self, master: ttk.Frame, *args, **kwargs):
        self._button = ttk.Button(master, *args, **kwargs)

    def configure(self, 
        label: str="", 
        style: ButtonStyle=ButtonStyle.SUCCESS, 
        image: Optional[Tuple[Path, Tuple[int, int]]] = None, 
        command: Optional[Callable[[], None]] = None,
        enabled: Optional[bool] = None
    ):
        self._button.configure(text=label, style=style.value)
        if command:
            self._button.configure(command=command)
        if image:
            self._button.configure(image=ImageLoader.load_image(*image))
        if enabled is not None:
            self._button.configure(state=(ttk.NORMAL if enabled else ttk.DISABLED))

                