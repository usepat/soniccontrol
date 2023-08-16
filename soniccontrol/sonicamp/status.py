from typing import Any, Iterable
import abc


class StatusAdapter(abc.ABC):
    def __init__(self) -> None:
        super().__init__()

    @abc.abstractmethod
    def convert_data(self, data: str) -> Iterable[Any]:
        ...


class BasicStatusAdapter(StatusAdapter):
    def __init__(self) -> None:
        super().__init__()

    def convert_data(self, data: str) -> Iterable[Any]:
        return (0, 0, 0, 0, 0, 0)
