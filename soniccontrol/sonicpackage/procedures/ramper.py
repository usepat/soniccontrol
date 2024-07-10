from typing import List, Literal, Tuple, Type, Union
import asyncio

import attrs
from attrs import validators

from soniccontrol.sonicpackage.interfaces import Scriptable
from soniccontrol.sonicpackage.procedures.holder import Holder, HolderArgs, convert_to_holder_args
from soniccontrol.sonicpackage.procedures.procedure import Procedure


@attrs.define(auto_attribs=True)
class RamperArgs:
    freq_center: float | int = attrs.field(validator=[
        validators.instance_of(float | int),
        validators.ge(0),
        validators.le(1000000)
    ])
    half_range: float | int = attrs.field(validator=[
        validators.instance_of(float | int),
        validators.ge(0),
        validators.le(1000000)
    ])
    step: float | int = attrs.field(validator=[
        validators.instance_of(float | int),
        validators.ge(10),
        validators.le(100000)
    ])
    hold_on: HolderArgs = attrs.field(
        default=HolderArgs(100, "ms"), 
        converter=convert_to_holder_args
    )
    hold_off: HolderArgs = attrs.field(
        default=HolderArgs(0, "ms"),
        converter=convert_to_holder_args
    )


class Ramper(Procedure):
    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def get_args_class(cls) -> Type:
        return RamperArgs


class RamperLocal(Ramper):
    def __init__(self) -> None:
        super().__init__()

    async def execute(
        self,
        device: Scriptable,
        args: RamperArgs
    ) -> None:
        start = args.freq_center - args.half_range
        stop = args.freq_center + args.half_range + args.step # add a step to stop so that stop is inclusive
        values = [start + i * args.step for i in range(int((stop - start) / args.step)) ]

        try:
            await device.get_overview()
            # Do we need those two lines?
            # await device.execute_command(f"!freq={start}")
            # await device.set_signal_on()
            await self._ramp(device, list(values), args.hold_on, args.hold_off)
        finally:
            await device.set_signal_off()

    async def _ramp(
        self,
        device: Scriptable,
        values: List[Union[int, float]],
        hold_on: HolderArgs,
        hold_off: HolderArgs,
    ) -> None:
        i: int = 0
        while i < len(values):
            value = values[i]

            await device.execute_command(f"!freq={value}")
            if hold_off[0]:
                await device.set_signal_on()
            await Holder.execute(hold_on)

            if hold_off[0]:
                await device.set_signal_off()
                await Holder.execute(hold_off)

            i += 1


class RamperRemote(Ramper):
    def __init__(self) -> None:
        super().__init__()

    async def execute(
        self,
        device: Scriptable,
        args: RamperArgs
    ) -> None:
        try:
            hold_on_ms = args.hold_on.duration if args.hold_on.unit == 'ms' else args.hold_on.duration * 1000
            hold_off_ms = args.hold_off.duration if args.hold_off.unit == 'ms' else args.hold_off.duration * 1000

            await device.execute_command(f"!ramp_range={args.half_range}")
            await device.execute_command(f"!ramp_step={args.step}")
            await device.execute_command(f"!ramp_ton={hold_on_ms}")
            await device.execute_command(f"!ramp_toff={hold_off_ms}")
            # TODO t_pause is missing
            await device.execute_command(f"!freq={args.freq_center}")
        except asyncio.CancelledError:
            await device.execute_command("!stop")
        finally:
            await device.get_remote_proc_finished_event().wait()

        
