from __future__ import annotations
import datetime
import attrs
from sonicpackage.interfaces import Communicator
from sonicpackage.command import Command, CommandValidator



class CommandSetLegacy:    
    def __init__(self, serial: Communicator):
        self.get_overview: Command = Command(
            message="?",
            estimated_response_time=0.5,
            expects_long_answer=True,
            validators=(
                CommandValidator(pattern=r".*(khz|mhz).*", relay_mode=str),
                CommandValidator(
                    pattern=r".*freq[uency]*\s*=?\s*([\d]+).*", frequency=int
                ),
                CommandValidator(pattern=r".*gain\s*=?\s*([\d]+).*", gain=int),
                CommandValidator(
                    pattern=r".*signal.*(on|off).*",
                    signal=lambda b: bool(b.lower() == "on"),
                ),
            ),
            serial_communication=serial,
        )

        self.get_type: Command = Command(
            message="?type",
            estimated_response_time=0.5,
            validators=CommandValidator(
                pattern=r"sonic(catch|wipe|descale)", device_type=str
            ),
            serial_communication=serial,
        )

        self.get_info: Command = Command(
            message="?info",
            estimated_response_time=2.5,
            expects_long_answer=True,
            validators=(
                CommandValidator(
                    pattern=r".*ver.*([\d]+[.][\d]+).*", 
                    firmware_version=attrs.converters.pipe(str, lambda v: v + ".0") # add a third version number, so that it is in line with the newer firmware version format
                ),
                CommandValidator(pattern=r"sonic(catch|wipe|descale)", type_=str),
            ),
            serial_communication=serial,
        )
        self.set_frequency: Command = Command(
            message="!f=",
            validators=CommandValidator(
                pattern=r".*freq[uency]*\s*=?\s*([\d]+).*", frequency=int
            ),
            serial_communication=serial,
        )

        self.set_gain: Command = Command(
            message="!g=",
            validators=CommandValidator(pattern=r".*gain\s*=?\s*([\d]+).*", gain=int),
            serial_communication=serial,
        )

        self.set_switching_frequency: Command = Command(
            message="!swf=",
            validators=CommandValidator(
                pattern=r".*freq[uency]*\s*=?\s*([\d]+).*", switching_frequency=int
            ),
            serial_communication=serial,
        )

        self.get_status: Command = Command(
            message="-",
            estimated_response_time=0.35,
            validators=CommandValidator(
                pattern=r"([\d])(?:[-#])([\d]+)(?:[-#])([\d]+)(?:[-#])([\d]+)(?:[-#])([\d])(?:[-#])(?:[']?)([-]?[\d]+[.][\d]+)?(?:[']?)",
                error=int,
                frequency=int,
                gain=int,
                protocol=int,
                wipe_mode=attrs.converters.to_bool,
                temperature=attrs.converters.pipe(
                    float, lambda t: t if -70 < t < 200 else None
                ),
                signal={
                    "keywords": ("frequency",),
                    "worker": lambda frequency: frequency != 0,
                },
            ),
            serial_communication=serial,
        )

        self.get_sens: Command = Command(
            message="?sens",
            estimated_response_time=0.35,
            validators=(
                CommandValidator(
                    pattern=r"([\d]+)(?:[\s]+)([-]?[\d]+[.]?[\d]?)(?:[\s]+)([-]?[\d]+[.]?[\d]?)(?:[\s]+)([-]?[\d]+[.]?[\d]?)",
                    frequency=int,
                    urms=float,
                    irms=float,
                    phase=float,
                ),
                CommandValidator(
                    pattern=r".*(error).*",
                    signal=lambda error: False,
                    frequency=lambda error: 0,
                    urms=lambda error: 0,
                    irms=lambda error: 0,
                    phase=lambda error: 0,
                ),
            ),
            serial_communication=serial,
        )

        self.get_sens_factorised: Command = Command(
            message="?sens",
            estimated_response_time=0.35,
            validators=(
                CommandValidator(
                    pattern=r"([\d]+)(?:[\s]+)([-]?[\d]+[.]?[\d]?)(?:[\s]+)([-]?[\d]+[.]?[\d]?)(?:[\s]+)([-]?[\d]+[.]?[\d]?)",
                    frequency=int,
                    urms=attrs.converters.pipe(float, lambda urms: urms / 1000),
                    irms=attrs.converters.pipe(float, lambda irms: irms / 1000),
                    phase=attrs.converters.pipe(float, lambda phase: phase / 1_000_000),
                ),
                CommandValidator(
                    pattern=r".*(error).*",
                    signal=lambda error: False,
                    frequency=lambda error: 0,
                    urms=lambda error: 0,
                    irms=lambda error: 0,
                    phase=lambda error: 0,
                ),
            ),
            serial_communication=serial,
        )

        self.get_sens_fullscale_values: Command = Command(
            message="?sens",
            estimated_response_time=0.35,
            validators=(
                CommandValidator(
                    pattern=r"([\d]+)(?:[\s]+)([-]?[\d]+[.]?[\d]?)(?:[\s]+)([-]?[\d]+[.]?[\d]?)(?:[\s]+)([-]?[\d]+[.]?[\d]?)",
                    frequency=int,
                    urms=attrs.converters.pipe(
                        float,
                        lambda urms: urms if urms > 282_300 else 282_300,
                        lambda urms: (urms * 0.000_400_571 - 1_130.669_402) * 1000
                        + 0.5,
                    ),
                    irms=attrs.converters.pipe(
                        float,
                        lambda irms: irms if irms > 3_038_000 else 303_800,
                        lambda irms: (irms * 0.000_015_601 - 47.380671) * 1000 + 0.5,
                    ),
                    phase=attrs.converters.pipe(
                        float, lambda phase: phase * 0.125 * 100
                    ),
                ),
                CommandValidator(
                    pattern=r".*(error).*",
                    signal=lambda error: False,
                    frequency=lambda error: 0,
                    urms=lambda error: 0,
                    irms=lambda error: 0,
                    phase=lambda error: 0,
                ),
            ),
            serial_communication=serial,
        )

        self.signal_on: Command = Command(
            message="!ON",
            validators=(
                CommandValidator(
                    pattern=r"signal.*(on)", signal=lambda b: b.lower() == "on"
                ),
                CommandValidator(
                    pattern=r"\d+#(.+)", signal=lambda b: b.lower() == "on"
                ),
            ),
            serial_communication=serial,
        )

        self.signal_off: Command = Command(
            message="!OFF",
            estimated_response_time=0.4,
            validators=(
                CommandValidator(
                    pattern=r"signal.*(off)", signal=lambda b: not b.lower() == "off"
                ),
                CommandValidator(
                    pattern=r"\d+#(.+)", signal=lambda b: not b.lower() == "off"
                ),
            ),
            serial_communication=serial,
        )

        self.signal_auto: Command = Command(
            message="!AUTO",
            estimated_response_time=0.5,
            validators=CommandValidator(pattern=r".*(auto).*", protocol=str),
            serial_communication=serial,
        )

        self.set_serial_mode: Command = Command(
            message="!SERIAL",
            validators=CommandValidator(
                pattern=r".*mode.*(serial).*", communication_mode=str
            ),
            serial_communication=serial,
        )

        self.set_analog_mode: Command = Command(
            message="!ANALOG",
            validators=CommandValidator(
                pattern=r".*mode.*(analog).*", communication_mode=str
            ),
            serial_communication=serial,
        )

        self.set_khz_mode: Command = Command(
            message="!KHZ",
            validators=CommandValidator(pattern=r".*(khz).*", relay_mode=str),
            serial_communication=serial,
        )

        self.set_mhz_mode: Command = Command(
            message="!MHZ",
            validators=CommandValidator(pattern=r".*(mhz).*", relay_mode=str),
            serial_communication=serial,
        )

        self.set_atf1: Command = Command(
            message="!atf1=",
            validators=CommandValidator(
                pattern=r".*freq[quency]*.*1.*=.*([\d]+)", atf1=int
            ),
            serial_communication=serial,
        )

        self.get_atf1: Command = Command(
            message="?atf1",
            expects_long_answer=True,
            validators=CommandValidator(
                pattern=r"([\d]+)\n([-]?[\d]+[\.]?[\d]*)", atf1=int, atk1=float
            ),
            serial_communication=serial,
        )

        self.set_atk1: Command = Command(
            message="!atk1=",
            validators=CommandValidator(pattern=r"([-]?[\d]*[\.]?[\d]*)", atk1=float),
            serial_communication=serial,
        )

        self.set_atf2: Command = Command(
            message="!atf2=",
            validators=CommandValidator(
                pattern=r".*freq[quency]*.*2.*=.*([\d]+)", atf2=int
            ),
            serial_communication=serial,
        )

        self.get_atf2: Command = Command(
            message="?atf2",
            expects_long_answer=True,
            validators=CommandValidator(
                pattern=r"([\d]+)\n([-]?[\d]+[\.]?[\d]*)", atf2=int, atk2=float
            ),
            serial_communication=serial,
        )

        self.set_atk2: Command = Command(
            message="!atk2=",
            validators=CommandValidator(pattern=r"([-]?[\d]*[\.]?[\d]*)", atk2=float),
            serial_communication=serial,
        )

        self.set_atf3: Command = Command(
            message="!atf3=",
            validators=CommandValidator(
                pattern=r".*freq[quency]*.*3.*=.*([\d]+)", atf3=int
            ),
            serial_communication=serial,
        )

        self.get_atf3: Command = Command(
            message="?atf3",
            expects_long_answer=True,
            validators=CommandValidator(
                pattern=r"([\d]+)\n([-]?[\d]+[\.]?[\d]*)", atf3=int, atk3=float
            ),
            serial_communication=serial,
        )

        self.set_atk3: Command = Command(
            message="!atk3=",
            validators=CommandValidator(pattern=r"([-]?[\d]*[\.]?[\d]*)", atk3=float),
            serial_communication=serial,
        )

        self.set_att1: Command = Command(
            message="!att1=",
            validators=CommandValidator(pattern=r"([-]?[\d]*[\.]?[\d]*)", att1=float),
            serial_communication=serial,
        )

        self.get_att1: Command = Command(
            message="?att1",
            validators=CommandValidator(pattern=r"([-]?[\d]*[\.]?[\d]*)", att1=float),
            serial_communication=serial,
        )

