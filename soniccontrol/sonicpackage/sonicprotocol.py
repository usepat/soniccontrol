from enum import Enum
from typing import Callable, Any, Tuple
import abc
from soniccontrol.sonicpackage.package_parser import Package, PackageParser
from soniccontrol.sonicpackage import logger


class ProtocolType(Enum):
    SONIC_PROTOCOL = "Sonic Protocol"

class CommunicationProtocol:
    @property
    def start_symbol(self) -> str:
        return PackageParser.start_symbol

    @property
    def end_symbol(self) -> str:
        return PackageParser.end_symbol

    @property
    def max_bytes(self) -> int:
        return PackageParser.max_bytes

    @abc.abstractmethod
    def parse_response(self, response: str) -> Any: ...

    @abc.abstractmethod
    def parse_request(self, request: str, request_id: int) -> Any: ...

    @abc.abstractmethod
    def prot_type(self) -> ProtocolType: ...

    @property
    @abc.abstractmethod
    def major_version(self) -> int: ...


class LegacySonicProtocol(CommunicationProtocol):
    def __init__(self):
        super().__init__()

    @property
    def start_symbol(self) -> str:
        return ""

    @property
    def end_symbol(self) -> str:
        return "\n"

    @property
    def max_bytes(self) -> int:
        return PackageParser.max_bytes

    def parse_response(self, response: str) -> str:
        return response

    def parse_request(self, request: str, request_id: int) -> Any:
        return request
    
    @abc.abstractmethod
    def prot_type(self) -> ProtocolType:
        return ProtocolType.SONIC_PROTOCOL

    @property
    @abc.abstractmethod
    def major_version(self) -> int:
        return 1


class SonicProtocol(CommunicationProtocol):
    def __init__(self, log_callback: Callable[[str], None]):
        self._log_callback: Callable[[str], None] = log_callback
        super().__init__()

    @property
    def start_symbol(self) -> str:
        return PackageParser.start_symbol

    @property
    def end_symbol(self) -> str:
        return PackageParser.end_symbol

    @property
    def max_bytes(self) -> int:
        return PackageParser.max_bytes

    def parse_response(self, response: str) -> tuple[int, str]:
        package = PackageParser.parse_package(response)
        lines = package.content.splitlines()
        answer = ""
        for line in lines:
            if line.startswith("LOG"):
                self._log_callback(line)
            elif line.isspace() or len(line) == 0:
                continue  # ignore whitespace
            else:
                answer += line

        return package.identifier, answer

    def parse_request(self, request: str, request_id: int) -> str:
        package = Package("0", "0", request_id, request)
        message_str = (
            PackageParser.write_package(package) + "\n"
        )  # \n is needed after the package.
        logger.debug(f"WRITE_PACKAGE({message_str})")

        return message_str
    
    @abc.abstractmethod
    def prot_type(self) -> ProtocolType:
        return ProtocolType.SONIC_PROTOCOL

    @property
    @abc.abstractmethod
    def major_version(self) -> int:
        return 2

