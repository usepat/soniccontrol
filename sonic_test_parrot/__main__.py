import asyncio

from soniccontrol.sonicpackage.builder import AmpBuilder
from soniccontrol.sonicpackage.serial_communicator import SerialCommunicator

async def main():
    process = await asyncio.create_subprocess_shell(
        "/home/david-wild/Documents/sonic-firmware/build/linux/test/cli/cli_simulation_mvp/cli_simulation_mvp",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    communicator = SerialCommunicator()
    await communicator.connect(process.stdout, process.stdin)
    
    builder = AmpBuilder()
    sonicAmp = await builder.build_amp(communicator)

    for _ in range(10):
        print(await sonicAmp.get_status())

if __name__ == "__main__":
    asyncio.run(main())