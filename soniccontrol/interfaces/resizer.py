from typing import Optional, Iterable, Any
from soniccontrol.interfaces.layout import Layout
from soniccontrol.interfaces.gui_interfaces import Resizable
import logging

logger = logging.getLogger(__name__)


class Resizer():
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