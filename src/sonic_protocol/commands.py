from typing import Any, Dict
import attrs
from sonic_protocol.defs import CommandCode


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

    frequency: int = attrs.field()    

@attrs.define()
class SetGain(Command):
    def __attrs_post_init__(self):
        super().__init__(code=CommandCode.SET_GAIN)

    gain: int = attrs.field()

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
    atf: int = attrs.field()
