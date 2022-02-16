
import time
import serial
import serial.tools.list_ports
from abc import ABC, abstractclassmethod, abstractmethod
from sonicpackage.amp_tools import Command, SonicAmpData, Modules, Status
from sonicpackage.helpers import threaded, validate_connection

class SonicAmp(ABC):
    """
    Class that directs and handles the data
    """
    @property
    def serial(self):
        return self._serial

    def __init__(self, serial: object) -> None:
        """ 
        The first parameter is the serial communcation itself
        Then follows the other parameters used to construct a SonicAmp
        """
        self._serial: SerialConnection = serial
        self.data: SonicAmp
        self.initialize_amp()

    @abstractclassmethod
    def start(cls) -> object:
        """ 
        Constructs a SonicAmp object with a serial communication 
        without passing an existing serial interface
        
        Returns said object
        """
        pass
        
    @abstractmethod
    def initialize_amp(self) -> None:
        """ Initializes the amp and all the dataclasses that are used """
        pass
    
    def set_serial(self) -> bool:
        """ Sets the SonicAmp to serial mode """
        self.serial.send_and_get(Command.SET_SERIAL)

    def set_frq(self, frequency: int = 0) -> bool:
        """ Sets the frequency of an amp to the given frequency """
        self.serial.send_and_get(Command.SET_FRQ + frequency)
    
    def set_signal_on(self) -> bool:
        """ Turns the ultrasound signal of a sonicamp on """
        self.serial.send_and_get(Command.SET_SIGNAL_ON)
    
    def set_signal_off(self) -> bool:
        """ Turns the ultrasound signal of a sonicamp off """
        self.serial.send_and_get(Command.SET_SIGNAL_OFF)
    
    def set_prot_range(self, prot_range: int) -> bool:
        """ Sets the frequency range for protocols """
        self.serial.send_and_get(Command.SET_PROT_RANGE + prot_range)
    
    def set_prot_step(self, step: int) -> bool:
        """ Sets the step range for protocols """
        self.serial.send_and_get(Command.SET_PROT_STEP + step)
    
    def set_prot_time_on(self, time: int) -> bool:
        """ Sets the time for signal on for protocol """
        self.serial.send_and_get(Command.SET_PROT_TIME_ON + time)
    
    def set_prot_time_off(self, time: int) -> bool:
        """ Sets the time for signal off for protocol """
        self.serial.send_and_get(Command.SET_PROT_TIME_OFF + time)
    
    def get_info(self) -> str:
        """ Gets the firmware info from the sonicamp """
        return self.serial.send_and_get(Command.GET_INFO)
    
    def get_type(self) -> str:
        """ Gets the type from the sonicamp """
        return self.serial.send_and_get(Command.GET_TYPE)
    
    def get_frq(self) -> str:
        """ Gets the current frequency from a SonicAmp """
        return self.serial.send_and_get(Command.GET_FRQ)
    
    def get_prot_frq1(self) -> str:
        """ Gets the 1st protocol frequency """
        return self.serial.send_and_get(Command.GET_PROT_FRQ1)

    def get_prot_frq2(self) -> str:
        """ Gets the 2nd protocol frequency """
        return self.serial.send_and_get(Command.GET_PROT_FRQ2)

    def get_prot_frq3(self) -> str:
        """ Gets the 3rd protocol frequency """
        return self.serial.send_and_get(Command.GET_PROT_FRQ3)
    
    def get_prot_values(self) -> str:
        """ Gets the values for the protocol """
        return self.serial.send_and_get(Command.GET_PROT_VALUES)
    
    def get_overview(self) -> str:
        """ Gets the overview on the progress state """
        return self.serial.send_and_get(Command.GET_OVERVIEW)

    def ramp(self, start_frq: int, stop_frq: int, step_frq: int, time_delay: float=0.1) -> None:
        for frq in range(start_frq, stop_frq, step_frq):
            self.set_frq(frq)
            time.sleep(time_delay)



class SonicCatch(SonicAmp):
    
    def __init__(self, serial: object) -> None:
        super().__init__(serial)
        
    @classmethod    
    def start(cls) -> object:
        serial: SerialConnection = SerialConnection()
        if serial.auto_connect():
            obj = cls(serial)
            return obj
        
    def initialize_amp(self) -> None:
        if self.serial.is_connected:
            self.set_serial()
            self.data: SonicAmp = SonicAmp(
                    port = self.serial.serial.port,
                    amp_type = self.get_type(),
                    connection = "Connected",
                    firmware = self.get_info(),
                    modules = Modules.construct_from_str(
                        self.serial.send_and_get(Command.GET_MODULES)),
                    status = Status.construct_from_str(
                        self.serial.send_and_get(Command.GET_STATUS)))
        else:
            pass
    
    def set_gain(self, gain: int = 0) -> bool:
        """ Sets the gain of an amp to the given value """
        self.serial.send_and_get(Command.SET_GAIN + gain)
        
    def set_khz(self) -> bool:
        """ Sets the SonicCatch to kHz range """
        self.serial.send_and_get(Command.SET_KHZ)
        
    def set_mhz(self) -> bool:
        """ Sets the SonicCatch to MHz range """
        self.serial.send_and_get(Command.SET_MHZ)
        return True

    def set_current1(self, current: float) -> bool:
        """ Sets the current from interface 1 to the given value"""
        self.serial.send_and_get(Command.SET_CURRENT1 + current)
        
    def set_current2(self, current: float) -> bool:
        """ Sets the current from interface 2 to the given value"""
        self.serial.send_and_get(Command.SET_CURRENT2 + current)
    
    def set_auto_mode(self) -> bool:
        """ Sets a soniccatch to auto mode """
        self.serial.send_and_get(Command.SET_AUTO)
    
    def set_tuning_step(self, hertz: int) -> bool:
        """ Sets the tuning steps in Hz """
        self.serial.send_and_get(Command.SET_TUNING_STEP + hertz)
        
    def set_tuning_pause(self, milliseconds: int) -> bool:
        """ Sets the tuning pause in milliseconds """
        self.serial.send_and_get(Command.SET_TUNING_PAUSE + milliseconds)
        
    def set_scanning_step(self, hertz: int) -> bool:
        """ Sets the scanning step in hertz """
        self.serial.send_and_get(Command.SET_SCANNING_STEP + hertz)
        
    def get_gain(self) -> int:
        """ Gets the current gain of the SonicCatch """
        answer = self.serial.send_and_get(Command.GET_GAIN)
        return int(answer)

    def get_temperature(self) -> int:
        """ Gets the value from the PT100 in a Soniccatch """
        return self.serial.send_and_get(Command.GET_TEMP)



