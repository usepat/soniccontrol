import os
print(os.listdir())

import soniccontrol as sc
from ttkbootstrap.utility import enable_high_dpi_awareness, scale_size

import platform

if platform.system() == 'Windows':
    enable_high_dpi_awareness()
    gui = sc.Root()
    
elif platform.system() == 'Linux':
    gui = sc.Root()
    enable_high_dpi_awareness(gui)

gui.mainloop()

# on
# startloop 10
# hold 5s
# frequency 1200000
# startloop 2
# ramp 1200000 900000 10000 100
# endloop
# off