import pytest
import pytest_asyncio
from sonicpackage.communication.serial_communicator import SerialCommunicator
from tests.sonicpackage.communication.mock_connection_factory import connection
from unittest.mock import Mock

@pytest_asyncio.fixture
async def communicator(connection):
    communicator = SerialCommunicator()
    await communicator.open_communication(connection)
    yield communicator
    if communicator.connection_opened.is_set():
        await communicator.close_communication()

@pytest.mark.asyncio
async def test_communicator_close_communication_closes_streamwriter(communicator, connection):
    await communicator.close_communication()

    connection.writer.close.assert_called_once()
    connection.writer.wait_closed.assert_called_once()

@pytest.mark.asyncio
async def test_communicator_close_communication_raises_event(communicator):
    mock_close_callback = Mock()
    communicator.subscribe(communicator.DISCONNECTED_EVENT, mock_close_callback)
    
    await communicator.close_communication()

    mock_close_callback.assert_called_once()

@pytest.mark.asyncio
async def test_communicator_read_message_allowed_while_send_and_await(communicator, connection):
    pass

@pytest.mark.asyncio
async def test_communicator_send_and_wait_does_not_throw_parsing_error(communicator, connection):
    pass

@pytest.mark.asyncio
async def test_communicator_send_and_wait_connection_error_on_timeout_3_times(communicator, connection):
    pass

