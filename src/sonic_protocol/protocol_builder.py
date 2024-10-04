
import attrs
from typing import Callable, Dict, List, TypeVar
from sonic_protocol.defs import AnswerDef, AnswerFieldDef, CommandCode, CommandContract, CommandDef, ConverterType, DeviceType, MetaExport, Protocol, Version
from sonic_protocol.answer import AnswerValidator


@attrs.define()
class CommandLookUp:
    command_def: CommandDef = attrs.field()
    answer_def: AnswerDef = attrs.field() # probably not needed, we leave it anyway here
    answer_validator: AnswerValidator = attrs.field()


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
                validator = self._create_answer_validator(answer_def)
                lookups[command.code] = CommandLookUp(
                    command_def,
                    answer_def,
                    validator
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

    def _create_answer_validator(self, answer: AnswerDef) -> AnswerValidator:
        converters: Dict[ConverterType, Callable] = {
            ConverterType.SIGNAL: lambda x: x.lower() == "on"
        }
        
        value_dict: Dict[str, Callable] = {}
        for field in answer.fields:
            if field.converter_ref:
                value_dict[field.field_name] = converters[field.converter_ref]
            else:
                value_dict[field.field_name] = field.field_type

        regex = self._create_regex_for_answer(answer)
        
        return AnswerValidator(regex, **value_dict)

    def _create_regex_for_answer(self, answer: AnswerDef) -> str:
        regex_patterns: List[str] = []

        # TODO: add command code to regex

        for answer_field in answer.fields:
            regex_patterns.append(self._create_regex_for_answer_field(answer_field)) 

        return "#".join(regex_patterns)
    
    def _create_regex_for_answer_field(self, answer_field: AnswerFieldDef) -> str:
        value_str = ""

        if answer_field.converter_ref is None:
            if answer_field.field_type is int:
                value_str = r"([\+\-]?\d+)"
            elif answer_field.field_type is float:
                value_str = r"([\+\-]?\d+(\.\d+)?)"
            elif answer_field.field_type is bool:
                value_str = r"([Tt]rue)|([Ff]alse)|0|1"
            elif answer_field.field_type is str:
                value_str = r".*"
        else:
            value_str = r".*"

        if answer_field.si_prefix and answer_field.si_unit:
            value_str += " " + answer_field.si_prefix.value + answer_field.si_unit.value
        
        return answer_field.prefix + value_str + answer_field.postfix
    
