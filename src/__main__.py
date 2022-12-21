import platform
import soniccontrol as sc
from ttkbootstrap.utility import enable_high_dpi_awareness

if platform.system() == 'Windows':
    enable_high_dpi_awareness()
    gui: sc.Root = sc.Root()
elif platform.system() == 'Linux':
    gui: sc.Root = sc.Root()
    enable_high_dpi_awareness(gui)

gui.mainloop()