import abc
import enum
import logging
from typing import TYPE_CHECKING, Union, Callable, Any

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Layout:
    def __init__(
        self,
        condition: Callable[[Any], Any],
        command: Callable[[Any], Any],
        min_size: int = 10,
    ) -> None:
        self._min_size: int = min_size
        self._condition: Callable[[Any], Any] = condition
        self._command: Callable[[Any], Any] = command

    @property
    def min_size(self) -> None:
        return self._min_size

    def __repr__(self) -> str:
        return f"Layout({self.min_size, self._condition, self._command})"

    def should_be_applied(self, event) -> bool:
        logger.debug(f"Should be applied?: {event.widget, self._condition}")
        return self._condition(event)

    def apply(self, event: Any = None) -> None:
        logger.debug(f"Applying: {event.widget, self._command}")
        return self._command(event)


class WidthLayout(Layout):
    def __init__(self, min_width: int, command: Callable[[Any], Any]) -> None:
        super().__init__(
            lambda event: None,
            command,
            min_size=min_width,
        )

    def should_be_applied(self, event) -> bool:
        logger.debug(f"event width: {event.width},")
        logger.debug(f"width: {self.min_size},")
        logger.debug(f"condition: {(event.width - self.min_size) >= 0}")
        return (event.width - self.min_size) >= 0

    def __repr__(self) -> str:
        return f"Layout({self.min_size, self._command})"


class HeightLayout(Layout):
    def __init__(self, min_height: int, command: Callable[[Any], Any]) -> None:
        self._min_size: int = min_height
        super().__init__(
            lambda event: (event.height - self.min_size) >= 0,
            command,
            min_size=min_height,
        )

    def should_be_applied(self, event) -> bool:
        return (event.height - self.min_size) >= 0

    def __repr__(self) -> str:
        return f"Layout({self.min_size, self._command})"
