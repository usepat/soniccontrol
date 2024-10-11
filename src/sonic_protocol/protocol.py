from sonic_protocol.defs import (
    CommandCode, CommandListExport, ConverterType, FieldType, MetaExportDescriptor, Protocol, Version, CommandDef, AnswerDef, CommandParamDef, 
    AnswerFieldDef, CommandContract, DeviceType, SIUnit, SIPrefix
)
from sonic_protocol.field_names import StatusAttr

# Version instance
version = Version(major=1, minor=0, patch=0)

frequency_field_type = FieldType(
    field_type=int,
    si_unit=SIUnit.HERTZ,
    si_prefix=SIPrefix.KILO,
)

# CommandParamDef instances (for "param_frequency")
param_frequency = CommandParamDef(
    name=StatusAttr.FREQUENCY.value,
    param_type=frequency_field_type,
    description="Frequency of the transducer"
)

# AnswerFieldDef instances (for "answer_frequency")
answer_field_frequency = AnswerFieldDef(
    field_path=[StatusAttr.FREQUENCY.value],
    field_type=frequency_field_type,
    description=None
)

frequency_command = CommandContract(
    code=CommandCode.SET_FREQ,
    command_defs=[
        CommandDef(
            string_identifier=["!f", "!freq", "!frequency", "set_frequency"],
            index_param=None,
            setter_param=param_frequency
        )
    ],
    answer_defs=[
        AnswerDef(
            fields=[answer_field_frequency]
        )
    ],
    description="Command to set the frequency of the transducer on the device.",
    is_release=True,
    tags=["frequency", "transducer", "control"]
)


# The ?protocol command is the most important command
# Without ?protocol there is no way to determine which protocol is used.
# So this command is needed.
# There should also only exist one version of this command
# If you want to extend the ?protocol command. consider adding other commands
get_protocol_command = CommandContract(
    code=CommandCode.GET_PROTOCOL,
    command_defs=[
        CommandDef(string_identifier="?protocol")
    ],
    answer_defs=[
        AnswerDef(
            fields=[
                AnswerFieldDef(
                    field_path=["device_type"], 
                    field_type=FieldType(DeviceType), 
                    converter_ref=ConverterType.ENUM
                ),
                AnswerFieldDef(
                    field_path=["version"], 
                    field_type=FieldType(Version), 
                    converter_ref=ConverterType.VERSION
                ),
                AnswerFieldDef(
                    field_path=["is_release"], 
                    field_type=FieldType(bool), 
                    converter_ref=ConverterType.BUILD_TYPE
                )
            ]
        )
    ],
    is_release=True
)

# Protocol instance
protocol = Protocol(
    version=Version(1, 0, 0),
    commands=[
        CommandListExport(
            exports=[
                get_protocol_command 
            ],
            descriptor=MetaExportDescriptor(
                min_protocol_version=Version(major=1, minor=0, patch=0)
            )
        ),
        CommandListExport(
            exports=[
                frequency_command
            ],
            descriptor = MetaExportDescriptor(
                min_protocol_version=Version(major=1, minor=0, patch=0),
                excluded_device_types=[DeviceType.DESCALE]
            )
        )
    ]
)

# Now you have `protocol` representing the JSON structure
