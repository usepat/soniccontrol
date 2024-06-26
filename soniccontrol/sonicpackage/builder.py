import asyncio
from typing import *

import attrs
from icecream import ic
from soniccontrol.sonicpackage.command import Answer
from soniccontrol.sonicpackage.interfaces import Communicator
from soniccontrol.sonicpackage.sonicamp_ import (
    Command,
    Commands,
    Info,
    Modules,
    SerialCommunicator,
    SonicAmp,
    Status,
)


@attrs.define
class AmpBuilder:
    def _add_commands_from_list_command_answer(
        self, commands: Commands, sonicAmp: SonicAmp, answer: Answer
    ) -> None:
        command_names = answer.string.split("#")
        for command_name in command_names:
            command_attrs = [
                command
                for name, command in commands.__dict__.items()
                if not name.startswith("_") and not callable(command)
            ]
            command = next(
                filter(lambda c: c.message == command_name, command_attrs), None
            )
            if command:
                sonicAmp.add_command(command)

    async def build_amp(self, ser: Communicator, commands: Commands) -> SonicAmp:
        await ser.connection_opened.wait()

        result_dict: Dict[str, Any] = ser.init_command.status_result

        if hasattr(commands, "get_type"):
            await commands.get_type.execute()
            if commands.get_type.answer.valid:
                result_dict.update(commands.get_type.status_result)

        await commands.get_info.execute()
        if commands.get_info.answer.valid:
            result_dict.update(commands.get_info.status_result)

        if hasattr(commands, "get_overview"):
            await commands.get_overview.execute()
            if commands.get_overview.answer.valid:
                result_dict.update(commands.get_overview.status_result)

        status = Status()
        info = Info()
        await status.update(**result_dict)
        info.update(**result_dict)
        info.firmware_info = commands.get_info.answer.string

        ic(result_dict)
        sonicamp: SonicAmp = SonicAmp(serial=ser, info=info, status=status)

        if hasattr(commands, "get_command_list"):
            await commands.get_command_list.execute()
            if commands.get_command_list.answer.valid:
                self._add_commands_from_list_command_answer(
                    commands, sonicamp, commands.get_command_list.answer
                )
                return sonicamp

        basic_commands: Tuple[Command] = (
            commands.signal_on,
            commands.signal_off,
            commands.get_overview,
            commands.get_info,
        )

        basic_catch_commands: Tuple[Command] = (
            commands.set_frequency,
            commands.set_gain,
            commands.set_serial_mode,
            commands.set_khz_mode,
            commands.set_mhz_mode,
        )

        atf_commands: Tuple[Command] = (
            commands.set_atf1,
            commands.get_atf1,
            commands.set_atk1,
            commands.set_atf2,
            commands.get_atf2,
            commands.set_atk2,
            commands.set_atf3,
            commands.get_atf3,
            commands.set_atk3,
            commands.set_att1,
            commands.get_att1,
        )

        basic_wipe_commands: Tuple[Command] = (commands.set_frequency,)

        basic_descale_commands: Tuple[Command] = (
            commands.set_switching_frequency,
            commands.set_analog_mode,
            commands.set_serial_mode,
            commands.set_gain,
        )

        sonicamp.add_commands(basic_commands)
        if sonicamp.info.version >= 0.3:
            sonicamp.add_commands((commands.get_status, commands.get_type))

        if sonicamp.info.device_type == "catch":
            sonicamp.add_commands(basic_catch_commands)
            if sonicamp.info.version == 0.3:
                sonicamp.add_command(commands.get_sens)
            elif sonicamp.info.version == 0.4:
                sonicamp.add_command(commands.get_sens_factorised)
            elif sonicamp.info.version == 0.5:
                sonicamp.add_command(commands.get_sens_fullscale_values)

            if sonicamp.info.version >= 0.4:
                sonicamp.add_commands(atf_commands)
                for command in atf_commands:
                    await sonicamp.execute_command(command)

        elif sonicamp.info.device_type == "descale":
            sonicamp.add_commands(basic_descale_commands)

        elif sonicamp.info.device_type == "wipe":
            sonicamp.add_commands(basic_wipe_commands)

        return sonicamp
