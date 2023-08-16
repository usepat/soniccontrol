from typing import Literal
from soniccontrol.sonicamp.sonicagent import SerialAgent
from soniccontrol.sonicamp.serial_interface import SerialCommand

import soniccontrol.sonicamp.constants as const


class Controller:
    def __init__(self, serial_agent: SerialAgent) -> None:
        self._serial_agent: SerialAgent = serial_agent

    def operation(self) -> None:
        pass


class FrequencyController(Controller):
    def __init__(self) -> None:
        super().__init__()

    def operation(self, frequency: int) -> None:
        self._serial_agent.add_job(
            SerialCommand(message=f"!f={frequency}"), const.Priority.TOP
        )


class GainController(Controller):
    def __init__(self, serial_agent: SerialAgent) -> None:
        super().__init__(serial_agent)

    def operation(self, gain: int) -> None:
        self._serial_agent.add_job(
            SerialCommand(message=f"!g={gain}"), const.Priority.TOP
        )


class SignalController(Controller):
    def __init__(self, serial_agent: SerialAgent) -> None:
        super().__init__(serial_agent)

    def operation(self, action: Literal["on", "off"]) -> None:
        if action == "on":
            return self.signal_on()
        elif action == "off":
            return self.signal_off()

    def signal_on(self) -> None:
        pass

    def signal_off(self) -> None:
        pass


class CatchSignalController(SignalController):
    def __init__(self, serial_agent: SerialAgent) -> None:
        super().__init__(serial_agent)

    def operation(self, action: Literal["on", "off", "auto"]) -> None:
        if action == "auto":
            return self.signal_auto()
        return super().operation(action)

    def signal_auto(self) -> None:
        pass


class WipeSignalController(SignalController):
    def __init__(self, serial_agent: SerialAgent) -> None:
        super().__init__(serial_agent)

    def operation(self, action: Literal["on", "off", "wipe"]) -> None:
        if action == "wipe":
            return self.signal_wipe()
        return super().operation(action=action)

    def signal_wipe(self) -> None:
        pass


class CatchAmpModeController(Controller):
    def __init__(self, serial_agent: SerialAgent) -> None:
        super().__init__(serial_agent)

    def operation(self, action: Literal["wipe", "catch"]) -> None:
        if action == "catch":
            return self.catch_mode_on()
        elif action == "wipe":
            return self.wipe_mode_on()

    def catch_mode_on(self) -> None:
        pass

    def wipe_mode_on(self) -> None:
        pass


class OldCatchAmpController(CatchAmpModeController):
    def __init__(self, serial_agent: SerialAgent) -> None:
        super().__init__(serial_agent)

    def catch_mode_on(self) -> None:
        return super().catch_mode_on()

    def wipe_mode_on(self) -> None:
        return super().wipe_mode_on()
