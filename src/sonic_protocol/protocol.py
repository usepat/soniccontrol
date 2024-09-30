from sonic_protocol.defs import (
    CommandListExport, MetaExportDescriptor, Protocol, Version, CommandDef, AnswerDef, CommandParamDef, 
    AnswerFieldDef, Command, DeviceType, SIUnit, SIPrefix
)

# Version instance
version = Version(major=1, minor=0, patch=0)

# CommandParamDef instances (for "param_frequency")
param_frequency = CommandParamDef(
    param_type=int,
    default_value=100000,
    si_unit=SIUnit.HERTZ,
    si_prefix=SIPrefix.KILO,
    min_value=0,
    max_value=1000000,
    allowed_values=None,
    description="Frequency of the transducer"
)

# AnswerFieldDef instances (for "answer_frequency")
answer_frequency = AnswerFieldDef(
    field_name="frequency",
    field_type=int,
    converter_ref=None,
    si_unit=SIUnit.HERTZ,
    si_prefix=SIPrefix.KILO,
    format_str="freq: {value}{si}",
    description=None
)

frequency_command = Command(
    code=1000,
    command_defs=[
        CommandDef(
            string_identifier="!freq",
            aliases=["!f", "!frequency", "set_frequency"],
            index_param=None,
            setter_param=param_frequency
        )
    ],
    answer_defs=[
        AnswerDef(
            fields=[answer_frequency]
        )
    ],
    description="Command to set the frequency of the transducer on the device.",
    tags=["frequency", "transducer", "control"]

)


# Protocol instance
protocol = Protocol(
    version=version,
    commands=[
        CommandListExport(
            exports=[
                frequency_command
            ],
            descriptor = MetaExportDescriptor(
                min_protocol_version=Version(major=1, minor=0, patch=0),
                deprecated_protocol_version=None,
                included_device_types=None,
                excluded_device_types=[DeviceType.DESCALE]
            )
        )
    ]
)

# Now you have `protocol` representing the JSON structure
