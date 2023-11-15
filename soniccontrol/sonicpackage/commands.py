import attrs
from soniccontrol.sonicpackage.command import Command, CommandValidator


class Commands:
    frequency_pattern: str = r".*freq[uency]*\s*=?\s*([\d]+).*"
    gain_pattern: str = r".*gain\s*=?\s*([\d]+).*"
    khz_mhz_pattern: str = r".*(khz|mhz).*"
    signal_on_off_pattern: str = r".*signal.*(on|off).*"
    type_pattern: str = r"sonic(catch|wipe|descale)"
    version_pattern: str = r".*ver.*([\d]+[.][\d]+).*"
    status_pattern: str = (
        r"([\d])(?:[-#])"  # Error
        r"([\d]+)(?:[-#])"  # Frequency
        r"([\d]+)(?:[-#])"  # Gain
        r"([\d]+)(?:[-#])"  # Protocol
        r"([\d])(?:[-#])"  # Wipe Mode / Auto Mode
        r"(?:[']?)([-]?[\d]+[.][\d]+)?(?:[']?)"  # Temperature
    )
    sens_pattern: str = (
        r"([\d]+)(?:[\s]+)"  # Frequency
        r"([-]?[\d]+[.]?[\d]?)(?:[\s]+)"  # urms
        r"([-]?[\d]+[.]?[\d]?)(?:[\s]+)"  # irms
        r"([-]?[\d]+[.]?[\d]?)"  # phase
    )
    error_pattern: str = r".*(error).*"

    frequency_validator: CommandValidator = CommandValidator(
        pattern=frequency_pattern, frequency=int
    )
    gain_validator: CommandValidator = CommandValidator(pattern=gain_pattern, gain=int)  # type: ignore
    switching_frequency_validator: CommandValidator = CommandValidator(
        pattern=frequency_pattern, switching_frequency=int
    )
    relay_mode_validator: CommandValidator = CommandValidator(
        pattern=khz_mhz_pattern, relay_mode=str
    )
    signal_on_validator: CommandValidator = CommandValidator(
        pattern=signal_on_off_pattern,
        signal=lambda b: bool(b.lower() == "on"),
    )
    type_validator: CommandValidator = CommandValidator(
        pattern=type_pattern, device_type=str
    )
    version_validator: CommandValidator = CommandValidator(
        pattern=version_pattern, version=float
    )
    status_validator: CommandValidator = CommandValidator(
        pattern=status_pattern,
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
    )

    sens_normal_validator: CommandValidator = CommandValidator(
        pattern=sens_pattern,
        frequency=int,
        urms=float,
        irms=float,
        phase=float,
    )
    sens_error_validator: CommandValidator = CommandValidator(
        pattern=error_pattern,
        signal=lambda error: False,
        frequency=lambda error: 0,
        urms=lambda error: 0,
        irms=lambda error: 0,
        phase=lambda error: 0,
    )
    sens_factorised_validator: CommandValidator = CommandValidator(
        pattern=sens_pattern,
        frequency=int,
        urms=attrs.converters.pipe(float, lambda urms: urms / 1000),
        irms=attrs.converters.pipe(float, lambda irms: irms / 1000),
        phase=attrs.converters.pipe(float, lambda phase: phase / 1_000_000),
    )
    sens_fullscale_validator: CommandValidator = CommandValidator(
        pattern=sens_pattern,
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
    )
    auto_mode_validator: CommandValidator = CommandValidator(
        pattern=r".*(auto).*", protocol=str
    )
    communication_mode_validator: CommandValidator = CommandValidator(
        pattern=r".*mode.*(serial|analog|manual).*", communication_mode=str
    )

    set_frequency: Command = Command(message="!f=")

    set_gain: Command = Command(message="!g=")

    set_switching_frequency: Command = Command(message="!swf=")

    get_overview: Command = Command(
        message="?",
        estimated_response_time=0.5,
        expects_long_answer=True,
        validators=(  # type: ignore
            frequency_validator,
            gain_validator,
            relay_mode_validator,
            signal_on_validator,
            communication_mode_validator,
            auto_mode_validator,
            type_validator,
        ),
    )

    get_type: Command = Command(
        message="?type",
        estimated_response_time=0.5,
        validators=type_validator,  # type: ignore
    )

    get_info: Command = Command(
        message="?info",
        estimated_response_time=0.5,
        expects_long_answer=True,
        validators=version_validator,  # type: ignore
    )

    get_status: Command = Command(
        message="-",
        estimated_response_time=0.35,
        validators=status_validator,  # type: ignore
    )

    get_sens: Command = Command(
        message="?sens",
        estimated_response_time=0.35,
        validators=sens_normal_validator,  # type: ignore
    )

    get_sens_factorised: Command = Command(
        message="?sens",
        estimated_response_time=0.35,
        validators=sens_factorised_validator,  # type: ignore
    )

    get_sens_fullscale_values: Command = Command(
        message="?sens",
        estimated_response_time=0.35,
        validators=sens_fullscale_validator,  # type: ignore
    )

    signal_on: Command = Command(
        message="!ON",
    )

    signal_off: Command = Command(
        message="!OFF",
        estimated_response_time=0.4,
        validators=signal_on_validator,  # type: ignore
    )

    signal_auto: Command = Command(
        message="!AUTO",
        estimated_response_time=0.5,
        validators=auto_mode_validator,  # type: ignore
    )

    set_serial_mode: Command = Command(
        message="!SERIAL",
        validators=communication_mode_validator,  # type: ignore
    )

    set_analog_mode: Command = Command(
        message="!ANALOG",
        validators=communication_mode_validator,  # type: ignore
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
from soniccontrol.sonicpackage.serial_communicator import SerialCommunicator
from icecream import ic
import serial.tools.list_ports as list_ports


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
