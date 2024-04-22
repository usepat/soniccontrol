import asyncio
from typing import *

import attrs
from icecream import ic
from soniccontrol.sonicpackage.sonicamp_ import (Command, Commands, Info,
                                                 Modules, SerialCommunicator,
                                                 SonicAmp, Status)


@attrs.define
class AmpBuilder:
    async def build_amp(self, ser: SerialCommunicator) -> SonicAmp:
        await ser.connect()
        await ser.connection_opened.wait()
        Command.set_serial_communication(ser)

        result_dict: Dict[str, Any] = ser.init_command.status_result

        await Commands.get_type.execute()
        if Commands.get_type.answer.valid:
            result_dict.update(Commands.get_type.status_result)

        await Commands.get_info.execute()
        if Commands.get_info.answer.valid:
            result_dict.update(Commands.get_info.status_result)

        await Commands.get_overview.execute()
        if Commands.get_overview.answer.valid:
            result_dict.update(Commands.get_overview.status_result)

        status: Status = await Status().update(**result_dict)
        info: Info = Info(firmware_info=Commands.get_info.answer.string).update(
            **result_dict
        )

        ic(result_dict)
        sonicamp: SonicAmp = SonicAmp(serial=ser, info=info, status=status)

        basic_commands: Tuple[Command] = (
            Commands.signal_on,
            Commands.signal_off,
            Commands.get_overview,
            Commands.get_info,
        )

        basic_catch_commands: Tuple[Command] = (
            Commands.set_frequency,
            Commands.set_gain,
            Commands.set_serial_mode,
            Commands.set_khz_mode,
            Commands.set_mhz_mode,
        )

        atf_commands: Tuple[Command] = (
            Commands.set_atf1,
            Commands.get_atf1,
            Commands.set_atk1,
            Commands.set_atf2,
            Commands.get_atf2,
            Commands.set_atk2,
            Commands.set_atf3,
            Commands.get_atf3,
            Commands.set_atk3,
            Commands.set_att1,
            Commands.get_att1,
        )

        basic_wipe_commands: Tuple[Command] = (Commands.set_frequency,)

        basic_descale_commands: Tuple[Command] = (
            Commands.set_switching_frequency,
            Commands.set_analog_mode,
            Commands.set_serial_mode,
            Commands.set_gain,
        )

        sonicamp.add_commands(basic_commands)
        if sonicamp.info.version >= 0.3:
            sonicamp.add_commands((Commands.get_status, Commands.get_type))

        if sonicamp.info.device_type == "catch":
            sonicamp.should_update.set()
            sonicamp.add_commands(basic_catch_commands)
            if sonicamp.info.version == 0.3:
                sonicamp.add_command(Commands.get_sens)
            elif sonicamp.info.version == 0.4:
                sonicamp.add_command(Commands.get_sens_factorised)
            elif sonicamp.info.version == 0.5:
                sonicamp.add_command(Commands.get_sens_fullscale_values)

            if sonicamp.info.version >= 0.4:
                sonicamp.add_commands(atf_commands)
                for command in atf_commands:
                    await sonicamp.execute_command(command)

        elif sonicamp.info.device_type == "descale":
            sonicamp.add_commands(basic_descale_commands)

        elif sonicamp.info.device_type == "wipe":
            sonicamp.should_update.set()
            sonicamp.add_commands(basic_wipe_commands)

        return sonicamp


async def main():
    builder = AmpBuilder()
    sonicamp = await builder.build_amp("/dev/cu.usbserial-AB0M45SW")
    ic(sonicamp)


if __name__ == "__main__":
    asyncio.run(main())
