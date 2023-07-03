from __future__ import annotations
import abc
import enum

from tkinter import dnd


class Mediator(abc.ABC):
    def __init__(self, root: Root) -> None:
        self._root: Root = root

    @property
    def root(self) -> Root:
        self._root

    @abc.abstractmethod
    def notify(self, sender: Component, event: enum.Enum) -> None:
        pass


class Event(enum.Enum):
    status_update = 0
    resizing = 1


class EventDispatcher(abc.ABC):
    def __init__(self) -> None:
        self._handlers = {Event.status_update: [], Event.resizing: []}

    def add_handler(self, event_type, handler) -> None:
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def dispatch_event(self, event_type, event_data) -> None:
        handlers = (
            handler for handler in self._handlers if event_type in self._handlers
        )
        for handler in handlers:
            handler(event_data)


class Component:
    def __init__(self, mediator: Mediator = None) -> None:
        super().__init__()
        self._mediator = mediator

    @property
    def mediator(self) -> Mediator:
        return self._mediator

    @mediator.setter
    def mediator(self, mediator: Mediator) -> None:
        self._mediator = mediator


class Resizer:
    def __init__(self) -> None:
        self._subscriber
        self.updater_lookup_dict = {}
