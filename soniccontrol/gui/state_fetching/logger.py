import asyncio
import logging
import logging.handlers

from soniccontrol.gui.utils.observable_list import ObservableList
from soniccontrol.files import files


def create_logger_for_connection(connection_name: str) -> logging.Logger:
    logger = logging.getLogger(connection_name)
    logger.setLevel(logging.DEBUG)
    log_file_handler = logging.handlers.RotatingFileHandler(
        files.LOG_DIR / f"device_on_{connection_name}.log",
        maxBytes=40000,
        backupCount=3
    )
    detailed_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)s:%(funcName)s - %(message)s - exception: %(exc_info)s")
    log_file_handler.setFormatter(detailed_formatter)
    logger.addHandler(log_file_handler)
    return logger

def get_base_logger(logger: logging.Logger) -> logging.Logger:
    try:
        base_logger_name = logger.name.split(".").pop(0)
    except IndexError:
        base_logger_name = ""
    
    return logging.getLogger(base_logger_name)

class DeviceLogFilter(logging.Filter):
    def filter(self, record) -> bool:
        return "device" in record.name
    
class NotDeviceLogFilter(logging.Filter):
    def filter(self, record) -> bool:
        return "device" not in record.name

class LogStorage:
    class LogStorageHandler(logging.Handler):
        def __init__(self, logStorage: "LogStorage"):
            super(LogStorage.LogStorageHandler, self).__init__()
            formatter = logging.Formatter("%(asctime)s: %(levelname)s - %(name)s - %(message)s")
            self.setFormatter(formatter)
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

    def create_log_handler(self) -> LogStorageHandler:
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
