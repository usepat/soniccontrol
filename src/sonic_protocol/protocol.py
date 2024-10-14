from sonic_protocol.defs import (
    CommandCode, CommandListExport, ConverterType, FieldType, MetaExportDescriptor, 
    Protocol, SonicTextCommandAttrs, UserManualAttrs, Version, CommandDef, AnswerDef,
    AnswerFieldDef, CommandContract, DeviceType,
)
from sonic_protocol.command_contracts.fields import (
    field_frequency, field_gain, field_temperature, field_urms, field_irms, field_phase, field_signal, field_ts_flag,
)
from sonic_protocol.command_contracts.transducer_commands import (
    set_frequency, get_frequency, set_swf, get_swf, get_atf, set_atf, get_att, set_att, get_atk, set_atk,
    set_gain, get_gain, set_on, set_off, get_temp, get_uipt,
)
from sonic_protocol.command_contracts.communication_commands import (
     set_termination, set_physical_comm_channel, set_comm_protocol, set_input_source,
)

# Version instance
version = Version(major=1, minor=0, patch=0)

"""!
    The ?protocol command is the most important command
    Without ?protocol there is no way to determine which protocol is used.
    So this command is needed.
    There should also only exist one version of this command. Because else determining the protocol version would be a nightmare.
    If you want to extend the ?protocol command. consider adding other commands
"""

field_device_type = AnswerFieldDef(
    field_path=["device_type"],
    field_type=FieldType(DeviceType, converter_ref=ConverterType.ENUM),
)

def create_version_field(name: str) -> AnswerFieldDef:
    return AnswerFieldDef(
        field_path=[name], 
        field_type=FieldType(Version, converter_ref=ConverterType.VERSION), 
    )

get_protocol = CommandContract(
    code=CommandCode.GET_PROTOCOL,
    command_defs=CommandDef(
        sonic_text_attrs=SonicTextCommandAttrs(
            string_identifier="?protocol"
        )
    ),
    answer_defs=AnswerDef(
        fields=[
            field_device_type,
            create_version_field("version"),
            AnswerFieldDef(
                field_path=["is_release"], 
                field_type=FieldType(bool, converter_ref=ConverterType.BUILD_TYPE), 
            )
        ]
    ),
    is_release=True
)

build_date_field = AnswerFieldDef(
    field_path=["build_date"],
    field_type=FieldType(str)
)

build_hash_field = AnswerFieldDef(
    field_path=["build_hash"],
    field_type=FieldType(str)
)

get_info = CommandContract(
    code=CommandCode.GET_INFO,
    command_defs=CommandDef(
        sonic_text_attrs=SonicTextCommandAttrs(
            string_identifier="?info"
        )
    ),
    answer_defs=AnswerDef(
        fields=[
            field_device_type,
            create_version_field("hardware_version"),
            create_version_field("firmware_version"),
            build_hash_field,
            build_date_field,
        ]
    ),
    is_release=True
)

list_available_commands = CommandContract(
    code=CommandCode.LIST_AVAILABLE_COMMANDS,
    command_defs=CommandDef(
        sonic_text_attrs=SonicTextCommandAttrs(
            string_identifier=["?list_commands", "?commands"]
        )
    ),
    answer_defs=AnswerDef(
        fields=[
            AnswerFieldDef(
                field_path=["list_commands"],
                field_type=FieldType(str)
            )
        ]
    ),
    user_manual_attrs=UserManualAttrs(
        description="Command to get a list of available commands."
    ),
    is_release=True,
    tags=["commands"]
)

get_help = CommandContract(
    code=CommandCode.GET_HELP,
    command_defs=CommandDef(
        sonic_text_attrs=SonicTextCommandAttrs(
            string_identifier="?help"
        )
    ),
    answer_defs=AnswerDef(
        fields=[
            AnswerFieldDef(
                field_path=["help"],
                field_type=FieldType(str)
            )
        ]
    ),
    user_manual_attrs=UserManualAttrs(
        description="Command to get help information."
    ),
    is_release=True,
    tags=["help"]
)

error_code_field = AnswerFieldDef(
    field_path=["error_code"],
    field_type=FieldType(field_type=int)
)

procedure_field = AnswerFieldDef(
    field_path=["procedure"],
    field_type=FieldType(field_type=int)
)

get_update = CommandContract(
    code=CommandCode.DASH,
    command_defs=CommandDef(
        sonic_text_attrs=SonicTextCommandAttrs(
            string_identifier=["-", "get_update"]
        )
    ),
    answer_defs=AnswerDef(
        fields=[
            error_code_field,
            field_frequency,
            field_gain,
            procedure_field,
            field_temperature,
            field_urms,
            field_irms,
            field_phase,
            field_signal,
            field_ts_flag
        ]
    ),
    user_manual_attrs=UserManualAttrs(
        description="Mainly used by sonic control to get a short and computer friendly parsable status update."
    ),
    is_release=True,
    tags=["update", "status"]
)


protocol = Protocol(
    version=Version(1, 0, 0),
    commands=[
        CommandListExport(
            exports=[
                get_protocol,
                get_info,
                list_available_commands,
                get_help,
                get_update,
                set_gain,
                get_gain,
                set_on,
                set_off,
                get_temp,
                get_uipt,
                set_termination,
                set_physical_comm_channel,
                set_comm_protocol,
                set_input_source,
            ],
            descriptor=MetaExportDescriptor(
                min_protocol_version=Version(major=1, minor=0, patch=0)
            )
        ),
        CommandListExport(
            exports=[
                set_frequency,
                get_frequency,
                get_atf,
                set_atf,
                get_att,
                set_att,
                get_atk,
                set_atk,
            ],
            descriptor = MetaExportDescriptor(
                min_protocol_version=Version(major=1, minor=0, patch=0),
                excluded_device_types=[DeviceType.DESCALE]
            )
        ),
        CommandListExport(
            exports=[
                set_swf,
                get_swf,
            ],
            descriptor = MetaExportDescriptor(
                min_protocol_version=Version(major=1, minor=0, patch=0),
                included_device_types=[DeviceType.DESCALE]
            )
        )
    ]
)

