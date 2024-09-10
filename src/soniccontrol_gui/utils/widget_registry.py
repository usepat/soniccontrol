import asyncio
from typing import Dict, Optional
import tkinter as tk
from dataclasses import dataclass
import datetime

@dataclass
class WidgetReference:
    widget: tk.Widget
    text_has_changed: asyncio.Event = asyncio.Event()
    old_text_value: str = ""
    last_time_text_has_changed: datetime.datetime = datetime.datetime.now()

"""!
@brief Registry solely used for robot testing library
"""
global_widget_registry: Dict[str, WidgetReference] = {}

def register_widget(widget: tk.Widget, widget_name: str, parent_widget_name: Optional[str] = None):
    key = (parent_widget_name + "." + widget_name) if parent_widget_name else widget_name
    global_widget_registry[key] = WidgetReference(widget)

def get_widget(full_widget_name) -> tk.Widget:
    return global_widget_registry[full_widget_name].widget

async def wait_for_widget_to_change(full_widget_name: str):
    pass
