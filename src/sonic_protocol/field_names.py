from enum import Enum


class StatusAttr(Enum):
    FREQUENCY = "freq"
    SWF = "swf"
    GAIN = "gain"
    TEMPERATURE = "temp"
    SIGNAL = "signal"
    URMS = "urms"
    IRMS = "irms"
    PHASE = "phase"

    ATF = "atf"
    ATK = "atk"
    ATT = "att"
    ATON = "aton"

    COMM_MODE = "communication_mode"

    PROCEDURE = "procedure"

    TIME_STAMP = "time_stamp"
