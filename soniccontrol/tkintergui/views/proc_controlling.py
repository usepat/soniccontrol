from typing import Callable, Dict, List
from soniccontrol.interfaces.ui_component import UIComponent
from soniccontrol.interfaces.view import View
from soniccontrol.sonicpackage.procedures.procedure_controller import ProcedureController

import ttkbootstrap as ttk

from soniccontrol.tkintergui.utils.constants import ui_labels
from soniccontrol.tkintergui.widgets.procedure_widget import ProcedureWidget


class ProcControlling(UIComponent):
    def __init__(self, parent: UIComponent, proc_controller: ProcedureController):
        self._proc_controller = proc_controller
        self._view = ProcControllingView(parent.view)
        self._proc_widgets: Dict[str, ProcedureWidget] = []
        super().__init__(parent, self._view)
        self._add_proc_widgets()

    def _add_proc_widgets(self):
        pass

    def _on_proc_selected(self):
        pass

    def _on_run_pressed(self):
        pass

    def _on_stop_pressed(self):
        pass

    def on_procedure_stopped(self):
        pass

class ProcControllingView(View):
    def __init__(self, master: ttk.Frame | View, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

    def _initialize_children(self) -> None:
        self._selected_procedure_var = ttk.StringVar()
        self._procedure_combobox = ttk.Combobox(self, textvariable=self._selected_procedure_var)

        # Procedure widget placeholder
        self._procedure_widget_frame = ttk.Frame(self)

        # Control buttons
        self._controls_frame = ttk.Frame(self)
        self._start_button = ttk.Button(self._controls_frame, text=ui_labels.START_LABEL, command=self.start_procedure)
        self._stop_button = ttk.Button(self._controls_frame, text=ui_labels.STOP_LABEL, command=self.stop_procedure)
        self._running_proc_label = ttk.Label(self._controls_frame, text="Status: Not running")

    def _initialize_publish(self) -> None:
        self._procedure_combobox.pack(fill=ttk.X, pady=5)
        self._procedure_widget_frame.pack(fill=ttk.BOTH, expand=True, pady=5)
        self._controls_frame.pack(fill=ttk.X, pady=5)
        self._start_button.pack(side=ttk.LEFT, padx=5)
        self._stop_button.pack(side=ttk.LEFT, padx=5)
        self._running_proc_label.pack(side=ttk.LEFT, fill=ttk.X, expand=True, padx=5)

    def set_running_proc_label(self, text: str) -> None:
        self._running_proc_label.configure(text=text)

    @property
    def selected_procedure(self) -> str:
        return self._selected_procedure_var.get()
    
    def set_procedure_selected_command(self, command: Callable[[], None]) -> None:
        self._procedure_combobox.bind("<<ComboboxSelected>>", lambda _: command())

    def set_start_button_command(self, command: Callable[[], None]) -> None:
        self._start_button.configure(command=command)

    def set_stop_button_command(self, command: Callable[[], None]) -> None:
        self._stop_button.configure(command=command)
