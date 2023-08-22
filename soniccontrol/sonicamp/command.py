from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Callable, Any, Dict, Iterable
import threading
import time


@dataclass
class Command:
    message: str = field(default="")
    answer: str = field(default="")
    type_: str = field(default="")
    meta_data: Any = field(default=None)
    processed: threading.Event = field(default_factory=threading.Event, repr=False)
    processed_timestamp: Optional[float] = field(default=None, repr=False)
    expected_big_answer: bool = field(default=False)
    callback: Optional[Callable[[Any], Any]] = field(default=None)
    timestamp: float = field(default_factory=time.time)

    def __lt__(self, other: Command):
        return self.timestamp < other.timestamp

    def __gt__(self, other: Command):
        return self.timestamp > other.timestamp

    def set_processed(self, answer: str) -> Command:
        self.processed_timestamp = time.time()
        self.processed.set()
        self.answer = answer
        return self


@dataclass
class SerialCommand(Command):
    pass


@dataclass
class SonicAmpCommand(Command):
    method_name: str = field(default="")
    method: Optional[Callable[[Any], Any]] = field(default=None, repr=False)
    method_args: Iterable[Any] = field(default_factory=list)
    method_kwargs: Dict[str, Any] = field(default_factory=dict)
