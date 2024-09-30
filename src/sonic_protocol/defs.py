from enum import Enum
from typing import Any, Dict, List, Tuple, Type, TypeVar, Generic
import attrs


T = TypeVar("T", int, float, str)
Reference = str


class DeviceType(Enum):
    DESCALE = 0
    CATCH = 1
    MVP_WORKER = 2

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
    


@attrs.define()
class CommandParamDef(Generic[T]):
    param_type: Type[T] = attrs.field()
    default_value: T = attrs.field()
    si_unit: SIUnit | None = attrs.field(default=None)
    si_prefix: SIPrefix | None = attrs.field(default=None)
    min_value: T | None = attrs.field(default=None)
    max_value: T | None = attrs.field(default=None)
    allowed_values: List[T] | None = attrs.field(default=None) # can we do this better with enum support?
    description: str | None = attrs.field(default=None)

@attrs.define()
class CommandDef:
    string_identifier: str = attrs.field()
    aliases: List[str] = attrs.field(default=[])
    index_param: CommandParamDef | Reference | None = attrs.field(default=None)
    setter_param: CommandParamDef | Reference | None = attrs.field(default=None)

@attrs.define()
class AnswerFieldDef(Generic[T]):
    field_name: str = attrs.field()
    field_type: Type[T] = attrs.field()
    converter_ref: Reference | None = attrs.field(default=None) # converters are defined in the code and the json only references to them
    si_unit: SIUnit | None = attrs.field(default=None)
    si_prefix: SIPrefix | None = attrs.field(default=None)
    format_str: str = attrs.field(default="%s") # Maybe format strings are not good to parse on the firmware side.
    description: str | None = attrs.field(default=None)

@attrs.define()
class AnswerDef:
    fields: List[AnswerFieldDef | Reference] = attrs.field()

@attrs.define()
class MetaExportDescriptor:
    min_protocol_version: Version = attrs.field()
    deprecated_protocol_version: Version | None = attrs.field(default=None)
    included_device_types: List[DeviceType] | None = attrs.field(default=None)
    excluded_device_types: List[DeviceType] | None = attrs.field(default=None)

E = TypeVar("E")
@attrs.define()
class MetaExport(Generic[E]):
    exports: E = attrs.field()
    descriptor: MetaExportDescriptor = attrs.field()

@attrs.define()
class Command:
    code: int = attrs.field()
    command_defs: List[MetaExport[CommandDef] | CommandDef] = attrs.field()
    answer_defs: List[MetaExport[AnswerDef] | AnswerDef] = attrs.field()
    description: str | None = attrs.field(default=None)
    tags: List[str] = attrs.field(default=[])

CommandExport = MetaExport[Command]
CommandListExport = MetaExport[List[Command]]

@attrs.define()
class Protocol:
    version: Version = attrs.field()
    commands: List[CommandExport | CommandListExport] = attrs.field()

