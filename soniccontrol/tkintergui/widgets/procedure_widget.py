from typing import Any, Callable, Dict, List, Union

import attrs
from soniccontrol.interfaces.ui_component import UIComponent
from soniccontrol.interfaces.view import View

import ttkbootstrap as ttk

from soniccontrol.sonicpackage.procedures.ramper import HoldTuple
from soniccontrol.tkintergui.utils.events import Event

class FloatFieldView(View):
    def __init__(self, master: ttk.Frame | View, field_name: str, *args, default_value: float = 0., **kwargs):
        self._field_name = field_name
        self._value: ttk.DoubleVar = ttk.DoubleVar(value=default_value)
        super().__init__(master, *args, **kwargs)

    def _initialize_children(self) -> None:
        self.label = ttk.Label(self, text=self._field_name)
        self.entry = ttk.Entry(self, textvariable=self._value)

    def _initialize_publish(self) -> None:
        self.grid_columnconfigure(1, weight=1)

        self.label.grid(row=0, column=0, padx=5, pady=5)
        self.entry.grid(row=0, column=1, padx=5, pady=5)

    @property
    def field_name(self) -> str:
        return self._field_name

    @property
    def value(self) -> float:
        return self._value.get()
    
    @value.setter
    def value(self, v: float) -> None:
        self._value.set(v)

class TimeFieldView(View):
    def __init__(self, master: ttk.Frame | View, field_name: str, *args, default_value: HoldTuple = (0., "ms"), **kwargs):
        self._field_name = field_name
        self._time_value: ttk.DoubleVar = ttk.DoubleVar(value=default_value[0])
        self._unit_value: ttk.StringVar = ttk.StringVar(value=default_value[1])
        super().__init__(master, *args, **kwargs)

    def _initialize_children(self) -> None:
        self._label = ttk.Label(self, text=self._field_name)
        self._entry_time = ttk.Entry(self, textvariable=self._time_value)
        self._unit_button = ttk.Button(self, text=self._unit_value.get(), command=self._toggle_unit)

    def _initialize_publish(self) -> None:
        self.grid_columnconfigure(1, weight=1)

        self._label.grid(row=0, column=0, padx=5, pady=5)
        self._entry_time.grid(row=0, column=1, padx=5, pady=5)
        self._unit_button.grid(row=0, column=2, padx=5, pady=5)

    def _toggle_unit(self) -> None:
        unit = self._unit_value.get()
        unit = "ms" if unit == "s" else "s"
        self._unit_value.set(unit)
        self._unit_button.configure(text=unit)

    @property
    def field_name(self) -> str:
        return self._field_name

    @property
    def value(self) -> HoldTuple:
        return (self._time_value.get(), self._unit_value.get())
    
    @value.setter
    def value(self, v: HoldTuple) -> None:
        self._time_value.set(v[0])
        self._unit_value.set(v[1])
        self._unit_button.configure(text=v[1])


"""
This class holds only information about the procedure args.
It cannot 
"""
class ProcedureWidget(UIComponent):
    def __init__(self, parent: UIComponent, parent_view: View, procedure_name: str, proc_args_class: any):
        self._proc_args_class = proc_args_class
        self._fields: List[Union[TimeFieldView, FloatFieldView]] = []
        self._procedure_name = procedure_name
        self._view = ProcedureWidgetView(parent_view)
        self._view.set_procedure_name(self._procedure_name)
        super().__init__(self, self._view)
        self._add_fields_to_widget()

    def _add_fields_to_widget(self):
        for field_name, field in attrs.fields_dict(self._proc_args_class).items():
            if field.type is int or field.type is float:
                self._fields.append(FloatFieldView(self._view.field_slot, field_name))
            elif field.type is HoldTuple:
                self._fields.append(TimeFieldView(self._view.field_slot, field_name))
            else:
                raise TypeError(f"The field with name {field_name} has the type {field.type}, which is not supported")
        self._view._initialize_publish()

    def _get_args(self) -> Dict[str, Any]:
        dict_args: Dict[str, Any] = {}
        for field in self._fields:
            dict_args[field.field_name] = field.value
        return dict_args
        
class ProcedureWidgetView(View):
    def __init__(self, master: ttk.Frame | View, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

    def _initialize_children(self) -> None:
        pass

    def _initialize_publish(self) -> None:
        pass

    @property
    def field_slot(self) -> ttk.Frame:
        pass
    
    def set_procedure_name(self, procedure_name: str) -> None:
        pass

