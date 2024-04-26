import attrs
from soniccontrol.sonicpackage.command import Command, CommandValidator


class Commands:
    set_frequency: Command = Command(
        message="!f=",
        validators=CommandValidator(
            pattern=r".*freq[uency]*\s*=?\s*([\d]+).*", frequency=int
        ),
    )

    set_gain: Command = Command(
        message="!g=",
        validators=CommandValidator(pattern=r".*gain\s*=?\s*([\d]+).*", gain=int),
    )

    set_switching_frequency: Command = Command(
        message="!swf=",
        validators=CommandValidator(
            pattern=r".*freq[uency]*\s*=?\s*([\d]+).*", switching_frequency=int
        ),
    )

    get_overview: Command = Command(
        message="?",
        estimated_response_time=0.5,
        expects_long_answer=True,
        validators=(
            CommandValidator(pattern=r".*(khz|mhz).*", relay_mode=str),
            CommandValidator(pattern=r".*freq[uency]*\s*=?\s*([\d]+).*", frequency=int),
            CommandValidator(pattern=r".*gain\s*=?\s*([\d]+).*", gain=int),
            CommandValidator(
                pattern=r".*signal.*(on|off).*",
                signal=lambda b: bool(b.lower() == "on"),
            ),
        ),
    )

    get_type: Command = Command(
        message="?type",
        estimated_response_time=0.5,
        validators=CommandValidator(
            pattern=r"sonic(catch|wipe|descale)", device_type=str
        ),
    )

    get_info: Command = Command(
        message="?info",
        estimated_response_time=0.5,
        expects_long_answer=True,
        validators=(
            CommandValidator(pattern=r".*ver.*([\d]+[.][\d]+).*", version=float),
            CommandValidator(pattern=r"sonic(catch|wipe|descale)", type_=str),
        ),
    )

    get_command_list: Command = Command(
        message="?list_commands",
        estimated_response_time=0.5,
        expects_long_answer=True,
        validators=CommandValidator(pattern=r"(.+)(#(.+))+")
    )

    get_status: Command = Command(
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
    )

    get_sens: Command = Command(
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
    )

    get_sens_factorised: Command = Command(
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
    )

    get_sens_fullscale_values: Command = Command(
        message="?sens",
        estimated_response_time=0.35,
        validators=(
            CommandValidator(
                pattern=r"([\d]+)(?:[\s]+)([-]?[\d]+[.]?[\d]?)(?:[\s]+)([-]?[\d]+[.]?[\d]?)(?:[\s]+)([-]?[\d]+[.]?[\d]?)",
                frequency=int,
                urms=attrs.converters.pipe(
                    float,
                    lambda urms: urms if urms > 282_300 else 282_300,
                    lambda urms: (urms * 0.000_400_571 - 1_130.669_402) * 1000 + 0.5,
                ),
                irms=attrs.converters.pipe(
                    float,
                    lambda irms: irms if irms > 3_038_000 else 303_800,
                    lambda irms: (irms * 0.000_015_601 - 47.380671) * 1000 + 0.5,
                ),
                phase=attrs.converters.pipe(float, lambda phase: phase * 0.125 * 100),
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
    )

    signal_on: Command = Command(
        message="!ON",
        validators=CommandValidator(
            pattern=r"signal.*(on)", signal=lambda b: b.lower() == "on"
        ),
    )

    signal_off: Command = Command(
        message="!OFF",
        estimated_response_time=0.4,
        validators=CommandValidator(
            pattern=r"signal.*(off)", signal=lambda b: not b.lower() == "off"
        ),
    )

    signal_auto: Command = Command(
        message="!AUTO",
        estimated_response_time=0.5,
        validators=CommandValidator(pattern=r".*(auto).*", protocol=str),
    )

    set_serial_mode: Command = Command(
        message="!SERIAL",
        validators=CommandValidator(
            pattern=r".*mode.*(serial).*", communication_mode=str
        ),
    )

    set_analog_mode: Command = Command(
        message="!ANALOG",
        validators=CommandValidator(
            pattern=r".*mode.*(analog).*", communication_mode=str
        ),
    )

    set_khz_mode: Command = Command(
        message="!KHZ",
        validators=CommandValidator(pattern=r".*(khz).*", relay_mode=str),
    )

    set_mhz_mode: Command = Command(
        message="!MHZ",
        validators=CommandValidator(pattern=r".*(mhz).*", relay_mode=str),
    )

    set_atf1: Command = Command(
        message="!atf1=",
        validators=CommandValidator(
            pattern=r".*freq[quency]*.*1.*=.*([\d]+)", atf1=int
        ),
    )

    get_atf1: Command = Command(
        message="?atf1",
        expects_long_answer=True,
        validators=CommandValidator(
            pattern=r"([\d]+)\n([-]?[\d]+[\.]?[\d]*)", atf1=int, atk1=float
        ),
    )

    set_atk1: Command = Command(
        message="!atk1=",
        validators=CommandValidator(pattern=r"([-]?[\d]*[\.]?[\d]*)", atk1=float),
    )

    set_atf2: Command = Command(
        message="!atf2=",
        validators=CommandValidator(
            pattern=r".*freq[quency]*.*2.*=.*([\d]+)", atf2=int
        ),
    )

    get_atf2: Command = Command(
        message="?atf2",
        expects_long_answer=True,
        validators=CommandValidator(
            pattern=r"([\d]+)\n([-]?[\d]+[\.]?[\d]*)", atf2=int, atk2=float
        ),
    )

    set_atk2: Command = Command(
        message="!atk2=",
        validators=CommandValidator(pattern=r"([-]?[\d]*[\.]?[\d]*)", atk2=float),
    )

    set_atf3: Command = Command(
        message="!atf3=",
        validators=CommandValidator(
            pattern=r".*freq[quency]*.*3.*=.*([\d]+)", atf3=int
        ),
    )

    get_atf3: Command = Command(
        message="?atf3",
        expects_long_answer=True,
        validators=CommandValidator(
            pattern=r"([\d]+)\n([-]?[\d]+[\.]?[\d]*)", atf3=int, atk3=float
        ),
    )

    set_atk3: Command = Command(
        message="!atk3=",
        validators=CommandValidator(pattern=r"([-]?[\d]*[\.]?[\d]*)", atk3=float),
    )

    set_att1: Command = Command(
        message="!att1=",
        validators=CommandValidator(pattern=r"([-]?[\d]*[\.]?[\d]*)", att1=float),
    )

    get_att1: Command = Command(
        message="?att1",
        validators=CommandValidator(pattern=r"([-]?[\d]*[\.]?[\d]*)", att1=float),
    )


import asyncio

import serial.tools.list_ports as list_ports
from icecream import ic
from soniccontrol.sonicpackage.serial_communicator import SerialCommunicator


async def main():
    ic([port.device for port in list_ports.comports()])
    ser = SerialCommunicator("/dev/cu.usbserial-AB0M45SW")
    await ser.connect()
    await ser.connection_opened.wait()
    Command.set_serial_communication(ser)

    await Commands.get_status.execute()
    await Commands.signal_on.execute()
    await Commands.get_sens.execute()
    await Commands.get_att1.execute()
    await Commands.get_atf1.execute()
    await Commands.get_atf2.execute()
    await Commands.get_atf3.execute()
    await Commands.get_overview.execute()
    await Commands.get_type.execute()
    await Commands.get_info.execute()
    await Commands.set_mhz_mode.execute()
    await Commands.get_status.execute()
    await Commands.signal_off.execute()
    await Commands.get_status.execute()


if __name__ == "__main__":
    asyncio.run(main())
