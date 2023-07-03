from __future__ import annotations
import abc

from typing import Optional


class Root(abc.ABC):
    _instance: Optional[SCRoot] = None

    def __new__(cls, *args, **kwargs) -> SCRoot:
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @abstractmethod
    def reinitialize(self) -> None:
        ...

    @abstractmethod
    def thread_engine(self) -> None:
        ...

    @abstractmethod
    def attach_data(self, status: Status) -> None:
        ...

    @abstractmethod
    def abolish_data(self) -> None:
        ...

    @abstractmethod
    def on_closing(self) -> None:
        ...

    @abstractmethod
    def on_resizing(self, event) -> None:
        ...
