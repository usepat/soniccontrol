import abc
import time
from typing import List, Literal, Tuple, Union
import asyncio

import attrs

from soniccontrol.sonicpackage.interfaces import Scriptable
from soniccontrol.sonicpackage.procedures.holder import Holder


HoldTuple = Tuple[Union[int, float], Literal["ms", "s"]]
RampTuple = Tuple[Union[int, float], Union[int, float], Union[float, int]]


@attrs.define(auto_attribs=True)
class RamperArgs:
    freq_center: float | int = attrs.field()
    half_range: float | int = attrs.field()
    step: float | int = attrs.field()
    hold_on: HoldTuple = attrs.field(default=(100, "ms"))
    hold_off: HoldTuple = attrs.field(default=(0, "ms"))

class Ramper(abc.ABC):
    def __init__(self) -> None:
        super().__init__()

    @abc.abstractmethod
    async def execute(
        self,
        device: Scriptable,
        args: RamperArgs
    ) -> None: ...

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

        await device.get_overview()
        await device.execute_command(f"!freq={args.start}")
        await device.set_signal_on()
        await self._ramp(device, list(values), args.hold_on, args.hold_off)
        await device.set_signal_off()

    async def _ramp(
        self,
        device: Scriptable,
        values: List[Union[int, float]],
        hold_on: HoldTuple,
        hold_off: HoldTuple,
    ) -> None:
        i: int = 0
        while i < len(values):
            value = values[i]

            await device.execute_command(f"!freq={value}")
            if hold_off[0]:
                await device.set_signal_on()
            await Holder.execute(*hold_on)

            if hold_off[0]:
                await device.set_signal_off()
                await Holder.execute(*hold_off)

            i += 1


class RamperRemote(Ramper):
    def __init__(self) -> None:
        super().__init__()

    async def execute(
        self,
        device: Scriptable,
        args: RamperArgs
    ) -> None:
        hold_on_ms = args.hold_on[0] if args.hold_on[1] == 'ms' else args.hold_on[0] * 1000
        hold_off_ms = args.hold_off[0] if args.hold_off[1] == 'ms' else args.hold_off[0] * 1000

        await device.execute_command(f"!ramp_range={args.half_range}")
        await device.execute_command(f"!ramp_step={args.step}")
        await device.execute_command(f"!ramp_ton={hold_on_ms}")
        await device.execute_command(f"!ramp_toff={hold_off_ms}")
        # TODO t_pause is missing
        await device.execute_command(f"!freq={args.freq_center}")
        await device.get_remote_proc_finished_event().wait()
        
