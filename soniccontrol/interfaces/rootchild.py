import logging
import tkinter as tk
from typing import TYPE_CHECKING, Any, Iterable, Optional, Set, Union

import PIL
import ttkbootstrap as ttk
from PIL.ImageTk import PhotoImage
from ttkbootstrap.scrolled import ScrolledFrame

import soniccontrol.constants as const
from soniccontrol.interfaces.gui_interfaces import Resizable, Tabable
from soniccontrol.interfaces.layout import Layout
from soniccontrol.interfaces.resizer import Resizer
from soniccontrol.interfaces.root import Root

logger = logging.getLogger(__name__)


class RootChild(ScrolledFrame, Resizable, Tabable):
    def __init__(
        self,
        parent_frame: Root,
        tab_title: str,
        image: PhotoImage,
        autohide: bool = True,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(master=parent_frame, autohide=autohide, *args, **kwargs)
        self._width_layouts: Optional[Iterable[Layout]] = None
        self._height_layouts: Optional[Iterable[Layout]] = None
        self._tab_title: str = tab_title
        self._image: PhotoImage = image
        self._resizer: Resizer = Resizer(self)

        style = ttk.Style()
        style.configure("LightGreyLabel.TLabel", background="grey")

        logger.debug("RootChild initialized")

    @property
    def root(self) -> Union[tk.Tk, tk.Toplevel]:
        return self.winfo_toplevel()

    @property
    def resizer(self) -> Resizer:
        return self._resizer

    @property
    def width_layouts(self) -> Optional[Iterable[Layout]]:
        return self._width_layouts

    @property
    def height_layouts(self) -> Optional[Iterable[Layout]]:
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


class RootChildFrame(ttk.Frame, Resizable, Tabable):
    def __init__(
        self, parent_frame: Root, tab_title: str, image: PIL.Image, *args, **kwargs
    ) -> None:
        super().__init__(master=parent_frame, *args, **kwargs)
        self._width_layouts: Optional[Iterable[Layout]] = None
        self._height_layouts: Optional[Iterable[Layout]] = None
        self._tab_title: str = tab_title
        self._image: PhotoImage = image
        self._resizer: Resizer = Resizer(self)

        logger.debug("RootChild initialized")

    @property
    def root(self) -> Root:
        return self.winfo_toplevel()

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


class RootLabel(ttk.Label):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # dot animation
        self.dot_position: int = 0
        self.dot_text: str = "   "
        self.is_dot_animation_running: bool = False
        self.original_text: str = self.cget("text")

    def animate_dots(self, text: str = "") -> None:
        self.is_dot_animation_running = True
        self.dot_animator(text=text)

    def stop_animation_of_dots(self) -> None:
        self.is_dot_animation_running = False

    def dot_animator(self, text: Optional[str] = None) -> None:
        if not self.is_dot_animation_running:
            return
        logger.debug("running dot animation...")
        if text is not None:
            self.original_text = text
        if self.dot_position > 3:
            self.dot_position = 0
        logger.debug(
            f"with text {self.original_text} and boolean {self.is_dot_animation_running} and {self.dot_position} position"
        )

        self.dot_text = "." * self.dot_position + " " * (3 - self.dot_position)

        logger.debug(self.dot_text)
        self.configure(text=f"{self.original_text}{self.dot_text}")
        self.dot_position += 1
        self.after(500, self.dot_animator)


# class RootChild:
#     def __init__(self, subject, *args, **kwargs) -> None:
#         self._subject: tk.Widget = subject(*args, **kwargs)

#     @property
#     def subject(self) -> tk.Widget:
#         return self._subject

#     @property
#     def root(self) -> Root:
#         return self.subject.wifo_toplevel()

#     def bind_events(self) -> None:
#         ...


# class RootChildFrame(RootChild):
#     def __init__(self, *args, **kwargs) -> None:
#         super().__init__(ttk.Frame, *args, **kwargs)


# class RootChildScrolledFrame(RootChild):
#     def __init__(self, *args, **kwargs) -> None:
#         super().__init__(ScrolledFrame, *args, **kwargs)


# class RootChildLabel(RootChild):
#     def __init__(self, *args, **kwargs) -> None:
#         super().__init__(ttk.Label, *args, **kwargs)
#         self.dot_position: int = 0
#         self.dot_text: str = "   "
#         self.is_dot_animation_running: bool = False
#         self.original_text: str = self.subject.cget("text")

#     def animate_dots(self, text: str = "") -> None:
#         self.is_dot_animation_running = True
#         self.dot_animator(text=text)

#     def stop_animation_of_dots(self) -> None:
#         self.is_dot_animation_running = False

#     def dot_animator(self, text: Optional[str] = None) -> None:
#         if not self.is_dot_animation_running:
#             return
#         logger.debug("running dot animation...")
#         if text is not None:
#             self.original_text = text
#         if self.dot_position > 3:
#             self.dot_position = 0
#         logger.debug(
#             f"with text {self.original_text} and boolean {self.is_dot_animation_running} and {self.dot_position} position"
#         )

#         self.dot_text = "." * self.dot_position + " " * (3 - self.dot_position)

#         logger.debug(self.dot_text)
#         self.configure(text=f"{self.original_text}{self.dot_text}")
#         self.dot_position += 1
#         self.after(500, self.dot_animator)


# class TabableRootChildFrame(RootChildFrame, Tabable, Resizable):
#     def __init__(self, tab_title: str, image: PhotoImage, *args, **kwargs) -> None:
#         super().__init__(*args, **kwargs)
#         self._tab_title: str = tab_title
#         self._image: PhotoImage = image

#         self._layouts: Optional[Iterable[Layout]] = None
#         self._resizer: Resizer = Resizer(self)

#     @property
#     def tab_title(self) -> None:
#         return self._tab_title

#     @property
#     def image(self) -> None:
#         return self._image

#     @property
#     def resizer(self) -> Resizer:
#         return self._resizer

#     @property
#     def layouts(self) -> Iterable[Layout]:
#         return self._layouts


# class TabableRootChildScrolledFrame(RootChildScrolledFrame, Tabable, Resizable):
#     def __init__(self, tab_title: str, image: PhotoImage, *args, **kwargs) -> None:
#         super().__init__(*args, **kwargs)
#         self._tab_title: str = tab_title
#         self._image: PhotoImage = image

#         self._layouts: Optional[Iterable[Layout]] = None
#         self._resizer: Resizer = Resizer(self)

#     @property
#     def tab_title(self) -> None:
#         return self._tab_title

#     @property
#     def image(self) -> None:
#         return self._image

#     @property
#     def resizer(self) -> Resizer:
#         return self._resizer

#     @property
#     def layouts(self) -> Iterable[Layout]:
#         return self._layouts


# class RootChildNotebook(RootChild, Resizable):
#     def __init__(self, *args, **kwargs) -> None:
#         super().__init__(ttk.Notebook, *args, **kwargs)
#         self._layouts: Optional[Iterable[Layout]] = None
#         self._resizer: Resizer = Resizer(self)
#         self._currently_managed_tabs: Iterable[RootChild] = list()
#         self._last_focused_tab: Optional[RootChild] = None
#         self._currently_with_images: bool = False
#         self._currently_with_titles: bool = False

#     @property
#     def resizer(self) -> Resizer:
#         return self._resizer

#     @property
#     def last_focused_tab(self) -> RootChild:
#         return self._last_focused_tab

#     @property
#     def layouts(self) -> Iterable[Layout]:
#         return self._layouts

#     @property
#     def currently_managed_tabs(self) -> Iterable[RootChild]:
#         return self._currently_managed_tabs

#     def bind_events(self) -> None:
#         self.bind(const.Events.RESIZING, self.on_resizing)

#     def on_resizing(self, event: Any) -> None:
#         return self.resizer.resize(event=event)

#     def add_tab(
#         self,
#         frame: RootChild,
#         with_image: bool = False,
#         with_tab_title: bool = False,
#         **kwargs,
#     ) -> str:
#         kwargs.update(
#             {"image": frame.image, "compound": ttk.TOP}
#             if with_image and frame.image is not None
#             else {}
#         )
#         kwargs.update(
#             {"text": frame.tab_title}
#             if with_tab_title and frame.tab_title is not None
#             else {}
#         )

#         tab_id: str = self.subject.add(
#             frame.subject.container if isinstance(frame, TabableRootChildScrolledFrame) else frame, **kwargs
#         )
#         self._currently_managed_tabs.append(frame)
#         return tab_id

#     def add_tabs(
#         self,
#         frames: Iterable[RootChild],
#         with_images: bool = True,
#         with_tab_titles: bool = True,
#         **kwargs,
#     ) -> None:
#         frames = self.currently_managed_tabs.copy() if frames is None else frames
#         for frame in frames:
#             self.add_tab(
#                 frame, with_image=with_images, with_tab_title=with_tab_titles, **kwargs
#             )
#         self._currently_with_images = with_images
#         self._currently_with_titles = with_tab_titles

#     def forget_tabs(self, frames: Optional[RootChild] = None) -> None:
#         self._last_focused_tab = self.select()
#         frames = self.currently_managed_tabs.copy() if frames is None else frames
#         for frame in frames:
#             self.forget_tab(frame)

#     def forget_tab(self, frame: Optional[RootChild] = None) -> None:
#         if frame not in self.currently_managed_tabs:
#             return
#         self.forget(frame.container if isinstance(frame, ScrolledFrame) else frame)
#         self._currently_managed_tabs.remove(frame)

#     def configure_tabs(
#         self, tab_titles: Optional[bool] = None, images: Optional[bool] = None
#     ) -> None:
#         if not len(self.tabs()):
#             return
#         temporary_tabs: Set[RootChild] = self.currently_managed_tabs.copy()
#         self.forget_tabs()
#         self.add_tabs(
#             temporary_tabs,
#             with_images=self._currently_with_images if images is None else images,
#             with_tab_titles=self._currently_with_titles
#             if tab_titles is None
#             else tab_titles,
#         )
#         self.select(self._last_focused_tab)

#     def forget_and_add_tabs(self, tabs: Iterable[RootChild]) -> None:
#         self.forget_tabs()
#         self.add_tabs(tabs)
#         try:
#             self.select(self._last_focused_tab)
#         except Exception as e:
#             logger.debug(e)

#     def hide_images(self) -> None:
#         logger.debug("hiding images")
#         self.configure_tabs(images=False)

#     def show_images(self) -> None:
#         logger.debug("showing images")
#         self.configure_tabs(images=True)

#     def show_images_without_titles(self, *args, **kwargs) -> None:
#         logger.debug("showing images without titles")
#         self.configure_tabs(images=True, tab_titles=False)

#     def show_tab_titles(self, *args, **kwargs) -> None:
#         logger.debug("showing tab titles")
#         self.configure_tabs(tab_titles=True)

#     def hide_tab_titles(self) -> None:
#         logger.debug("hiding tab titles")
#         self.configure_tabs(tab_titles=False)
