import asyncio

from soniccontrol.tkintergui.utils.observable_list import ObservableList


class Logger:
    def __init__(self):
        self._logs: ObservableList = ObservableList()
        self._queue: asyncio.Queue = asyncio.Queue()
        self._worker_handle = asyncio.create_task(self._worker())

    def insert_log_to_queue(self, log: str) -> None:
        self._queue.put_nowait(log)

    async def _worker(self):
        while True:
            item = await self._queue.get()
            self._logs.append(item)

            # Maybe add a constraint to logs, that not too many are saved
    
    @property
    def logs(self) -> ObservableList:
        return self._logs
    
    def __del__(self):
        self._worker_handle.cancel()
