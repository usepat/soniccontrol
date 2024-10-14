

import abc
from sonic_protocol.defs import DeviceType, Version, Protocol


class ManualCompiler(abc.ABC):
    @abc.abstractmethod
    def compile_manual(self, protocol: Protocol) -> str: ...

    @abc.abstractmethod
    def compile_manual_for_specific_device(self, protocol: Protocol, device: DeviceType, protocol_version: Version) -> str: ...


class MarkdownManualCompiler(ManualCompiler):
    pass


