from typing import Literal, Optional
from soniccontrol.sonicpackage.procedures.procedure_instantiator import ProcedureInstantiator
from soniccontrol.sonicpackage.procedures.ramper import Ramper, RamperArgs
from soniccontrol.sonicpackage.sonicamp_ import SonicAmp


class ProcedureController:
    def __init__(self, device: SonicAmp):
        self._device = device
        proc_instantiator = ProcedureInstantiator()
        self._ramp: Optional[Ramper] = proc_instantiator.instantiate_ramp(self._device)

    async def ramp_freq(
        self,
        start: int,
        stop: int,
        step: int,
        hold_on_time: float = 100,
        hold_on_unit: Literal["ms", "s"] = "ms",
        hold_off_time: float = 0,
        hold_off_unit: Literal["ms", "s"] = "ms",
    ) -> None:
        if self._ramp is None:
            raise Exception("No Ramp procedure available for the current device")

        return await self._ramp.execute(
            self._device,
            RamperArgs(
                start, 
                stop, 
                step,
                (hold_on_time, hold_on_unit),
                (hold_off_time, hold_off_unit)
            )
        )