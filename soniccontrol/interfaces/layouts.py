from typing import Literal, Callable, Optional
import attrs
from soniccontrol.interfaces.tkintertypes import Event


@attrs.define
class Layout:
    _command: Callable[[], None] = attrs.field(alias="command")
    _min_size: Optional[int] = attrs.field(default=1)
    _orientation: Optional[Literal["width", "height"]] = attrs.field(default=None)
    _condition: Optional[Callable[[Event], bool]] = attrs.field(
        default=None, alias="condition"
    )
    _active: bool = attrs.field(init=False, default=False)

    @property
    def active(self) -> bool:
        return self._active

    @property
    def min_size(self) -> Optional[int]:
        return self._min_size

    def should_apply(self, event: Event) -> bool:
        return not self._active and (
            (self._condition is not None and self._condition(event))
            or (
                self._min_size is not None
                and self._orientation is not None
                and (getattr(event, self._orientation) - self._min_size) >= 0
            )
        )

    def apply(self) -> None:
        self._command()
        self._active = True

    def unapply(self) -> None:
        self._active = False


@attrs.define
class WidthLayout(Layout):
    _condition: None = None
    _orientation: Literal["width"] = "width"


@attrs.define
class HeightLayout(Layout):
    _condition: None = None
    _orientation: Literal["height"] = "height"
