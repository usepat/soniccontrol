from enum import Enum
from sonic_protocol.defs import (
    CommandCode, CommandExport, CommandListExport, ConverterType, MetaExportDescriptor, Protocol, Version, CommandDef, AnswerDef, CommandParamDef, 
    AnswerFieldDef, CommandContract, DeviceType, SIUnit, SIPrefix
)

# Version instance
version = Version(major=1, minor=0, patch=0)

# CommandParamDef instances (for "param_frequency")
param_frequency = CommandParamDef(
    name="frequency",
    param_type=int,
    si_unit=SIUnit.HERTZ,
    si_prefix=SIPrefix.KILO,
    description="Frequency of the transducer"
)

# AnswerFieldDef instances (for "answer_frequency")
answer_field_frequency = AnswerFieldDef(
    field_name="frequency",
    field_type=int,
    converter_ref=None,
    si_unit=SIUnit.HERTZ,
    si_prefix=SIPrefix.KILO,
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
                AnswerFieldDef(field_name="device_type", field_type=DeviceType, converter_ref=ConverterType.ENUM),
                AnswerFieldDef(field_name="version", field_type=Version, converter_ref=ConverterType.VERSION),
                AnswerFieldDef(field_name="is_release", field_type=bool, converter_ref=ConverterType.BUILD_TYPE, allowed_values_str=["release", "debug"])
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
