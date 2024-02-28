from typing import Any

import soniccontrol.utils as utils
import soniccontrol.utils.constants as const
import ttkbootstrap as ttk
from icecream import ic
from soniccontrol.interfaces.layouts import Layout
from soniccontrol.interfaces.view import TabView, View
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.tableview import (TableColumn, TableEvent,
                                    TableHeaderRightClickMenu, TableRow,
                                    Tableview)

from soniccontrol import soniccontrol_logger as logger


class SonicMeasureView(TabView):
    def __init__(self, master: ttk.Window, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)

    def _initialize_children(self) -> None:
        self._main_frame: ttk.Frame = ttk.Frame(self)
        self._notebook: ttk.Notebook = ttk.Notebook(self._main_frame)

        self._liveplot_frame: LivePlotView = LivePlotView(self._main_frame)
        self._sonic_measure_frame: SonicMeasureFrame = SonicMeasureFrame(
            self._main_frame
        )
        self._data_visualizer: DataVisualizer = DataVisualizer(self._main_frame)

    @property
    def image(self) -> ttk.ImageTk.PhotoImage:
        return utils.ImageLoader.load_image(
            const.images.LINECHART_ICON_BLACK, const.misc.TAB_ICON_SIZE
        )

    @property
    def tab_title(self) -> str:
        return const.ui.SONIC_MEASURE_LABEL

    @property
    def layouts(self) -> set[Layout]:
        ...

    def _initialize_publish(self) -> None:
        self._main_frame.pack(expand=True, fill=ttk.BOTH)
        self._notebook.pack(expand=True, fill=ttk.BOTH)
        self._notebook.add(self._liveplot_frame, text=const.ui.LIVE_PLOT)
        self._notebook.add(self._sonic_measure_frame, text=const.ui.SONIC_MEASURE_LABEL)
        self._notebook.add(self._data_visualizer, text=const.ui.DATA_VISUALIZER)

    def set_small_width_layout(self) -> None:
        ...

    def set_large_width_layout(self) -> None:
        ...

    def publish(self) -> None:
        ...


