from typing import Protocol


class Event(Protocol):
    @property
    def width(self) -> int:
        ...

    @property
    def height(self) -> int:
        ...
