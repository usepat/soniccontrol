from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Callable, Any, Dict, Iterable
import time


@dataclass
class Command:
    message: str = field(default="")
    answer: str = field(default="")
    type_: str = field(default="")
    expected_big_answer: bool = field(default=False)
    callback: Optional[Callable[[Any], Any]] = field(default=None)
    timestamp: float = field(default_factory=time.time)

    def __lt__(self, other: Command):
        return self.timestamp < other.timestamp

    def __gt__(self, other: Command):
        return self.timestamp > other.timestamp


@dataclass
class SerialCommand(Command):
    pass


@dataclass
class SonicAmpCommand(Command):
    method_name: str = field(default="")
    method: Optional[Callable[[Any], Any]] = field(default=None)
    method_args: Iterable[Any] = field(default_factory=list)
    method_kwargs: Dict[str, Any] = field(default_factory=dict)
