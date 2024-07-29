import asyncio
import logging
import logging.handlers

from soniccontrol.tkintergui.utils.observable_list import ObservableList
from utils.files import files


def create_logger_for_connection(connection_name: str) -> logging.Logger:
        logger = logging.getLogger(connection_name)
        logger.setLevel(logging.DEBUG)
        file_log_callback = logging.handlers.RotatingFileHandler(
            files.LOG_DIR / f"device_on_{connection_name}.log",
            maxBytes=40000,
            backupCount=3
        )
        logger.addHandler(file_log_callback)
        return logger


class LogStorage:
    class LogStorageHandler(logging.Handler):
        def __init__(self, logStorage: "LogStorage"):
            super(LogStorage.LogStorageHandler, self).__init__()
            self._logStorage = logStorage

        def emit(self, record: logging.LogRecord) -> None:
            try:
                log = self.format(record)
                self._logStorage._queue.put_nowait(log)
            except:
                self.handleError(record)


    _MAX_SIZE_LOGS = 100

    def __init__(self):
        self._logs: ObservableList = ObservableList()
        self._queue: asyncio.Queue = asyncio.Queue()
        self._worker_handle = asyncio.create_task(self._worker())

    def insert_log_to_queue(self, log: str) -> None:
        self._queue.put_nowait(log)

    def create_log_callback(self) -> LogStorageHandler:
        return LogStorage.LogStorageHandler(self)

    async def _worker(self):
        while True:
            item = await self._queue.get()
            self._logs.append(item)
            if len(self._logs) > LogStorage._MAX_SIZE_LOGS:
                 self._logs.remove_at(0)
    
    @property
    def logs(self) -> ObservableList:
        return self._logs
    
    def __del__(self):
        self._worker_handle.cancel()
