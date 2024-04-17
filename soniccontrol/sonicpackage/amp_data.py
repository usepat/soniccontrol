from __future__ import annotations

import asyncio
import datetime
from enum import Enum, auto
from typing import Any, Callable, Dict, Generic, Optional, TypeVar, Union

import attrs
from icecream import ic

from soniccontrol.sonicpackage.command import Command

T = TypeVar("T")


class ObserverAction(Enum):
    READ = auto()
    WRITE = auto()


class ObservableVar(Generic[T]):
    def __init__(self, value: T) -> None:
        self._value: T = value
        self._callbacks: dict[ObserverAction, list[Callable[[T], Any]]] = {
            ObserverAction.READ: [],
            ObserverAction.WRITE: [],
        }

    def __repr__(self) -> str:
        return f"ObservableVar(value={self._value})"

    def set(self, value: T) -> None:
        self._value = value
        self._invoke_callbacks(ObserverAction.WRITE)

    def get(self) -> T:
        self._invoke_callbacks(ObserverAction.READ)
        return self._value

    def _invoke_callbacks(self, action: ObserverAction) -> None:
        for callback in self._callbacks.get(action, []):
            callback(self._value)

    def add_read_callback(self, callback: Callable[[T], Any]) -> None:
        self._callbacks[ObserverAction.READ].append(callback)

    def add_write_callback(self, callback: Callable[[T], Any]) -> None:
        self._callbacks[ObserverAction.WRITE].append(callback)


class Status1:
    error: ObservableVar[ErrorType] = ObservableVar(ErrorType.NO_ERROR)
    frequency: ObservableVar[int] = ObservableVar(0)
    gain: ObservableVar[int] = ObservableVar(0)
    procedureType: ObservableVar[ProcedureType] = ObservableVar(ProcedureType.NONE)
    wipe_mode: ObservableVar[bool] = ObservableVar(False)
    temperature: ObservableVar[Optional[float]] = ObservableVar(None)


def default_if_none(default: Any, type_: type = int) -> Callable[[Any], Any]:
    none_converter = attrs.converters.default_if_none(default)

    def converter(value) -> None:
        value = none_converter(value)
        try:
            value = type_(none_converter(value))
        except Exception as e:
            ic(f"VALUE ERROR {e}, {value} is not {type_}")
        return value

    return converter


@attrs.define()
class Status:
    error: int = attrs.field(
        default=0,
        repr=False,
        converter=default_if_none(0, int),
        validator=attrs.validators.instance_of(int),
    )
    frequency: int = attrs.field(
        default=0,
        converter=default_if_none(0, int),
        validator=attrs.validators.instance_of(int),
    )
    gain: int = attrs.field(
        default=0,
        converter=default_if_none(0, int),
        validator=attrs.validators.instance_of(int),
    )
    protocol: int = attrs.field(
        default=0,
        converter=default_if_none(0, int),
        validator=attrs.validators.instance_of(int),
    )
    wipe_mode: bool = attrs.field(
        default=False,
        converter=default_if_none(False, attrs.converters.to_bool),
        validator=attrs.validators.instance_of(bool),
    )
    temperature: Optional[float] = attrs.field(default=None)
    signal: bool = attrs.field(
        default=False,
        converter=default_if_none(False, bool),
        validator=attrs.validators.instance_of(bool),
    )
    urms: float = attrs.field(
        default=0.0,
        converter=default_if_none(0.0, float),
        validator=attrs.validators.instance_of(float),
    )
    irms: float = attrs.field(
        default=0.0,
        converter=default_if_none(0.0, float),
        validator=attrs.validators.instance_of(float),
    )
    phase: float = attrs.field(
        default=0.0,
        converter=default_if_none(0.0, float),
        validator=attrs.validators.instance_of(float),
    )
    atf1: int = attrs.field(
        default=0,
        converter=default_if_none(0, int),
        validator=attrs.validators.instance_of(int),
    )
    atk1: float = attrs.field(
        default=0.0,
        converter=default_if_none(0.0, float),
        validator=attrs.validators.instance_of(float),
    )
    atf2: int = attrs.field(
        default=0,
        converter=default_if_none(0, int),
        validator=attrs.validators.instance_of(int),
    )
    atk2: float = attrs.field(
        default=0.0,
        converter=default_if_none(0.0, float),
        validator=attrs.validators.instance_of(float),
    )
    atf3: int = attrs.field(
        default=0,
        converter=default_if_none(0, int),
        validator=attrs.validators.instance_of(int),
    )
    atk3: float = attrs.field(
        default=0.0,
        converter=default_if_none(0.0, float),
        validator=attrs.validators.instance_of(float),
    )
    att1: float = attrs.field(
        default=0.0,
        converter=default_if_none(0.0, float),
        validator=attrs.validators.instance_of(float),
    )
    relay_mode: Optional[Literal["KHz", "MHz"]] = attrs.field(
        default=None,
        converter=attrs.converters.optional(str),
        kw_only=True,
    )
    communication_mode: Optional[Literal["Serial", "Manual", "Analog"]] = attrs.field(
        default="Manual"
    )
    timestamp: datetime.datetime = attrs.field(
        factory=datetime.datetime.now,
        eq=False,
        converter=lambda b: (
            datetime.datetime.fromtimestamp(b) if isinstance(b, float) else b
        ),
    )
    _changed: asyncio.Event = attrs.field(init=False, factory=asyncio.Event)
    _changed_data: Dict[str, Any] = attrs.field(init=False, factory=dict)
    _version: int = attrs.field(init=False, default=0)

    @property
    def changed(self) -> asyncio.Event:
        return self._changed

    @property
    def changed_data(self) -> Dict[str, Any]:
        return self._changed_data

    @property
    def version(self) -> int:
        return self._version

    async def update(self, **kwargs) -> Status:
        self._changed.clear()
        self._changed_data.clear()
        kwargs["timestamp"] = (
            datetime.datetime.now()
            if not kwargs.get("timestamp")
            else datetime.datetime.fromtimestamp(kwargs.get("timestamp"))
        )
        changed: bool = False
        for key, value in kwargs.items():
            if hasattr(self, key) and getattr(self, key) != value:
                try:
                    setattr(self, key, value)
                    self._changed_data[key] = value
                    changed = key != "timestamp" or changed
                except AttributeError:
                    continue
        if changed:
            self._changed.set()
            await asyncio.sleep(0.1)
            self._changed.clear()
        return self


