import asyncio
from typing import Type

import attrs
from attrs import validators

from sonicpackage.interfaces import Scriptable
from sonicpackage.procedures.holder import HolderArgs, convert_to_holder_args
from sonicpackage.procedures.procedure import Procedure


@attrs.define(auto_attribs=True)
class TuneArgs:
    step: int = attrs.field(validator=[
        validators.instance_of(int),
        validators.ge(10),
        validators.le(100000)
    ])
    time: HolderArgs = attrs.field(
        default=HolderArgs(100, "ms"), 
        converter=convert_to_holder_args
    )

class TuneProc(Procedure):
    @classmethod
    def get_args_class(cls) -> Type: 
        return TuneArgs

    async def execute(self, device: Scriptable, args: TuneArgs) -> None:
        try:
            await device.execute_command(f"!tune_step={args.step}")
            await device.execute_command(f"!tune_time={args.time.duration_in_ms}")
            await device.execute_command("!tune")
        except asyncio.CancelledError:
            await device.execute_command("!stop")
        finally:
            await device.get_remote_proc_finished_event().wait()