class CommandSet:
    def __init__(self, serial: Communicator):
        # TODO: Ask about ?error, how do we validate errors, if there is not a known number of errors
        type_validator: CommandValidator = CommandValidator(
            pattern=r"sonic(catch|wipe|descale)", type_=str
        )
        firmware_version_validator: CommandValidator = CommandValidator(
            pattern=r".*([\d]\.[\d]\.[\d]).*", firmware_version=str
        )
        update_date_validator: CommandValidator = CommandValidator(
            pattern=r".*(\d{2}.\d{2}.\d{4}).*",
            date=lambda date: (datetime.datetime.strptime(date, "%d.%m.%Y").date()),
        )
        protocol_version_validator: CommandValidator = CommandValidator(
            pattern=r".*([\d]\.[\d]\.[\d]).*", protocol_version=str
        )
        pzt_validator: CommandValidator = CommandValidator(
            pattern=r"(.*)[#](\d+)", id=str, frequency=int
        )
        frequency_validator: CommandValidator = CommandValidator(
            pattern=r"(\d+)\s*Hz", frequency=int
        )
        gain_validator: CommandValidator = CommandValidator(
            pattern=r"(\d+)\s*%", gain=int
        )
        temp_validator: CommandValidator = CommandValidator(
            pattern=r"(\d+)\s*°C", temp=float
        )

        # TODO: What should be the units in sonicpackage?
        uipt_validator: CommandValidator = CommandValidator(
            pattern=r"(\d+)\s*uV[#](\d+)\s*uA[#](\d+)\s*mDeg[#](\d+)\s*mDegC",
            urms=int,
            irms=int,
            phase=int,
            temperature=int,
        )
        adc_validator: CommandValidator = CommandValidator(
            pattern=r"(\d+)\s*uV", adc_voltage=int
        )

        # TODO: Ask about the diffirence between !EXTERN and !RELAY
        control_mode_validator: CommandValidator = CommandValidator(
            pattern=r"(\w+)\s*mode", control_mode=str
        )
        relay_mode_validator: CommandValidator = CommandValidator(
            pattern=r"(\w+)\s*mode", relay_mode=str
        )

        # ATF validators
        atf1_validator: CommandValidator = CommandValidator(
            pattern=r"atf1=(\d+)\s*Hz", atf1=int
        )
        atf2_validator: CommandValidator = CommandValidator(
            pattern=r"atf2=(\d+)\s*Hz", atf2=int
        )
        atf3_validator: CommandValidator = CommandValidator(
            pattern=r"atf3=(\d+)\s*Hz", atf3=int
        )
        atf4_validator: CommandValidator = CommandValidator(
            pattern=r"atf4=(\d+)\s*Hz", atf4=int
        )

        # ATK validators
        atk1_validator: CommandValidator = CommandValidator(
            pattern=r"atk1=(\d+\.\d+)", atk1=float
        )
        atk2_validator: CommandValidator = CommandValidator(
            pattern=r"atk2=(\d+\.\d+)", atk2=float
        )
        atk3_validator: CommandValidator = CommandValidator(
            pattern=r"atk3=(\d+\.\d+)", atk3=float
        )
        atk4_validator: CommandValidator = CommandValidator(
            pattern=r"atk4=(\d+\.\d+)", atk4=float
        )

        # ATON validators
        aton1_validator: CommandValidator = CommandValidator(
            pattern=r"aton1=(\d+)\s*ms", aton1=int
        )
        aton2_validator: CommandValidator = CommandValidator(
            pattern=r"aton2=(\d+)\s*ms", aton2=int
        )
        aton3_validator: CommandValidator = CommandValidator(
            pattern=r"aton3=(\d+)\s*ms", aton3=int
        )
        aton4_validator: CommandValidator = CommandValidator(
            pattern=r"aton4=(\d+)\s*ms", aton4=int
        )

        # ATT validators
        att1_validator: CommandValidator = CommandValidator(
            pattern=r"att1=(\d+\.\d+)\s*°C", att1=float
        )
        att2_validator: CommandValidator = CommandValidator(
            pattern=r"att2=(\d+\.\d+)\s*°C", att2=float
        )
        att3_validator: CommandValidator = CommandValidator(
            pattern=r"att3=(\d+\.\d+)\s*°C", att3=float
        )
        att4_validator: CommandValidator = CommandValidator(
            pattern=r"att4=(\d+\.\d+)\s*°C", att4=float
        )

        signal_off_validator: CommandValidator = CommandValidator(
            pattern=r".*(off).*", signal=lambda b: not b.lower() == "off"
        )
        signal_on_validator: CommandValidator = CommandValidator(
            pattern=r".*(on).*", signal=lambda b: b.lower() == "on"
        )

        ms_value_validator: CommandValidator = CommandValidator(
            pattern=r"(\d+)\s*ms", time_value=int
        )
        float_value_validator: CommandValidator = CommandValidator(
            pattern=r"(\d+\.\d+)", value=float
        )

        self.set_frequency: Command = Command(
            message="!freq=",
            validators=frequency_validator,
            serial_communication=serial,
        )
        self.set_gain: Command = Command(
            message="!gain=",
            validators=gain_validator,
            serial_communication=serial,
        )
        self.set_switching_frequency: Command = Command(
            message="!swf=",
            validators=frequency_validator,
            serial_communication=serial,
        )

        # TODO: implement this command for MVP AMP, if needed
        # self.get_overview: Command = Command(
        #     message="?",
        #     estimated_response_time=0.5,
        #     expects_long_answer=True,
        #     validators=(
        #         CommandValidator(pattern=r".*(khz|mhz).*", relay_mode=str),
        #         CommandValidator(
        #             pattern=r".*freq[uency]*\s*=?\s*([\d]+).*", frequency=int
        #         ),
        #         CommandValidator(pattern=r".*g ain\s*=?\s*([\d]+).*", gain=int),
        #         CommandValidator(
        #             pattern=r".*signal.*(on|off).*",
        #             signal=lambda b: bool(b.lower() == "on"),
        #         ),
        #     ),
        #     serial_communication=serial,
        # )

        # TODO: Is the type command in the set of MVP AMP commands?
        # self.get_type: Command = Command(
        #     message="?type",
        #     estimated_response_time=0.5,
        #     validators=type_validator,
        #     serial_communication=serial,
        # )

        self.get_info: Command = Command(
            message="?info",
            estimated_response_time=2.5,
            expects_long_answer=True,
            validators=(
                type_validator,
                firmware_version_validator,
                # TODO: Here should be a HARDWARE ID validator
                update_date_validator,
            ),
            serial_communication=serial,
        )

        # TODO: maybe refactor CommandValidator to store multiple values
        self.get_command_list: Command = Command(
            message="?list_commands",
            estimated_response_time=0.5,
            expects_long_answer=True,
            validators=CommandValidator(pattern=r"(.+)(#(.+))+"),
            serial_communication=serial,
        )

        # TODO: Ask if there are really 2 procedures sending like in the excel sheet
        rInt = r"(\d+)"
        rFloat = r"(\d+\.\d+)"
        rAlpha = r"([a-zA-Z]+)"
        self.get_status: Command = Command(
            message="-",
            estimated_response_time=0.35,
            validators=CommandValidator(
                pattern=f"{rInt}#{rInt}#{rInt}#{rInt}#{rFloat}#{rInt}#{rInt}#{rInt}#{rInt}#{rAlpha}",
                error=int,
                frequency=int,
                gain=int,
                procedure=int,
                temperature=float,
                urms=int,
                irms=int,
                phase=int,
                ts_flag=int,
                signal=attrs.converters.to_bool,
            ),
            serial_communication=serial,
        )

        self.signal_on: Command = Command(
            message="!ON",
            validators=signal_on_validator,
            serial_communication=serial,
        )
        self.signal_off: Command = Command(
            message="!OFF",
            estimated_response_time=0.4,
            validators=signal_off_validator,
            serial_communication=serial,
        )

        # TODO: Implement this command using info from david
        # self.signal_auto: Command = Command(
        #     message="!AUTO",
        #     estimated_response_time=0.5,
        #     validators=CommandValidator(pattern=r".*(auto).*", protocol=str),
        #     serial_communication=serial,
        # )

        self.get_frequency: Command = Command(
            message="?freq",
            validators=frequency_validator,
            serial_communication=serial,
        )
        self.get_gain: Command = Command(
            message="?gain",
            validators=gain_validator,
            serial_communication=serial,
        )
        self.get_uipt: Command = Command(
            message="?uipt",
            validators=uipt_validator,
            serial_communication=serial,
        )
        self.get_pzt: Command = Command(
            message="?pzt",
            validators=pzt_validator,
            serial_communication=serial,
        )

        # ?-ATF,ATK,ATT,ATON Commands
        self.get_atf_values: Command = Command(
            message="?atf",
            estimated_response_time=0.5,
            validators=(
                atf1_validator,
                atf2_validator,
                atf3_validator,
                atf4_validator,
            ),
            serial_communication=serial,
        )
        self.get_atk_values: Command = Command(
            message="?atk",
            estimated_response_time=0.5,
            validators=(
                atk1_validator,
                atk2_validator,
                atk3_validator,
                atk4_validator,
            ),
            serial_communication=serial,
        )
        self.get_att_values: Command = Command(
            message="?att",
            estimated_response_time=0.5,
            validators=(
                att1_validator,
                att2_validator,
                att3_validator,
                att4_validator,
            ),
            serial_communication=serial,
        )
        self.get_aton_values: Command = Command(
            message="?aton",
            estimated_response_time=0.5,
            validators=(
                aton1_validator,
                aton2_validator,
                aton3_validator,
                aton4_validator,
            ),
            serial_communication=serial,
        )

        # ATF Commands
        self.set_atf1: Command = Command(
            message="!atf1=",
            validators=frequency_validator,
            serial_communication=serial,
        )
        self.set_atf2: Command = Command(
            message="!atf2=",
            validators=frequency_validator,
            serial_communication=serial,
        )
        self.set_atf3: Command = Command(
            message="!atf3=",
            validators=frequency_validator,
            serial_communication=serial,
        )
        self.set_atf4: Command = Command(
            message="!atf4=",
            validators=frequency_validator,
            serial_communication=serial,
        )

        # ATON Commands
        self.set_aton1: Command = Command(
            message="!aton1=",
            validators=ms_value_validator,
            serial_communication=serial,
        )
        self.set_aton2: Command = Command(
            message="!aton2=",
            validators=ms_value_validator,
            serial_communication=serial,
        )
        self.set_aton3: Command = Command(
            message="!aton3=",
            validators=ms_value_validator,
            serial_communication=serial,
        )
        self.set_aton4: Command = Command(
            message="!aton4=",
            validators=ms_value_validator,
            serial_communication=serial,
        )

        # ATK Commands
        self.set_atk1: Command = Command(
            message="!atk1=",
            validators=float_value_validator,
            serial_communication=serial,
        )
        self.set_atk2: Command = Command(
            message="!atk2=",
            validators=float_value_validator,
            serial_communication=serial,
        )
        self.set_atk3: Command = Command(
            message="!atk3=",
            validators=float_value_validator,
            serial_communication=serial,
        )
        self.set_atk4: Command = Command(
            message="!atk4=",
            validators=float_value_validator,
            serial_communication=serial,
        )

        # ATT Commands
        self.set_att1: Command = Command(
            message="!att1=",
            validators=float_value_validator,
            serial_communication=serial,
        )
        self.set_att2: Command = Command(
            message="!att2=",
            validators=float_value_validator,
            serial_communication=serial,
        )
        self.set_att3: Command = Command(
            message="!att3=",
            validators=float_value_validator,
            serial_communication=serial,
        )
        self.set_att4: Command = Command(
            message="!att4=",
            validators=float_value_validator,
            serial_communication=serial,
        )
