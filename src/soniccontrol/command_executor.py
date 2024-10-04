

from sonic_protocol.commands import Command, CommandValidator
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
        
        return await self.send_message(request_str, answer_validator=lookup_command.answer_validator,  **lookup_command.command_def.kwargs)

    async def send_message(self, message: str, answer_validator: AnswerValidator | None = None, **kwargs) -> Answer:
        response_str = await self._communicator.send_and_wait_for_response(message, **kwargs)
        
        if answer_validator is None:
            command_code = self._lookup_message(message)
            if command_code is not None:
                lookup_command = self._command_lookup_table[command_code]
                answer_validator = lookup_command.answer_validator
                answer = answer_validator.validate(response_str)
            else:
                answer = Answer(response_str, True, False)
        else:
            answer = answer_validator.validate(response_str)
        return answer


    def _lookup_message(self, message: str) -> CommandCode | None: 
        # We give back CommandCode instead of CommandLookUp directly, because like this it is easier to test.
        for command_code, command_lookup in self._command_lookup_table.items():
            if CommandValidator().validate(message, command_lookup.command_def):
                return command_code    
        return None

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
