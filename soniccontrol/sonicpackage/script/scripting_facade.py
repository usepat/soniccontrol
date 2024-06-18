import abc
import sys
from typing import Optional, Tuple
from icecream import ic
import attrs


@attrs.define()
class ParsingError:
    line_begin: int = attrs.field()
    col_begin: int = attrs.field()
    line_end: Optional[int] = attrs.field(default=None)
    col_end: Optional[int] = attrs.field(default=None)
    msg: str = attrs.field()

class ScriptError:
    pass


class Script(abc.ABC):
    def __init__(self) -> None:
        super().__init__()

    """
    Raises:
        ScriptError: If an operation fails
    """
    @abc.abstractmethod
    async def _execute_step(self) -> None: ...

    @property
    @abc.abstractmethod
    def current_line(self) -> int: ...
    
    @property
    @abc.abstractmethod
    def current_task(self) -> str: ...

    @property
    @abc.abstractmethod
    def is_finished(self) -> bool: ...

    @abc.abstractmethod
    async def _before_script(self) -> None: ...

    @abc.abstractmethod
    async def _after_script(self) -> None: ...

    async def __aiter__(self):
        await self._before_script()
        return self
    
    async def __anext__(self) -> Tuple[int, str]:
        if self.is_finished:
            await self._after_script()
            raise StopIteration
        elif self.current_line == 0: # to return and highlight the line before we execute the line
            return self.current_line, self.current_task
        else:
            try:
                await self._execute_step()
            except:
                ic(sys.exc_info())
                await self._after_script()
                raise # propagate exception
            return self.current_line, self.current_task


class ScriptingFacade(abc.ABC):
    def __init__(self) -> None:
        super().__init__()

    @abc.abstractmethod
    def parse_script(self, text: str) -> Script: ...

    @abc.abstractmethod
    def lint_text(self, text: str) -> str: ...
