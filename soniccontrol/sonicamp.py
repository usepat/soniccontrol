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

    def send_and_get(
        self, message: Union[str, Enum], delay: float = 0.3, flush: bool = True
    ) -> Union[str, list]:
        """A modified send_and_get function to manage the thread of the soniccontrol"""
        if self.thread.paused:
            answer: str = super().send_and_get(message, delay, flush)
        else:
            self.thread.pause()
            answer: str = super().send_and_get(message, delay, flush)
            self.thread.resume()
        
        return answer
    
    def send_get_for_threads(self, message: Union[str, Enum], delay: float = 0.3, flush: bool = True) -> Union[str, list]:
        return super().send_and_get(message, delay, flush)
