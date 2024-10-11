

from typing import Any, Dict
from sonic_protocol.commands import Command
from sonic_protocol.defs import CommandCode, CommandDef
from sonic_protocol.protocol_builder import CommandLookUpTable
from sonic_protocol.answer import Answer, AnswerValidator
from soniccontrol.communication.communicator import Communicator


class CommandExecutor:
    def __init__(self, command_lookup_table: CommandLookUpTable, communicator: Communicator):
        self._command_lookup_table = command_lookup_table
        self._communicator = communicator

    def has_command(self, command: CommandCode | Command) -> bool:
        if isinstance(command, Command):
            return command.code in self._command_lookup_table
        return command in self._command_lookup_table

    async def send_command(self, command: Command) -> Answer:
        lookup_command = self._command_lookup_table.get(command.code)
        assert lookup_command is not None # throw error?

        request_str = self._create_request_string(command, lookup_command.command_def)
        
        answer = await self.send_message(
            request_str, 
            lookup_command.answer_validator,
            command.args,  
            **lookup_command.command_def.kwargs
        )

        return answer

    async def send_message(self, message: str, answer_validator: AnswerValidator | None = None, derived_params: Dict[str, Any] = {}, **kwargs) -> Answer:
        response_str = await self._communicator.send_and_wait_for_response(message, **kwargs)
        
        code: CommandCode | None = None
        if "#" in response_str:
            code_str, response_str  = response_str.split(sep="#", maxsplit=1)
            code = CommandCode(int(code_str))
        
        if answer_validator is None:
            answer = Answer(response_str, True, was_validated=False)
        else:
            answer = answer_validator.validate(response_str)
        
        answer.update_field_paths(derived_params)
        answer.command_code = code
        return answer

    def _create_request_string(self, command: Command, command_def: CommandDef) -> str:
        identifier = command_def.string_identifier
        request_msg: str = identifier[0] if isinstance(identifier, list) else identifier
        if command_def.index_param:
            assert "index"in command.args
            request_msg += str(command.args["index"])
        if command_def.setter_param:
            assert "value"in command.args 
            request_msg += "=" + str(command.args["value"])

        return request_msg
