from typing_extensions import Any, Callable
import attrs


@attrs.frozen(kw_only=True)
class Layout:
    _command: Callable[..., Any] = attrs.field()
    _condition: Callable[..., Any] = attrs.field()

