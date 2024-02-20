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

        self._main_frame: ttk.Frame = ttk.Frame(self)
        self._notebook: ttk.Notebook = ttk.Notebook(self._main_frame)

        self._liveplot_frame: LivePlotView = LivePlotView(self._main_frame)
        self._sonic_measure_frame: SonicMeasureFrame = SonicMeasureFrame(
            self._main_frame
        )

        self._init_publish()

    @property
    def image(self) -> ttk.ImageTk.PhotoImage:
        return utils.ImageLoader.load_image(const.images.LINECHART_ICON_BLACK, (25, 25))

    @property
    def tab_title(self) -> str:
        return const.ui.SONIC_MEASURE_LABEL

    @property
    def layouts(self) -> set[Layout]:
        ...

    def _init_publish(self) -> None:
        self._main_frame.pack(expand=True, fill=ttk.BOTH)
        self._notebook.pack(expand=True, fill=ttk.BOTH)
        self._notebook.add(self._liveplot_frame, text="LivePlot")
        self._notebook.add(self._sonic_measure_frame, text="SonicMeasure")

    def set_small_width_layout(self) -> None:
        ...

    def set_large_width_layout(self) -> None:
        ...

    def publish(self) -> None:
        ...


class LabelEntry(ttk.Frame):
    def __init__(self, master: ttk.tk.Widget, label: str, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)
        self._label: ttk.Label = ttk.Label(self, text=label)
        self._spinbox: ttk.Spinbox = ttk.Spinbox(self)

    def publish(self) -> None:
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self._label.grid(row=0, column=0, padx=5, pady=5, sticky=ttk.E)
        self._spinbox.grid(row=0, column=1, padx=5, pady=5, sticky=ttk.W)


class LabelEntryTime(ttk.Frame):
    def __init__(self, master: ttk.tk.Widget, label: str, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)
        self._label: ttk.Label = ttk.Label(self, text=label)
        self._spinbox: ttk.Spinbox = ttk.Spinbox(self)
        self._combobox: ttk.Combobox = ttk.Combobox(self)

    def publish(self) -> None:
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=0)
        self.rowconfigure(0, weight=1)
        self._label.grid(row=0, column=0, padx=5, pady=5, sticky=ttk.E)
        self._spinbox.grid(row=0, column=1, padx=5, pady=5, sticky=ttk.EW)
        self._combobox.grid(row=0, column=2, padx=5, pady=5, sticky=ttk.W)


class SonicMeasureFrame(ttk.Frame):
    def __init__(self, master: ttk.tk.Widget, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)
        self._master: ttk.tk.Widget = master
        self._main_frame: ttk.Frame = ttk.Frame(self)
        self._navigation_frame: ttk.Frame = ttk.Frame(self._main_frame)

        self._back_button: ttk.Button = ttk.Button(
            self._navigation_frame,
            text=const.ui.BACK_LABEL,
            style=ttk.DARK,
            compound=ttk.LEFT,
            image=utils.ImageLoader.load_image(
                const.images.BACK_ICON_WHITE, const.misc.BUTTON_ICON_SIZE
            ),
        )
        self._start_stop_button: ttk.Button = ttk.Button(
            self._navigation_frame,
            text=const.ui.START_LABEL,
            style=ttk.SUCCESS,
            compound=ttk.RIGHT,
            image=utils.ImageLoader.load_image(
                const.images.FORWARDS_ICON_WHITE, const.misc.BUTTON_ICON_SIZE
            ),
        )
        self._restart_button: ttk.Button = ttk.Button(
            self._navigation_frame,
            text=const.ui.RESTART,
            style=ttk.DARK,
            compound=ttk.LEFT,
            image=utils.ImageLoader.load_image(
                const.images.REFRESH_ICON_WHITE, const.misc.BUTTON_ICON_SIZE
            ),
        )
        self._end_new_button: ttk.Button = ttk.Button(
            self._navigation_frame,
            text=const.ui.END,
            style=ttk.DANGER,
            compound=ttk.LEFT,
            # image=utils.ImageLoader.load_image(
            #     const.images.END_ICON_WHITE, const.misc.BUTTON_ICON_SIZE
            # ),
        )

        self._greeter_frame: ttk.Frame = ttk.Frame(self._main_frame)
        self._toggle_scripting: ttk.Checkbutton = ttk.Checkbutton(
            self._greeter_frame,
            text="use Scripting instead",
            style="dark-square-toggle",
        )
        self._start_value_frame: LabelEntry = LabelEntry(
            self._greeter_frame, label="Start value:"
        )
        self._stop_value_frame: LabelEntry = LabelEntry(
            self._greeter_frame, label="Stop value:"
        )
        self._step_value_frame: LabelEntry = LabelEntry(
            self._greeter_frame, label="Step value:"
        )
        self._pause_during_on_frame: LabelEntry = LabelEntryTime(
            self._greeter_frame, label="ON duration:"
        )
        self._pause_during_off_frame: LabelEntry = LabelEntryTime(
            self._greeter_frame, label="OFF duration:"
        )

        self._init_publish()

    def _init_publish(self) -> None:
        self._main_frame.pack(expand=True, fill=ttk.BOTH)
        self._main_frame.columnconfigure(0, weight=1)
        self._main_frame.rowconfigure(0, weight=0, minsize=10)
        self._main_frame.rowconfigure(1, weight=1)

        self._navigation_frame.grid(row=0, column=0, padx=7, pady=5, sticky=ttk.EW)
        self._navigation_frame.rowconfigure(0, weight=0, minsize=10)
        self._navigation_frame.columnconfigure(1, weight=1)

        self._back_button.grid(row=0, column=0, padx=5, pady=5, sticky=ttk.W)
        self._start_stop_button.grid(row=0, column=1, padx=5, pady=5, sticky=ttk.E)

        self._greeter_frame.grid(row=1, column=0, padx=7, pady=5, sticky=ttk.NSEW)
        self._greeter_frame.columnconfigure(0, weight=1)
        self._toggle_scripting.grid(row=0, column=0, padx=5, pady=5)
        self._start_value_frame.grid(row=1, column=0, padx=5, pady=5)
        self._stop_value_frame.grid(row=2, column=0, padx=5, pady=5)
        self._step_value_frame.grid(row=3, column=0, padx=5, pady=5)
        self._pause_during_on_frame.grid(row=4, column=0, padx=5, pady=5)
        self._pause_during_off_frame.grid(row=5, column=0, padx=5, pady=5)

        for child in self._greeter_frame.winfo_children():
            if hasattr(child, "publish"):
                child.publish()