class SonicMeasureFrame(View):
    def __init__(self, master: ttk.tk.Widget, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)

    def _initialize_children(self) -> None:
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

        self._greeter_frame: ScrolledFrame = ScrolledFrame(
            self._main_frame, autohide=True
        )
        self._parameters_frame: ttk.Frame = ttk.Frame(self._greeter_frame)

        self._start_value_label: ttk.Label = ttk.Label(
            self._parameters_frame, text=const.ui.START_VALUE
        )
        self._start_value_entry: ttk.Spinbox = ttk.Spinbox(self._parameters_frame)

        self._stop_value_label: ttk.Label = ttk.Label(
            self._parameters_frame, text=const.ui.STOP_VALUE
        )
        self._stop_value_entry: ttk.Spinbox = ttk.Spinbox(self._parameters_frame)

        self._step_value_label: ttk.Label = ttk.Label(
            self._parameters_frame, text=const.ui.STEP_VALUE
        )
        self._step_value_entry: ttk.Spinbox = ttk.Spinbox(self._parameters_frame)

        self._on_duration_label: ttk.Label = ttk.Label(
            self._parameters_frame, text=const.ui.ON_DURATION
        )
        self._on_duration_entry: ttk.Spinbox = ttk.Spinbox(self._parameters_frame)
        self._on_duration_unit_entry: ttk.Combobox = ttk.Combobox(
            self._parameters_frame, width=const.misc.MEDIUM_PADDING
        )

        self._off_duration_label: ttk.Label = ttk.Label(
            self._parameters_frame, text=const.ui.OFF_DURATION
        )
        self._off_duration_entry: ttk.Spinbox = ttk.Spinbox(self._parameters_frame)
        self._off_duration_unit_entry: ttk.Combobox = ttk.Combobox(
            self._parameters_frame, width=const.misc.MEDIUM_PADDING
        )

        self._toggle_scripting: ttk.Checkbutton = ttk.Checkbutton(
            self._parameters_frame,
            text=const.ui.USE_SCRIPTING_INSTEAD,
            style=const.style.DARK_SQUARE_TOGGLE,
        )

    def _initialize_publish(self) -> None:
        self._main_frame.pack(expand=True, fill=ttk.BOTH)
        self._main_frame.columnconfigure(0, weight=const.misc.EXPAND)
        self._main_frame.rowconfigure(0, weight=const.misc.DONT_EXPAND, minsize=10)
        self._main_frame.rowconfigure(1, weight=const.misc.EXPAND)

        self._navigation_frame.grid(
            row=0,
            column=0,
            padx=const.misc.LARGE_PART_PADDING,
            pady=const.misc.MEDIUM_PADDING,
            sticky=ttk.EW,
        )
        self._navigation_frame.rowconfigure(
            0, weight=const.misc.DONT_EXPAND, minsize=10
        )
        self._navigation_frame.columnconfigure(1, weight=const.misc.EXPAND)

        self._back_button.grid(
            row=0,
            column=0,
            padx=const.misc.MEDIUM_PADDING,
            pady=const.misc.MEDIUM_PADDING,
            sticky=ttk.W,
        )
        self._start_stop_button.grid(
            row=0,
            column=1,
            padx=const.misc.MEDIUM_PADDING,
            pady=const.misc.MEDIUM_PADDING,
            sticky=ttk.E,
        )

        self._greeter_frame.grid(row=1, column=0, sticky=ttk.NSEW)
        self._greeter_frame.columnconfigure(0, weight=const.misc.EXPAND)
        self._greeter_frame.rowconfigure(0, weight=const.misc.EXPAND)
        self._parameters_frame.grid(
            row=0,
            column=0,
            padx=const.misc.SIDE_PADDING,
            pady=const.misc.MEDIUM_PADDING,
            sticky=ttk.NSEW,
        )
        self._parameters_frame.columnconfigure(0, weight=const.misc.DONT_EXPAND)
        self._parameters_frame.columnconfigure(1, weight=const.misc.EXPAND, minsize=10)
        self._parameters_frame.columnconfigure(
            2, weight=const.misc.DONT_EXPAND, minsize=10
        )

        self._start_value_label.grid(
            row=0,
            column=0,
            padx=const.misc.MEDIUM_PADDING,
            pady=const.misc.MEDIUM_PADDING,
            sticky=ttk.E,
        )
        self._start_value_entry.grid(
            row=0,
            column=1,
            columnspan=2,
            padx=const.misc.MEDIUM_PADDING,
            pady=const.misc.MEDIUM_PADDING,
            sticky=ttk.EW,
        )
        self._stop_value_label.grid(
            row=1,
            column=0,
            padx=const.misc.MEDIUM_PADDING,
            pady=const.misc.MEDIUM_PADDING,
            sticky=ttk.E,
        )
        self._stop_value_entry.grid(
            row=1,
            column=1,
            columnspan=2,
            padx=const.misc.MEDIUM_PADDING,
            pady=const.misc.MEDIUM_PADDING,
            sticky=ttk.EW,
        )
        self._step_value_label.grid(
            row=2,
            column=0,
            padx=const.misc.MEDIUM_PADDING,
            pady=const.misc.MEDIUM_PADDING,
            sticky=ttk.E,
        )
        self._step_value_entry.grid(
            row=2,
            column=1,
            columnspan=2,
            padx=const.misc.MEDIUM_PADDING,
            pady=const.misc.MEDIUM_PADDING,
            sticky=ttk.EW,
        )
        self._on_duration_label.grid(
            row=3,
            column=0,
            padx=const.misc.MEDIUM_PADDING,
            pady=const.misc.MEDIUM_PADDING,
            sticky=ttk.E,
        )
        self._on_duration_entry.grid(
            row=3,
            column=1,
            padx=const.misc.MEDIUM_PADDING,
            pady=const.misc.MEDIUM_PADDING,
            sticky=ttk.EW,
        )
        self._on_duration_unit_entry.grid(
            row=3,
            column=2,
            padx=const.misc.MEDIUM_PADDING,
            pady=const.misc.MEDIUM_PADDING,
            sticky=ttk.W,
        )
        self._off_duration_label.grid(
            row=4,
            column=0,
            padx=const.misc.MEDIUM_PADDING,
            pady=const.misc.MEDIUM_PADDING,
            sticky=ttk.E,
        )
        self._off_duration_entry.grid(
            row=4,
            column=1,
            padx=const.misc.MEDIUM_PADDING,
            pady=const.misc.MEDIUM_PADDING,
            sticky=ttk.EW,
        )
        self._off_duration_unit_entry.grid(
            row=4,
            column=2,
            padx=const.misc.MEDIUM_PADDING,
            pady=const.misc.MEDIUM_PADDING,
            sticky=ttk.W,
        )
        self._toggle_scripting.grid(
            row=5,
            column=0,
            columnspan=3,
            padx=const.misc.MEDIUM_PADDING,
            pady=const.misc.LARGE_PADDING,
        )


