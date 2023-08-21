from typing import Optional, Iterable
import sys
import logging
import threading

from soniccontrol.sonicamp.command import Command, SonicAmpCommand
from soniccontrol.sonicamp.serialagent import SerialAgent
from soniccontrol.sonicamp.threads import SonicThread
from soniccontrol.sonicamp.sonicamp import SonicAmp

logger = logging.getLogger(__name__)


class SonicInterface(SonicThread):
    def __init__(self, port: str) -> None:
        super().__init__()
        self.ready_for_actions: threading.Condition = threading.Condition(
            threading.Lock()
        )
        self.serial: SerialAgent = SerialAgent(port)
        self.serial.daemon = True
        self.sonicamp: Optional[SonicAmp] = None

    def setup(self) -> None:
        self.serial.start()
        self.serial.resume()

        with self.serial.connection:
            self.serial.connection.wait_for(
                lambda: self.serial.connection_established.is_set()
                or self.shutdown_request.is_set()
                or self.serial.exceptions_queue.qsize()
            )

        if self.serial.exceptions_queue.qsize():
            self.exceptions_queue.put(self.serial.exceptions_queue.get())
            return
        if self.shutdown_request.is_set():
            return

        try:
            print("building amp")
            self.sonicamp = SonicAmp.build_amp(self, self.serial)
        except Exception as e:
            exc_info = sys.exc_info()
            logger.warning(exc_info)
            self.exceptions_queue.put(exc_info)
            raise e
        else:
            with self.ready_for_actions:
                self.ready_for_actions.notify_all()

    def worker(self) -> None:
        if self.shutdown_request.is_set():
            return
        try:
            if self.serial.exceptions_queue.qsize():
                self.exceptions_queue.put(self.serial.exceptions_queue.get())
            if not (
                self.sonicamp.ramp_running.is_set() or self.sonicamp.holding.is_set()
            ):
                priority, input_command = self.input_queue.get()  # Blocking call
                print(f"SonicAgent got {input_command}")
                input_command = self.sonicamp.react_on_command(command=input_command)

            priority, output_command = self.serial.get_job()
            print(f"SonicAgenn processed {output_command}")
            output_command = self.sonicamp.process_output_command(output_command)
            self.output_queue.put((priority, output_command))

            self.input_queue.task_done()
            # self.sonicamp.get_status(SonicAmpCommand(type_="status"))
        except Exception as e:
            self.exceptions_queue.put(sys.exc_info())

    def add_job(self, priority: int, method_name: str, *args, **kwargs) -> None:
        self.input_queue.put(
            (priority, SonicAmpCommand(method_name=method_name, *args, **kwargs))
        )

    def add_important_job(self, method_name: str, *args, **kwargs) -> None:
        return self.add_job(0, method_name, method_args=args, method_kwargs=kwargs)


def main() -> None:
    # sonicagent = SonicInterface(port="COM6")
    sonicagent = SonicInterface(port="/dev/cu.usbserial-AB0M45SW")
    sonicagent.daemon = True
    sonicagent.start()
    sonicagent.resume()

    with sonicagent.ready_for_actions:
        sonicagent.ready_for_actions.wait()

    sonicagent.add_important_job("set_signal_off")
    sonicagent.add_important_job("get_overview")
    sonicagent.add_important_job("get_status")
    sonicagent.add_important_job("set_frequency", 1000000)
    sonicagent.add_important_job("get_modules")
    # sonicagent.add_important_job("ramp", 1000000, 2000000, 10000, 1000, "ms")
    sonicagent.add_important_job("ramp", 1000000, 2000000, 10000)
    sonicagent.add_important_job("ramp", 2000000, 1000000, 10000)
    # sonicagent.add_important_job("set_signal_auto")
    sonicagent.add_important_job("ramp", 1000000, 1055000, 10000, 5, "s", 5, "s")

    oldcommand = None
    hertz = 0
    mean_hertz = 0
    hertz_collection = []

    while True:
        if sonicagent.exceptions_queue.qsize():
            print(sonicagent.exceptions_queue.get())
        # sonicagent.add_important_job("get_status")
        # sonicagent.add_important_job("get_sens")
        prio, command = sonicagent.get_job()
        # if oldcommand:
        #     hertz = 1 / (command.timestamp - oldcommand.timestamp)
        #     hertz_collection.append(hertz)
        #     hertz_collection.pop(0) if len(hertz_collection) == 10 else None
        #     mean_hertz = sum(hertz_collection) / len(hertz_collection)
        print("Getting from SonicAgent")
        print(f"{command} with {mean_hertz} Hz")
        oldcommand = command


if __name__ == "__main__":
    main()
