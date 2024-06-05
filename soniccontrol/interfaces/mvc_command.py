import abc
from async_tkinter_loop import async_handler

class MvcCommand:
    def __init__(self, target = None, source = None):
        self.target = target
        self.source = source

    @async_handler
    async def __call__(self):
        if self.can_execute():
            await self.execute()

    @abc.abstractmethod
    def can_execute(self) -> bool:
        return True

    @abc.abstractmethod
    async def execute(self) -> None:
        ...
    