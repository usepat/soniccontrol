import time
from typing import Any, Callable, List, Literal, Tuple, Union
import asyncio

from soniccontrol.sonicpackage.interfaces import Scriptable


HoldTuple = Tuple[Union[int, float], Literal["ms", "s"]]
RampTuple = Tuple[Union[int, float], Union[int, float], Union[float, int]]


class Holder:
    @staticmethod
    async def execute(
        duration: float = None,
        unit: Literal["ms", "s"] = "s"
    ) -> None:
        duration = duration if unit == "s" else duration / 1000
        end_time: float = time.time() + duration
        while time.time() < end_time:
            await asyncio.sleep(0.01)


class Ramper:
    @staticmethod
    async def execute(
        device: Scriptable,
        action: Callable[[Union[int, float]], Any],
        ramp_values: RampTuple,
        hold_on: HoldTuple = (100, "ms"),
        hold_off: HoldTuple = (0, "ms"),
    ) -> None:
        start_value, stop_value, step_value = ramp_values
        step_value = step_value if start_value < stop_value else - step_value
        stop_value = stop_value + step_value
        values = range(start_value, stop_value, step_value)

        await device.get_overview()
        await action(values[0])
        await device.set_signal_on()
        await Ramper._ramp(device, action, values, hold_on, hold_off)
        await device.set_signal_off()

    @staticmethod
    async def _ramp(
        device: Scriptable,
        action: Callable[[Union[int, float]], Any],
        values: List[Union[int, float]],
        hold_on: HoldTuple,
        hold_off: HoldTuple,
    ) -> None:
        i: int = 0
        value: int = 0
        while i < len(values):
            value = values[i]

            await action(value)
            if hold_off[0]:
                await device.set_signal_on()
            await Holder.execute(*hold_on)

            if hold_off[0]:
                await device.set_signal_off()
                await Holder.execute(*hold_off)

            i += 1
