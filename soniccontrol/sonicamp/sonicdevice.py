class SonicAmp:
    def __init__(self, serial: Connection) -> None:
        self._serial: Connection = serial

    @property
    def serial(self) -> Connection:
        return self._serial

    @staticmethod
    def build_amp(data: AmpData) -> SonicAmp:
        return AmpFactory.build_amp(data)
