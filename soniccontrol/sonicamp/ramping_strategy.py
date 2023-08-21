class Ramp:
    def __init__(self) -> None:
        self.sonicamp: SonicAmp = sonicamp
        self.values: Iterable[Any] = []
        self.current_value: Optional[Any] = None
        self.unit: str = unit
        self.action: Callable[[Any], Any] = action
        self.callback: Callable[[Any], Any] = callback

    def __repr__(self) -> str:
        return f"Ramp @ {self.current_value} {self.unit}"

    def execute(self) -> None:
        sonicamp.set_signal_on()

        for value in values:
            result = action(value)
            callback()
