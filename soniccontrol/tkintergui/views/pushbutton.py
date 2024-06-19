from typing import Callable, Optional, Tuple
import ttkbootstrap as ttk
from enum import Enum

from soniccontrol.tkintergui.utils.image_loader import ImageLoader

class ButtonStyle(Enum):
    SUCCESS = "success.TButton"
    DANGER = "danger.TButton"


class PushButtonView:
    def __init__(self, master: any, *args, **kwargs):
        self._button = ttk.Button(master, *args, **kwargs)

    def configure(self, 
        label: str="", 
        style: ButtonStyle=ButtonStyle.SUCCESS, 
        image: Optional[Tuple[str, Tuple[int, int]]] = None, 
        command: Optional[Callable[[None], None]] = None,
        enabled: Optional[bool] = None
    ):
        self._button.configure(text=label, style=style.value)
        if command:
            self._button.configure(command=command)
        if image:
            self._button.configure(image=ImageLoader.load_image(*image))
        if enabled is not None:
            self._button.configure(state=(ttk.NORMAL if enabled else ttk.DISABLED))

                