class DataVisualizer(View):
    def __init__(self, master: ttk.tk.Widget, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)

    def _initialize_children(self) -> None:
        self._main_frame: ttk.Frame = ttk.Frame(self)

        # self._navigation_frame: ttk.Frame = ttk.Frame(self._main_frame)
        # self._refresh_button: ttk.Button = ttk.Button(
        #     self._navigation_frame,
        #     text=const.ui.REFRESH,
        #     compound=ttk.LEFT,
        #     style=ttk.DARK,
        #     image=utils.ImageLoader.load_image(
        #         const.images.REFRESH_ICON_WHITE, const.misc.BUTTON_ICON_SIZE
        #     ),
        # )
        # self._visualize_button: ttk.Button = ttk.Button(
        #     self._navigation_frame,
        #     text=const.ui.VISUALIZE,
        #     compound=ttk.RIGHT,
        #     style=ttk.SUCCESS,
        #     image=utils.ImageLoader.load_image(
        #         const.images.FORWARDS_ICON_WHITE, const.misc.BUTTON_ICON_SIZE
        #     ),
        #     command=self._visualize,
        # )

        column_data: list[dict[str, Any]] = [
            {"text": "Date", "stretch": False},
            {"text": "From", "stretch": False},
            {"text": "Until", "stretch": False},
            {"text": "Duration", "stretch": False},
            {"text": "Description", "stretch": True},
            {"text": "Device Type", "stretch": False},
            {"text": "Filename", "stretch": False},
        ]
        row_data: list[tuple[str, str, str, str, str, str, str]] = [
            (
                "12.03.2023",
                "13:30",
                "17:44",
                "03:10",
                "Decristilazation SYNGENTA",
                "sonicwipe",
                "sonicmeasure.json",
            ),
            (
                "23.03.2023",
                "09:16",
                "10:22",
                "01:06",
                "Growth of a new field",
                "soniccatch",
                "sonicmeasure1.json",
            ),
            (
                "23.05.2023",
                "11:10",
                "15:21",
                "04:06",
                "A lab research",
                "soniccatch",
                "sonicmeasure2.json",
            ),
            (
                "23.03.2023",
                "09:16",
                "10:22",
                "01:06",
                "Growth of a new field",
                "soniccatch",
                "sonicmeasure1.json",
            ),
        ]
        self._tableview: Tableview = Tableview(
            self._main_frame,
            bootstyle=ttk.DARK,
            paginated=True,
            coldata=column_data,
            rowdata=row_data,
            autofit=True,
            searchable=True,
        )
        self._tableview.view.bind("<<TreeviewSelect>>", self._visualize, add=True)
        self._tableview.view.configure(selectmode="browse")
        self._tableview.view.bind(
            "<Double-Button-1>", lambda event: ic("Double-Button-1", event)
        )
        self._tableview.view.bind("<Button-2>", lambda event: ic(event))
        self._tableview.view.bind("<Button-3>", lambda event: ic(event))

        self._navigation_frame: ttk.Frame = self._tableview.winfo_children()[0]
        self._navigation_frame.configure(
            padding=(0, const.misc.MEDIUM_PADDING, 0, const.misc.LARGE_PADDING)
        )
        self._search_label: ttk.Label = self._navigation_frame.winfo_children()[0]
        self._search_entry: ttk.Entry = self._navigation_frame.winfo_children()[1]
        self._refresh_button: ttk.Button = ttk.Button(
            self._navigation_frame,
            text=const.ui.REFRESH,
            compound=ttk.LEFT,
            style=ttk.DARK,
            image=utils.ImageLoader.load_image(
                const.images.REFRESH_ICON_WHITE, const.misc.BUTTON_ICON_SIZE
            ),
        )
        self._visualize_button: ttk.Button = ttk.Button(
            self._navigation_frame,
            text=const.ui.VISUALIZE,
            compound=ttk.RIGHT,
            style=ttk.SUCCESS,
            image=utils.ImageLoader.load_image(
                const.images.FORWARDS_ICON_WHITE, const.misc.BUTTON_ICON_SIZE
            ),
            command=self._visualize,
        )

    def _initialize_publish(self) -> None:
        self._main_frame.pack(expand=True, fill=ttk.BOTH)
        self._main_frame.rowconfigure(0, weight=const.misc.EXPAND)
        self._main_frame.columnconfigure(0, weight=const.misc.EXPAND)

        # self._navigation_frame.grid(
        #     row=0,
        #     column=0,
        #     sticky=ttk.EW,
        #     pady=const.misc.MEDIUM_PADDING,
        #     padx=const.misc.SIDE_PADDING,
        # )
        for child in self._navigation_frame.winfo_children():
            child.pack_forget()
        self._navigation_frame.columnconfigure(2, weight=const.misc.EXPAND)
        self._refresh_button.grid(row=0, column=0, sticky=ttk.W)
        self._search_label.grid(row=0, column=1, padx=const.misc.SMALL_PADDING)
        self._search_entry.grid(
            row=0, column=2, sticky=ttk.EW, padx=const.misc.SMALL_PADDING
        )
        self._visualize_button.grid(row=0, column=3, sticky=ttk.E)
        self._tableview.grid(
            row=0,
            column=0,
            sticky=ttk.NSEW,
            padx=const.misc.SIDE_PADDING,
            pady=const.misc.MEDIUM_PADDING,
        )

    def _visualize(self, event: Any = None, *args, **kwargs) -> None:
        ic(event)
        rows: list[TableRow] = self._tableview.get_rows(selected=True)
        for row in rows:
            ic(row)
            ic(row.values)


