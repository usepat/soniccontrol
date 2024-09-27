from enum import Enum
from typing import Dict, List, Tuple, Type, TypeVar, Generic
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

@attrs.define()
class Version:
    MAJOR: int = attrs.field()
    MINOR: int = attrs.field()
    PATCH: int = attrs.field()
    # TODO: make that the version can be converted to a list and created from a list by default

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


E = TypeVar("E", AnswerDef, CommandDef, "Command")
@attrs.define()
class MetaExportDescriptor(Generic[E]):
    export: E = attrs.field()
    min_protocol_version: Version = attrs.field()
    deprecated_protocol_version: Version | None = attrs.field(default=None)
    included_device_types: List[DeviceType] | None = attrs.field(default=None)
    excluded_device_types: List[DeviceType] | None = attrs.field(default=None)


@attrs.define()
class Command:
    code: int = attrs.field()
    command_defs: List[MetaExportDescriptor[CommandDef] | CommandDef] = attrs.field()
    answer_defs: List[MetaExportDescriptor[AnswerDef] | AnswerDef] = attrs.field()
    description: str | None = attrs.field(default=None)
    tags: List[str] = attrs.field(default=[])

@attrs.define()
class Protocol:
    version: Version = attrs.field()
    commands: List[MetaExportDescriptor[Command]] = attrs.field()
    command_param_defs: Dict[Reference, CommandParamDef] = attrs.field(default={})
    answer_field_defs: Dict[Reference, AnswerFieldDef] = attrs.field(default={})

