
from soniccontrol.interfaces.ui_component import UIComponent
from soniccontrol.interfaces.view import TabView
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame

from soniccontrol.tkintergui.utils.constants import sizes, ui_labels
from soniccontrol.tkintergui.utils.events import Event
from soniccontrol.utils.files import images
from soniccontrol.tkintergui.utils.image_loader import ImageLoader
from soniccontrol.tkintergui.utils.observable_list import ObservableList


class Logging(UIComponent):
    def __init__(self, parent: UIComponent, logs: ObservableList):
        self._logs = logs
        super().__init__(parent, LoggingView(parent.view))
        self._init_logs()
        self._logs.subscribe(ObservableList.EVENT_ITEM_ADDED, self._add_log)

    def _init_logs(self):
        for log in self._logs:
            self.view.add_text_line(log)

    def _add_log(self, e: Event):
        self.view.add_text_line(e.data.item)



class LoggingView(TabView):
    def __init__(self, master: ttk.Window, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)

    @property
    def image(self) -> ttk.ImageTk.PhotoImage:
        return ImageLoader.load_image(images.CONSOLE_ICON_BLACK, sizes.TAB_ICON_SIZE)

    @property
    def tab_title(self) -> str:
        return ui_labels.LOGS_LABEL

    def _initialize_children(self) -> None:
        self._main_frame: ttk.Frame = ttk.Frame(self)
        self._output_frame: ttk.Labelframe = ttk.Labelframe(
            self._main_frame, text=ui_labels.OUTPUT_LABEL
        )
        self._scrolled_frame: ScrolledFrame = ScrolledFrame(
            self._output_frame, autohide=True
        )

    def _initialize_publish(self) -> None:
        self._main_frame.pack(expand=True, fill=ttk.BOTH)
        self._main_frame.columnconfigure(0, weight=sizes.EXPAND)
        self._main_frame.rowconfigure(0, weight=sizes.EXPAND)
        self._main_frame.rowconfigure(1, weight=sizes.DONT_EXPAND, minsize=40)
        self._output_frame.grid(
            row=0,
            column=0,
            sticky=ttk.NSEW,
            pady=sizes.MEDIUM_PADDING,
            padx=sizes.LARGE_PADDING,
        )
        self._scrolled_frame.pack(
            expand=True,
            fill=ttk.BOTH,
            pady=sizes.MEDIUM_PADDING,
            padx=sizes.MEDIUM_PADDING,
        )

    def add_text_line(self, text: str):
        ttk.Label(self._scrolled_frame, text=text, font=("Consolas", 10)).pack(
            fill=ttk.X, side=ttk.TOP, anchor=ttk.W
        )
        self._scrolled_frame.update()
        self._scrolled_frame.yview_moveto(1)
