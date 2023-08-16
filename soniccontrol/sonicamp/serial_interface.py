from __future__ import annotations
from typing import Optional, Callable, Any
from dataclasses import dataclass, field
import time


@dataclass
class Command:
    message: str = field(default="")
    answer: str = field(default="")
    type_: str = field(default="")
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
    pass
