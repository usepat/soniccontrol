
import soniccontrol as sc
from ttkbootstrap.utility import enable_high_dpi_awareness

gui = sc.Root()
gui.mainloop()

# on
# startloop 2
# hold 5s
# frequency 1200000
# gain 100
# frequency 9000000
# startloop 2
# ramp 1200000 900000 10000 100ms
# endloop
# endloop
# off
