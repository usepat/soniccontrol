import asyncio
from typing import Type

import attrs

from sonicpackage.interfaces import Scriptable
from sonicpackage.procedures.procedure import Procedure


@attrs.define(auto_attribs=True)
class AutoArgs:
    pass

class AutoProc(Procedure):
    @classmethod
    def get_args_class(cls) -> Type: 
        return AutoArgs

    async def execute(self, device: Scriptable, _args: AutoArgs) -> None:
        try:
            await device.execute_command("!auto")
        except asyncio.CancelledError:
            await device.execute_command("!stop")
        finally:
            await device.get_remote_proc_finished_event().wait()
