import asyncio
from typing import Type

import attrs
from attrs import validators

from sonicpackage.interfaces import Scriptable
from sonicpackage.procedures.holder import HolderArgs, convert_to_holder_args
from sonicpackage.procedures.procedure import Procedure


@attrs.define(auto_attribs=True)
class WipeArgs:
    rang: int = attrs.field(validator=[
        validators.instance_of(int),
        validators.ge(0),
        validators.le(1000000)
    ])
    step: int = attrs.field(validator=[
        validators.instance_of(int),
        validators.ge(10),
        validators.le(100000)
    ])
    sing: HolderArgs = attrs.field(
        default=HolderArgs(100, "ms"), 
        converter=convert_to_holder_args
    )
    pause: HolderArgs = attrs.field(
        default=HolderArgs(100, "ms"), 
        converter=convert_to_holder_args
    )
    break_time: HolderArgs = attrs.field(
        default=HolderArgs(100, "ms"), 
        converter=convert_to_holder_args
    )

class WipeProc(Procedure):
    @classmethod
    def get_args_class(cls) -> Type: 
        return WipeArgs

    async def execute(self, device: Scriptable, args: WipeArgs) -> None:
        try:
            await device.execute_command(f"!wipe_rang={args.rang}")
            await device.execute_command(f"!wipe_step={args.step}")
            await device.execute_command(f"!wipe_sing={args.sing.duration_in_ms}")
            await device.execute_command(f"!wipe_pause={args.pause.duration_in_ms}")
            await device.execute_command(f"!wipe_break={args.break_time.duration_in_ms}")
            await device.execute_command("!wipe")
        except asyncio.CancelledError:
            await device.execute_command("!stop")
        finally:
            await device.get_remote_proc_finished_event().wait()
