
import soniccontrol as sc
from ttkbootstrap.utility import enable_high_dpi_awareness

#* 
# enable_high_dpi_awareness(root=None, scaling=None)

gui = sc.Root()
gui.mainloop()


# on
# frequency 1000000
# gain 100
# hold 3s
# startloop 3
# ramp 1900000 2100000 10000 100ms
# endloop
# off

