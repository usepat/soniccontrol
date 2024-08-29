import logging
from typing import Any, Dict, Tuple, Union

from sonicpackage.command import Answer
from sonicpackage.commands import CommandSet, CommandSetLegacy
from sonicpackage.communication.communicator import Communicator
from sonicpackage.sonicamp_ import (
    Command,
    Info,
    SonicAmp,
    Status,
)


class AmpBuilder:
    def _add_commands_from_list_command_answer(
        self, commands: CommandSet, sonicAmp: SonicAmp, answer: Answer
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

    async def build_amp(self, ser: Communicator, commands: Union[CommandSet, CommandSetLegacy], logger: logging.Logger = logging.getLogger()) -> SonicAmp:
        builder_logger = logging.getLogger(logger.name + "." + AmpBuilder.__name__)
        
        await ser.connection_opened.wait()
        builder_logger.debug("Serial connection is open, start building device")

        result_dict: Dict[str, Any] = ser.handshake_result

        builder_logger.debug("Try to figure out which device it is with ?info, ?type, ?")
        if isinstance(commands, CommandSetLegacy):
            await commands.get_type.execute()
            if commands.get_type.answer.valid:
                result_dict.update(commands.get_type.status_result)

        await commands.get_info.execute()
        if commands.get_info.answer.valid:
            result_dict.update(commands.get_info.status_result)

        if isinstance(commands, CommandSetLegacy):
            await commands.get_overview.execute()
            if commands.get_overview.answer.valid:
                result_dict.update(commands.get_overview.status_result)

        status = Status()
        info = Info()
        await status.update(**result_dict)
        info.update(**result_dict)
        info.firmware_info = commands.get_info.answer.string
        builder_logger.info("Device type: %s", info.device_type)
        builder_logger.info("Firmware version: %s", info.firmware_version)
        builder_logger.info("Firmware info: %s", info.firmware_info)

        builder_logger.debug("Build device")
        sonicamp: SonicAmp = SonicAmp(serial=ser, info=info, status=status, logger=logger)

        if isinstance(commands, CommandSet):
            builder_logger.debug("Get list of available commands of device")
            await commands.get_command_list.execute()
            if commands.get_command_list.answer.valid:
                self._add_commands_from_list_command_answer(
                    commands, sonicamp, commands.get_command_list.answer
                )
                builder_logger.debug("List of the commands that are supported: %s", str(sonicamp.commands.keys()))
                return sonicamp
            else:
                raise Exception("Wtf, the new devices with Sonic Protocol v2 have to implement get_command_list")
        else:

            basic_commands: Tuple[Command, ...] = (
                commands.signal_on,
                commands.signal_off,
                commands.get_overview,
                commands.get_info,
            )

            basic_catch_commands: Tuple[Command, ...] = (
                commands.set_frequency,
                commands.set_gain,
                commands.set_serial_mode,
                commands.set_khz_mode,
                commands.set_mhz_mode,
            )

            atf_commands: Tuple[Command, ...] = (
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

            basic_wipe_commands: Tuple[Command, ...] = (commands.set_frequency,)

            basic_descale_commands: Tuple[Command, ...] = (
                commands.set_switching_frequency,
                commands.set_analog_mode,
                commands.set_serial_mode,
                commands.set_gain,
            )

            builder_logger.debug("Add commands depending on the version and type of the device")
            sonicamp.add_commands(basic_commands)
            if sonicamp.info.firmware_version >= (0, 3, 0):
                sonicamp.add_commands((commands.get_status, commands.get_type))

            if sonicamp.info.device_type == "catch":
                sonicamp.add_commands(basic_catch_commands)
                if sonicamp.info.firmware_version[:2] == (0, 3):
                    sonicamp.add_command(commands.get_sens)
                elif sonicamp.info.firmware_version[:2] == (0, 4):
                    sonicamp.add_command(commands.get_sens_factorised)
                elif sonicamp.info.firmware_version[:2] == (0, 5):
                    sonicamp.add_command(commands.get_sens_fullscale_values)

                if sonicamp.info.firmware_version >= (0, 4, 0):
                    sonicamp.add_commands(atf_commands)
                    for command in atf_commands:
                        await sonicamp.execute_command(command)

            elif sonicamp.info.device_type == "descale":
                sonicamp.add_commands(basic_descale_commands)

            elif sonicamp.info.device_type == "wipe":
                sonicamp.add_commands(basic_wipe_commands)

            builder_logger.debug("List of the commands that are supported: %s", str(sonicamp.commands.keys()))
            return sonicamp
