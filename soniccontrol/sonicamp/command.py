from typing import Dict
import re
import attrs
from soniccontrol.sonicamp.interfaces import Command, CommandValidationDict, SonicAmp


class CommandValidator:
    def __init__(self, sonicamp: SonicAmp) -> None:
        self.sonicamp: SonicAmp = sonicamp
        self.validation_patterns: Dict[type, re.Pattern] = {
            command_type: re.compile(
                command_type().validation_pattern["pattern"], re.IGNORECASE
            )
            for command_type in self.sonicamp.commands
        }

    def accepts(self, command: Command) -> bool:
        if command.validation_pattern is None:
            return False

        pattern = self.validation_patterns.get(type(command))
        if pattern is None:
            raise AttributeError(
                f"{Command = } is not part of {self.sonicamp = }'s commands"
            )

        match = pattern.search(command.answer_string)
        if match is None:
            return False

        command.value = command.validation_pattern["return_type"](match.group(1))
        return True


class Commands:
    @attrs.define
    class SetFrequency(Command):
        message: str = attrs.field(default="!f=")
        _validation_pattern: CommandValidationDict = {
            "pattern": r"frequency\s*=?\s*([\d]+)",
            "return_type": int,
        }

    @attrs.define
    class SetGain(Command):
        message: str = attrs.field(default="!g=")
        _validation_pattern: CommandValidationDict = {
            "pattern": r"gain\s*=?\s*([\d]+)",
            "return_type": int,
        }

    @attrs.define
    class SetKhzMode(Command):
        message: str = attrs.field(default="!KHZ")
        _validation_pattern: CommandValidationDict = {
            "pattern": r"(khz)",
            "return_type": str,
        }

    @attrs.define
    class SetMhzMode(Command):
        message: str = attrs.field(default="!MHZ")
        _validation_pattern: CommandValidationDict = {
            "pattern": r"(mhz)",
            "return_type": str,
        }

    @attrs.define
    class SetSignalOn(Command):
        message: str = attrs.field(default="!ON")
        _validation_pattern: CommandValidationDict = {
            "pattern": r"(Signal\s+is\s+?ON|signal\s+on|1)",
            "return_type": str,
        }

    @attrs.define
    class SetSignalOff(Command):
        message: str = attrs.field(default="!OFF")
        _validation_pattern: CommandValidationDict = {
            "pattern": r"(Signal\s+is\s+?OFF|signal\s+off|1)",
            "return_type": str,
        }

    @attrs.define
    class SetSignalAuto(Command):
        message: str = attrs.field(default="!AUTO")
        _validation_pattern: CommandValidationDict = {
            "pattern": r"(auto\s*mode\s*on|auto\s*mode|auto|\d+)",
            "return_type": str,
        }
