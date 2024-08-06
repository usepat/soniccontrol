from enum import Enum
import logging
from typing import Any, Dict, Literal, Optional, Type
import asyncio

from soniccontrol.sonicpackage.procedures.holder import HolderArgs
from soniccontrol.sonicpackage.procedures.procedure import Procedure
from soniccontrol.sonicpackage.procedures.procedure_instantiator import ProcedureInstantiator
from soniccontrol.sonicpackage.procedures.ramper import Ramper, RamperArgs
from soniccontrol.sonicpackage.sonicamp_ import SonicAmp
from soniccontrol.gui.state_fetching.logger import get_base_logger
from soniccontrol.gui.constants import events
from soniccontrol.sonicpackage.events import Event, EventManager


class ProcedureType(Enum):
    RAMP = "Ramp"

class ProcedureController(EventManager):
    def __init__(self, device: SonicAmp):
        super().__init__()
        base_logger = get_base_logger(device._logger)
        self._logger = logging.getLogger(base_logger.name + "." + ProcedureController.__name__)
        self._device = device

        self._logger.debug("Instantiate procedures")
        proc_instantiator = ProcedureInstantiator()
        self._ramp: Optional[Ramper] = proc_instantiator.instantiate_ramp(self._device)
        self._procedures: Dict[ProcedureType, Optional[Procedure]] = {
            ProcedureType.RAMP: self._ramp
        }
        self._running_proc_task: Optional[asyncio.Task] = None
        self._running_proc_type: Optional[ProcedureType] = None

    @property
    def proc_args_list(self) -> Dict[ProcedureType, Type]:
        return { 
            proc_type: procedure.get_args_class() 
            for proc_type, procedure in self._procedures.items() 
            if procedure is not None 
        }

    @property
    def is_proc_running(self) -> bool:
        return not (self._running_proc_task is None or self._running_proc_task.done() or self._running_proc_task.cancelled())

    @property
    def running_proc_type(self) -> Optional[ProcedureType]:
        return self._running_proc_type

    def execute_proc(self, proc_type: ProcedureType, args: Any) -> None:
        assert(proc_type in self._procedures)
        procedure = self._procedures[proc_type]
        if procedure is None:
            raise Exception(f"The procedure {repr(proc_type)} is not available for the current device")
        if self.is_proc_running:
            raise Exception(f"There is already a procedure running")
        
        self._logger.info("Run procedure %s with args %s", proc_type.name, str(args))
        self._running_proc_type = proc_type
        self._running_proc_task = asyncio.create_task(procedure.execute(self._device, args))
        self._running_proc_task.add_done_callback(lambda _e: self._on_proc_finished())

    async def stop_proc(self) -> None:
        self._logger.info("Stop procedure")
        if self._running_proc_task: 
            self._running_proc_task.cancel()
            await self._running_proc_task
            self._on_proc_finished()

    def _on_proc_finished(self) -> None:
        self._logger.info("Procedure stopped")
        self._running_proc_task = None
        self._running_proc_type = None
        self.emit(Event(events.PROCEDURE_STOPPED))

    async def ramp_freq(
        self,
        freq_center: int,
        half_range: int,
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
                freq_center, 
                half_range,
                step,
                HolderArgs(hold_on_time, hold_on_unit),
                HolderArgs(hold_off_time, hold_off_unit)
            )
        )
    
    async def ramp_freq_range(
        self,
        start: int,
        stop: int,
        step: int,
        hold_on_time: float = 100,
        hold_on_unit: Literal["ms", "s"] = "ms",
        hold_off_time: float = 0,
        hold_off_unit: Literal["ms", "s"] = "ms",
    ) -> None:
        half_range = (stop - start) // 2
        freq_center = start + half_range
        assert(half_range > 0)

        return await self.ramp_freq(
            freq_center, 
            half_range, 
            step,
            hold_on_time, hold_on_unit,
            hold_off_time, hold_off_unit
        )