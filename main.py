import soniccontrol as sc
from sonicpackage import SonicCatch

# sc: SonicCatch = SonicCatch.start()
# sc.set_frq(1200000)
# sc.set_gain(40)
# sc.ramp(1000000, 6000000, 10000, 0.2)



gui = sc.Root()
gui.mainloop()