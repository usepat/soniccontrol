from __future__ import annotations
from typing import Optional, Literal
import datetime
import attrs

from soniccontrol.sonicamp.command import Command


@attrs.define
class Status:
    error: int = attrs.field(default=0, repr=False)
    frequency: int = attrs.field(default=0)
    gain: int = attrs.field(default=0)
    current_protocol: int = attrs.field(default=0, repr=False)
    wipe_mode: bool = attrs.field(default=False, repr=False)
    temperature: float = attrs.field(default=0)
    signal: bool = attrs.field(default=False)
    urms: float = attrs.field(
        default=0.0, validator=attrs.validators.instance_of(float)
    )
    irms: float = attrs.field(
        default=0.0, validator=attrs.validators.instance_of(float)
    )
    phase: float = attrs.field(
        default=0.0, validator=attrs.validators.instance_of(float)
    )
    relay_mode: Optional[Literal["kHz", "MHz"]] = attrs.field(
        default=None, kw_only=True
    )
    timestamp: datetime.datetime = attrs.field(factory=datetime.datetime.now, eq=False)

    def from_sens_command(
        self,
        command: Command,
        calculation_strategy: Optional[Literal["fullscale", "factorised"]] = None,
        old_status: Optional[Status] = None,
    ) -> Status:
        freq, urms, irms, phase = map(int, command.answer_string.split(" "))

        if calculation_strategy and calculation_strategy == "fullscale":
            urms = urms if urms > 282_300 else 282_300
            urms = (urms * 0.000_400_571 - 1130.669402) * 1000 + 0.5
            irms = irms if irms > 3_038_000 else 303_800
            irms = (irms * 0.000_015_601 - 47.380671) * 1000 + 0.5
            phase = (phase * 0.125) * 100
        elif calculation_strategy and calculation_strategy == "factorised":
            urms /= 1000
            irms /= 1000
            phase /= 1_000_000

        if old_status:
            return attrs.evolve(
                self,
            )


@attrs.frozen
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


@attrs.frozen
class Info:
    device_type: Literal["soniccatch", "sonicwipe", "sonicdescale"] = attrs.field(
        default="soniccatch"
    )
    firmware_info: str = attrs.field(default="")
    version: float = attrs.field(default=0.2)
    modules: Modules = attrs.field(factory=Modules)
