import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame
import logging
import abc
from typing import Any, Iterable, Optional, Set
import soniccontrol.constants as const
from soniccontrol.interfaces.rootchild import RootChild
from soniccontrol.interfaces.layout import Layout
from soniccontrol.interfaces.gui_interfaces import Resizable
from soniccontrol.interfaces.resizer import Resizer

logger = logging.getLogger(__name__)


class RootNotebook(ttk.Notebook, Resizable):
    def __init__(self, parent_frame: ttk.Frame, *args, **kwargs) -> None:
        super().__init__(parent_frame, *args, **kwargs)
        self._width_layouts: Optional[Iterable[Layout]] = None
        self._height_layouts: Optional[Iterable[Layout]] = None
        self._resizer: Resizer = Resizer(self)
        self._currently_managed_tabs: Iterable[RootChild] = list()
        self._last_focused_tab: Optional[RootChild] = None
        self._currently_with_images: bool = False
        self._currently_with_titles: bool = False

    @property
    def resizer(self) -> Resizer:
        return self._resizer

    @property
    def last_focused_tab(self) -> RootChild:
        return self._last_focused_tab

    @property
    def width_layouts(self) -> Iterable[Layout]:
        return self._width_layouts

    @property
    def height_layouts(self) -> Iterable[Layout]:
        return self._height_layouts

    @property
    def currently_managed_tabs(self) -> Iterable[RootChild]:
        return self._currently_managed_tabs

    def bind_events(self) -> None:
        self.bind(const.Events.RESIZING, self.on_resizing)

    def on_resizing(self, event: Any) -> None:
        return self.resizer.resize(event=event)

    def add_tab(
        self,
        frame: RootChild,
        with_image: bool = False,
        with_tab_title: bool = False,
        **kwargs,
    ) -> str:
        kwargs.update(
            {"image": frame.image, "compound": ttk.TOP}
            if with_image and frame.image is not None
            else {}
        )
        kwargs.update(
            {"text": frame.tab_title}
            if with_tab_title and frame.tab_title is not None
            else {}
        )

        tab_id: str = self.add(
            frame.container if isinstance(frame, ScrolledFrame) else frame, **kwargs
        )
        self._currently_managed_tabs.append(frame)
        return tab_id

    def add_tabs(
        self,
        frames: Iterable[RootChild],
        with_images: bool = True,
        with_tab_titles: bool = True,
        **kwargs,
    ) -> None:
        frames = self.currently_managed_tabs.copy() if frames is None else frames
        for frame in frames:
            self.add_tab(
                frame, with_image=with_images, with_tab_title=with_tab_titles, **kwargs
            )
        self._currently_with_images = with_images
        self._currently_with_titles = with_tab_titles

    def forget_tabs(self, frames: Optional[RootChild] = None) -> None:
        self._last_focused_tab = self.select()
        frames = self.currently_managed_tabs.copy() if frames is None else frames
        for frame in frames:
            self.forget_tab(frame)

    def forget_tab(self, frame: Optional[RootChild] = None) -> None:
        if frame not in self.currently_managed_tabs:
            return
        self.forget(frame.container if isinstance(frame, ScrolledFrame) else frame)
        self._currently_managed_tabs.remove(frame)

    def configure_tabs(
        self, tab_titles: Optional[bool] = None, images: Optional[bool] = None
    ) -> None:
        if not len(self.tabs()):
            return
        temporary_tabs: Set[RootChild] = self.currently_managed_tabs.copy()
        self.forget_tabs()
        self.add_tabs(
            temporary_tabs,
            with_images=self._currently_with_images if images is None else images,
            with_tab_titles=self._currently_with_titles
            if tab_titles is None
            else tab_titles,
        )
        self.select(self._last_focused_tab)

    def forget_and_add_tabs(self, tabs: Iterable[RootChild]) -> None:
        self.forget_tabs()
        self.add_tabs(tabs)
        try:
            self.select(self._last_focused_tab)
        except Exception as e:
            logger.debug(e)

    def hide_images(self) -> None:
        logger.debug("hiding images")
        self.configure_tabs(images=False)

    def show_images(self) -> None:
        logger.debug("showing images")
        self.configure_tabs(images=True)

    def show_images_without_titles(self, *args, **kwargs) -> None:
        logger.debug("showing images without titles")
        self.configure_tabs(images=True, tab_titles=False)

    def show_tab_titles(self, *args, **kwargs) -> None:
        logger.debug("showing tab titles")
        self.configure_tabs(tab_titles=True)

    def hide_tab_titles(self) -> None:
        logger.debug("hiding tab titles")
        self.configure_tabs(tab_titles=False)
