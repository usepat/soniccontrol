import asyncio
from typing import Tuple
from unittest.mock import Mock
import pytest
from sonicpackage.communication.connection_factory import ConnectionFactory


class MockConnectionFactory(ConnectionFactory):
    def __init__(self):
        self.reader = Mock(wraps=asyncio.StreamReader)()
        self.writer = Mock(spec=asyncio.StreamWriter)

    async def open_connection(self) -> Tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        return self.reader, self.writer

@pytest.fixture()
def connection(event_loop):
    connection_factory = MockConnectionFactory()
    connection_factory.writer.close.return_value = None
    connection_factory.writer.wait_closed.return_value = asyncio.Future()
    return connection_factory