class LivePlotView(View):
    def __init__(self, master: ttk.tk.Widget, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)

    def _initialize_children(self) -> None:
        self._main_frame: ttk.Frame = ttk.Frame(self)
        self._navigation_frame: ttk.Frame = ttk.Frame(self._main_frame)
        self._start_stop_button: ttk.Button = ttk.Button(
            self._navigation_frame,
            text=const.ui.START_LIVE_PLOT,
            style=ttk.SUCCESS,
            image=utils.ImageLoader.load_image(
                const.images.PLAY_ICON_WHITE, const.misc.BUTTON_ICON_SIZE
            ),
            compound=ttk.RIGHT,
        )
        self._toggle_button_frame: ttk.Frame = ttk.Frame(self._navigation_frame)
        self._toggle_frequency_button: ttk.Checkbutton = ttk.Checkbutton(
            self._toggle_button_frame,
            text=const.ui.FREQUENCY,
            style=const.style.DARK_SQUARE_TOGGLE,
        )
        self._toggle_gain_button: ttk.Checkbutton = ttk.Checkbutton(
            self._toggle_button_frame,
            text=const.ui.GAIN,
            style=const.style.DARK_SQUARE_TOGGLE,
        )
        self._toggle_urms_button: ttk.Checkbutton = ttk.Checkbutton(
            self._toggle_button_frame,
            text=const.ui.URMS,
            style=const.style.DARK_SQUARE_TOGGLE,
        )
        self._toggle_irms_button: ttk.Checkbutton = ttk.Checkbutton(
            self._toggle_button_frame,
            text=const.ui.IRMS,
            style=const.style.DARK_SQUARE_TOGGLE,
        )
        self._toggle_phase_button: ttk.Checkbutton = ttk.Checkbutton(
            self._toggle_button_frame,
            text=const.ui.PHASE,
            style=const.style.DARK_SQUARE_TOGGLE,
        )
        self._body_frame: ttk.Frame = ttk.Frame(self._main_frame)

    def _initialize_publish(self) -> None:
        self._main_frame.pack(expand=True, fill=ttk.BOTH)
        self._main_frame.columnconfigure(0, weight=const.misc.EXPAND)
        self._main_frame.rowconfigure(0, weight=const.misc.DONT_EXPAND, minsize=10)
        self._main_frame.rowconfigure(1, weight=const.misc.EXPAND)

        self._navigation_frame.grid(
            row=0,
            column=0,
            padx=const.misc.LARGE_PART_PADDING,
            pady=const.misc.MEDIUM_PADDING,
            sticky=ttk.EW,
        )
        self._navigation_frame.rowconfigure(
            0, weight=const.misc.DONT_EXPAND, minsize=10
        )
        self._navigation_frame.columnconfigure(1, weight=const.misc.EXPAND)

        self._start_stop_button.grid(
            row=0, column=0, padx=const.misc.SMALL_PADDING, sticky=ttk.W
        )
        self._toggle_button_frame.grid(row=0, column=1, sticky=ttk.E)
        self._toggle_frequency_button.grid(
            row=0, column=0, padx=const.misc.SMALL_PADDING
        )
        self._toggle_gain_button.grid(row=0, column=1, padx=const.misc.SMALL_PADDING)
        self._toggle_urms_button.grid(row=0, column=2, padx=const.misc.SMALL_PADDING)
        self._toggle_irms_button.grid(row=0, column=3, padx=const.misc.SMALL_PADDING)
        self._toggle_phase_button.grid(row=0, column=4, padx=const.misc.SMALL_PADDING)

        self._body_frame.grid(row=1, column=0, sticky=ttk.NSEW)
