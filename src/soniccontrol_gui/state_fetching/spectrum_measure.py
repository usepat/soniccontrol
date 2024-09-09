
from typing import Any, Dict, List, Type, Union
from attrs import validators
import attrs

from soniccontrol_gui.state_fetching.updater import Updater
from sonicpackage.interfaces import Scriptable
from sonicpackage.procedures.holder import Holder, HolderArgs
from sonicpackage.procedures.procedure import Procedure
from sonicpackage.procedures.procs.ramper import RamperArgs

@attrs.define()
class SpectrumMeasureModel:
    form_fields: Dict[str, Any] = attrs.field(default={})


# TODO: This class can be easily merged with RamperLocal
class SpectrumMeasure(Procedure):
    def __init__(self, updater: Updater) -> None:
        self._updater = updater        

    @classmethod
    def get_args_class(cls) -> Type: 
        return RamperArgs

    async def execute(
        self,
        device: Scriptable,
        args: RamperArgs
    ) -> None:
        start = args.freq_center - args.half_range
        stop = args.freq_center + args.half_range + args.step # add a step to stop so that stop is inclusive
        values = [start + i * args.step for i in range(int((stop - start) / args.step)) ]

        try:
            await self._updater.stop()
            await device.get_overview()
            await self._ramp(device, list(values), args.hold_on, args.hold_off)
        finally:
            await device.set_signal_off()
            self._updater.start()

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
            if hold_off.duration:
                await device.set_signal_on()

            await Holder.execute(hold_on)
            await self._updater.update()

            if hold_off.duration:
                await device.set_signal_off()
                await Holder.execute(hold_off)
                await self._updater.update()

            i += 1

