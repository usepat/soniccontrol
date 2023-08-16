from __future__ import annotations
import threading
import queue
from abc import ABC, abstractmethod
from typing import Any, Tuple, Type
from types import TracebackType
from sonicpackage.helpers import logger
from soniccontrol.sonicamp.serial_interface import Command


class SonicThread(ABC, threading.Thread):
    """
    Abstract class for threads that are used in the sonicpackage
    This class inherets from the threading.Thread object and builds
    it's own methods to run, pause or resume a thread. Moreover it
    contains it's own queue object, that can be used for transfering data
    """

    @property
    def _run(self):
        return self.run

    def __init__(self) -> None:
        """Initializes the parent constructor with a worker function for the target"""
        threading.Thread.__init__(self, target=self._run)
        self.pause_request: threading.Event = threading.Event()
        self.shutdown_request: threading.Event = threading.Event()
        self.pause_cond: threading.Condition = threading.Condition(threading.Lock())

        self.output_queue: queue.PriorityQueue[Any] = queue.PriorityQueue()
        self.input_queue: queue.PriorityQueue[Any] = queue.PriorityQueue()
        self.exceptions_queue: queue.Queue[
            Tuple[
                Type[BaseException],
                BaseException,
                TracebackType,
            ]
        ] = queue.Queue()

        self.pause()

    def run(self) -> None:
        """The worker function itself, that must be implemented in a concrete class"""
        self.setup()
        while not self.shutdown_request.is_set():
            with self.pause_cond:
                while self.pause_request.is_set():
                    self.pause_cond.wait()
                self.worker()

    @abstractmethod
    def setup(self) -> None:
        ...

    @abstractmethod
    def worker(self) -> None:
        ...

    def shutdown(self) -> None:
        logger.debug("Shutdown requested")
        self.shutdown_request.set()

    def add_job(self, command: Command, priority: int) -> None:
        self.input_queue.put((priority, command))

    def pause(self) -> None:
        """Function to pause the thread"""
        if self.pause_request.is_set():
            return
        self.pause_request.set()
        self.pause_cond.acquire()
        logger.debug("Pausing thread")

    def resume(self) -> None:
        """Function to resume the thread"""
        if not self.pause_request.is_set():
            return
        self.pause_request.clear()
        self.pause_cond.notify()
        self.pause_cond.release()
        logger.debug("Resuming thread")
