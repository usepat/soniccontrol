import threading
import queue
from abc import ABC, abstractclassmethod
from sonicpackage.amp_tools import Command

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
        """ Initializes the parent constructor with a worker function for the target """
        threading.Thread.__init__(self, target=self._run)
        self.paused: bool = False
        self.pause_cond: threading.Condition = threading.Condition(threading.Lock())
        self.queue: queue.Queue = queue.Queue()
        
    @abstractclassmethod
    def run(self) -> None:
        """ The worker function itself, that must be implemented in a concrete class"""
        pass
    
    def pause(self) -> None:
        """  Function to pause the thread """
        self.paused = True
        self.pause_cond.acquire()
        # print(f"im pausing myself {self.getName()}")
        
        
    def resume(self) -> None:
        """ Function to resume the thread """
        self.paused = False
        self.pause_cond.notify()
        self.pause_cond.release()
        # print(f"im resuming myself {self.getName()}")


class SonicAgent(SonicThread):
    """
    The SonicAgent sends the Command.GET_STATUS command to get the status data
    from a SonicAmp. It puts that data into the inhereted queue.
    Furthermore it has access to the serial connection through it's parameters
    """
    @property
    def serial(self):
        """ The serial communication object """
        return self._serial
    
    def __init__(self, serial: object) -> None:
        super().__init__(self)
        self._serial: object = serial
        
    
    def run(self) -> None:
        while True:
            # in case the thread is paused
            with self.pause_cond:
                while self.paused:
                    self.pause_cond.wait()
                
                # thread should not try to do something if paused
                # in case not paused
                if self.serial.is_open:
                    try:
                        data_str = self.serial.send_and_get(Command.GET_STATUS)
                        if len(data_str) > 1:
                            self.queue.put(data_str)
                    except:
                        print("Not the value I was looking for")
                else:
                    self.pause_cond.wait()