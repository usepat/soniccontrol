import ttkbootstrap as ttk
from soniccontrol.components.horizontalscrolled import HorizontalScrolledFrame
from soniccontrol.interfaces.layouts import Layout
from soniccontrol.utils import constants

from soniccontrol import utils


class StatusBarView(ttk.Frame):
    def __init__(self, master: ttk.Window, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)
        self._master: ttk.Window = master

        self._main_frame: ttk.Frame = ttk.Frame(self, style=ttk.SECONDARY)

        self._program_state_frame: ttk.Frame = ttk.Frame(self._main_frame)
        self._program_state_label: ttk.Label = ttk.Label(
            self._program_state_frame, style=constants.style.INVERSE_SECONDARY
        )

        self._scrolled_info_frame: HorizontalScrolledFrame = HorizontalScrolledFrame(
            self._main_frame, style=ttk.SECONDARY, autohide=True
        )
        self._scrolled_info_frame.hide_scrollbars()

        self._freq_frame: ttk.Frame = ttk.Frame(self._scrolled_info_frame)
        self._freq_label: ttk.Label = ttk.Label(
            self._freq_frame, style=constants.style.INVERSE_SECONDARY
        )

        self._gain_frame: ttk.Frame = ttk.Frame(self._scrolled_info_frame)
        self._gain_label: ttk.Label = ttk.Label(
            self._gain_frame,
            style=constants.style.INVERSE_SECONDARY,
        )

        self._temperature_frame: ttk.Frame = ttk.Frame(self._scrolled_info_frame)
        self._temperature_label: ttk.Label = ttk.Label(
            self._temperature_frame,
            style=constants.style.INVERSE_SECONDARY,
        )

        self._mode_frame: ttk.Frame = ttk.Frame(self._scrolled_info_frame)
        self._mode_label: ttk.Label = ttk.Label(
            self._mode_frame,
            style=constants.style.INVERSE_SECONDARY,
        )

        self._urms_frame: ttk.Frame = ttk.Frame(self._scrolled_info_frame)
        self._urms_label: ttk.Label = ttk.Label(
            self._urms_frame,
            style=constants.style.INVERSE_SECONDARY,
        )

        self._irms_frame: ttk.Frame = ttk.Frame(self._scrolled_info_frame)
        self._irms_label: ttk.Label = ttk.Label(
            self._irms_frame,
            style=constants.style.INVERSE_SECONDARY,
        )

        self._phase_frame: ttk.Frame = ttk.Frame(self._scrolled_info_frame)
        self._phase_label: ttk.Label = ttk.Label(
            self._phase_frame,
            style=constants.style.INVERSE_SECONDARY,
        )

        self._signal_frame: ttk.Frame = ttk.Frame(self)
        ICON_LABEL_PADDING: tuple[int, int, int, int] = (8, 0, 0, 0)
        self._connection_label: ttk.Label = ttk.Label(
            self._signal_frame,
            style=constants.style.INVERSE_DANGER,
            padding=ICON_LABEL_PADDING,
            image=utils.ImageLoader.load_image(
                constants.images.CONNECTION_ICON_WHITE, constants.misc.BUTTON_ICON_SIZE
            ),
            compound=ttk.LEFT,
        )
        self._signal_label: ttk.Label = ttk.Label(
            self._signal_frame,
            style=constants.style.INVERSE_DANGER,
            padding=ICON_LABEL_PADDING,
            image=utils.ImageLoader.load_image(
                constants.images.LIGHTNING_ICON_WHITE, constants.misc.BUTTON_ICON_SIZE
            ),
            compound=ttk.LEFT,
        )
        self._init_publish()

    @property
    def layouts(self) -> set[Layout]:
        ...

    def _init_publish(self) -> None:
        self._program_state_label.pack(side=ttk.LEFT, ipadx=5)
        self._freq_label.pack(side=ttk.LEFT)
        self._gain_label.pack(side=ttk.LEFT)
        self._mode_label.pack(side=ttk.LEFT)
        self._temperature_label.pack(side=ttk.LEFT)
        self._urms_label.pack(side=ttk.LEFT)
        self._irms_label.pack(side=ttk.LEFT)
        self._phase_label.pack(side=ttk.LEFT)

        self._signal_frame.pack(side=ttk.RIGHT)
        self._signal_label.pack(side=ttk.RIGHT, ipadx=3)
        self._connection_label.pack(side=ttk.RIGHT, ipadx=3)


class StatusView(ttk.Frame):
    def __init__(self, master: ttk.Window, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)

    @property
    def layouts(self) -> set[Layout]:
        ...
