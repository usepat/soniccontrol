from __future__ import annotations

import asyncio
import datetime
from typing import Any, Callable, Dict, Literal, Optional, Tuple

import attrs
from icecream import ic


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


@attrs.define(slots=True)
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
    procedure: int = attrs.field(
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
    _remote_proc_finished_running: asyncio.Event = attrs.field(init=False, factory=asyncio.Event)
    

    @property
    def changed(self) -> asyncio.Event:
        return self._changed

    @property
    def changed_data(self) -> Dict[str, Any]:
        return self._changed_data

    @property
    def version(self) -> int:
        return self._version
    
    @property 
    def remote_proc_finished_running(self) -> asyncio.Event:
        return self._remote_proc_finished_running
    
    def get_dict(self) -> dict:
        result = {}
        for field in attrs.fields(Status):
            if field.name in ["timestamp", "_changed", "_changed_data", "_remote_proc_finished_running"]: # skip not json serializable fields like datetime
                continue
            result[field.name] = getattr(self, field.name)
        return result

    async def update(self, **kwargs) -> Status:
        self._changed.clear()
        self._changed_data.clear()
        kwargs["timestamp"] = (
            datetime.datetime.now()
            if not kwargs.get("timestamp")
            else datetime.datetime.fromtimestamp(kwargs.get("timestamp"))
        )
        procedure = self.procedure
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
            #  check if the procedure was changed or finished
            if procedure != 0 and self.procedure != procedure:
                self._remote_proc_finished_running.set()
                await asyncio.sleep(0.1)
                self._remote_proc_finished_running.clear()
            
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
        return cls(*map(bool, module_string.split("=")))

Version = Tuple[int, int, int]

def to_version(x: Any) -> Version:
    if isinstance(x, str):
        version = tuple(map(int, x.split(".")))
        if len(version) != 3:
            raise ValueError("The Version needs to have exactly two separators '.'")
        return version
    elif type(x) is Version:
        return x
    else:
        raise TypeError("The type cannot be converted into a version")
    

@attrs.define
class Info:
    device_type: Literal["catch", "wipe", "descale"] = attrs.field(default="descale")
    firmware_info: str = attrs.field(default="")
    firmware_version: Version = attrs.field(default=(0, 0, 0), converter=to_version) # TODO: delete this. Is just there, so I can implement in the meantime the home tab
    modules: Modules = attrs.field(factory=Modules)

    def update(self, **kwargs) -> Info:
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self
