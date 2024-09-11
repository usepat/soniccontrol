import asyncio
from typing import Any, Coroutine, Optional
from async_tkinter_loop import async_mainloop
import tkinter as tk
from async_tkinter_loop.async_tkinter_loop import main_loop
import ttkbootstrap as ttk
from robot.api.deco import keyword, library
import robot.api.logger as logger
from ttkbootstrap.utility import enable_high_dpi_awareness
from soniccontrol_gui.views.core.connection_window import ConnectionWindow
from sonicpackage.system import PLATFORM, System
from soniccontrol_gui.utils.widget_registry import WidgetRegistry, get_text_of_widget


async def timeout_wrapper(timeout_ms: int, coroutine: Coroutine[Any, Any, None]):
    timeout = timeout_ms/1000
    try:
        await asyncio.wait_for(coroutine, timeout=timeout)
    except asyncio.TimeoutError:
        return False
    else:
        return True


@library(auto_keywords=False, scope="SUITE")
class RobotSonicControlGui:
    def __init__(self):
        self._root: Optional[tk.Tk | tk.Toplevel] = None
        self._loop = asyncio.get_event_loop()

    @keyword('Open app')
    def open_app(self):
        WidgetRegistry.set_up()
        main_window = ConnectionWindow(True)
        if PLATFORM != System.WINDOWS:
            enable_high_dpi_awareness(main_window.view)
        self._root = main_window.view.winfo_toplevel()
        self._loop.create_task(main_loop(main_window.view))  # type: ignore

    @keyword('Close app')
    def close_app(self):
        if self._root is None:
            raise RuntimeError("Root was None")

        self._loop.run_until_complete(WidgetRegistry.clean_up()) # Maybe we can do this better. But Idk
        self._root.destroy()

    @keyword('Does the widget "${name_widget}" exist')
    def does_widget_exist(self, name_widget: str) -> bool:
        return WidgetRegistry.is_widget_registered(name_widget)

    @keyword('Wait up to "${timeout_ms}" ms for the widget "${name_widget}" to be registered')
    def wait_for_widget_to_be_registered(self, timeout_ms: int, name_widget: str) -> None:
        task = timeout_wrapper(timeout_ms, WidgetRegistry.wait_for_widget_to_be_registered(name_widget))
        widget_registered = self._loop.run_until_complete(task)
        if not widget_registered:
            raise TimeoutError(f"Widget '{name_widget}' did not change in the timeout of {timeout_ms} ms")

    @keyword('Wait up to "${timeout_ms}" ms for the widget "${name_widget}" to change')
    def wait_for_widget_to_change(self, timeout_ms: int, name_widget: str) -> None:  
        task = timeout_wrapper(timeout_ms, WidgetRegistry.wait_for_widget_to_change(name_widget))
        widget_changed = self._loop.run_until_complete(task)
        if not widget_changed:
            raise TimeoutError(f"Widget '{name_widget}' did not change in the timeout of {timeout_ms} ms")

    @keyword('Get text of widget "${name_widget}"')
    def get_widget_text(self, name_widget: str) -> str:         
        widget = WidgetRegistry.get_widget(name_widget)
        return get_text_of_widget(widget)

    @keyword('Set text of widget "${name_widget}" to "${text}"')
    def set_widget_text(self, name_widget: str, text: str) -> None:
        widget = WidgetRegistry.get_widget(name_widget)
        if isinstance(widget, (tk.Entry, ttk.Entry)):
            widget.delete(0, ttk.END)
            widget.insert(0, text)
        elif isinstance(widget, ttk.ScrolledText):
            widget.delete(1.0, ttk.END) # type: ignore
            widget.insert(ttk.INSERT, text)
        elif isinstance(widget, ttk.Combobox):
            widget.set(text)
        elif isinstance(widget, ttk.Meter):
            widget.configure(amountused=int(text))
        elif isinstance(widget, (tk.Label, ttk.Label, tk.Button, ttk.Button)):
            widget.config(text=text)
        else:
            raise TypeError("The object has to be of type tk.Label, tk.Entry or tk.Button or inherit from them")

    @keyword('Press button "${name_widget}"')
    def press_button(self, name_widget: str) -> None:
        widget = WidgetRegistry.get_widget(name_widget)
        if isinstance(widget, (tk.Button, ttk.Button)):
            widget.invoke()
        else:
            raise TypeError(f"The registered object '{name_widget}' is not a button")
        

