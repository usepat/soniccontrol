from pathlib import Path
from robot.api.deco import keyword, library

from sonicpackage.procedures.procedure_controller import ProcedureType
from sonicpackage.procedures.ramper import RamperArgs

@library()
class RemoteController():
    def __init__(self):
        pass

    @keyword('Connect via serial to')
    def connect_via_serial(self, url: str) -> None:
        raise NotImplementedError()

    @keyword('Connect via process to')
    def connect_via_process(self, process_file: Path) -> None:
        raise NotImplementedError()

    @keyword('Set "${attr}" to "${val}"')
    def set_attr(self, attr: str, val: str) -> None:
        raise NotImplementedError()
    
    @keyword('Get "${attr}"')
    def get_attr(self, attr: str) -> None:
        raise NotImplementedError()

    @keyword('Execute script')
    def execute_script(self, text: str) -> None:
        raise NotImplementedError()
    
    @keyword('Stop script')
    def stop_script(self) -> None:
        raise NotImplementedError()
    
    @keyword('Execute ramp with ')
    def execute_ramp(self, ramp_args: RamperArgs) -> None:
        raise NotImplementedError()

    @keyword('Execute procedure "${procedure}" with "${args}"')
    def execute_procedure(self, procedure: ProcedureType, args: dict) -> None:
        raise NotImplementedError()
    
    @keyword('Stop procedure')
    def stop_procedure(self) -> None:
        raise NotImplementedError()
    
    @keyword('Disconnect')
    def disconnect(self) -> None:
        raise NotImplementedError()