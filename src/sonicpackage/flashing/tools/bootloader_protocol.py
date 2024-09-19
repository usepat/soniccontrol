from asyncio import StreamReader, StreamWriter
import asyncio
import logging
import time
from typing import ClassVar, Optional, Tuple
import serial
import binascii
from sonicpackage.flashing.tools.utils import hex_bytes_to_int, bytes_to_little_end_uint32, little_end_uint32_to_bytes, custom_crc32
from dataclasses import dataclass, field


def read_from_serial(conn, total_timeout=0.001):
    end_time = time.time() + total_timeout
    response = b''

    while time.time() < end_time:
        if conn.inWaiting() > 0:
            data_byte = conn.read(conn.inWaiting())
            response += data_byte
        else:
            time.sleep(0.0005)  # Briefly sleep to wait for more data

    return response

@dataclass
class PicoInfo:
    flash_addr: int
    flash_size: int
    erase_size: int
    write_size: int
    max_data_len: int


@dataclass
class Protocol_RP2040:
    MAX_SYNC_ATTEMPTS: ClassVar[int] = 3  # Class-level constant
    has_sync: bool = False
    wait_time_before_read: float = 0.01  # seconds
    
    Opcodes: ClassVar[dict] = {
        'Sync': b'SYNC',
        'Read': b'READ',
        'Csum': b'CSUM',
        'CRC': b'CRCC',
        'Erase': b'ERAS',
        'Write': b'WRIT',
        'Seal': b'SEAL',
        'Go': b'GOGO',
        'Info': b'INFO',
        'Boot': b'BOOT',
        'ResponseSync': b'PICO',
        'ResponseSyncWota': b'WOTA',
        'ResponseOK': b'OKOK',
        'ResponseErr': b'ERR!',
    }

    _writer: StreamWriter = field(init=False)  # Instance-level fields, initialized later
    _reader: StreamReader = field(init=False)

    def __init__(self, logger: logging.Logger, writer: StreamWriter, reader: StreamReader):
        super().__init__()
        self._logger = logging.getLogger(logger.name + "." + Protocol_RP2040.__name__)
        self._writer = writer
        self._reader = reader

    async def write(self, data: bytes) -> None:
        self._writer.write(data)
        await self._writer.drain()

    async def read(self, response_len, wait_before_read = wait_time_before_read) -> Tuple[bytes, bytes]:
        await asyncio.sleep(wait_before_read)
        response = b""
        try:
            response = await asyncio.wait_for(self._reader.read(response_len), timeout=1.0)
        except asyncio.TimeoutError:
            pass  # Timeout means no more data, or read operation took too long
        except Exception as e:
            self._logger.info(f"{e}")
            pass
        
        err_byte = response.removeprefix(self.Opcodes["ResponseErr"][:])
        data_bytes = bytes()
        if len(err_byte) == response_len:
            data_bytes = response.removeprefix((self.Opcodes["ResponseOK"][:]))
        else:
            self._logger.info("Error encountered when reading response")
            return b"", b""
            # Error encoutered in RPi Pico! Please POR your Pico and try again.
            pass
        return response, data_bytes

        

    # def read_bootloader_resp(self, conn: serial.Serial, response_len: int, exit_before_flash=True) -> (bytes, bytes):
    #     # Do a small sleep because we need to wait for Pico to be able to respond.
    #     time.sleep(self.wait_time_before_read)
    #     #debug("Start blocking code reponse length is hit. Resp_len: " + str(response_len))
    #     all_bytes = conn.read(response_len)
    #     print(all_bytes)
    #     err_byte = all_bytes.removeprefix(self.Opcodes["ResponseErr"][:])
    #     data_bytes = bytes()
    #     if len(err_byte) == response_len:
    #         data_bytes = all_bytes.removeprefix((self.Opcodes["ResponseOK"][:]))
    #         #debug("No error encoutered")
    #     else:
    #         puts("Error encoutered in RPi Pico! Please POR your Pico and try again.")
    #         exit_prog(exit_before_flash)

    #     debug("Complete Buff: " + str(all_bytes))
    #     debug("Data buff: " + str(data_bytes))
    #     debug("Len Data buff: " + str(len(data_bytes)))
    #     return all_bytes, data_bytes

    async def sync_cmd(self) -> bool:
        for i in range(1, self.MAX_SYNC_ATTEMPTS + 1):
            # print(i)
            response = bytes()
            response, _ = await self.read(20)
            # debug(response)
            try:
                #debug("Serial conn port used: " + str(conn.port))
                # conn.flushInput()
                # conn.flushOutput()
                #debug("Starting sync command by sending: " + str(self.Opcodes["Sync"][:]))
                self._logger.info(f"Send sync command: {self.Opcodes['Sync'][:]}")
                await self.write(self.Opcodes["Sync"][:])

                #debug("Have send Sync command, start reading response")
                response, _ = await self.read(4)
                self._logger.info(f"Reponse: {response}")
                #debug("Whole response has arrived: " + str(response))
                #self.log_device_output(response)
                #file.write_new_line(str(response))
                if response == self.Opcodes["ResponseSync"][:]:
                    #puts("Found a Pico device who responded to sync.")
                    self.has_sync = True
                    return self.has_sync
                else:
                    self._logger.info("Sync failed")
                    
                   # puts("No Pico bootloader found that will respond to the sync command. Is your device connected "
                         #"and in bootloader?")
                    #exit_prog(True)
                # debug("Response: " + str(response))
            except serial.SerialTimeoutException:
                pass
                #puts("Serial timeout expired.")
                #exit_prog(True)
        return False

    async def info_cmd(self) -> Optional[PicoInfo]:
        expected_len = len(self.Opcodes['ResponseOK']) + (4 * 5)
        #file.write_new_line(self.Opcodes["Info"][:])
        await self.write(self.Opcodes["Info"][:])
        #self.log_plc_output(self.Opcodes["Info"][:])
        #debug("Written following bytes to Pico: " + str(self.Opcodes["Info"][:]))
        all_bytes, resp_ok_bytes = await self.read(expected_len, 0.5)
        #self.log_device_output(all_bytes)
        #file.write_new_line(all_bytes)
        decoded_arr = []
        if len(resp_ok_bytes) <= 0:
            self._logger.info("Info command failed")
            return None
            # puts("Something went horribly wrong. Please POR and retry.")
            # exit_prog(True)
        else:
            decoded_arr = hex_bytes_to_int(resp_ok_bytes)
            #debug("Decoded data array: " + str(decoded_arr))

        flash_addr = bytes_to_little_end_uint32(resp_ok_bytes)
        flash_size = bytes_to_little_end_uint32(resp_ok_bytes[4:])
        erase_size = bytes_to_little_end_uint32(resp_ok_bytes[8:])
        write_size = bytes_to_little_end_uint32(resp_ok_bytes[12:])
        max_data_len = bytes_to_little_end_uint32(resp_ok_bytes[16:])
        this_pico_info = PicoInfo(flash_addr, flash_size, erase_size, write_size, max_data_len)

        self._logger.info(f"flash_addr: {flash_addr}")
        self._logger.info(f"flash_size: {flash_size}")
        self._logger.info(f"erase_size: {erase_size}")
        self._logger.info(f"write_size: {write_size}")
        self._logger.info(f"max_data_len: {max_data_len}")

        # debug("flash_addr: " + str(flash_addr))
        # debug("flash_size: " + str(flash_size))
        # debug("erase_size: " + str(erase_size))
        # debug("write_size: " + str(write_size))
        # debug("max_data_len: " + str(max_data_len))

        return this_pico_info

    async def erase_cmd(self, addr, length) -> bool:
        expected_bit_n = 3 * 4
        write_buff = bytes()
        write_buff += self.Opcodes['Erase'][:]
        write_buff += little_end_uint32_to_bytes(addr)
        write_buff += little_end_uint32_to_bytes(length)
        if len(write_buff) != expected_bit_n:
            missing_bits = expected_bit_n - len(write_buff)
            b = bytes(missing_bits)
            write_buff += b
        # write_readable = hex_bytes_to_int(write_buff)
        #file.write_new_line(write_buff)
        n = await self.write(write_buff)
        #self.log_plc_output(write_buff)
        #debug("Number of bytes written: " + str(n))
        all_bytes, resp_ok_bytes = await self.read(len(self.Opcodes['ResponseOK']))
        #file.write_new_line(all_bytes)
        #self.log_device_output(all_bytes)
        #debug("Erased a length of bytes, response is: " + str(all_bytes))
        self._logger.info(f"Erased, response is: {all_bytes}")
        if all_bytes != self.Opcodes['ResponseOK']:
            return False
        return True

    async def write_cmd(self, addr, length, data):
        expected_bit_n_no_data = len(self.Opcodes['Write']) + 4 + 4
        # expected_bit_n = expected_bit_n_no_data + len(data)
        write_buff = bytes()
        write_buff += self.Opcodes['Write'][:]
        write_buff += little_end_uint32_to_bytes(addr)
        write_buff += little_end_uint32_to_bytes(length)
        len_before_data = len(write_buff)
        if len_before_data != expected_bit_n_no_data:
            missing_bits = expected_bit_n_no_data - len_before_data
            b = bytes(missing_bits)
            write_buff += b
        write_buff += data
        #file.write_new_line(write_buff)
        n = await self.write(write_buff)
        #self.log_plc_output(write_buff)
        #debug("Number of bytes written: " + str(n))
        all_bytes, data_bytes = await self.read(len(self.Opcodes['ResponseOK']) + 4)
        #file.write_new_line(all_bytes)
        #self.log_device_output(all_bytes)
        #debug("All bytes return from read: " + str(all_bytes))
        self._logger.info(f"Written, response is: {all_bytes}")
        if all_bytes == b"" or data_bytes == b"":
            return False
        # all_bytes_readable = hex_bytes_to_int(all_bytes)
        resp_crc = bytes_to_little_end_uint32(data_bytes)
        calc_crc = binascii.crc32(data)

        if resp_crc != calc_crc:
            return False
        return True

    async def seal_cmd(self, addr, data):
        expected_bits_before_crc = len(self.Opcodes['Seal']) + 4 + 4
        data_length = len(data)
        crc = binascii.crc32(data)
        #crc = custom_crc32(data)
        write_buff = bytes()
        write_buff += self.Opcodes['Seal'][:]
        # print(write_buff)
        write_buff += little_end_uint32_to_bytes(addr)
        # print(write_buff)
        # print(data_length)
        # print(little_end_uint32_to_bytes(data_length))
        write_buff += little_end_uint32_to_bytes(data_length)
        # print(write_buff)
        len_before_data = len(write_buff)
        if len_before_data != expected_bits_before_crc:
            missing_bits = expected_bits_before_crc - len_before_data
            b = bytes(missing_bits)
            write_buff += b
        # print(write_buff)
        write_buff += little_end_uint32_to_bytes(crc)
        wr_buff_read = hex_bytes_to_int(write_buff)
        #file.write_new_line(write_buff)
        # print(write_buff)
        n = await self.write(write_buff)
        #elf.log_plc_output(write_buff)
        #debug("Number of bytes written: " + str(n))
        all_bytes, data_bytes = await self.read(len(self.Opcodes['ResponseOK']), 0.5)
        self._logger.info(f"Sealed, response is: {all_bytes}")
        #file.write_new_line(all_bytes)
        #self.log_device_output(all_bytes)
        #debug("All bytes seal: " + str(all_bytes))
        if all_bytes[:4] != self.Opcodes['ResponseOK']:
            return False
        return True

    # def go_to_application_cmd(self, addr):
    #     expected_bit_n = len(self.Opcodes['Go']) + 4
    #     write_buff = bytes()
    #     write_buff += self.Opcodes['Go'][:]
    #     write_buff += little_end_uint32_to_bytes(addr)
    #     if len(write_buff) != expected_bit_n:
    #         missing_bits = expected_bit_n - len(write_buff)
    #         b = bytes(missing_bits)
    #         write_buff += b
    #     write_readable = hex_bytes_to_int(write_buff)
    #     n = conn.write(write_buff)
    #     self.log_plc_output(write_buff)
    #     #file.write_new_line(write_buff)

    #     # Hopaatskeeeeee

    #     debug("Go.")

    async def boot_cmd(self):
        expected_bit_n = len(self.Opcodes['Boot']) + 4
        write_buff = bytes()
        write_buff += self.Opcodes['Boot'][:]
        write_buff += little_end_uint32_to_bytes(0)
        if len(write_buff) != expected_bit_n:
            missing_bits = expected_bit_n - len(write_buff)
            b = bytes(missing_bits)
            write_buff += b
        write_readable = hex_bytes_to_int(write_buff)
        self._logger.info(f"Send boot command: {write_buff}")
        n = await self.write(write_buff)

        all_bytes, data_bytes = await self.read(len(self.Opcodes['ResponseOK']))
        self._logger.info(f"Booted, response is: {all_bytes}")
        if all_bytes == b"":
            return True
        #file.write_new_line(all_bytes)
        #self.log_device_output(all_bytes)
        #debug("All bytes seal: " + str(all_bytes))
        elif all_bytes[:4] == self.Opcodes['ResponseErr']:
            return False
        self._logger.info(f"Unexpected response to boot command: {all_bytes}")
        return False
        #file.write_new_line(write_buff)

        # Hopaatskeeeeee
