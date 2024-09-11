import asyncio
from typing import Dict, Optional
import tkinter as tk
import ttkbootstrap as ttk
from dataclasses import dataclass
import datetime


def get_text_of_widget(widget: tk.Widget):
    if isinstance(widget, (tk.Entry, ttk.Combobox)):
        return widget.get()
    elif isinstance(widget, ttk.ScrolledText):
        return widget.get(1.0, ttk.END)
    elif isinstance(widget, (tk.Label, tk.Button)):
        return widget.cget("text")
    else:
        raise TypeError("The object has to be of type tk.Label, tk.Entry or tk.Button or inherit from them")


@dataclass
class WidgetReference:
    widget: tk.Widget
    text_has_changed: asyncio.Event = asyncio.Event()
    old_text_value: str = ""
    last_time_text_has_changed: datetime.datetime = datetime.datetime.now()

"""!
@brief Registry solely used for robot testing library

The widgets are available in a static directory of this class. 
This would be bad practice for normal code, because we have global state.
However for our robot testing library it is necessary, so that we can access the widgets easily.

You have to enable the registry with @ref WidgetRegistry.set_up, 
before you register widgets.
"""
class WidgetRegistry:
    _widget_registry: Dict[str, WidgetReference] = {}
    _enabled = False
    _polling_task: Optional[asyncio.Task] = None

    @staticmethod
    def register_widget(widget: tk.Widget, widget_name: str, parent_widget_name: Optional[str] = None):
        if WidgetRegistry._enabled:
            key = (parent_widget_name + "." + widget_name) if parent_widget_name else widget_name
            WidgetRegistry._widget_registry[key] = WidgetReference(widget)

    @staticmethod
    def is_widget_registered(full_widget_name: str) -> bool:
        return full_widget_name in WidgetRegistry._widget_registry

    @staticmethod
    def get_widget(full_widget_name: str) -> tk.Widget:
        return WidgetRegistry._widget_registry[full_widget_name].widget

    @staticmethod
    async def wait_for_widget_to_change(full_widget_name: str):
        try:
            start_time = datetime.datetime.now()
            ref = WidgetRegistry._widget_registry[full_widget_name]

            await ref.text_has_changed.wait()
            if ref.last_time_text_has_changed < start_time:
                ref.text_has_changed.clear()
                await ref.text_has_changed.wait()
                
        except asyncio.CancelledError:
            return

    @staticmethod
    def set_up():
        WidgetRegistry._enabled = True
        WidgetRegistry._polling_task = asyncio.create_task(WidgetRegistry._polling_worker())

    @staticmethod
    async def clean_up():
        if WidgetRegistry._polling_task and WidgetRegistry._polling_task.cancel():
            await WidgetRegistry._polling_task

    @staticmethod
    def _poll_updates():
        for ref in WidgetRegistry._widget_registry.values():
            current_text = get_text_of_widget(ref.widget)
            if current_text != ref.old_text_value:
                ref.last_time_text_has_changed = datetime.datetime.now()
                ref.old_text_value = current_text
                ref.text_has_changed.set()

    @staticmethod
    async def _polling_worker():
        try:
            while True:
                await asyncio.sleep(0.1)
                WidgetRegistry._poll_updates()
        except asyncio.CancelledError:
            pass
