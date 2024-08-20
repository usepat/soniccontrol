import asyncio
import logging
import pytest
import pytest_asyncio
from shared.system import PLATFORM
from sonicpackage.command import Command
from sonicpackage.communication.package_parser import Package, PackageParser
from sonicpackage.communication.serial_communicator import SerialCommunicator
from tests.sonicpackage.communication.mock_connection_factory import connection # this import is used by the tests. Do not delete it
from unittest.mock import Mock
from callee import Contains


@pytest_asyncio.fixture()
async def communicator(connection):
    communicator = SerialCommunicator()
    await communicator.open_communication(connection, loop=asyncio.get_running_loop())
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
async def test_communicator_send_and_wait_returns_answer(communicator, connection):
    msg = "hello communicator!"
    msg_id = 2
    msg_str = PackageParser.write_package(Package("0", "0", msg_id, msg))
    connection.reader.feed_data(data=msg_str.encode(PLATFORM.encoding))
    command = Command(message="?greet")

    await communicator.send_and_wait_for_answer(command)

    assert connection.writer.write.assert_called_once_with(Contains("?greet"))
    assert command.answer == msg

@pytest.mark.asyncio
async def test_communicator_send_and_wait_does_not_throw_parsing_error(communicator, connection):
    pass

@pytest.mark.asyncio
async def test_communicator_send_and_wait_connection_error_on_timeout(communicator, connection):
    logger = logging.getLogger()
    logger.warn = Mock()
    communicator._logger = logger
    with pytest.raises(ConnectionError):
        await communicator.send_and_wait_for_answer(Command(message="-"))

@pytest.mark.asyncio
async def test_communicator_send_and_wait_connection_error_if_disconnect(communicator, connection):
    await communicator.close_communication()

    with pytest.raises(ConnectionError):
        await communicator.send_and_wait_for_answer(Command(message="-"))

@pytest.mark.asyncio
async def test_communicator_read_message_allowed_while_send_and_await(communicator, connection):
    pass
