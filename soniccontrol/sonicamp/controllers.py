from typing import Literal
from soniccontrol.sonicamp.sonicagent import SerialAgent
from soniccontrol.sonicamp.command import SerialCommand, Command, SonicAmpCommand

import soniccontrol.sonicamp.constants as const


class Controller:
    def __init__(self, serial_agent: SerialAgent) -> None:
        self._serial_agent: SerialAgent = serial_agent

    def operation(self, command: Command, *args, **kwargs) -> None:
        pass


class FrequencyController(Controller):
    def __init__(self, serial_agent: SerialAgent) -> None:
        super().__init__(serial_agent)

    def operation(self, command: SonicAmpCommand) -> None:
        command.message = f"!f={command.method_args}"
        self._serial_agent.add_job(command, const.Priority.TOP)


class GainController(Controller):
    def __init__(self, serial_agent: SerialAgent) -> None:
        super().__init__(serial_agent)

    def operation(self, command: SonicAmpCommand) -> None:
        command.message = f"!g={command.method_args}"
        self._serial_agent.add_job(command, const.Priority.TOP)


class SignalController(Controller):
    def __init__(self, serial_agent: SerialAgent) -> None:
        super().__init__(serial_agent)

    def operation(self, action: Literal["on", "off"]) -> None:
        if action == "on":
            return self.signal_on()
        elif action == "off":
            return self.signal_off()

    def signal_on(self) -> None:
        self._serial_agent.add_job(SerialCommand(message=f"!ON"), const.Priority.TOP)

    def signal_off(self) -> None:
        self._serial_agent.add_job(SerialCommand(message=f"!OFF"), const.Priority.TOP)


class CatchSignalController(SignalController):
    def __init__(self, serial_agent: SerialAgent) -> None:
        super().__init__(serial_agent)

    def operation(self, action: Literal["on", "off", "auto"]) -> None:
        if action == "auto":
            return self.signal_auto()
        return super().operation(action)

    def signal_auto(self) -> None:
        self._serial_agent.add_job(SerialCommand(message=f"!AUTO"), const.Priority.TOP)


class WipeSignalController(SignalController):
    def __init__(self, serial_agent: SerialAgent) -> None:
        super().__init__(serial_agent)

    def operation(self, action: Literal["on", "off", "wipe"]) -> None:
        if action == "wipe":
            return self.signal_wipe()
        return super().operation(action=action)

    def signal_wipe(self) -> None:
        self._serial_agent.add_job(SerialCommand(message=f"!WIPE"), const.Priority.TOP)


class CatchAmpModeController(Controller):
    def __init__(self, serial_agent: SerialAgent) -> None:
        super().__init__(serial_agent)

    def operation(self, action: Literal["wipe", "catch"]) -> None:
        if action == "catch":
            return self.catch_mode_on()
        elif action == "wipe":
            return self.wipe_mode_on()

    def catch_mode_on(self) -> None:
        self._serial_agent.add_job(SerialCommand(message=f"!SIN"), const.Priority.TOP)

    def wipe_mode_on(self) -> None:
        self._serial_agent.add_job(
            SerialCommand(message=f"!SQUARE"), const.Priority.TOP
        )


class OldCatchAmpController(CatchAmpModeController):
    def __init__(self, serial_agent: SerialAgent) -> None:
        super().__init__(serial_agent)

    def catch_mode_on(self) -> None:
        self._serial_agent.add_job(SerialCommand(message=f"!ON"), const.Priority.TOP)

    def wipe_mode_on(self) -> None:
        return super().wipe_mode_on()
