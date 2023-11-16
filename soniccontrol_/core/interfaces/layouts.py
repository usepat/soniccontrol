from typing import Callable, Any, Optional
import logging
import attrs

logger = logging.getLogger(__name__)


@attrs.frozen(kw_only=True)
class Layout:
    command: Callable[[Any], Any] = attrs.field()
    condition: Callable[[Any], bool] = attrs.field()
    min_size: int = attrs.field(
        default=10, eq=True, order=int, validator=attrs.validators.instance_of(int)
    )

    def should_be_applied(self, event: Any, *args, **kwargs) -> bool:
        return bool(self.condition(event))

    def apply(self, event: Any = None) -> None:
        return self.command()


@attrs.frozen(kw_only=True)
class WidthLayout(Layout):
    condition: Optional[Callable[[Any], Any]] = attrs.field(default=None)

    def __attrs_post_init__(self) -> None:
        if self.condition is None:
            object.__setattr__(
                self,
                "condition",
                lambda event: bool((event.width - self.min_size) >= 0),
            )


@attrs.frozen(kw_only=True)
class HeightLayout(Layout):
    condition: Optional[Callable[[Any], Any]] = attrs.field(default=None)

    def __attrs_post_init__(self) -> None:
        if self.condition is None:
            object.__setattr__(
                self, "condition", lambda event: (event.height - self.min_size) >= 0
            )
