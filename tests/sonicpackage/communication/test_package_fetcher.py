import pytest

from sonicpackage.communication.package_fetcher import PackageFetcher
from sonicpackage.communication.sonicprotocol import SonicProtocol
from tests.sonicpackage.communication.stream_reader_fake import StreamReaderFake


@pytest.mark.asyncio
async def test_get_answer_of_package_ensures_that_order_does_not_matter():
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

