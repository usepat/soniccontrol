from typing import Callable, Dict, List
from sonic_protocol.answer import AnswerValidator, Converter
from sonic_protocol.defs import AnswerDef, AnswerFieldDef, ConverterType


class AnswerValidatorBuilder:
    def create_answer_validator(self, answer_def: AnswerDef) -> AnswerValidator:
        converters: Dict[ConverterType, Callable | Converter] = {
            ConverterType.SIGNAL: lambda x: x.lower() == "on"
        }
        
        value_dict: Dict[str, Callable | Converter] = {}
        for field in answer_def.fields:
            if field.converter_ref:
                value_dict[field.field_name] = converters[field.converter_ref]
            else:
                value_dict[field.field_name] = field.field_type

        regex = self._create_regex_for_answer(answer_def)
        
        return AnswerValidator(regex, **value_dict)

    def _create_regex_for_answer(self, answer_def: AnswerDef) -> str:
        regex_patterns: List[str] = []

        # TODO: add command code to regex

        for answer_field in answer_def.fields:
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