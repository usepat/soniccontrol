import pytest
import asyncio
from asyncio import StreamReader

from shared.system import PLATFORM
from sonicpackage.communication.package_fetcher import PackageFetcher
from sonicpackage.communication.sonicprotocol import SonicProtocol


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


@pytest.mark.asyncio
async def test_get_answer_of_package_order_does_not_matter():
    reader = StreamReaderFake()
    protocol = SonicProtocol()
    pkg_fetcher = PackageFetcher(reader, protocol)

    msg = "Hello Package Fetcher"
    msg_id = 15
    msg_str = protocol.parse_request(msg, msg_id)

    try:
        pkg_fetcher.run()

        await reader.feed_data(protocol.parse_request("asdfd", 10))
        await reader.feed_data(msg_str)
        await reader.feed_data(protocol.parse_request("hsghfare", 23))

        answer = await pkg_fetcher.get_answer_of_package(15)
        await pkg_fetcher.stop()
    except Exception as e:
        pytest.fail(f"Unexpected exception raised: {e}")

    assert (answer == msg)

