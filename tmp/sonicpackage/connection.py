from ctypes import LittleEndianStructure
from os import stat
import serial
import serial.tools.list_ports
import time
import sys
import signal
import queue



class SerialConnection():

    LINE = 'line'
    BLOCK = 'block'

    def __init__(self):
        self.device_list = self.get_ports()
        self.port = ''
        self.baudrate = 115200
        self.is_connected = False
        self.queue = queue.Queue()


    def get_ports(self):
        return [port.device for index, port in enumerate(serial.tools.list_ports.comports(), start=0) if port.device != 'COM1']


    def connect_to_port(self, auto=False, port=None):
        try:
            if len(self.device_list) == 1 and auto == True:
                self.port = self.device_list[0]
                self.ser = serial.Serial(self.port, self.baudrate, timeout=0.3)    
            elif port:
                self.ser = serial.Serial(port, self.baudrate, timeout=0.3)
            else:
                print("error")
                raise Exception

            self.is_connected = True
            time.sleep(5)
            self.initialize()
        
        except:
            self.is_connected = False
            return False
    

    def initialize(self):
        self.send_message('!SERIAL', SerialConnection.LINE, True, 0.5)
        


    def send_message(self, message, read_mode='line', flush=False, delay=0.1):
        try:
            if self.ser.is_open:
                if flush:
                    self.ser.flushInput()
                
                self.ser.write(f"{message}\n".encode())
                time.sleep(delay)
                
                if read_mode == SerialConnection.LINE:
                    return self.ser.readline().rstrip().decode()
                
                else:
                    return self.ser.read(255).rstrip().decode()
            
            else:
                return False
        
        except:
            pass


    def connection_worker(self):
        while self.is_connected:
            time.sleep(0.1)
            status = [int(statuspart) for statuspart in self.send_message('-').split('-')]
            if len(status) > 1:
                self.queue.put(status)
    
    
    def disconnect(self):
        self.ser.close()


        
class SonicAmp(SerialConnection):

    def __init__(self):
        super().__init__()
 
        self.info = {}
        self.modules = {}


    def get_info(self):
        if self.is_connected:
            self.info = {
                'port':     self.port,
                'type':     self.send_message('?type', flush=True, delay=0),
                'firmware': self.send_message('?info', read_mode='block', flush=True, delay=0.5),
                'modules' : self.get_modules([bool(int(module)) for module in self.send_message('=', delay=0.35).split('=')]),
                'status':   {}
            }
        else:
            self.info = {
                'port':     self.port,
                'type':     'not connected',
                'firmware': False,
                'modules':  False,
                'status':   False
            }

    
    def get_modules(self, module_list):
        self.modules = { 
            'buffer':       module_list[0],
            'DISPLAY':      module_list[1],
            'EEPROM':       module_list[2],
            'FRAM':         module_list[3],
            'I_CURRENT':    module_list[4],
            'CURRENT1':     module_list[5],
            'CURRENT2':     module_list[6],
            'IO_SERIAL':    module_list[7],
            'THERMO_EXT':   module_list[8],
            'THERMO_INT':   module_list[9],
            'KHZ':          module_list[10],
            'MHZ':          module_list[11],
            'PORTEXPANDER': module_list[12],
            'PROTOCOL':     [self.get_protocols(module_list[13])],
            'PROTOCOL_FIX': module_list[14],
            'RELAIS':       module_list[15],
            'SONSENS':      module_list[16],
            'SCANNING':     module_list[17],
            'TUNING':       module_list[18],
            'SWITCH':       module_list[19],
            'SWITCH2':      module_list[20],
        }

        return self.modules

    
    def get_status(self, status):
        self.info['status'] = {
            'error':            status[0],
            'frequency':        status[1],
            'gain':             status[2],
            'current_protocol': self.get_current_protocol(status[3]),
            'wipe_mode':        bool(status[4])

        }
        return self.info['status']
    

    def get_current_protocol(self, protocol_string):
        if protocol_string == 100:
            return 'fix'
        elif protocol_string == 101:
            return None
        else:
            return int(protocol_string)


    def get_protocols(self, protocols):
        return protocols


