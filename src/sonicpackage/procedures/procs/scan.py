import asyncio
from typing import Type

import attrs
from attrs import validators

from sonicpackage.interfaces import Scriptable
from sonicpackage.procedures.holder import HolderArgs, convert_to_holder_args
from sonicpackage.procedures.procedure import Procedure


@attrs.define(auto_attribs=True)
class ScanArgs:
    gext: int = attrs.field(validator=[
        validators.instance_of(int),
        validators.ge(0),
        validators.le(1000000)
    ])
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

class ScanProc(Procedure):
    @classmethod
    def get_args_class(cls) -> Type: 
        return ScanArgs

    async def execute(self, device: Scriptable, args: ScanArgs) -> None:
        try:
            await device.execute_command(f"!scan_gext={args.gext}")
            await device.execute_command(f"!scan_rang={args.rang}")
            await device.execute_command(f"!scan_step={args.step}")
            await device.execute_command(f"!scan_sing={args.sing.duration_in_ms}")
            await device.execute_command("!scan")
        except asyncio.CancelledError:
            await device.execute_command("!stop")
        finally:
            await device.get_remote_proc_finished_event().wait()
