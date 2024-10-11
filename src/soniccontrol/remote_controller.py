from pathlib import Path
from typing import Optional

from soniccontrol.builder import DeviceBuilder
from soniccontrol.communication.communicator_builder import CommunicatorBuilder
from soniccontrol.communication.connection_factory import CLIConnectionFactory, ConnectionFactory, SerialConnectionFactory
from soniccontrol.logging import create_logger_for_connection
from soniccontrol.procedures.procedure_controller import ProcedureController, ProcedureType
from soniccontrol.procedures.procs.ramper import RamperArgs
from soniccontrol.scripting.legacy_scripting import LegacyScriptingFacade
from soniccontrol.scripting.scripting_facade import ScriptingFacade
from soniccontrol.sonic_device import SonicDevice


class RemoteController:
    NOT_CONNECTED = "Controller is not connected to a device"

    def __init__(self, log_path: Optional[Path]=None):
        self._device: Optional[SonicDevice] = None
        self._scripting: Optional[ScriptingFacade] = None
        self._proc_controller: Optional[ProcedureController] = None
        self._log_path: Optional[Path] = log_path

    async def _connect(self, connection_factory: ConnectionFactory, connection_name: str):
        if self._log_path:
            logger = create_logger_for_connection(connection_name, self._log_path)   
        else:
            logger = create_logger_for_connection(connection_name)
        serial, commands = await CommunicatorBuilder.build(
            connection_factory,
            logger=logger
        )
        self._device = await DeviceBuilder().build_amp(comm=serial, commands=commands, logger=logger)
        await self._device.communicator.connection_opened.wait()
        self._scripting = LegacyScriptingFacade(self._device)
        self._proc_controller = ProcedureController(self._device)

    async def connect_via_serial(self, url: Path) -> None:
        assert self._device is None
        connection_name = url.name
        connection_factory = SerialConnectionFactory(connection_name=connection_name, url=url)
        await self._connect(connection_factory, connection_name)
        assert self._device is not None

    async def connect_via_process(self, process_file: Path) -> None:
        assert self._device is None
        connection_name = process_file.name
        connection_factory = CLIConnectionFactory(connection_name=connection_name, bin_file=process_file)
        await self._connect(connection_factory, connection_name)
        assert self._device is not None

    async def set_attr(self, attr: str, val: str) -> str:
        assert self._device is not None,    RemoteController.NOT_CONNECTED
        answer = await self._device.execute_command("!" + attr + "=" + val)
        return answer.message

    async def get_attr(self, attr: str) -> str:
        assert self._device is not None,    RemoteController.NOT_CONNECTED
        answer = await self._device.execute_command("?" + attr)
        return answer.message
    
    async def send_command(self, command_str: str) -> str:
        assert self._device is not None,    RemoteController.NOT_CONNECTED
        answer = await self._device.execute_command(command_str)
        return answer.message

    async def execute_script(self, text: str) -> None:
        assert self._device is not None,    RemoteController.NOT_CONNECTED
        assert self._scripting is not None

        interpreter = self._scripting.parse_script(text)
        async for line_index, task in interpreter:
            pass

    def execute_ramp(self, ramp_args: RamperArgs) -> None:
        assert self._device is not None,    RemoteController.NOT_CONNECTED
        assert self._proc_controller is not None

        self._proc_controller.execute_proc(ProcedureType.RAMP, ramp_args)

    def execute_procedure(self, procedure: ProcedureType, args: dict) -> None:
        assert self._device is not None,    RemoteController.NOT_CONNECTED
        assert self._proc_controller is not None

        arg_class = self._proc_controller.proc_args_list[procedure]
        procedure_args = arg_class(args)
        self._proc_controller.execute_proc(procedure, procedure_args)

    async def stop_procedure(self) -> None:
        assert self._device is not None,    RemoteController.NOT_CONNECTED
        assert self._proc_controller is not None

        await self._proc_controller.stop_proc()
    
    async def disconnect(self) -> None:
        if self._device is not None:
            await self._device.disconnect()
            self._scripting = None
            self._proc_controller = None
            self._device = None
        assert self._device is None