class LivePlotView(ttk.Frame):
    def __init__(self, master: ttk.tk.Widget, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)
        self._master: ttk.tk.Widget = master
        self._main_frame: ttk.Frame = ttk.Frame(self)
        self._navigation_frame: ttk.Frame = ttk.Frame(self._main_frame)
        self._start_stop_button: ttk.Button = ttk.Button(
            self._navigation_frame,
            text="Start LiveView",
            style=ttk.SUCCESS,
            image=utils.ImageLoader.load_image(
                const.images.PLAY_ICON_WHITE, const.misc.BUTTON_ICON_SIZE
            ),
            compound=ttk.RIGHT,
        )
        self._toggle_button_frame: ttk.Frame = ttk.Frame(self._navigation_frame)
        self._toggle_frequency_button: ttk.Checkbutton = ttk.Checkbutton(
            self._toggle_button_frame,
            text="Frequency",
            style="dark-square-toggle",
        )
        self._toggle_gain_button: ttk.Checkbutton = ttk.Checkbutton(
            self._toggle_button_frame,
            text="Gain",
            style="dark-square-toggle",
        )
        self._toggle_urms_button: ttk.Checkbutton = ttk.Checkbutton(
            self._toggle_button_frame,
            text="Urms",
            style="dark-square-toggle",
        )
        self._toggle_irms_button: ttk.Checkbutton = ttk.Checkbutton(
            self._toggle_button_frame,
            text="Irms",
            style="dark-square-toggle",
        )
        self._toggle_phase_button: ttk.Checkbutton = ttk.Checkbutton(
            self._toggle_button_frame,
            text="Phase",
            style="dark-square-toggle",
        )
        self._body_frame: ttk.Frame = ttk.Frame(self._main_frame)
        self._init_publish()

    def _init_publish(self) -> None:
        self._main_frame.pack(expand=True, fill=ttk.BOTH)
        self._main_frame.columnconfigure(0, weight=1)
        self._main_frame.rowconfigure(0, weight=0, minsize=10)
        self._main_frame.rowconfigure(1, weight=1)

        self._navigation_frame.grid(row=0, column=0, padx=7, pady=5, sticky=ttk.EW)
        self._navigation_frame.rowconfigure(0, weight=0, minsize=10)
        self._navigation_frame.columnconfigure(1, weight=1)

        self._start_stop_button.grid(row=0, column=0, padx=3, sticky=ttk.W)
        self._toggle_button_frame.grid(row=0, column=1, sticky=ttk.E)
        self._toggle_frequency_button.grid(row=0, column=0, padx=3)
        self._toggle_gain_button.grid(row=0, column=1, padx=3)
        self._toggle_urms_button.grid(row=0, column=2, padx=3)
        self._toggle_irms_button.grid(row=0, column=3, padx=3)
        self._toggle_phase_button.grid(row=0, column=4, padx=3)

        self._body_frame.grid(row=1, column=0, sticky=ttk.NSEW)
