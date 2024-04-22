import asyncio

from soniccontrol.sonicpackage.builder import AmpBuilder
from soniccontrol.sonicpackage.serial_communicator import SerialCommunicator

async def main():
    process = await asyncio.create_subprocess_shell(
        "",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    communicator = SerialCommunicator()
    communicator.connect(process.stdout, process.stdin)
    
    builder = AmpBuilder()
    sonicAmp = await builder.build_amp(communicator)

    for _ in range(10):
        print(await sonicAmp.get_status())
