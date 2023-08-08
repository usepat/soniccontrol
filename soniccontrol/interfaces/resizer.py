from typing import Optional, Iterable, Any
from soniccontrol.interfaces.layout import Layout
from soniccontrol.interfaces.gui_interfaces import Resizable
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


class Resizer:
    def __init__(
        self,
        subject: Resizable,
    ) -> None:
        super().__init__()
        self._subject: Resizable = subject
        self._active_width_layout: Optional[Layout] = None
        self._active_height_layout: Optional[Layout] = None

    @property
    def subject(self) -> Resizable:
        return self._subject

    @property
    def active_height_layout(self) -> Layout:
        return self._active_height_layout

    @property
    def active_width_layout(self) -> Layout:
        return self._active_width_layout

    def resize(self, event: Any) -> None:
        if event.widget != self.subject:
            return

        def check_width() -> None:
            if not self.subject.width_layouts:
                return
            for layout in self.subject.width_layouts:
                if layout.should_be_applied(event):
                    if self.active_width_layout == layout:
                        return
                    layout.apply(event=event)
                    self._active_width_layout = layout
                    return

        def check_height() -> None:
            if not self.subject.height_layouts:
                return
            for layout in self.subject.height_layouts:
                if layout.should_be_applied(event):
                    if self.active_height_layout == layout:
                        return
                    layout.apply(event=event)
                    self._active_height_layout = layout
                    return

        logger.debug(event)
        check_width()
        check_height()


# class Resizer:
#     def __init__(
#         self,
#         subject: Resizable,
#     ) -> None:
#         super().__init__()
#         self._subject: Resizable = subject
#         self._active_width_layout: Optional[Layout] = None
#         self._active_height_layout: Optional[Layout] = None

#         self._height_layouts, self._width_layouts = (
#             sorted(
#                 (
#                     layout
#                     for layout in self.subject.layouts
#                     if isinstance(layout, layout_class)
#                 ),
#                 key=lambda layout: layout.minsize,
#             )
#             for layout_class in (HeightLayout, WidthLayout)
#         )
#         self._rheight_layouts, self._rwidth_layouts = (
#             self._height_layouts[::-1],
#             self._width_layouts[::-1],
#         )

#         self.old_event: Any = None
#         self.width_resizing_direction: int = 0
#         self.height_resizing_direction: int = 0

#     @property
#     def subject(self) -> Resizable:
#         return self._subject

#     @property
#     def active_height_layout(self) -> Layout:
#         return self._active_height_layout

#     @property
#     def active_width_layout(self) -> Layout:
#         return self._active_width_layout

#     def resize(self, event: Any) -> None:
#         if event.widget != self.subject:
#             return

#         if self.old_event is None:
#             self.old_event = event

#         self._active_width_layout, self._active_height_layout = (
#             check_layouts(
#                 self._width_layouts
#                 if event.width < self.old_event.width
#                 else self._rwidth_layouts,
#                 self.active_layout,
#             ),
#             check_layouts(
#                 self._height_layouts
#                 if event.height < self.old_event.height
#                 else self._rheight_layouts,
#                 self.active_layout,
#             ),
#         )

#         def check_layouts(layouts, active_layout) -> Optional[Layout]:
#             if not layouts:
#                 return None
#             for layout in layouts:
#                 if layout != active_layout:
#                     layout.apply()
#                 return layout
