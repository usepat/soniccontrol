
import abc
from enum import Enum
from soniccontrol_gui.views.control.editor import ScriptFile
from soniccontrol_gui.views.control.proc_controlling import ProcControllingModel
from sonicpackage.events import Event, EventManager, PropertyChangeEvent
from sonicpackage.procedures.procedure_controller import ProcedureController
from sonicpackage.scripting.interpreter_engine import InterpreterEngine, InterpreterState
from sonicpackage.scripting.scripting_facade import ScriptingFacade


class CaptureTargets(Enum):
    FREE = "Free"
    SCRIPT = "Script"
    PROCEDURE = "Procedure"
    SPECTRUM_MEASURE = "Spectrum Measure"


class CaptureTarget(abc.ABC, EventManager):
    COMPLETED_EVENT = "<<COMPLETED_EVENT>>"

    def __init__(self):
        super().__init__()

    @abc.abstractmethod
    async def before_start_capture(self) -> None: ...

    @abc.abstractmethod
    def run_to_capturing_task(self) -> None: ...

    @abc.abstractmethod
    async def after_end_capture(self) -> None: ...


class CaptureFree(CaptureTarget):
    def __init__(self):
        super().__init__()

    async def before_start_capture(self) -> None:
        # nothing needed
        pass

    def run_to_capturing_task(self) -> None:
        # nothing needed
        pass

    async def after_end_capture(self) -> None:
        # nothing needed
        pass


class CaptureScript(CaptureTarget):
    def __init__(self, script_file: ScriptFile, scripting_facade: ScriptingFacade, interpreter_engine: InterpreterEngine):
        super().__init__()
        self._script_file = script_file
        self._interpreter_engine = interpreter_engine
        self._scripting_facade = scripting_facade
        self._is_capturing = False
        self._interpreter_engine.subscribe_property_listener(
            InterpreterEngine.PROPERTY_INTERPRETER_STATE, 
            self._complete_on_script_finish
        )

    def _complete_on_script_finish(self, _event: PropertyChangeEvent) -> None:
        if self._interpreter_engine.script is None:
            return
        
        if self._interpreter_engine.script.is_finished and self._is_capturing:
            self.emit(Event(CaptureTarget.COMPLETED_EVENT))

    async def before_start_capture(self) -> None:
        text = self._script_file.text
        script = self._scripting_facade.parse_script(text)
        self._interpreter_engine.script = script
        self._is_capturing = True

    def run_to_capturing_task(self) -> None:
        self._interpreter_engine.start()

    async def after_end_capture(self) -> None:
        self._is_capturing = False
        if self._interpreter_engine.interpreter_state == InterpreterState.RUNNING:
            await self._interpreter_engine.stop()

class CaptureProcedure(CaptureTarget):
    pass

class CaptureSpectrumMeasure(CaptureTarget):
    pass

