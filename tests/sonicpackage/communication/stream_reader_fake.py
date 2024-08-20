from asyncio import StreamReader
import asyncio

from shared.system import PLATFORM


class StreamReaderFake(StreamReader):
    def __init__(self):
        self._stream_content = b""
        self._lock = asyncio.Lock()
        super().__init__()

    async def readuntil(self, separator = b"\n") -> bytes:
        while True:
            print("I am awake")
            async with self._lock:
                index = self._stream_content.find(separator)
            if index == -1:
                print("I am sleeping")
                await asyncio.sleep(0.5)
            else:
                break
        async with self._lock:
            ret = self._stream_content[:index+1]
            self._stream_content = self._stream_content[index+1:]
            print (b"read data: " + ret)
            print (b"rest of data: " + self._stream_content)
            return ret
    
    async def feed_data(self, data: bytes | str) -> None:
        if isinstance(data, str):
            data = data.encode(PLATFORM.encoding)
        print (b"feed data: " + data)
        async with self._lock:
            self._stream_content += data