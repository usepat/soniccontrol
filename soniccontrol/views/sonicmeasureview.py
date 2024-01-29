import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame

import soniccontrol.utils as utils
import soniccontrol.utils.constants as const
from soniccontrol.interfaces.layouts import Layout


# TODO: Look into how to tile sonicmeasure and liveplot
class SonicMeasureView(ttk.Frame):
    def __init__(self, master: ttk.Window, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)
        self._master: ttk.Window = master
        self._image: ttk.ImageTk.PhotoImage = utils.give_image(
            const.images.LINECHART_ICON_BLACK, (25, 25)
        )

        self._mainframe: ScrolledFrame = ScrolledFrame(self, autohide=True)

    @property
    def image(self) -> ttk.ImageTk.PhotoImage:
        return utils.ImageLoader.load_image(const.images.LINECHART_ICON_BLACK, (25, 25))

    @property
    def tab_title(self) -> str:
        return const.ui.SONIC_MEASURE_LABEL

    @property
    def layouts(self) -> set[Layout]:
        ...

    def set_small_width_layout(self) -> None:
        ...

    def set_large_width_layout(self) -> None:
        ...

    def publish(self) -> None:
        ...
