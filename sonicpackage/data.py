import enum
from dataclasses import dataclass, field


class Command(enum.Enum):
    
    SET_SERIAL: str = "!SERIAL\n".encode()         #    
    SET_FRQ: str = "!f=".encode()
    SET_GAIN: str = "!g=".encode()
    SET_CURRENT1: str = "!cur1".encode()
    SET_CURRENT2: str = "!cur2".encode()
    SET_KHZ: str = "!KHZ\n".encode()
    SET_MHZ: str = "!MHZ\n".encode()
    SET_SIGNAL_ON: str = "!ON\n".encode()
    SET_SIGNAL_OFF: str = "!OFF\n".encode()
    SET_WIPE_INF: str = "!WIPE".encode()
    SET_WIPE_DEF: str = "!WIPE=".encode()
    SET_PROT: str = "!prot=".encode()
    SET_PROT_RANGE: str = "!rang=".encode()
    SET_PROT_STEP: str = "!step=".encode()
    SET_PROT_TIME_ON: str = "!sing=".encode()
    SET_PROT_TIME_OFF: str = "!paus=".encode()
    SET_AUTO: str = "!auto\n".encode()
    SET_PROT_FRQ1: str = "!atf1\n".encode()
    SET_PROT_FRQ2: str = "!atf2\n".encode()
    SET_PROT_FRQ3: str = "!atf3\n".encode()
    SET_TUNING_STEP: str = "!tust=".encode()
    SET_TUNING_PAUSE: str = "!tutm=".encode()
    SET_SCANNING_STEP: str = "!scst=".encode()
    SET_FLOW: str = "!flow=".encode()
    
    GET_INFO: str = "?info\n".encode()             #
    GET_TYPE: str = "?type\n".encode()    #
    GET_FRQ: str = "?freq\n".encode()
    GET_GAIN: str = "?gain\n".encode()
    GET_TEMP: str = "?temp\n".encode()
    GET_INT_TEMP: str = "?tpcb\n".encode()
    GET_CURRENT1: str = "?cur1\n".encode()
    GET_CURRENT2: str = "?cur2\n".encode()
    GET_SENS: str = "?sens\n".encode()
    GET_PROTOCOL: str = "?prot\n".encode()
    GET_PROTOCOL_LIST: str = "?list\n".encode()
    GET_PROT_FRQ1: str = "?atf1\n".encode()
    GET_PROT_FRQ2: str = "?atf2\n".encode()
    GET_PROT_FRQ3: str = "?atf3\n".encode()
    GET_PROT_VALUES: str = "?pval\n".encode()
    GET_OVERVIEW: str = "?\n".encode()
    GET_STATUS: str = "-\n".encode()
    GET_MODULES: str = "=\n".encode()
    
    def __add__(self, value: int):
        return self.value + f"{str(value)}\n".encode()


@dataclass
class SonicAmp:    
    
    port: str = field(default='-')
    amp_type: str = field(default=None)
    connection: str = field(default=False)
    signal: str = field(default=False)
    error: str = field(default=None)
    firmware: str = field(default=None)
    modules: object = field(default=None)
    status: object = field(default=None)    
    

@dataclass
class Modules:
    
    buffer: bool = field(default=False)
    display: bool = field(default=False)
    eeprom: bool = field(default=False)
    fram: bool = field(default=False)
    i_current: bool = field(default=False)
    current1: bool = field(default=False)
    current2: bool = field(default=False)
    io_serial: bool = field(default=False)
    thermo_ext: bool = field(default=False)
    thermo_int: bool = field(default=False)
    khz: bool = field(default=False)
    mhz: bool = field(default=False)
    portexpnder: bool = field(default=False)
    protocol: bool = field(default=False)
    protocol_fix: bool = field(default=False)
    relais: bool = field(default=False)
    sonsens: bool = field(default=False)
    scanning: bool = field(default=False)
    tuning: bool = field(default=False)
    switch: bool = field(default=False)
    switch2: bool = field(default=False)
    
    @classmethod
    def construct_from_str(cls, module_string: str) -> object:
        module_list = [bool(int(module)) for module in module_string.split('=')]
        obj = cls(module_list[0],
                  module_list[1],
                  module_list[2],
                  module_list[3],
                  module_list[4],
                  module_list[5],
                  module_list[6],
                  module_list[7],
                  module_list[8],
                  module_list[9],
                  module_list[10],
                  module_list[11],
                  module_list[12],
                  module_list[13],
                  module_list[14],
                  module_list[15],
                  module_list[16],
                  module_list[17],
                  module_list[18],
                  module_list[19],
                  module_list[20])
        return obj
    
    

@dataclass
class Status:
    
    error: int = field(default=False)
    frequency: int = field(default=False)
    gain: int = field(default=False)
    current_prtcl: int = field(default=False)
    wipe_mode: bool = field(default=False)

    @classmethod
    def construct_from_str(cls, status_str: str) -> object:
        try:
            status_list = [int(status) for status in status_str.split('-')]
            obj = cls(status_list[0], #error
                      status_list[1], #frequency
                      status_list[2], #gain
                      status_list[3], #current_prtcl
                      status_list[4]) #wipe_mode
        except:
            return None
        return obj