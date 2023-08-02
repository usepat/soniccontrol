import PIL
import logging
from typing import Iterable, Optional, TYPE_CHECKING, Set, Any
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame
from PIL.ImageTk import PhotoImage
from soniccontrol.interfaces.layout import Layout
import soniccontrol.constants as const
from soniccontrol.interfaces.root import Root
from soniccontrol.interfaces.gui_interfaces import Resizable
from soniccontrol.interfaces.resizer import Resizer

logger = logging.getLogger(__name__)


class RootChild(ScrolledFrame, Resizable):
    def __init__(
        self, parent_frame: Root, tab_title: str, image: PIL.Image, 
        autohide: bool = True,
        *args, **kwargs
    ) -> None:
        super().__init__(master=parent_frame, autohide=autohide, *args, **kwargs)
        self._width_layouts: Optional[Iterable[Layout]] = None
        self._height_layouts: Optional[Iterable[Layout]] = None
        self._tab_title: str = tab_title
        self._image: PhotoImage = image
        self._resizer: Resizer = Resizer(self)
        self.root: Root = parent_frame

        logger.debug('RootChild initialized')

    @property
    def resizer(self) -> Resizer:
        return self._resizer
    
    @property
    def width_layouts(self) -> Iterable[Layout]:
        return self._width_layouts
    
    @property
    def height_layouts(self) -> Iterable[Layout]:
        return self._height_layouts

    @property
    def tab_title(self) -> str:
        return self._tab_title

    @property
    def image(self) -> PhotoImage:
        return self._image
    
    def bind_events(self) -> None:
        self.bind(const.Events.RESIZING, self.on_resizing)

    def on_resizing(self, event: Any) -> None:
        return self.resizer.resize(event=event)
    

class RootChildFrame(ttk.Frame, Resizable):
    def __init__(
        self, parent_frame: Root, tab_title: str, image: PIL.Image, 
        *args, **kwargs
    ) -> None:
        super().__init__(master=parent_frame, *args, **kwargs)
        self._width_layouts: Optional[Iterable[Layout]] = None
        self._height_layouts: Optional[Iterable[Layout]] = None
        self._tab_title: str = tab_title
        self._image: PhotoImage = image
        self._resizer: Resizer = Resizer(self)
        self.root: Root = parent_frame

        logger.debug('RootChild initialized')

    @property
    def resizer(self) -> Resizer:
        return self._resizer
    
    @property
    def width_layouts(self) -> Iterable[Layout]:
        return self._width_layouts
    
    @property
    def height_layouts(self) -> Iterable[Layout]:
        return self._height_layouts

    @property
    def tab_title(self) -> str:
        return self._tab_title

    @property
    def image(self) -> PhotoImage:
        return self._image
    
    def bind_events(self) -> None:
        self.bind(const.Events.RESIZING, self.on_resizing)

    def on_resizing(self, event: Any) -> None:
        return self.resizer.resize(event=event)