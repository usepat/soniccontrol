from enum import Enum, IntEnum
from typing import Any, Dict, List, Tuple, Type, TypeVar, Generic
import attrs


T = TypeVar("T", int, float, str)


@attrs.define(order=True) # order True, lets attrs define automatically comparision methods
class Version:
    major: int = attrs.field()
    minor: int = attrs.field()
    patch: int = attrs.field()
    # TODO: make that the version can be converted to a list and created from a list by default

    def __iter__(self):
        return iter((self.major, self.minor, self.patch))
    
    def __str__(self) -> str:
        return f"v{self.major}.{self.minor}.{self.patch}"
    
    @staticmethod
    def to_version(x: Any) -> "Version":
        if isinstance(x, str):
            if x[0] == "v":
                x = x[1:]
            version = tuple(map(int, x.split(".")))
            if len(version) != 3:
                raise ValueError("The Version needs to have exactly two separators '.'")
            return Version(*version)
        elif isinstance(x, tuple):
            return Version(*x)
        else:
            raise TypeError("The type cannot be converted into a version")


class DeviceType(Enum):
    DESCALE = 0
    CATCH = 1
    MVP_WORKER = 2



class CommandCode(IntEnum):
    INVALID = 0
    UNIMPLEMENTED = 1
    SHUT_DOWN = 2
    LIST_AVAILABLE_COMMANDS = 3
    GET_HELP = 4
    # NOTIFY = 5 (commented out in the original)
    EQUALSIGN = 10
    DASH = 20

    QUESTIONMARK = 30
    GET_INFO = 40
    GET_FREQ = 50
    GET_GAIN = 60
    GET_TEMP = 70
    GET_TMCU = 80
    GET_UIPT = 90
    GET_ADC = 100
    GET_PROT = 110
    GET_PROT_LIST = 120
    GET_PVAL = 130
    GET_ATF = 140
    GET_TON = 150
    GET_ATK = 160
    GET_ATT = 171
    GET_SWF = 180
    GET_AUTO = 210
    GET_SCAN = 300
    GET_TUNE = 310
    GET_WIPE = 320

    SET_EXTERN = 1010
    SET_ANALOG = 1020
    SET_DAC0 = 1031
    SET_DAC1 = 1032
    SET_KHZ = 1040
    SET_FREQ = 1050
    SET_GAIN = 1060
    SET_MHZ = 1070
    SET_ON = 1080
    SET_OFF = 1090
    SET_WIPE = 1100
    SET_PROC = 1110
    SET_WIPE_X = 1120
    SET_RAMP = 1130
    SET_ATF = 1140
    SET_TON = 1150
    SET_TOFF = 1151
    SET_ATK = 1160
    SET_AUTO = 1210
    SET_RAMPD = 1220
    SET_SWF = 1260
    SET_TERMINATION = 1270
    SET_COM_PROT = 1280
    SET_RS485 = 1290 
    SET_SCAN = 1300
    SET_TUNE = 1310
    SET_GEXT = 1320
    SET_ATT = 1330

    SET_MANUAL = 5000
    SET_DEFAULT = 6000
    SET_FLASH_USB = 7001
    SET_FLASH_9600 = 7002
    SET_FLASH_115200 = 7003
    SET_NOTIFY = 999
    SET_DUTY_CYCLE = 8000
    SET_LOG_DEBUG = 9000
    SET_LOG_INFO = 10000
    SET_LOG_WARN = 11000
    SET_LOG_ERROR = 12000
    SET_SCAN_F_RANGE = 13000 
    SET_SCAN_F_STEP = 13001
    SET_SCAN_T_STEP = 13002
    SET_TUNE_F_STEP = 13003
    SET_TUNE_T_TIME = 13004
    SET_TUNE_T_STEP = 13005
    SET_WIPE_F_RANGE = 13006
    SET_WIPE_F_STEP = 13007
    SET_WIPE_T_ON = 13008
    SET_WIPE_T_OFF = 13009
    SET_WIPE_T_PAUSE = 13010
    SET_RAMP_F_START = 13011
    SET_RAMP_F_STOP = 13012
    SET_RAMP_F_STEP = 13013
    SET_RAMP_T_ON = 13014
    SET_RAMP_T_OFF = 13015



