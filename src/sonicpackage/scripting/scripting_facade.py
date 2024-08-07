import abc
import sys
from typing import Optional, Tuple
from icecream import ic
import attrs


@attrs.define()
class ParsingError:
    msg: str = attrs.field()
    line_begin: int = attrs.field()
    col_begin: int = attrs.field()
    line_end: Optional[int] = attrs.field(default=None)
    col_end: Optional[int] = attrs.field(default=None)

class ScriptError:
    pass


class Script(abc.ABC):
    def __init__(self) -> None:
        super().__init__()
        self._script_started = False

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

    def __aiter__(self):
        return self
    
    async def __anext__(self) -> Tuple[int, str]:
        if self.is_finished:
            self._script_started = False
            await self._after_script()
            raise StopAsyncIteration
        elif not self._script_started: # to return and highlight the line before we execute the line and run before_script
            self._script_started = True
            await self._before_script()
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
