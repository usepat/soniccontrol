import asyncio
import re
import json
import logging
from dataclasses import dataclass
from typing import List, Literal, Optional, Union, ClassVar

from soniccontrol.sonicpackage.builder import AmpBuilder
from soniccontrol.sonicpackage.serial_communicator import SerialCommunicator


@dataclass
class LogCommandCall:
    argument: str
    message: str

    LOG_STR: ClassVar[str] = "COMMAND_CALL"

@dataclass
class LogDeviceState:
    # only add those attributes we are interested in and that we can compare easely. We know they will not change
    error: int =  0
    frequency: int = 0
    gain: int = 0
    protocol: int = 0
    signal: bool = False
    atf1: int = 0
    atk1: float = 0.0
    atf2: int = 0
    atk2: float = 0.0
    atf3: int = 0
    atk3: float = 0.0
    att1: float = 0.0
    communication_mode: Optional[Literal["Serial", "Manual", "Analog"]] = "Manual"
    _version: int = 0

    LOG_STR: ClassVar[str] = "DEVICE_STATE"


ParrotLog = Union[LogCommandCall, LogDeviceState]


class LogParser:
    @staticmethod
    def parse_logs(lines: List[str]) -> List[ParrotLog]:
        result = []
        for line in lines:
            log = LogParser.parse_log(line)
            if log:
                result.append(log)
        return result
    
    @staticmethod
    def parse_log(line: str) -> Optional[ParrotLog]:
        if LogCommandCall.LOG_STR in line:
            return LogParser._parse_command_call(line)
        elif LogDeviceState.LOG_STR in line:
            return LogParser._parse_device_state(line)
        else:
            return None

    @staticmethod
    def _parse_command_call(line: str) -> LogCommandCall:
        regex = fr".*{LogCommandCall.LOG_STR}\((.+)\).*"
        match = re.match(regex, line)
        data = json.loads(match.group(1))
        return LogCommandCall(**data)

    @staticmethod
    def _parse_device_state(line: str) -> LogDeviceState:
        regex = fr".*{LogDeviceState.LOG_STR}\((.+)\).*"
        match = re.match(regex, line)
        data = json.loads(match.group(1))
        data = { k: v for (k, v) in data.items() if k in LogDeviceState.__dict__ } # filter out those attributes we are interested in
        return LogDeviceState(**data)



class Parrot:
    class ParrotLogHandler(logging.Handler):
        def __init__(self, parrot):
            super(Parrot.ParrotLogHandler, self).__init__()
            self.parrot = parrot
            self.setLevel(logging.DEBUG)

        def emit(self, record: logging.LogRecord):
            try:
                msg = self.format(record)
                log = LogParser.parse_log(msg)
                if log:
                    self.parrot.parrot_logs.append(log)
            except:
                self.handleError(record)


    def __init__(self, serial_communicator: SerialCommunicator, log_lines: List[str]):
        self.serial_communicator = serial_communicator
        self.sonic_amp = None
        self.logs = LogParser.parse_logs(log_lines)
        self.log_iter = iter(self.logs)
        self.log_elem = next(self.log_iter, None)
        self.parrot_logs: List[ParrotLog] = []

    def register_parrot_log_handler(self, logger: logging.Logger):
        parrot_log_handler = Parrot.ParrotLogHandler(self)
        logger.addHandler(parrot_log_handler)

    async def setup_amp(self):
        builder = AmpBuilder()
        self.sonic_amp = await builder.build_amp(self.serial_communicator)

        self._validate_imitation()
        
    async def run_imitation(self):
        if not self.sonic_amp:
            raise RuntimeError("Sonic amp was not initialized. Call setup_amp first") 
        
        while self.log_elem:
            if type(self.log_elem) is not LogCommandCall:
                raise TypeError("Expected a command call")

            argument = self.log_elem.argument
            message = self.log_elem.message

            if message == "-":
                self._skip_logs_until_next_command_call()
                continue

            await self.sonic_amp.execute_command(message, argument)
            self._validate_imitation()

            
    def _skip_logs_until_next_command_call(self):
        while self.log_elem is not LogCommandCall and self.log_elem is not None:
            self.log_elem = next(self.log_iter, None)

    def _validate_imitation(self): # Maybe it would be better to call this after the run of an imitation
        for parrot_log in self.parrot_logs:
            if type(self.log_elem) is type(parrot_log) and self.log_elem == parrot_log:
                self.log_elem = next(self.log_iter, None)
            else:
                raise RuntimeError(f"Logs are not identical: log {self.log_elem}, parrot_log: {parrot_log}")
        self.parrot_logs.clear()