class SIUnit(Enum):
    METER = "m"
    SECONDS = "s"
    HERTZ = "Hz"
    CELSIUS = "C°"
    VOLTAGE = "V"
    AMPERE = "A"
    RAD = "°"

class SIPrefix(Enum):
    NANO  = 'n'   # 10⁻⁹
    MICRO = 'µ'   # 10⁻⁶
    MILLI = 'm'   # 10⁻³
    NONE  = ''    # 10⁰ (base unit, no prefix)
    KILO  = 'k'   # 10³
    MEGA  = 'M'   # 10⁶
    GIGA  = 'G'   # 10⁹


class ConverterType(Enum):
    SIGNAL = 0


@attrs.define()
class CommandParamDef(Generic[T]):
    param_type: type[T] = attrs.field()
    allowed_values: List[T] | None = attrs.field(default=None) # can we do this better with enum support?
    si_unit: SIUnit | None = attrs.field(default=None)
    si_prefix: SIPrefix | None = attrs.field(default=None)
    description: str | None = attrs.field(default=None)

@attrs.define()
class CommandDef:
    string_identifier: str | List[str] = attrs.field()
    index_param: CommandParamDef | None = attrs.field(default=None)
    setter_param: CommandParamDef | None = attrs.field(default=None)

@attrs.define()
class AnswerFieldDef(Generic[T]):
    field_name: str = attrs.field()
    field_type: type[T] = attrs.field()
    allowed_values: List[T] | None = attrs.field(default=None)
    converter_ref: ConverterType | None = attrs.field(default=None) # converters are defined in the code and the json only references to them
    si_unit: SIUnit | None = attrs.field(default=None)
    si_prefix: SIPrefix | None = attrs.field(default=None)
    prefix: str = attrs.field(default="")
    postfix: str = attrs.field(default="")
    description: str | None = attrs.field(default=None)

@attrs.define()
class AnswerDef:
    fields: List[AnswerFieldDef] = attrs.field()

@attrs.define()
class MetaExportDescriptor:
    min_protocol_version: Version = attrs.field()
    deprecated_protocol_version: Version | None = attrs.field(default=None)
    included_device_types: List[DeviceType] | None = attrs.field(default=None)
    excluded_device_types: List[DeviceType] | None = attrs.field(default=None)

    def is_valid(self, version: Version, device_type: DeviceType) -> bool:
        if self.min_protocol_version > version:
            return False
        if self.deprecated_protocol_version and self.deprecated_protocol_version <= version:
            return False
        if self.included_device_types and device_type not in self.included_device_types:
            return False
        if self.excluded_device_types and device_type in self.excluded_device_types:
            return False
        return True

E = TypeVar("E")
@attrs.define()
class MetaExport(Generic[E]):
    exports: E = attrs.field()
    descriptor: MetaExportDescriptor = attrs.field()

@attrs.define()
class CommandContract:
    code: CommandCode = attrs.field()
    command_defs: List[MetaExport[CommandDef] | CommandDef] = attrs.field()
    answer_defs: List[MetaExport[AnswerDef] | AnswerDef] = attrs.field()
    description: str | None = attrs.field(default=None)
    is_release: bool = attrs.field(default=False) # some commands are only for debugging. They should not be included in release
    tags: List[str] = attrs.field(default=[])

CommandExport = MetaExport[CommandContract]
CommandListExport = MetaExport[List[CommandContract]]

@attrs.define()
class Protocol:
    version: Version = attrs.field()
    commands: List[CommandExport | CommandListExport] = attrs.field()

