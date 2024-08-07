import sys
from enum import Enum
from typing import Final


class System(Enum):
    WINDOWS = "win32", "windows-1252"
    LINUX = "linux", "utf-8"
    MAC = "darwin", "utf-8"
    UNKNOWN = "unknown", "utf-8"

    def __init__(self, platform: str, encoding: str) -> None:
        super().__init__()
        self.platform_name = platform
        self.encoding = encoding


def decode_platform() -> System:
    platform: System = System.UNKNOWN
    if sys.platform == System.WINDOWS.platform_name:
        platform = System.WINDOWS
    elif sys.platform == System.LINUX.platform_name:
        platform = System.LINUX
    elif sys.platform == System.MAC.platform_name:
        platform = System.MAC
    return platform


PLATFORM: Final[System] = decode_platform()
