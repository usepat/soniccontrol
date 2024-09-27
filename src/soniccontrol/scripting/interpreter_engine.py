import asyncio
from enum import Enum
import logging
from typing import Optional

import attrs
from soniccontrol.events import Event, EventManager, PropertyChangeEvent
from soniccontrol.scripting.scripting_facade import Script



class InterpreterState(Enum):
    READY = 0
    PAUSED = 1
    RUNNING = 2


@attrs.define()
class CurrentTarget:
    line: Optional[int] = attrs.field()
    task: str = attrs.field()

    @staticmethod
    def default():
        return CurrentTarget(line=None, task="Idle")

class InterpreterEngine(EventManager):
    INTERPRETATION_ERROR = "<<INTERPRETATION_ERROR>>"
    PROPERTY_INTERPRETER_STATE = "interpreter_state"
    PROPERTY_CURRENT_TARGET = "current_target"

    def __init__(self, logger: logging.Logger):
        super().__init__()
        self._interpreter_worker = None
        self._script: Optional[Script] = None
        self._interpreter_state = InterpreterState.READY
        self._current_target = CurrentTarget.default()
        self._logger = logging.getLogger(logger.name + "." + InterpreterEngine.__name__)

    @property
    def interpreter_state(self) -> InterpreterState:
        return self._interpreter_state

    def _set_interpreter_state(self, state: InterpreterState):
        old_val = self._interpreter_state
        self._interpreter_state = state
        if old_val != state:
            self.emit(PropertyChangeEvent(InterpreterEngine.PROPERTY_INTERPRETER_STATE, old_val, self._interpreter_state))

    def _set_current_target(self, target: CurrentTarget):
        old_val = self._current_target
        self._current_target = target
        if old_val != target:
            self.emit(PropertyChangeEvent(InterpreterEngine.PROPERTY_CURRENT_TARGET, old_val, self._current_target))

    @property
    def script(self) -> Optional[Script]:
        return self._script
    
    @script.setter
    def script(self, script: Optional[Script]) -> None:
        self._script = script

    def start(self):
        self._logger.info("Start script")
        assert self._interpreter_state != InterpreterState.RUNNING
        
        self._set_interpreter_state(InterpreterState.RUNNING)
        self._interpreter_worker = asyncio.create_task(self._interpreter_engine(single_instruction=False))

    def single_step(self):
        self._logger.info("Start script")
        assert self._interpreter_state != InterpreterState.RUNNING
        
        self._set_interpreter_state(InterpreterState.RUNNING)
        self._interpreter_worker = asyncio.create_task(self._interpreter_engine(single_instruction=True))

    async def stop(self):
        self._logger.info("Stop script")
        assert self._interpreter_state != InterpreterState.READY

        if self._interpreter_worker and not self._interpreter_worker.done() and not self._interpreter_worker.cancelled():
            self._interpreter_worker.cancel()
            await self._interpreter_worker
        
        self._set_current_target(CurrentTarget.default())
        self._set_interpreter_state(InterpreterState.READY)

    async def pause(self):
        self._logger.info("Pause script")
        assert self._interpreter_state == InterpreterState.RUNNING

        if self._interpreter_worker and not self._interpreter_worker.done() and not self._interpreter_worker.cancelled():
            self._interpreter_worker.cancel()
            await self._interpreter_worker
        
        self._set_interpreter_state(InterpreterState.PAUSED)

    async def _interpreter_engine(self, single_instruction: bool = False):
        if self._script is None:
            return
        try:
            async for line_index, task in self._script:
                self._set_current_target(CurrentTarget(line_index, task))
                self._logger.info("Current task: %s", task)
                if single_instruction and line_index != 0:
                    break
        except asyncio.CancelledError:
            self._logger.warn("Interpreter got interrupted, while executing a script")
            return
        except Exception as e:
            self._logger.error(e)
            self.emit(Event(InterpreterEngine.INTERPRETATION_ERROR, exception=e))   
            self._set_interpreter_state(InterpreterState.PAUSED)
            return
        self._set_interpreter_state(InterpreterState.PAUSED if single_instruction and not self._script.is_finished else InterpreterState.READY)


