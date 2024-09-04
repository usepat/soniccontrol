
from soniccontrol_gui.state_fetching.capture import Capture
from soniccontrol_gui.views.control.editor import ScriptFile
from soniccontrol_gui.views.control.proc_controlling import ProcControllingModel
from sonicpackage.events import EventManager
from sonicpackage.procedures.procedure_controller import ProcedureController
from sonicpackage.scripting.interpreter_engine import InterpreterEngine


class CaptureMediator(EventManager):
    def __init__(self, 
            capture: Capture, 
            interpreter_engine: InterpreterEngine, 
            script_file: ScriptFile,
            proc_controller: ProcedureController,
            proc_model: ProcControllingModel
            # sonic_measure
        ):
        super().__init__()

    
