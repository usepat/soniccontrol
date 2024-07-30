import asyncio
import logging
from typing import Dict
from asyncio import StreamReader
import sys
from icecream import ic

from soniccontrol.sonicpackage.sonicprotocol import SonicProtocol
from soniccontrol.utils.system import PLATFORM

logger = logging.getLogger()


class PackageFetcher:
    def __init__(self, reader: StreamReader, protocol: SonicProtocol) -> None:
        self._reader = reader
        self._answers: Dict[int, str] = {}
        self._answer_received = asyncio.Event()
        self._task = None
        self._protocol: SonicProtocol = protocol

    async def get_answer_of_package(self, package_id: int) -> str:
        while True:
            await self._answer_received.wait()
            self._answer_received.clear()
            if package_id in self._answers:
                answer: str = self._answers.pop(package_id)
                return answer

    def run(self) -> None:
        self._task = asyncio.create_task(self._worker())

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def _worker(self) -> None:
        while True:
            try:
                response = await self._read_response()
                package_id, answer = self._protocol.parse_response(response)
            except asyncio.CancelledError:
                ic(f"Task was cancelled {sys.exc_info()}")
                return
            except Exception as e:
                ic(f"Exception while reading/parsing package {sys.exc_info()}")
                raise

            if len(answer) > 0:
                self._answers[package_id] = answer
                self._answer_received.set()

    async def _read_response(self) -> str:
        if self._reader is None:
            raise RuntimeError("reader was not initialized")

        message: str = self._protocol.start_symbol
        garbage_data = await self._reader.readuntil(
            self._protocol.start_symbol.encode(PLATFORM.encoding)
        )
        garbage = garbage_data.decode(PLATFORM.encoding)
        if garbage.strip() != self._protocol.start_symbol:
            raise RuntimeError(
                f"Before the package start, there were unexpected characters: {garbage}"
            )

        data = await self._reader.readuntil(
            self._protocol.end_symbol.encode(PLATFORM.encoding)
        )
        message += data.decode(PLATFORM.encoding)

        return message
