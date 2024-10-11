import abc
from enum import Enum, IntEnum
from typing import Any, TypeVar

from sonic_protocol.defs import ConverterType, Version


class Converter(abc.ABC):
    @abc.abstractmethod
    def validate_val(self, value: Any) -> bool: ...

    @abc.abstractmethod
    def convert_val(self, value: Any) -> str: ...

    @abc.abstractmethod
    def validate_str(self, text: str) -> bool: ...

    @abc.abstractmethod
    def convert_str(self, text: str) -> Any: ...


class SignalConverter(Converter):
    def validate_val(self, value: Any) -> bool:
        return isinstance(value, bool)

    def convert_val(self, value: Any) -> str: 
        assert(self.validate_val(value))
        return "ON" if value else "OFF"

    def validate_str(self, text: str) -> bool: 
        return text.lower() in ["false", "true", "on", "off"]

    def convert_str(self, text: str) -> Any:
        assert(self.validate_str(text))
        return text.lower() in ["true", "on"]

class VersionConverter(Converter):
    def validate_val(self, value: Any) -> bool:
        return isinstance(value, Version)

    def convert_val(self, value: Any) -> str:
        assert (self.validate_val(value))
        return str(value)

    def validate_str(self, text: str) -> bool: 
        try:
            Version.to_version(text)
        except Exception as _:
            return False
        else:
            return True

    def convert_str(self, text: str) -> Any: 
        return Version.to_version(text)

class EnumConverter(Converter):
    def __init__(self, target_enum_class: type[Enum]):
        self._target_enum_class: type[Enum] = target_enum_class

    def validate_val(self, value: Any) -> bool: 
        return isinstance(value, Enum)

    def convert_val(self, value: Any) -> str: 
        assert (self.validate_val(value))
        return str(value.value)

    def validate_str(self, text: str) -> bool: 
        return text in [ str(enum_member.value) for enum_member in self._target_enum_class]

    def convert_str(self, text: str) -> Any: 
        assert(self.validate_str(text))
        if isinstance(self._target_enum_class, IntEnum):
            return self._target_enum_class(int(text))
        return self._target_enum_class(text)

class BuildTypeConverter(Converter):
    def validate_val(self, value: Any) -> bool:
        return isinstance(value, bool)

    def convert_val(self, value: Any) -> str: 
        assert(self.validate_val(value))
        return "RELEASE" if value else "BUILD"

    def validate_str(self, text: str) -> bool: 
        return text.lower() in ["release", "build"]

    def convert_str(self, text: str) -> Any:
        assert(self.validate_str(text))
        return text.lower() == "release"
    
T = TypeVar("T", int, str, bool, float)
class PrimitiveTypeConverter(Converter):
    def __init__(self, target_class: type[T]):
        self._target_class = target_class

    def validate_val(self, value: Any) -> bool: 
        return isinstance(value, self._target_class)

    def convert_val(self, value: Any) -> str: 
        assert (self.validate_val(value))
        return str(value)

    def validate_str(self, text: str) -> bool: 
        try:
            self._target_class(text)
        except Exception as _:
            return False
        else:
            return True

    def convert_str(self, text: str) -> Any: 
        return self._target_class(text)



def get_converter(converter_type: ConverterType, target_class: Any) -> Converter:
    match converter_type:
        case ConverterType.SIGNAL:
            return SignalConverter()
        case ConverterType.ENUM:
            assert(issubclass(target_class, Enum))
            return EnumConverter(target_class)
        case ConverterType.VERSION:
            return VersionConverter()
        case ConverterType.BUILD_TYPE:
            return BuildTypeConverter()
        case ConverterType.PRIMITIVE:
            return PrimitiveTypeConverter(target_class)
