
import attrs
from typing import Dict, List, TypeVar
from sonic_protocol.answer_validator_builder import AnswerValidatorBuilder
from sonic_protocol.defs import AnswerDef, CommandCode, CommandContract, CommandDef, DeviceType, MetaExport, Protocol, Version
from sonic_protocol.answer import AnswerValidator


@attrs.define()
class CommandLookUp:
    command_def: CommandDef = attrs.field()
    answer_def: AnswerDef = attrs.field() # probably not needed, we leave it anyway here
    answer_validator: AnswerValidator = attrs.field()
    description: str | None = attrs.field(default=None)


T = TypeVar("T", CommandDef, AnswerDef)
CommandLookUpTable = Dict[CommandCode, CommandLookUp]
class ProtocolBuilder:
    def __init__(self, protocol: Protocol):
        self._protocol = protocol

    def build(self, device_type: DeviceType, version: Version, release: bool) -> CommandLookUpTable:
        lookups: Dict[CommandCode, CommandLookUp] = {}

        if version > self._protocol.version:
            # TODO: how to react if version is higher?
            # log? warn? error?
            pass

        for export in self._protocol.commands:
            if not export.descriptor.is_valid(version, device_type):
                continue

            commands: List[CommandContract] = export.exports if isinstance(export.exports, list) else [export.exports]
            for command in commands:
                if release and not command.is_release:
                    continue

                command_def = self._filter_defs(command.command_defs, version, device_type)
                answer_def = self._filter_defs(command.answer_defs, version, device_type)
                validator = AnswerValidatorBuilder().create_answer_validator(answer_def)
                lookups[command.code] = CommandLookUp(
                    command_def,
                    answer_def,
                    validator,
                    command.description
                )

        return lookups


    def _filter_defs(self, defs: List[T | MetaExport[T]], version: Version, device_type: DeviceType) -> T:
        for def_entry in defs:
            if isinstance(def_entry, MetaExport):
                if def_entry.descriptor.is_valid(version, device_type):
                    return def_entry.exports
            else:
                return def_entry
        raise LookupError(f"There was no definition exported for the combination of version {version} and type {device_type}")

    
