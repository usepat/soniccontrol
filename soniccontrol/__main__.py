import sys
from async_tkinter_loop import async_mainloop
from soniccontrol import SonicControl

# import faulthandler


# faulthandler.enable()


if __name__ == "__main__":
    if "3.10" not in sys.version:
        print("Warning: Please use Python 3.10 to run SonicControl")
    else:
        sc: SonicControl = SonicControl()
        async_mainloop(sc)

# Scirpting Testing examples
"""
startloop
frequency 5000000
gain 150
off
hold 3s
ramp_freq 1000000 2000000 10000 100ms
endloop
"""

"""
hold 3s
!ON
hold 3s
!OFF
hold 3s
!f=2345345
hold 3s
!g=100
hold 3s
!ON
hold 3s
"""

