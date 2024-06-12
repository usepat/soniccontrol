from typing import Callable
from soniccontrol.sonicpackage.package_parser import Package, PackageParser
from soniccontrol.sonicpackage import logger


class SonicProtocol:
    def __init__(self, log_callback: Callable[[str], None]):
        self._log_callback: Callable[[str], None] = log_callback

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