@attrs.define
class Modules:
    buffer: bool = attrs.field(default=False, converter=attrs.converters.to_bool)
    display: bool = attrs.field(default=False, converter=attrs.converters.to_bool)
    eeprom: bool = attrs.field(default=False, converter=attrs.converters.to_bool)
    fram: bool = attrs.field(default=False, converter=attrs.converters.to_bool)
    i_current: bool = attrs.field(default=False, converter=attrs.converters.to_bool)
    current1: bool = attrs.field(default=False, converter=attrs.converters.to_bool)
    current2: bool = attrs.field(default=False, converter=attrs.converters.to_bool)
    io_serial: bool = attrs.field(default=False, converter=attrs.converters.to_bool)
    thermo_ext: bool = attrs.field(default=False, converter=attrs.converters.to_bool)
    thermo_int: bool = attrs.field(default=False, converter=attrs.converters.to_bool)
    khz: bool = attrs.field(default=False, converter=attrs.converters.to_bool)
    mhz: bool = attrs.field(default=False, converter=attrs.converters.to_bool)
    portexpander: bool = attrs.field(default=False, converter=attrs.converters.to_bool)
    protocol: bool = attrs.field(default=False, converter=attrs.converters.to_bool)
    protocol_fix: bool = attrs.field(default=False, converter=attrs.converters.to_bool)
    relais: bool = attrs.field(default=False, converter=attrs.converters.to_bool)
    scanning: bool = attrs.field(default=False, converter=attrs.converters.to_bool)
    sonsens: bool = attrs.field(default=False, converter=attrs.converters.to_bool)
    tuning: bool = attrs.field(default=False, converter=attrs.converters.to_bool)
    switch: bool = attrs.field(default=False, converter=attrs.converters.to_bool)
    switch2: bool = attrs.field(default=False, converter=attrs.converters.to_bool)

    @classmethod
    def from_string(cls, module_string: str) -> Modules:
        return cls(*module_string.split("="))


@attrs.define
class Info:
    device_type: Literal["catch", "wipe", "descale"] = attrs.field(default="")
    firmware_info: str = attrs.field(default="")
    version: float = attrs.field(default=0.2)
    modules: Modules = attrs.field(factory=Modules)

    def update(self, **kwargs) -> Info:
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self

from typing import Any, TypeVar, Generic
from enum import Enum, auto

T = TypeVar("T")

class ObserverAction(Enum):
    READ = auto()
    WRITE = auto()

class ObservableVar(Generic[T]):
    def __init__(self, value: T) -> None:
        self._value: T = value
        self._callbacks: dict[ObserverAction, list[Callable[[T], Any]]] = {
            ObserverAction.READ: [],
            ObserverAction.WRITE: [],
        }
    
    def set(self, value: T) -> None:
        print("test")
        self._value = value
        self._invoke_callbacks(ObserverAction.WRITE)
        
    def get(self) -> T:
        print("test read")
        self._invoke_callbacks(ObserverAction.READ)
        return self._value        
            
    def _invoke_callbacks(self, action: ObserverAction) -> None:
        for callback in self._callbacks.get(action, []):
            callback(self._value)
    
    def add_read_callback(self, callback: Callable[[T], Any]) -> None:
        self._callbacks.get(ObserverAction.READ).append(callback)
        
    def add_write_callback(self, callback: Callable[[T], Any]) -> None:
        self._callbacks.get(ObserverAction.WRITE).append(callback)


class ObservableModel:
    _observers: dict[str, list[Callable[[Any], Any]]] = dict()
    
    def __setattr__(self, __name: str, __value: Any) -> None:
        if __name.startswith("_"):
            return
        if __name not in self._observers:
            self._observers[__name] = []
        self._notify(__name, __value)
        super().__setattr__(__name, __value)
    
    def _notify(self, name: str,   value: Any = None) -> None:
        if not self._observers[name]:
            return
        for callback in self._observers[name]:
            callback(value)

    def add_obverser(self, name: str,   callback: Callable[[Any], Any]) -> None:
        if name not in self._observers:
            self._observers[name] = []
        self._observers[name].append(callback)

class Model():
    lol: ObservableVar[int] = ObservableVar(10)
        
@attrs.define
class LolModel(ObservableModel):
    lol: int = attrs.field(default=10)
        
if __name__ == "__main__":
    # print("starting")
    # obj = Model()
    # obj.lol.add_read_callback(lambda x: print(f"get {x}"))
    # obj.lol.add_write_callback(lambda x: print(f"set {x}"))
    # obj.lol.get()
    # obj.lol.set(11)
    
    # print(obj.lol)

    model: LolModel = LolModel()
    model.add_obverser("lol", lambda x: print(f"set {x}"))
    model.add_obverser("lol", lambda x: print(f"set 2 {x}"))
    model.lol = 10
    print(model.lol)
    
