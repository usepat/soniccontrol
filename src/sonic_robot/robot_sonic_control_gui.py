from typing import Any, Optional
from async_tkinter_loop import async_mainloop
import tkinter as tk
import ttkbootstrap as ttk
from robot.api.deco import keyword, library
import robot.api.logger as logger
from ttkbootstrap.utility import enable_high_dpi_awareness
from soniccontrol_gui.view import View
from soniccontrol_gui.views.core.connection_window import ConnectionWindow
from sonicpackage.system import PLATFORM, System
from soniccontrol_gui.utils.widget_registry import global_widget_registry as registry


@library(auto_keywords=False, scope="SUITE")
class RobotSonicControlGui:
    def __init__(self):
        self._root: Optional[tk.Tk | tk.Toplevel] = None

    @keyword('Open app')
    def open_app(self):
        main_window = ConnectionWindow(True)
        if PLATFORM != System.WINDOWS:
            enable_high_dpi_awareness(main_window.view)
        self._root = main_window.view.winfo_toplevel()
        async_mainloop(main_window.view) # type: ignore

    @keyword('Close app')
    def close_app(self):
        if self._root is None:
            raise RuntimeError("Root was None")

        self._root.destroy()

    @keyword('Does the widget "{name_widget}" exist')
    def does_widget_exist(self, name_widget: str) -> bool:
        return name_widget in registry
    
    @keyword('Wait up to "{timeout_ms}" ms for the widget "{name_widget}" to change')
    def wait_for_widget_to_change(self, name_widget: str, timeout_ms: int) -> None:
        pass # TODO

    @keyword('Get text of widget')
    def get_widget_text(self, name_widget: str) -> str:
        if name_widget not in registry:
            raise KeyError(f"There is no widget registered with name '{name_widget}'")
         
        widget = registry.get(name_widget)
        if isinstance(widget, (tk.Entry, ttk.Combobox)):
            return widget.get()
        elif isinstance(widget, ttk.ScrolledText):
            return widget.get(1.0, ttk.END)
        elif isinstance(widget, (tk.Label, tk.Button)):
            return widget.cget("text")
        else:
            raise TypeError("The object has to be of type tk.Label, tk.Entry or tk.Button or inherit from them")


    @keyword('Set text of widget "{name_widget}" to "{text}"')
    def set_widget_text(self, name_widget: str, text: str) -> None:
        if name_widget not in registry:
            raise KeyError(f"There is no widget registered with name '{name_widget}'")
        
        widget = registry.get(name_widget)
        if isinstance(widget, tk.Entry):
            widget.delete(0, ttk.END)
            widget.insert(0, text)
        elif isinstance(widget, ttk.ScrolledText):
            widget.delete(1.0, ttk.END) # type: ignore
            widget.insert(ttk.INSERT, text)
        elif isinstance(widget, ttk.Combobox):
            widget.set(text)
        elif isinstance(widget, (tk.Label, tk.Button)):
            widget.config(text=text)
        else:
            raise TypeError("The object has to be of type tk.Label, tk.Entry or tk.Button or inherit from them")

    @keyword('Press button')
    def press_button(self, name_widget: str) -> None:
        if name_widget not in registry:
            raise KeyError(f"There is no button registered with name '{name_widget}'")
        
        widget = registry.get(name_widget)
        if isinstance(widget, tk.Button):
            widget.invoke()
        else:
            raise TypeError("The registered object is not a button")
        

