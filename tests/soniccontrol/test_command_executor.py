import pytest
from unittest.mock import Mock, AsyncMock

import sonic_protocol.commands as cmds
from sonic_protocol.defs import AnswerDef, AnswerFieldDef, CommandCode, CommandDef, CommandParamDef
from soniccontrol.command import AnswerValidator
from soniccontrol.command_executor import CommandExecutor
from soniccontrol.communication.communicator import Communicator
from sonic_protocol.protocol_builder import CommandLookUp, CommandLookUpTable


@pytest.fixture
def lookup_table() -> CommandLookUpTable:
    return {
        CommandCode.GET_GAIN: CommandLookUp(
            CommandDef(["?g", "?gain"]), 
            AnswerDef([AnswerFieldDef("gain", int)]),
            AnswerValidator("")
        ),
        CommandCode.SET_FREQ: CommandLookUp(
            CommandDef(["!f", "!freq", "!frequency"], setter_param=CommandParamDef(int)), 
            AnswerDef([AnswerFieldDef("frequency", field_type=int)]),
            AnswerValidator("")
        ),
        CommandCode.SET_GAIN: CommandLookUp(
            CommandDef(["!g", "!gain"], setter_param=CommandParamDef(int)), 
            AnswerDef([AnswerFieldDef("gain", int)]),
            AnswerValidator(pattern="")
        ),
        CommandCode.SET_ON: CommandLookUp(
            CommandDef("!ON"), 
            AnswerDef([AnswerFieldDef("signal", bool)]),
            AnswerValidator("")
        ),
        CommandCode.SET_ATF: CommandLookUp(
            CommandDef("!atf", index_param=CommandParamDef(int), setter_param=CommandParamDef(int)), 
            AnswerDef([AnswerFieldDef("atf", int)]),
            AnswerValidator("")
        ),
    }

@pytest.fixture
def communicator():
    communicator = Mock(Communicator) 
    communicator.send_and_wait_for_answer = AsyncMock(return_value="")
    return communicator

@pytest.fixture
def command_executor(communicator, lookup_table):
    return CommandExecutor(lookup_table, communicator)


@pytest.mark.asyncio
@pytest.mark.parametrize("command, answer", [
    (cmds.SetFrequency(1000), "!f=1000"),
    (cmds.SetFrequency(420), "!f=420"),
    (cmds.SetGain(1000), "!g=1000"),
    (cmds.GetGain(), "?g"),
    (cmds.SetOn(), "!ON"),
    (cmds.SetAtf(4, 10000), "!atf4=10000"),
])
async def test_send_command_creates_correct_request(command, request_str, communicator, command_executor):
    _ = await command_executor.send_command(command)

    communicator.send_and_wait_for_answer.assert_called_once_with(request_str)    


@pytest.mark.parametrize("message, command_code", [
    ("!f=1000", CommandCode.SET_FREQ),
    ("!f=420", CommandCode.SET_FREQ),
    ("!g=1000", CommandCode.SET_GAIN),
    ("?g", CommandCode.GET_GAIN),
    ("!ON", CommandCode.SET_ON),
    ("!atf4=10000", CommandCode.SET_ATF),
    ("!bullshit", None),
])
def test_lookup_message_selects_right_command(message, command_code, command_executor):
    returned_command_code = command_executor._lookup_message(message)

    assert returned_command_code == command_code  

@pytest.mark.parametrize("message, command_code", [
    ("!freg=1000", CommandCode.SET_FREQ),
    ("!frequency=420", CommandCode.SET_FREQ),
    ("!f=420", CommandCode.SET_FREQ),
    ("!gain=1000", CommandCode.SET_GAIN),
    ("!g=1000", CommandCode.SET_GAIN),
    ("!freqy=1000", None),
])
def test_lookup_message_selects_right_command_with_alias(message, command_code, command_executor):
    returned_command_code = command_executor._lookup_message(message)

    assert returned_command_code == command_code  

