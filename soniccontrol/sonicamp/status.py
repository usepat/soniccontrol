from __future__ import annotations
from typing import Any, Iterable, Union, Optional, Dict
import abc
import datetime
from dataclasses import dataclass, field


class StatusAdapter(abc.ABC):
    def __init__(self) -> None:
        super().__init__()

    @abc.abstractmethod
    def convert_data(self, data: str) -> Iterable[Any]:
        ...

    @abc.abstractmethod
    def update_data(self, old_status: Status, data: str) -> Iterable[Any]:
        ...


class BasicStatusAdapter(StatusAdapter):
    def __init__(self) -> None:
        super().__init__()

    def convert_data(self, data: str) -> Iterable[Any]:
        return (0, 0, 0, 0, 0, 0)


@dataclass
class Data:
    type_: str = field(default="")
    version: float = field(default=0.0)
    firmware_msg: str = field(default="")
    modules: Optional[Modules] = field(default=None)
    status: Optional[Status] = field(default=None)


@dataclass
class Status:
    error: int = field(default=0, repr=False)
    frequency: int = field(default=0)
    gain: int = field(default=0)
    current_protocol: int = field(default=0, repr=False)
    wipe_mode: bool = field(default=False, repr=False)
    temperature: float = field(default=0)
    signal: bool = field(default=False)
    urms: Union[float, int] = field(default=0)
    irms: Union[float, int] = field(default=0)
    phase: Union[float, int] = field(default=0)
    timestamp: datetime.datetime = field(
        default_factory=datetime.datetime.now, compare=False
    )
    default_adapter: StatusAdapter = field(
        default_factory=BasicStatusAdapter, repr=False, compare=False, hash=False
    )

    @classmethod
    def from_data(cls, data: str, adapter: Optional[StatusAdapter] = None) -> Status:
        return cls(
            *adapter.convert_data(data)
            if adapter
            else cls.default_adapter.convert_data(data)
        )

    @classmethod
    def from_updated_data(
        cls,
        old_status: Status,
        data: str,
        adapter: Optional[StatusAdapter] = None,
    ) -> Status:
        return cls(
            *adapter.update_data(old_status, data)
            if adapter
            else cls.default_adapter.update_data(old_status, data)
        )

    def dump(self) -> Dict[str, Any]:
        return self.__dict__


@dataclass(frozen=True)
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
    portexpander: bool = field(default=False)
    protocol: bool = field(default=False)
    protocol_fix: bool = field(default=False)
    relais: bool = field(default=False)
    scanning: bool = field(default=False)
    sonsens: bool = field(default=False)
    tuning: bool = field(default=False)
    switch: bool = field(default=False)
    switch2: bool = field(default=False)
