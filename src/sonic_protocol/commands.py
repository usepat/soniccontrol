from typing import Any, Dict, List
import attrs
from sonic_protocol.defs import CommandCode, CommandDef, CommandParamDef


class CommandValidator:
    def validate(self, message: str, command_def: CommandDef) -> bool:
        identifiers: List[str] = command_def.string_identifier if isinstance(command_def.string_identifier, list) else [command_def.string_identifier]

        for identifier in identifiers:
            if not message.startswith(identifier):
                continue
            
            args: List[str] = message[len(identifier):].split("=", maxsplit=1)
            args = list(filter(lambda arg: len(arg) > 0, args))

            if command_def.index_param is not None:
                index = args.pop(0)
                if not self._validate_param(index, command_def.index_param):
                    continue
                
            if command_def.setter_param is not None:
                setter = args.pop(0)
                if not self._validate_param(setter, command_def.setter_param):
                    continue
                
            if len(args) > 0:
                continue
            else:
                return True
                
        return False
    
    def _validate_param(self, arg: Any | None, command_param_def: CommandParamDef) -> bool:
        if arg is None:
            return False
        
        type_constructor = command_param_def.param_type
        
        try:
            value = type_constructor(arg)
        except Exception:
            return False
        
        if command_param_def.allowed_values:
            return value in command_param_def.allowed_values
        
        return True


class Command:
    def __init__(self, code: CommandCode):
        self._code = code

    @property
    def code(self) -> CommandCode:
        return self._code

    @property
    def args(self) -> Dict[str, Any]:
        return attrs.asdict(self)


@attrs.define()
class GetProtocol(Command):
    def __attrs_post_init__(self):
        super().__init__(code=CommandCode.GET_PROTOCOL)

@attrs.define()
class GetInfo(Command):
    def __attrs_post_init__(self):
        super().__init__(code=CommandCode.GET_INFO)

@attrs.define()
class ListAvailableCommands(Command):
    def __attrs_post_init__(self):
        super().__init__(code=CommandCode.LIST_AVAILABLE_COMMANDS)

@attrs.define()
class GetUpdate(Command):
    def __attrs_post_init__(self):
        super().__init__(code=CommandCode.DASH)

@attrs.define()
class GetGain(Command):
    def __attrs_post_init__(self):
        super().__init__(code=CommandCode.GET_GAIN)

@attrs.define()
class SetFrequency(Command):
    def __attrs_post_init__(self):
        super().__init__(code=CommandCode.SET_FREQ)

    value: int = attrs.field(alias="frequency")    

@attrs.define()
class SetGain(Command):
    def __attrs_post_init__(self):
        super().__init__(code=CommandCode.SET_GAIN)

    value: int = attrs.field(alias="gain")

@attrs.define()
class SetOn(Command):
    def __attrs_post_init__(self):
        super().__init__(code=CommandCode.SET_ON)

@attrs.define()
class SetOff(Command):
    def __attrs_post_init__(self):
        super().__init__(code=CommandCode.SET_OFF)

@attrs.define()
class SetAtf(Command):
    def __attrs_post_init__(self):
        super().__init__(code=CommandCode.SET_ATF)

    index: int = attrs.field()
    value: int = attrs.field(alias="atf")