class SonicWipe(SonicAmp):
    
    def __init__(self, serial: object) -> None:
        super().__init__(serial)
        
    @classmethod
    def start(cls) -> object:
        serial: SerialConnection = SerialConnection()
        if serial.auto_connect():
            obj = cls(serial)
            return obj
    
    def initialize_amp(self) -> None:
        if self.serial.is_connected:
            self.set_serial()
            self.data: SonicAmp = SonicAmp(
                    port = self.serial.serial.port,
                    connection = "Connected",
                    firmware = self.serial.send_and_get(Command.GET_INFO),
                    modules = Modules.construct_from_str(
                        self.serial.send_and_get(Command.GET_MODULES)),
                    status = Status.construct_from_str(
                        self.serial.send_and_get(Command.GET_STATUS)))
        else:
            pass
    
    def set_wipe(self, cycles: int) -> bool:
        """ Sets the wipe mode of a sonicwipe """
        if cycles:
            self.serial.send_and_get(Command.SET_WIPE_DEF + cycles)
        else:
            self.serial.send_and_get(Command.SET_WIPE_INF)
    
    def set_protocol(self, protocol: int) -> bool:
        """ Sets the protocol of a sonicwipe """
        self.serial.send_and_get(Command.SET_PROT + protocol)

    def get_protocol(self) -> str:
        """ Gets the current protocol """
        self.serial.send_and_get(Command.GET_PROTOCOL)
    
    def get_prot_list(self) -> str:
        """ Gets a list of available protocols from a sonicwipe """
        self.serial.send_and_get(Command.GET_PROTOCOL_LIST)



class Validator:

    @property
    def serial(self) -> object:
        return serial

    def __init__(self, serial: object) -> None:
        self._serial: SerialConnection = serial
        
    def checkout_amp(self) -> None:
        status_str: str = self.serial.send_and_get(Command.GET_STATUS)        
        status = Status.construct_from_str(status_str=status_str)
    
    



class SerialConnection:
    """
    This class handles the serial connection with a Sonicamp
    """
    @property
    def is_connected(self):
        return self._is_connected
    
    def __init__(self) -> None:
        self.serial: serial.Serial
        self.baudrate: int = 115200
        self._is_connected: bool = False
        self.device_list: list = self.get_ports()
    
    def get_ports(self) -> list:
        """ Gets all the possible serial ports and inserts them into a list """
        port_list: list = [port.device for index, port in enumerate(serial.tools.list_ports.comports(), start=0) if port.device != 'COM1']
        port_list.insert(0, '-')
        self.device_list = port_list
        return port_list

    def connect_to_port(self, port: str) -> bool:
        """ Connects to a given port-address (string) """
        self.serial = serial.Serial(port, self.baudrate, timeout=0.1)
        if self.serial.is_open:
            self._is_connected = True
            time.sleep(5)
            tmp = self.serial.read_until(b"!")
            print(tmp)
            return True
        else:
            return False

    def auto_connect(self) -> bool:
        """
        Tries to auto connect to a serial interface, 
        if there is only one to choose from
        """
        if len(self.device_list) == 2:
            self.serial = serial.Serial(self.device_list[1], self.baudrate, timeout=0.1)
            if self.serial.is_open:
                time.sleep(5)
                tmp = self.serial.read_until(b"!")
                print(tmp)
                return True
            else:
                return False
    
    def disconnect(self) -> None:
        self.serial.close()
        self._is_connected = False
    
    def send_message(self, command: Command, flush: bool=True, delay: float = 0.3) -> None:
        """ Sends a message to a SonicAmp """
        if flush:
            self.serial.flush()
        if self.serial.is_open:
            try:
                self.serial.write(command.value)
                print(f"sending: {command.value}")
            # in case the __add__ method is used in the Command class
            except AttributeError:
                print(f"sending: {command}")
                self.serial.write(command)
            time.sleep(delay)

    def get_answer(self) -> str:
        """ Reads a line from the buffer of a SonicAmp and returns it in form of a string """
        answer: str = self.serial.readline().rstrip().decode()
        print(f"received: {answer}")
        return answer
    
    def send_and_get(self, command: Command) -> str:
        """ Sends a command and returns the corresponding answer """
        self.send_message(command)
        print(f"receiving answer from {command}")
        return self.get_answer()

    def sc_sendget(self, command: Command, thread: object):
        """ send_and_get function, but it handles an agent in the meantime """
        thread.pause()
        answer: str = self.send_and_get(command)
        thread.resume()
        return answer
    