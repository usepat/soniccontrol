import asyncio
from pathlib import Path
from robot.api.deco import keyword, library
from sonicpackage.procedures.procedure_controller import ProcedureType
from sonicpackage.procedures.ramper import RamperArgs
from sonicpackage.remote_controller import RemoteController

@library(auto_keywords=False)
class RemoteControllerLibrary:
    def __init__(self):
        self._controller = RemoteController()
        self._loop = asyncio.get_event_loop()

    @keyword('Connect via serial to')
    def connect_via_serial(self, url: Path) -> None:
        self._loop.run_until_complete(self._controller.connect_via_serial(url))

    @keyword('Connect via process to')
    def connect_via_process(self, process_file: Path) -> None:
        self._loop.run_until_complete(self._controller.connect_via_process(process_file))

    @keyword('Set "${attr}" to "${val}"')
    def set_attr(self, attr: str, val: str) -> str:
        return self._loop.run_until_complete(self._controller.set_attr(attr, val))

    @keyword('Get "${attr}"')
    def get_attr(self, attr: str) -> str:
        return self._loop.run_until_complete(self._controller.get_attr(attr))

    @keyword('Send Command ')
    def send_command(self, command_str: str) -> str:
        return self._loop.run_until_complete(self._controller.send_command(command_str))

    @keyword('Execute script')
    def execute_script(self, text: str) -> None:
        self._loop.run_until_complete(self._controller.execute_script(text))
    
    @keyword('Execute ramp with ')
    def execute_ramp(self, ramp_args: RamperArgs) -> None:
        self._controller.execute_ramp(ramp_args)

    @keyword('Execute procedure "${procedure}" with "${args}"')
    def execute_procedure(self, procedure: ProcedureType, args: dict) -> None:
        self._controller.execute_procedure(procedure, args)
    
    @keyword('Stop procedure')
    def stop_procedure(self) -> None:
        self._loop.run_until_complete(self._controller.stop_procedure())
    
    @keyword('Disconnect')
    def disconnect(self) -> None:
        self._loop.run_until_complete(self._controller.disconnect())
