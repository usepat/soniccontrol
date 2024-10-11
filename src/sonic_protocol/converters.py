import abc
from typing import Any

from sonic_protocol.defs import ConverterType


class Converter(abc.ABC):
    @abc.abstractmethod
    def validate(self, value: Any) -> bool: ...

    @abc.abstractmethod
    def convert(self, value: Any) -> Any: ...


def get_converter(converter_type: ConverterType) -> Converter: ...
