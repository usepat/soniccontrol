from typing import *
import time
import asyncio
import attrs
from icecream import ic
from soniccontrol.sonicpackage.interfaces import Scriptable, Script


HoldTuple = Tuple[Union[int, float], Literal["ms", "s"]]
RampTuple = Tuple[Union[int, float], Union[int, float], Union[float, int]]


@attrs.define
class Holder(Script):
    _duration: float = attrs.field(
        init=False,
        default=100.0,
        converter=float,
        validator=attrs.validators.instance_of(float),
    )
    _unit: Literal["ms", "s"] = attrs.field(
        init=False,
        default="ms",
        validator=attrs.validators.in_(("ms", "s")),
    )
    _holding: asyncio.Event = attrs.field(init=False, repr=False, factory=asyncio.Event)
    _remaining_time: float = attrs.field(init=False, default=0.0)

    def __attrs_post_init__(self) -> None:
        self._duration = self._duration if self.unit == "s" else self._duration / 1000

    def __repr__(self) -> str:
        return f"Holding state: {self.remaining_time} seconds remaining"

    @property
    def remaining_time(self) -> Optional[float]:
        return self._remaining_time

    @property
    def duration(self) -> float:
        return self._duration

    @property
    def unit(self) -> Literal["ms", "s"]:
        return self._unit

    @property
    def holding(self) -> asyncio.Event:
        return self._holding

    def reset(self, duration: float, unit: Literal["ms", "s"] = "s") -> None:
        self._duration = duration
        self._unit = unit
        self._remaining_time = 0.0

    async def execute(self, duration: float, unit: Literal["ms", "s"] = "s") -> None:
        self.reset(duration=duration, unit=unit)
        self._holding.set()
        end_time: float = time.time() + self._duration
        while time.time() < end_time and self._holding.is_set():
            self._remaining_time = round(end_time - time.time(), 2)
            await asyncio.sleep(0.01)
        self._remaining_time = 0.0
        self._holding.clear()


@attrs.define
class Ramp(Script):
    _device: Scriptable = attrs.field(repr=False)
    _action: Callable[[Union[int, float]], Any] = attrs.field(repr=False)
    _external_event: asyncio.Event = attrs.field(default=None)

    _hold_on: Holder = attrs.field(init=False, factory=Holder)
    _hold_off: Holder = attrs.field(init=False, factory=Holder)
    _values: Iterable[int] = attrs.field(init=False, factory=tuple)
    _running: asyncio.Event = attrs.field(init=False, factory=asyncio.Event)
    _current_value: int = attrs.field(init=False, default=0)

    def __attrs_post_init__(self) -> None:
        if self._external_event is None:
            self._external_event = self._running

    def __repr__(self) -> str:
        if not self.running.is_set():
            return "Ramp at 0 Hz"
        value: str = (
            f"Ramp at {self.current_value if self.current_value is not None else 0} Hz"
        )
        ic(f"Ramp: {value}")
        return value

    @property
    def running(self) -> asyncio.Event:
        return self._running

    @property
    def current_value(self) -> int:
        return self._current_value

    def reset(
        self,
        ramp_values: RampTuple,
        hold_on: HoldTuple = (100, "ms"),
        hold_off: HoldTuple = (0, "ms"),
        external_event: Optional[asyncio.Event] = None,
    ) -> None:
        _start_value, _stop_value, _step_value = ramp_values
        _step_value = _step_value if _start_value < _stop_value else -_step_value
        _stop_value = _stop_value + _step_value
        self._values = range(_start_value, _stop_value, _step_value)
        self._hold_on.reset(*hold_on)
        self._hold_off.reset(*hold_off)
        if external_event is None:
            self._external_event = self._running

    async def update(self, update_strategy: Callable[[Any], Any] = None) -> None:
        await self.running.wait()
        if self.external_event is not None:
            return
        while self.external_event.is_set() and self.running.is_set():
            if update_strategy is None:
                await self.device.get_status()
            else:
                await update_strategy()

    async def execute(
        self,
        ramp_values: RampTuple,
        hold_on: HoldTuple,
        hold_off: HoldTuple,
        external_event: Optional[asyncio.Event] = None,
    ) -> None:
        self.reset(
            ramp_values=ramp_values,
            hold_on=hold_on,
            hold_off=hold_off,
            external_event=external_event,
        )
        self._action(ramp_values[0])
        await self.ramp()

        await self.device.get_overview()
        update_task = asyncio.create_task(self.update(update_coroutine))
        ramping_task = asyncio.create_task(self.ramp())
        await asyncio.gather(ramping_task, update_task)
        await self.device.set_signal_off()

    async def ramp(self) -> None:
        await self.device.set_frequency(self.start_value)
        self.running.set()
        await self.device.set_signal_on()

        i: int = 0
        value: int = 0
        while (
            self.external_event.is_set()
            and self.running.is_set()
            and i < len(self.values)
        ):
            value = self.values[i]
            self._current_value = value

            await self.device.set_frequency(value)
            if self.hold_off_time:
                await self.device.set_signal_on()
            await self.device.hold(self.hold_on_time, self.hold_on_time_unit)

            if self.hold_off_time:
                await self.device.set_signal_off()
                await self.device.hold(self.hold_off_time, self.hold_off_time_unit)

            i += 1

        self._current_value = 0
        self.running.clear()
