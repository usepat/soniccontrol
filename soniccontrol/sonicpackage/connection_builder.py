class ConnectionBuilder:
    def __init__(self) -> None:
        pass

    def build(self):
        reader, writer = await open_serial_connection(url=url, baudrate=baudrate)
        serial = SerialCommunicator()
        serial.connect(reader, writer, protocol=SonicProtocol())

        get_info = Commands.get_info
        get_info.execute()
        if get_info.answer.valid:
            return serial
        else:
            serial.change_protocol(LegacyProtocol())

        get_info = Commands.get_info
        get_info.execute()
        if get_info.answer.valid:
            return serial
        else:
            raise ConnectionError
