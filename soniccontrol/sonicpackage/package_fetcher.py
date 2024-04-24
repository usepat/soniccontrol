import asyncio
from typing import Dict, Callable
from asyncio import StreamReader

import soniccontrol.utils.constants as const
from soniccontrol.sonicpackage.package_parser import Package, PackageParser


class PackageFetcher():
    def __init__(self, reader: StreamReader, log_callback: Callable[[str], None]):
        self._reader = reader
        self._answers: Dict[int, str] = {}
        self._answer_received = asyncio.Event()
        self._log_callback = log_callback
    

    async def get_answer_of_package(self, package_id: int) -> str:
        while True:
            await self._answer_received.wait()
            self._answer_received.clear()
            if package_id in self._answers:
                answer = self._answers[package_id]
                del self._answers[package_id]
                return answer


    def run(self) -> None:
        asyncio.create_task(self._worker())


    async def _worker(self) -> None:
        while True:
            package = await self._read_package()

            if package.identifier == 0:
                raise NotImplementedError() # 0 id means that it is a update message, maybe also a log

            lines = package.content.splitlines()
            for line in lines:
                if line.startswith("LOG"):
                    self._log_callback(line)
                elif line.isspace() or len(line) == 0:
                    continue # ignore whitespace
                else:
                    self._answers[package.identifier] = line
                    self._answer_received.set()


    async def _read_package(self) -> Package:
        if self._reader is None:
            raise RuntimeError("reader was not initialized")
        
        # TODO: check for errors
        message: str = PackageParser.start_symbol
        await self._reader.readuntil(PackageParser.start_symbol.encode(const.misc.ENCODING))
        data = await self._reader.readuntil(PackageParser.end_symbol.encode(const.misc.ENCODING))
        message += data.decode(const.misc.ENCODING)

        return PackageParser.parse_package(message)
