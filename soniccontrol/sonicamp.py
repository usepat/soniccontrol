from typing import TYPE_CHECKING

from sonicpackage import SerialConnection, SonicThread
from sonicpackage import Enum
from sonicpackage import Union


class SerialConnectionGUI(SerialConnection):
    """A modified SerialConnection class for the soniccontrol to manage
    the thread of Root. Therefore, you need the to pass in a SonicThread
    thread into the constructor of the class 

    Args:
        SerialConnection (_type_): _description_
    """
    def __init__(self, thread: SonicThread, baudrate: int = 115200) -> None:
        super().__init__(baudrate)
        
        self.thread: SonicThread = thread
    
    def send_and_get(self, message: Union[str, Enum], delay: float = 0.3, flush: bool = True) -> Union[str, list]:
        """A modified send_and_get function to manage the thread of the soniccontrol"""
        return super().send_and_get(message, delay, flush)
        
    def send_get(self, message: Union[str, Enum], delay: float = 0.1, flush: bool = True) -> Union[str, list]:
        """A modified send_and_get method for the sonicagent thread"""
        self.thread.pause()
        answer = super().send_and_get(message, delay, flush)
        self.thread.resume()
        return answer
        