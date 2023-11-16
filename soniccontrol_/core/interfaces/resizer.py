from typing import Optional, Any, List
import attrs
from soniccontrol.core.interfaces.layouts import (
    Layout,
    WidthLayout,
    HeightLayout,
)
from soniccontrol.core.interfaces.gui_interfaces import Resizable


@attrs.define
class Resizer:
    _subject: Resizable = attrs.field(validator=attrs.validators.instance_of(Resizable))
    _active_height_layout: Optional[Layout] = attrs.field(default=None)
    _active_width_layout: Optional[Layout] = attrs.field(default=None)
    _height_layouts: List[Layout] = attrs.field(init=False, factory=list)
    _width_layouts: List[Layout] = attrs.field(init=False, factory=list)
    _old_event: Optional[Any] = attrs.field(default=None)

    def __attrs_post_init__(self) -> None:
        if not self._subject.layouts:
            return
        for layout in self._subject.layouts:
            if isinstance(layout, HeightLayout):
                self._height_layouts.append(layout)
            elif isinstance(layout, WidthLayout):
                self._width_layouts.append(layout)

        self._height_layouts.sort(key=lambda layout: layout.min_size, reverse=True)
        self._width_layouts.sort(key=lambda layout: layout.min_size, reverse=True)

    def resize(
        self,
        event: Any,
        width_direction: bool = True,
        height_direction: bool = True,
        *args,
        **kwargs
    ) -> None:
        def check_size(layouts, active_layout) -> None:
            for layout in layouts:
                if not layout.should_be_applied(event):
                    continue
                if layout == active_layout:
                    return
                layout.apply(event)
                active_layout = layout
                return

        if event is None or event.widget != self._subject:
            return
        check_size(self._width_layouts, self._active_width_layout)
        check_size(self._height_layouts, self._active_height_layout)
