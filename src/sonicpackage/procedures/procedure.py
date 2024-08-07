

import abc
from typing import Any, Type

from sonicpackage.interfaces import Scriptable


class Procedure(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def get_args_class(cls) -> Type: ...

    @abc.abstractmethod
    async def execute(self, device: Scriptable, args: Any) -> None: ...
