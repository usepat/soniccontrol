from enum import Enum

from soniccontrol.tkintergui.utils.events import EventManager, PropertyChangeEvent

class ExecutionState(Enum):
    NOT_RESPONSIVE = 0
    IDLE = 1
    BUSY_EXECUTING_PROCEDURE = 2
    BUSY_EXECUTING_SCRIPT = 3
    BUSY_FLASHING = 4

class AppState(EventManager):
    EXECUTION_STATE_PROP_NAME = "execution_state"

    def __init__(self):
        self._execution_state = ExecutionState.NOT_RESPONSIVE

    @property
    def execution_state(self) -> ExecutionState:
        return self._execution_state
    
    @execution_state.setter
    def execution_state(self, value: ExecutionState) -> None:
        old_val = self._execution_state
        self._execution_state = value
        if old_val != value:
            self.emit(PropertyChangeEvent(AppState.EXECUTION_STATE_PROP_NAME, old_val, value))
