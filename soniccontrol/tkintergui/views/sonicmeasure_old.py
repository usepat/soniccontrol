from typing import Any

import ttkbootstrap as ttk
from icecream import ic
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.tableview import (TableColumn, TableEvent,
                                    TableHeaderRightClickMenu, TableRow,
                                    Tableview)

import soniccontrol.utils as utils
from soniccontrol import soniccontrol_logger as logger
from soniccontrol.interfaces.view import TabView, View
from soniccontrol.tkintergui.utils.constants import sizes, style, ui_labels
from soniccontrol.tkintergui.utils.image_loader import ImageLoader
from soniccontrol.utils.files import images


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
        return ImageLoader.load_image(images.LINECHART_ICON_BLACK, sizes.TAB_ICON_SIZE)

    @property
    def tab_title(self) -> str:
        return ui_labels.SONIC_MEASURE_LABEL

    def _initialize_publish(self) -> None:
        self._main_frame.pack(expand=True, fill=ttk.BOTH)
        self._notebook.pack(expand=True, fill=ttk.BOTH)
        self._notebook.add(self._liveplot_frame, text=ui_labels.LIVE_PLOT)
        self._notebook.add(
            self._sonic_measure_frame, text=ui_labels.SONIC_MEASURE_LABEL
        )
        self._notebook.add(self._data_visualizer, text=ui_labels.DATA_VISUALIZER)

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
            text=ui_labels.BACK_LABEL,
            style=ttk.DARK,
            compound=ttk.LEFT,
            image=ImageLoader.load_image(
                images.BACK_ICON_WHITE, sizes.BUTTON_ICON_SIZE
            ),
        )
        self._start_stop_button: ttk.Button = ttk.Button(
            self._navigation_frame,
            text=ui_labels.START_LABEL,
            style=ttk.SUCCESS,
            compound=ttk.RIGHT,
            image=ImageLoader.load_image(
                images.FORWARDS_ICON_WHITE, sizes.BUTTON_ICON_SIZE
            ),
        )
        self._restart_button: ttk.Button = ttk.Button(
            self._navigation_frame,
            text=ui_labels.RESTART,
            style=ttk.DARK,
            compound=ttk.LEFT,
            image=ImageLoader.load_image(
                images.REFRESH_ICON_WHITE, sizes.BUTTON_ICON_SIZE
            ),
        )
        self._end_new_button: ttk.Button = ttk.Button(
            self._navigation_frame,
            text=ui_labels.END,
            style=ttk.DANGER,
            compound=ttk.LEFT,
            # image=utils.ImageLoader.load_image(
            #     images.END_ICON_WHITE, sizes.BUTTON_ICON_SIZE
            # ),
        )

        self._greeter_frame: ScrolledFrame = ScrolledFrame(
            self._main_frame, autohide=True
        )
        self._parameters_frame: ttk.Frame = ttk.Frame(self._greeter_frame)

        self._start_value_label: ttk.Label = ttk.Label(
            self._parameters_frame, text=ui_labels.START_VALUE
        )
        self._start_value_entry: ttk.Spinbox = ttk.Spinbox(self._parameters_frame)

        self._stop_value_label: ttk.Label = ttk.Label(
            self._parameters_frame, text=ui_labels.STOP_VALUE
        )
        self._stop_value_entry: ttk.Spinbox = ttk.Spinbox(self._parameters_frame)

        self._step_value_label: ttk.Label = ttk.Label(
            self._parameters_frame, text=ui_labels.STEP_VALUE
        )
        self._step_value_entry: ttk.Spinbox = ttk.Spinbox(self._parameters_frame)

        self._on_duration_label: ttk.Label = ttk.Label(
            self._parameters_frame, text=ui_labels.ON_DURATION
        )
        self._on_duration_entry: ttk.Spinbox = ttk.Spinbox(self._parameters_frame)
        self._on_duration_unit_entry: ttk.Combobox = ttk.Combobox(
            self._parameters_frame, width=sizes.MEDIUM_PADDING
        )

        self._off_duration_label: ttk.Label = ttk.Label(
            self._parameters_frame, text=ui_labels.OFF_DURATION
        )
        self._off_duration_entry: ttk.Spinbox = ttk.Spinbox(self._parameters_frame)
        self._off_duration_unit_entry: ttk.Combobox = ttk.Combobox(
            self._parameters_frame, width=sizes.MEDIUM_PADDING
        )

        self._toggle_scripting: ttk.Checkbutton = ttk.Checkbutton(
            self._parameters_frame,
            text=ui_labels.USE_SCRIPTING_INSTEAD,
            style=style.DARK_SQUARE_TOGGLE,
            command=self._toggle_scripting_command,
        )

    def _initialize_publish(self) -> None:
        self._main_frame.pack(expand=True, fill=ttk.BOTH)
        self._main_frame.columnconfigure(0, weight=sizes.EXPAND)
        self._main_frame.rowconfigure(0, weight=sizes.DONT_EXPAND, minsize=10)
        self._main_frame.rowconfigure(1, weight=sizes.EXPAND)

        self._navigation_frame.grid(
            row=0,
            column=0,
            padx=sizes.LARGE_PART_PADDING,
            pady=sizes.MEDIUM_PADDING,
            sticky=ttk.EW,
        )
        self._navigation_frame.rowconfigure(0, weight=sizes.DONT_EXPAND, minsize=10)
        self._navigation_frame.columnconfigure(1, weight=sizes.EXPAND)

        self._back_button.grid(
            row=0,
            column=0,
            padx=sizes.MEDIUM_PADDING,
            pady=sizes.MEDIUM_PADDING,
            sticky=ttk.W,
        )
        self._start_stop_button.grid(
            row=0,
            column=1,
            padx=sizes.MEDIUM_PADDING,
            pady=sizes.MEDIUM_PADDING,
            sticky=ttk.E,
        )

        self._greeter_frame.grid(row=1, column=0, sticky=ttk.NSEW)
        self._greeter_frame.columnconfigure(0, weight=sizes.EXPAND)
        self._greeter_frame.rowconfigure(0, weight=sizes.EXPAND)
        self._parameters_frame.grid(
            row=0,
            column=0,
            padx=sizes.SIDE_PADDING,
            pady=sizes.MEDIUM_PADDING,
            sticky=ttk.NSEW,
        )
        self._parameters_frame.columnconfigure(0, weight=sizes.DONT_EXPAND)
        self._parameters_frame.columnconfigure(1, weight=sizes.EXPAND, minsize=10)
        self._parameters_frame.columnconfigure(2, weight=sizes.DONT_EXPAND, minsize=10)

        self._start_value_label.grid(
            row=0,
            column=0,
            padx=sizes.MEDIUM_PADDING,
            pady=sizes.MEDIUM_PADDING,
            sticky=ttk.E,
        )
        self._start_value_entry.grid(
            row=0,
            column=1,
            columnspan=2,
            padx=sizes.MEDIUM_PADDING,
            pady=sizes.MEDIUM_PADDING,
            sticky=ttk.EW,
        )
        self._stop_value_label.grid(
            row=1,
            column=0,
            padx=sizes.MEDIUM_PADDING,
            pady=sizes.MEDIUM_PADDING,
            sticky=ttk.E,
        )
        self._stop_value_entry.grid(
            row=1,
            column=1,
            columnspan=2,
            padx=sizes.MEDIUM_PADDING,
            pady=sizes.MEDIUM_PADDING,
            sticky=ttk.EW,
        )
        self._step_value_label.grid(
            row=2,
            column=0,
            padx=sizes.MEDIUM_PADDING,
            pady=sizes.MEDIUM_PADDING,
            sticky=ttk.E,
        )
        self._step_value_entry.grid(
            row=2,
            column=1,
            columnspan=2,
            padx=sizes.MEDIUM_PADDING,
            pady=sizes.MEDIUM_PADDING,
            sticky=ttk.EW,
        )
        self._on_duration_label.grid(
            row=3,
            column=0,
            padx=sizes.MEDIUM_PADDING,
            pady=sizes.MEDIUM_PADDING,
            sticky=ttk.E,
        )
        self._on_duration_entry.grid(
            row=3,
            column=1,
            padx=sizes.MEDIUM_PADDING,
            pady=sizes.MEDIUM_PADDING,
            sticky=ttk.EW,
        )
        self._on_duration_unit_entry.grid(
            row=3,
            column=2,
            padx=sizes.MEDIUM_PADDING,
            pady=sizes.MEDIUM_PADDING,
            sticky=ttk.W,
        )
        self._off_duration_label.grid(
            row=4,
            column=0,
            padx=sizes.MEDIUM_PADDING,
            pady=sizes.MEDIUM_PADDING,
            sticky=ttk.E,
        )
        self._off_duration_entry.grid(
            row=4,
            column=1,
            padx=sizes.MEDIUM_PADDING,
            pady=sizes.MEDIUM_PADDING,
            sticky=ttk.EW,
        )
        self._off_duration_unit_entry.grid(
            row=4,
            column=2,
            padx=sizes.MEDIUM_PADDING,
            pady=sizes.MEDIUM_PADDING,
            sticky=ttk.W,
        )
        self._toggle_scripting.grid(
            row=5,
            column=0,
            columnspan=3,
            padx=sizes.MEDIUM_PADDING,
            pady=sizes.LARGE_PADDING,
        )

    def _toggle_scripting_command(self) -> None:
        pass


