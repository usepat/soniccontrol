from sonic_protocol.defs import DeviceType, FieldType, AnswerFieldDef, CommunicationChannel, ConverterType, SIPrefix, SIUnit, Version
from sonic_protocol.field_names import StatusAttr

field_termination = AnswerFieldDef(
	field_path=["termination"],
	field_type=FieldType(field_type=bool),
)

field_type_comm_channel = FieldType(
	field_type=CommunicationChannel, 
	converter_ref=ConverterType.ENUM
)

field_device_type = AnswerFieldDef(
	field_path=["device_type"],
	field_type=FieldType(DeviceType, converter_ref=ConverterType.ENUM),
)

def create_version_field(name: str) -> AnswerFieldDef:
	return AnswerFieldDef(
		field_path=[name], 
		field_type=FieldType(Version, converter_ref=ConverterType.VERSION), 
	)

field_type_frequency = FieldType(
    field_type=int,
    si_unit=SIUnit.HERTZ,
    si_prefix=SIPrefix.KILO,
)

field_frequency = AnswerFieldDef(
    field_path=[StatusAttr.FREQUENCY.value],
    field_type=field_type_frequency,
)

gain_type = FieldType(
    field_type=int,
    si_unit=SIUnit.PERCENT,
    si_prefix=SIPrefix.NONE,
)

field_gain = AnswerFieldDef(
    field_path=[StatusAttr.GAIN],
    field_type=gain_type
)

field_signal = AnswerFieldDef(
    field_path=[StatusAttr.SIGNAL],
    field_type=FieldType(field_type=bool, converter_ref=ConverterType.SIGNAL),
)

swf_field_type = FieldType(
    field_type=int,
    si_unit=SIUnit.HERTZ,
    si_prefix=SIPrefix.KILO,
)

field_swf = AnswerFieldDef(
    field_path=[StatusAttr.SWF],
    field_type=swf_field_type
)

field_type_temperature = FieldType(
    field_type=int,
    si_unit=SIUnit.CELSIUS,
    si_prefix=SIPrefix.NONE,
)

field_temperature = AnswerFieldDef(
    field_path=[StatusAttr.TEMPERATURE],
    field_type=field_type_temperature
)

urms_field_type = FieldType(
    field_type=int,
    si_unit=SIUnit.VOLTAGE,
    si_prefix=SIPrefix.MICRO,
)

irms_field_type = FieldType(
    field_type=int,
    si_unit=SIUnit.AMPERE,
    si_prefix=SIPrefix.MICRO,
)

phase_field_type = FieldType(
    field_type=int,
    si_unit=SIUnit.DEGREE,
    si_prefix=SIPrefix.MICRO,
)

ts_flag_field_type = FieldType(
    field_type=int,
    si_unit=SIUnit.VOLTAGE,
    si_prefix=SIPrefix.MICRO,
)

field_urms = AnswerFieldDef(
    field_path=[StatusAttr.URMS],
    field_type=urms_field_type
)

field_irms = AnswerFieldDef(
    field_path=[StatusAttr.IRMS],
    field_type=irms_field_type
)

field_phase = AnswerFieldDef(
    field_path=[StatusAttr.PHASE],
    field_type=phase_field_type
)

field_ts_flag = AnswerFieldDef(
    field_path=["ts_flag"],
    field_type=ts_flag_field_type
)

field_unknown_answer = AnswerFieldDef(
	field_path=["unknown_answer"],
	field_type=FieldType(str)
)
