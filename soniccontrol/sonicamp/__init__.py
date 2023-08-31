import serial
import serial.tools.list_ports as list_ports
from typing import Callable, Any, Optional
import logging
import sys
import time
import threading
from dataclasses import dataclass, field
import sonicpackage as sp
from sonicpackage.helpers import logger

logger = logging.getLogger(__name__)


class SonicAmpAgent(sp.SonicThread):
    def __init__(self, port: str) -> None:
        super().__init__()
        self._port: str = port
        self.connection: threading.Event = threading.Event()
        self.connection_established: threading.Event = threading.Event()
        self.sonicamp: Optional[sp.SonicInterface] = None

    @property
    def port(self) -> str:
        return self._port

    @port.setter
    def port(self, port: str) -> None:
        self._port = port

    def setup(self) -> None:
        if self.shutdown_request.is_set():
            return
        try:
            self.sonicamp = sp.SonicInterface(
                self.port,
                cancel_request=self.shutdown_request,
                logger_level=logging.DEBUG,
            )
        except Exception as e:
            exc_info = sys.exc_info()
            logger.warning(exc_info)
            self.exceptions_queue.put(exc_info)
            raise e
        if not self.shutdown_request.is_set():
            self.connection_established.set()
            self.connection.set()

    def worker(self) -> None:
        if self.shutdown_request.is_set():
            return
        try:
            priority, command = self.input_queue.get()  # Blocking call
            logger.debug(f"Receiving {command = }, with priority {priority = }")
            command.answer = self.sonicamp.serial.send_and_get(
                command.message, expected_big_answer=command.big_answer
            )
            logger.debug(f"Processed {command = }, with priority {priority = }")
            self.output_queue.put((priority, command))
            command.processed.set()
            self.input_queue.task_done()
        except Exception as e:
            self.exceptions_queue.put(sys.exc_info())

    def shutdown(self) -> None:
        super().shutdown()
        if self.sonicamp is not None:
            self.connection.clear()
            self.sonicamp.serial.disconnect()


@dataclass
class Command:
    message: str = field(default="")
    answer: str = field(default="")
    type_: str = field(default="")
    callback: Optional[Callable[[Any], Any]] = field(default=None)
    timestamp: float = field(default_factory=time.time)
    processed: threading.Event = field(default_factory=threading.Event)
    big_answer: bool = field(default=False)

    def __lt__(self, other):
        return self.timestamp < other.timestamp


def main() -> None:
    sonicamp = SonicAmpAgent(port="/dev/cu.usbserial-AB0M45SW")
    sonicamp.daemon = True
    sonicamp.start()
    sonicamp.resume()

    sonicamp.add_job(Command(message="!OFF"), 0)
    sonicamp.add_job(Command(message="?"), 0)
    sonicamp.add_job(Command(message="-"), 0)
    sonicamp.add_job(Command(message="!f=1000000"), 0)
    sonicamp.add_job(Command(message="="), 0)

    oldcommand = None
    hertz = 0
    while True:
        sonicamp.add_job(Command(message="-"), 0)
        prio, command = sonicamp.output_queue.get()
        if oldcommand:
            hertz = 1 / (command.timestamp - oldcommand.timestamp)
        print(f"{command} with {hertz} Hz")
        oldcommand = command


if __name__ == "__main__":
    main()
