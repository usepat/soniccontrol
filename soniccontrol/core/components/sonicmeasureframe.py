import logging
from typing import Iterable
import ttkbootstrap as ttk
import PIL
from soniccontrol.interfaces import RootChild, Layout

logger = logging.getLogger(__name__)


class SonicMeasureFrame(RootChild):
    def __init__(
        self, parent_frame: ttk.Frame, tab_title: str, image: PIL.Image, *args, **kwargs
    ):
        super().__init__(parent_frame, tab_title, image, *args, **kwargs)
    #     self._width_layouts: Iterable[Layout] = ()
    #     self._height_layouts: Iterable[Layout] = ()