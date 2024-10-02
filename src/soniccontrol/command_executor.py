

from sonic_protocol.commands import Command
from sonic_protocol.defs import CommandCode
from sonic_protocol.protocol_builder import CommandLookUpTable
from soniccontrol.command import Answer, AnswerValidator
from soniccontrol.communication.communicator import Communicator


class CommandExecutor:
    def __init__(self, command_lookup_table: CommandLookUpTable, communicator: Communicator):
        self._command_lookup_table = command_lookup_table
        self._communicator = communicator

    async def send_command(self, command: Command) -> Answer:
        pass

    async def send_message(self, message: str) -> Answer:
        pass

    def _lookup_message(self, message: str) -> CommandCode | None: 
        # We give back CommandCode instead of CommandLookUp directly, because like this it is easier to test.
        pass

    def _create_request_string(self, command: Command) -> str:
        pass

    def _parse_answer(self, answer_str: str, validator: AnswerValidator) -> Answer:
        pass
