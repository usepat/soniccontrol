
import asyncio
import time
from typing import Literal


class Holder:
    @staticmethod
    async def execute(
        duration: float = 0.,
        unit: Literal["ms", "s"] = "s"
    ) -> None:
        duration = duration if unit == "s" else duration / 1000
        end_time: float = time.time() + duration
        while time.time() < end_time:
            await asyncio.sleep(0.01)