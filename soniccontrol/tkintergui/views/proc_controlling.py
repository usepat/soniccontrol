from typing import Callable, Dict, Iterable

from async_tkinter_loop import async_handler
from ttkbootstrap.dialogs.dialogs import Messagebox
from soniccontrol.interfaces.ui_component import UIComponent
from soniccontrol.interfaces.view import TabView, View
from soniccontrol.sonicpackage.procedures.procedure_controller import ProcedureController, ProcedureType

import ttkbootstrap as ttk

from soniccontrol.tkintergui.utils.constants import events, sizes, ui_labels
from soniccontrol.tkintergui.utils.events import Event
from soniccontrol.tkintergui.utils.image_loader import ImageLoader
from soniccontrol.tkintergui.widgets.procedure_widget import ProcedureWidget
from soniccontrol.utils.files import images


class ProcControlling(UIComponent):
    def __init__(self, parent: UIComponent, proc_controller: ProcedureController):
        self._proc_controller = proc_controller
        self._view = ProcControllingView(parent.view)
        self._proc_widgets: Dict[ProcedureType, ProcedureWidget] = {}
        super().__init__(parent, self._view)
        self._add_proc_widgets()
        self._view.set_procedure_selected_command(self._on_proc_selected)
        self._view.set_start_button_command(self._on_run_pressed)
        self._view.set_stop_button_command(self._on_stop_pressed)
        self._proc_controller.subscribe(events.PROCEDURE_RUNNING, self.on_procedure_running)
        self._proc_controller.subscribe(events.PROCEDURE_STOPPED, self.on_procedure_stopped)

    def _add_proc_widgets(self):
        for proc_type, args_class in self._proc_controller.proc_args_list.items():
            proc_widget = ProcedureWidget(self, self._view.procedure_frame, proc_type.value, args_class)
            proc_widget.view.hide()
            self._proc_widgets[proc_type] = proc_widget
        proc_names = map(lambda proc_type: proc_type.value, self._proc_controller.proc_args_list.keys())
        self._view.set_procedure_combobox_items(proc_names)

    def _on_proc_selected(self):
        for proc_widget in self._proc_widgets.values():
            proc_widget.view.hide()
        proc_type = ProcedureType(self._view.selected_procedure)
        self._proc_widgets[proc_type].view.show()

    def _on_run_pressed(self):
        proc_type = ProcedureType(self._view.selected_procedure)
        proc_args = self._proc_widgets[proc_type].get_args()
        if proc_args is not None:
            try:
                self._proc_controller.execute_proc(proc_type, proc_args)
            except Exception as e:
                Messagebox.show_error(str(e))

    @async_handler
    async def _on_stop_pressed(self):
        await self._proc_controller.stop_proc()

    def on_procedure_running(self, e: Event):
        self._view.set_running_proc_label(ui_labels.PROC_RUNNING.format(e.data["proc_type"]))
        self._view.set_start_button_enabled(False)
        self._view.set_stop_button_enabled(True)

    def on_procedure_stopped(self, _e: Event):
        self._view.set_running_proc_label(ui_labels.PROC_NOT_RUNNING)
        self._view.set_start_button_enabled(True)
        self._view.set_stop_button_enabled(False)

class ProcControllingView(TabView):
    def __init__(self, master: ttk.Frame | View, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

    @property
    def image(self) -> ttk.ImageTk.PhotoImage:
        return ImageLoader.load_image(images.CONSOLE_ICON_BLACK, sizes.TAB_ICON_SIZE)

    @property
    def tab_title(self) -> str:
        return ui_labels.SERIAL_MONITOR_LABEL
    
    def _initialize_children(self) -> None:
        self._selected_procedure_var = ttk.StringVar()
        self._procedure_combobox = ttk.Combobox(self, textvariable=self._selected_procedure_var)

        # Procedure widget placeholder
        self._procedure_widget_frame = ttk.Frame(self)

        # Control buttons
        self._controls_frame = ttk.Frame(self)
        self._start_button = ttk.Button(self._controls_frame, text=ui_labels.START_LABEL)
        self._stop_button = ttk.Button(self._controls_frame, text=ui_labels.STOP_LABEL)
        self._running_proc_label = ttk.Label(self._controls_frame, text="Status: Not running")

    def _initialize_publish(self) -> None:
        self._procedure_combobox.pack(fill=ttk.X, pady=5)
        self._procedure_widget_frame.pack(fill=ttk.BOTH, expand=True, pady=5)
        self._controls_frame.pack(fill=ttk.X, pady=5)
        self._start_button.pack(side=ttk.LEFT, padx=5)
        self._stop_button.pack(side=ttk.LEFT, padx=5)
        self._running_proc_label.pack(side=ttk.LEFT, fill=ttk.X, expand=True, padx=5)

    @property
    def procedure_frame(self) -> ttk.Frame:
        return self._procedure_widget_frame

    @property
    def selected_procedure(self) -> str:
        return self._selected_procedure_var.get()
    
    def set_running_proc_label(self, text: str) -> None:
        self._running_proc_label.configure(text=text)

    def set_procedure_combobox_items(self, items: Iterable[str]) -> None:
        self._procedure_combobox["values"] = list(items)

    def set_procedure_selected_command(self, command: Callable[[], None]) -> None:
        self._procedure_combobox.bind("<<ComboboxSelected>>", lambda _: command())

    def set_start_button_command(self, command: Callable[[], None]) -> None:
        self._start_button.configure(command=command)

    def set_stop_button_command(self, command: Callable[[], None]) -> None:
        self._stop_button.configure(command=command)

    def set_start_button_enabled(self, enabled: bool) -> None:
        self._start_button.configure(state=ttk.NORMAL if enabled else ttk.DISABLED)

    def set_stop_button_enabled(self, enabled: bool) -> None:
        self._stop_button.configure(state=ttk.NORMAL if enabled else ttk.DISABLED)
