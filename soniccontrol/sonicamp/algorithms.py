from typing import Union, Iterable, Optional, Literal
import asyncio
import time
import attrs

from soniccontrol.sonicamp.interfaces import SonicAmp


@attrs.define
class Hold:
    duration: Union[int, float] = attrs.field(
        default=100,
        validator=attrs.validators.instance_of((int, float)),
    )
    unit: Literal["ms", "s"] = attrs.field(
        default="ms",
        validator=attrs.validators.in_(("ms", "s")),
    )
    holding: asyncio.Event = attrs.field(factory=asyncio.Event)
    _remaining_time: float = attrs.field(default=0.0)

    def __attrs_post_init__(self) -> None:
        self.duration = self.duration if self.unit == "s" else self.duration / 1000

    @property
    def remaining_time(self) -> Optional[float]:
        return self._remaining_time

    async def execute(self) -> None:
        self.holding.set()

        end_time: float = time.time() + self.duration
        while time.time() < end_time:
            self._remaining_time = round(end_time - time.time(), 2)
            await asyncio.sleep(0.01)

        self._remaining_time = 0
        self.holding.clear()


@attrs.define
class Ramp:
    sonicamp: SonicAmp = attrs.field()

    start_value: int = attrs.field()
    stop_value: int = attrs.field()
    step_value: int = attrs.field(converter=abs)

    hold_on_time: Union[float, int] = attrs.field(
        default=100,
        validator=attrs.validators.instance_of((int, float)),
    )
    hold_on_time_unit: Literal["ms", "s"] = attrs.field(
        default="ms",
        validator=attrs.validators.in_(("ms", "s")),
    )

    hold_off_time: Union[float, int] = attrs.field(
        default=0,
        validator=attrs.validators.instance_of((int, float)),
    )
    hold_off_time_unit: Literal["ms", "s"] = attrs.field(
        default="ms",
        validator=attrs.validators.in_(("ms", "s")),
    )

    values: Iterable[int] = attrs.field(factory=tuple)
    running: asyncio.Event = attrs.field(factory=asyncio.Event)
    _current_value: Optional[int] = attrs.field(default=None)

    def __attrs_post_init__(self):
        self.step_value = (
            self.step_value if self.start_value < self.stop_value else -self.step_value
        )
        self.stop_value = self.stop_value + self.step_value
        self.values = range(self.start_value, self.stop_value, self.step_value)
        self.hold_on_time = (
            self.hold_on_time
            if self.hold_on_time_unit == "s"
            else self.hold_on_time / 1000
        )
        self.hold_off_time = (
            self.hold_off_time
            if self.hold_off_time_unit == "s"
            else self.hold_off_time / 1000
        )

    @property
    def current_value(self) -> Optional[int]:
        return self._current_value

    async def update(self) -> None:
        while self.running.is_set():
            await self.sonicamp.get_sens()

    async def execute(self) -> None:
        self.running.set()
        update_task = asyncio.create_task(self.update())
        ramping_task = asyncio.create_task(self.ramp())
        # await self.ramp()
        await asyncio.gather(ramping_task, update_task)

    async def ramp(self) -> None:
        await self.sonicamp.set_signal_on()

        for value in self.values:
            self._current_value = value
            if self.hold_off_time:
                await self.sonicamp.set_signal_on()

            await self.sonicamp.set_frequency(value)
            await self.sonicamp.hold(self.hold_on_time, self.hold_on_time_unit)

            if self.hold_off_time:
                await self.sonicamp.set_signal_off()
                await self.sonicamp.hold(self.hold_off_time, self.hold_off_time_unit)

        self.running.clear()
