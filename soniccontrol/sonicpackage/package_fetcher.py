import asyncio
import logging
from typing import Dict, Callable
from asyncio import StreamReader
import sys
from icecream import ic

import soniccontrol.utils.constants as const
from soniccontrol.sonicpackage.package_parser import Package, PackageParser

logger = logging.getLogger()

class PackageFetcher():
    def __init__(self, reader: StreamReader, log_callback: Callable[[str], None]):
        self._reader = reader
        self._answers: Dict[int, str] = {}
        self._answer_received = asyncio.Event()
        self._log_callback = log_callback
        self._task = None
    

    async def get_answer_of_package(self, package_id: int) -> str:
        while True:
            await self._answer_received.wait()
            self._answer_received.clear()
            if package_id in self._answers:
                answer = self._answers[package_id]
                del self._answers[package_id]
                return answer


    def run(self) -> None:
        self._task = asyncio.create_task(self._worker())

    async def stop(self) -> None:
        if self._task  is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None


    async def _worker(self) -> None:
        while True:
            try:
                package = await self._read_package()
            except asyncio.CancelledError:
                ic(f"Task was cancelled {sys.exc_info()}")
                return
            except:
                ic(f"Exception while reading/parsing package {sys.exc_info()}")
                raise

            if package.identifier == 0:
                raise NotImplementedError() # 0 id means that it is a update message, maybe also a log

            lines = package.content.splitlines()
            answer = ""
            for line in lines:
                if line.startswith("LOG"):
                    self._log_callback(line)
                elif line.isspace() or len(line) == 0:
                    continue # ignore whitespace
                else:
                    answer += line
            
            if len(answer) > 0:
                self._answers[package.identifier] = answer
                self._answer_received.set()


    async def _read_package(self) -> Package:
        if self._reader is None:
            raise RuntimeError("reader was not initialized")
        
        message: str = PackageParser.start_symbol
        garbage_data = await self._reader.readuntil(PackageParser.start_symbol.encode(const.misc.ENCODING))
        garbage = garbage_data.decode(const.misc.ENCODING)
        if garbage.strip() != PackageParser.start_symbol:
            raise RuntimeError(f"Before the package start, there were unexpected characters: {garbage}")
        
        data = await self._reader.readuntil(PackageParser.end_symbol.encode(const.misc.ENCODING))
        message += data.decode(const.misc.ENCODING)

        logger.debug(f"READ_PACKAGE({message})")

        return PackageParser.parse_package(message)
