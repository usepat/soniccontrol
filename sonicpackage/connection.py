from ast import Try
import serial
import serial.tools.list_ports
import time
import queue
import threading

from data import Command
from sonicpackage.threads import SonicThread

class SerialConnection():

    @property
    def is_connected(self):
        return self._is_connected
    
    @is_connected.setter
    def is_connected(self, mode: bool):
        self._is_connected = mode

    @property
    def port(self):
        return self._port
    
    @port.setter
    def port(self, port: str):
        self._port = port
        
    @property
    def baudrate(self):
        return self._baudrate
    
    @baudrate.setter
    def baudrate(self, baudrate: int):
        self._baudrate = baudrate

    def __init__(self):
        self._port: str
        self._baudrate: int = 115200
        self._is_connected: bool = False
        self.ser: object
        self.device_list: list = self.get_ports()

    
    def get_ports(self) -> list:              
        port_list = [port.device for index, port in enumerate(serial.tools.list_ports.comports(), start=0) if port.device != 'COM1']
        port_list.insert(0, '-')
        self.device_list = port_list
        return port_list


    def auto_connect(self) -> None:
        if len(self.device_list) == 2:
            self.port = self.device_list[1]
            self.ser = serial.Serial(self.port, self.baudrate, timeout=0.1)    
            self.is_connected = True
            time.sleep(6)
            init_answer = self.ser.read_until(b"READY")
            init_answer = self.ser.readline()


    def connect_to_port(self, port: str=None) -> None:
        self.ser = serial.Serial(port, self.baudrate, timeout=0.1)
        self.is_connected = True
        self.port = port
        time.sleep(6)
        init_answer = self.ser.read_until(b"READY")
        init_answer = self.ser.readline()

        
    def send_command(self, command: Command, delay: float=0.1, flush=True) -> None:
        if flush:
            self.ser.flush()
        
        if self.ser.is_open:
            try:
                print(f'Sende nachricht: {command.value}')
                self.ser.write(command.value)
            except AttributeError:
                print(f'Sende nachricht: {command}')
                self.ser.write(command)
            
            time.sleep(delay)
            

    
    def get_answerline(self) -> str:
        answer = self.ser.readline().rstrip().decode()
        print(answer)
        return answer

    
    def get_answerblock(self) -> str:
        answer = self.ser.read(255).rstrip().decode()
        print(answer)
        return answer


    def send_and_get(self, command: Command) -> str:
        self.send_command(command)
        return self.get_answerline()
    
    
    def send_and_get_block(self, command: Command) -> str:
        self.send_command(command)
        return self.get_answerblock()
    
    
    def threaded_sendget(self, command: Command, thread: SonicThread):
        thread.pause()
        answer = self.send_and_get(command)
        thread.resume()
        return answer
    
    
    def disconnect(self) -> None:
        self.ser.close()
        self.is_connected = False
        