class DataVisualizer(View):
    def __init__(self, master: ttk.tk.Widget, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)

    def _initialize_children(self) -> None:
        self._main_frame: ttk.Frame = ttk.Frame(self)

        # self._navigation_frame: ttk.Frame = ttk.Frame(self._main_frame)
        # self._refresh_button: ttk.Button = ttk.Button(
        #     self._navigation_frame,
        #     text=ui_labels.REFRESH,
        #     compound=ttk.LEFT,
        #     style=ttk.DARK,
        #     image=utils.ImageLoader.load_image(
        #         images.REFRESH_ICON_WHITE, sizes.BUTTON_ICON_SIZE
        #     ),
        # )
        # self._visualize_button: ttk.Button = ttk.Button(
        #     self._navigation_frame,
        #     text=ui_labels.VISUALIZE,
        #     compound=ttk.RIGHT,
        #     style=ttk.SUCCESS,
        #     image=utils.ImageLoader.load_image(
        #         images.FORWARDS_ICON_WHITE, sizes.BUTTON_ICON_SIZE
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
            padding=(0, sizes.MEDIUM_PADDING, 0, sizes.LARGE_PADDING)
        )
        self._search_label: ttk.Label = self._navigation_frame.winfo_children()[0]
        self._search_label.configure(text=ui_labels.SEARCH)
        self._search_entry: ttk.Entry = self._navigation_frame.winfo_children()[1]
        self._refresh_button: ttk.Button = ttk.Button(
            self._navigation_frame,
            text=ui_labels.REFRESH,
            compound=ttk.LEFT,
            style=ttk.DARK,
            image=ImageLoader.load_image(
                images.REFRESH_ICON_WHITE, sizes.BUTTON_ICON_SIZE
            ),
        )
        # self._visualize_button: ttk.Button = ttk.Button(
        #     self._navigation_frame,
        #     text=ui_labels.VISUALIZE,
        #     compound=ttk.RIGHT,
        #     style=ttk.SUCCESS,
        #     image=utils.ImageLoader.load_image(
        #         images.FORWARDS_ICON_WHITE, sizes.BUTTON_ICON_SIZE
        #     ),
        #     command=self._visualize,
        # )

    def _initialize_publish(self) -> None:
        self._main_frame.pack(expand=True, fill=ttk.BOTH)
        self._main_frame.rowconfigure(0, weight=sizes.EXPAND)
        self._main_frame.columnconfigure(0, weight=sizes.EXPAND)

        # self._navigation_frame.grid(
        #     row=0,
        #     column=0,
        #     sticky=ttk.EW,
        #     pady=sizes.MEDIUM_PADDING,
        #     padx=sizes.SIDE_PADDING,
        # )
        for child in self._navigation_frame.winfo_children():
            child.pack_forget()
        self._navigation_frame.columnconfigure(2, weight=sizes.EXPAND)
        self._refresh_button.grid(row=0, column=0, sticky=ttk.W)
        self._search_label.grid(row=0, column=1, padx=sizes.LARGE_PADDING)
        self._search_entry.grid(row=0, column=2, sticky=ttk.EW)
        self._tableview.grid(
            row=0,
            column=0,
            sticky=ttk.NSEW,
            padx=sizes.SIDE_PADDING,
            pady=sizes.MEDIUM_PADDING,
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
            text=ui_labels.START_LIVE_PLOT,
            style=ttk.SUCCESS,
            image=ImageLoader.load_image(
                images.PLAY_ICON_WHITE, sizes.BUTTON_ICON_SIZE
            ),
            compound=ttk.RIGHT,
        )
        self._toggle_button_frame: ttk.Frame = ttk.Frame(self._navigation_frame)
        self._toggle_frequency_button: ttk.Checkbutton = ttk.Checkbutton(
            self._toggle_button_frame,
            text=ui_labels.FREQUENCY,
            style=style.DARK_SQUARE_TOGGLE,
        )
        self._toggle_gain_button: ttk.Checkbutton = ttk.Checkbutton(
            self._toggle_button_frame,
            text=ui_labels.GAIN,
            style=style.DARK_SQUARE_TOGGLE,
        )
        self._toggle_urms_button: ttk.Checkbutton = ttk.Checkbutton(
            self._toggle_button_frame,
            text=ui_labels.URMS,
            style=style.DARK_SQUARE_TOGGLE,
        )
        self._toggle_irms_button: ttk.Checkbutton = ttk.Checkbutton(
            self._toggle_button_frame,
            text=ui_labels.IRMS,
            style=style.DARK_SQUARE_TOGGLE,
        )
        self._toggle_phase_button: ttk.Checkbutton = ttk.Checkbutton(
            self._toggle_button_frame,
            text=ui_labels.PHASE,
            style=style.DARK_SQUARE_TOGGLE,
        )
        self._body_frame: ttk.Frame = ttk.Frame(self._main_frame)

    def _initialize_publish(self) -> None:
        self._main_frame.pack(expand=True, fill=ttk.BOTH)
        self._main_frame.columnconfigure(0, weight=sizes.EXPAND)
        self._main_frame.rowconfigure(0, weight=sizes.DONT_EXPAND, minsize=10)
        self._main_frame.rowconfigure(1, weight=sizes.EXPAND)

        self._navigation_frame.grid(
            row=0,
            column=0,
            padx=sizes.LARGE_PART_PADDING,
            pady=sizes.MEDIUM_PADDING,
            sticky=ttk.EW,
        )
        self._navigation_frame.rowconfigure(0, weight=sizes.DONT_EXPAND, minsize=10)
        self._navigation_frame.columnconfigure(1, weight=sizes.EXPAND)

        self._start_stop_button.grid(
            row=0, column=0, padx=sizes.SMALL_PADDING, sticky=ttk.W
        )
        self._toggle_button_frame.grid(row=0, column=1, sticky=ttk.E)
        self._toggle_frequency_button.grid(row=0, column=0, padx=sizes.SMALL_PADDING)
        self._toggle_gain_button.grid(row=0, column=1, padx=sizes.SMALL_PADDING)
        self._toggle_urms_button.grid(row=0, column=2, padx=sizes.SMALL_PADDING)
        self._toggle_irms_button.grid(row=0, column=3, padx=sizes.SMALL_PADDING)
        self._toggle_phase_button.grid(row=0, column=4, padx=sizes.SMALL_PADDING)

        self._body_frame.grid(row=1, column=0, sticky=ttk.NSEW)
