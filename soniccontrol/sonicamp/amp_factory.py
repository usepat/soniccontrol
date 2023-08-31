from soniccontrol.sonicamp.connection import SerialCommunicator
from soniccontrol.sonicamp.interfaces import SonicAmp


class SonicAmpFactory:
    @staticmethod
    def build_amp(serial: SerialCommunicator) -> SonicAmp:
        return SonicAmp(serial)
