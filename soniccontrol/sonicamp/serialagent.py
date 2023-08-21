from typing import Optional, Iterable, List
import threading
import platform
import sys
import serial
import copy
import time
import logging
import serial.tools.list_ports as list_ports

from soniccontrol.sonicamp.threads import SonicThread
from soniccontrol.sonicamp.command import SerialCommand

logger = logging.getLogger(__name__)


class SerialAgent(SonicThread):
    def __init__(self, port: str) -> None:
        super().__init__()
        self._port: str = port

        self._baudrate: int = 115200
        self._serial: Optional[serial.Serial] = None
        self.encoding: str = (
            "windows-1252" if platform.system() == "Windows" else "utf-8"
        )
        self.init_message: str = ""

        self.connection: threading.Condition = threading.Condition(threading.Lock())
        self.connection_established: threading.Event = threading.Event()
        self.serial: Optional[serial.Serial] = None

    @property
    def port(self) -> str:
        return self._port

    @port.setter
    def port(self, port: str) -> None:
        self._port = port

    @staticmethod
    def get_ports() -> Iterable[str]:
        return (port.device for port in list_ports.comports())

    def setup(self) -> None:
        if self.shutdown_request.is_set():
            return
        try:
            self.connect()
            self.init_message = self.read_message(all_=True)
        except Exception as e:
            exc_info = sys.exc_info()
            logger.warning(exc_info)
            self.exceptions_queue.put(exc_info)
            raise e
        if not self.shutdown_request.is_set():
            self.connection_established.set()
            with self.connection:
                self.connection.notify_all()

    def worker(self) -> None:
        if self.shutdown_request.is_set():
            return
        try:
            priority, command = self.input_queue.get()  # Blocking call
            logger.debug(f"Receiving {command = }, with priority {priority = }")
            command.update_answer(self.send_and_get(command))
            logger.debug(f"Processed {command = }, with priority {priority = }")
            self.output_queue.put((priority, command))
            command.processed.set()
            self.input_queue.task_done()
        except Exception as e:
            self.exceptions_queue.put(sys.exc_info())

    def connect(self) -> None:
        self._serial = serial.Serial(self._port, self._baudrate, timeout=1)
        for _ in range(50):
            if self.shutdown_request.is_set():
                logger.info("Cancelling connection...")
                return
            time.sleep(0.1)

    def read_message(self, all_: bool = False) -> str:
        return (self._serial.readall() if all_ else self._serial.readline()).decode(
            self.encoding
        )

    def send_message(self, command: SerialCommand) -> None:
        self._serial.flush()
        self._serial.write(f"{command.message}\n".encode(self.encoding))

    def send_and_get(self, command: SerialCommand) -> str:
        self.send_message(command=command)
        time.sleep(0.2)
        return self.read_message(command.expected_big_answer)

    def shutdown(self) -> None:
        super().shutdown()
        if self.serial is not None:
            self.connection.clear()
            self.serial.serial.disconnect()


def main() -> None:
    serialagent = SerialAgent(port="/dev/cu.usbserial-AB0M45SW")
    serialagent.daemon = True
    serialagent.start()
    serialagent.resume()

    serialagent.add_job(SerialCommand(message="!OFF"), 0)
    serialagent.add_job(SerialCommand(message="?", expected_big_answer=True), 0)
    serialagent.add_job(SerialCommand(message="-"), 0)
    serialagent.add_job(SerialCommand(message="!f=1000000"), 0)
    serialagent.add_job(SerialCommand(message="="), 0)
    serialagent.add_job(SerialCommand(message="!AUTO"), 0)

    oldcommand = None
    hertz = 0

    with serialagent.connection:
        serialagent.connection.wait_for(serialagent.connection_established.is_set)
    print(serialagent.init_message)

    while True:
        serialagent.add_job(SerialCommand(message="-"), 0)
        serialagent.add_job(SerialCommand(message="?sens"), 0)
        prio, command = serialagent.output_queue.get()
        if oldcommand:
            hertz = 1 / (command.timestamp - oldcommand.timestamp)
        print(f"{command} with {hertz} Hz")
        oldcommand = command


if __name__ == "__main__":
    main()
