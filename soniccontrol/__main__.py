import sys
from async_tkinter_loop import async_handler, async_mainloop
from soniccontrol import SonicControl

# import faulthandler

# faulthandler.enable()

if __name__ == "__main__":
    if not "3.10" in sys.version:
        print("Warning: Please use Python 3.10 to run SonicControl")
    else:
        sc: SonicControl = SonicControl()
        async_mainloop(sc)

"""
startloop
frequency 50000000
gain 150
off
hold 3s
ramp_freq 1000000 2000000 10000 100ms
endloop
"""
