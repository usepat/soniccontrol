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
