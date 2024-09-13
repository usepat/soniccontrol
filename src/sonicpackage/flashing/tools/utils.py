# Returns flasher usage message.
import struct
from typing import List
import zlib

def hex_bytes_to_int(hex_bytes: bytes) -> List[int]:
    tup = struct.unpack('<' + 'B' * len(hex_bytes), hex_bytes)
    test_list = list()
    for val in tup:
        test_list.append(val)
    return test_list


def bytes_to_little_end_uint32(b: bytes):
    new_int = int(b[0]) | int(b[1]) << 8 | int(b[2]) << 16 | int(b[3]) << 24
    return new_int


def little_end_uint32_to_bytes(v: int):
    return v.to_bytes((v.bit_length() + 7) // 8, 'little')

def custom_crc32(data, initial=0xFFFFFFFF):
    crc = zlib.crc32(data, initial) ^ 0xFFFFFFFF
    # Reverse the bits of the result for output compatibility if needed
    reversed_crc = int('{:032b}'.format(crc)[::-1], 2)
    return reversed_crc

def align(val, to):
    return (val + (to - 1)) & ~(to - 1)

