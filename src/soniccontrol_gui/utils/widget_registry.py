from typing import Dict, Optional
import tkinter as tk

from soniccontrol_gui.view import View

"""!
@brief Registry solely used for robot testing library
"""
global_widget_registry: Dict[str, View | tk.Widget | tk.Variable] = {}

def register_widget(widget: tk.Widget | tk.Variable, widget_name: str, parent_widget_name: Optional[str] = None):
    key = (parent_widget_name + "." + widget_name) if parent_widget_name else widget_name
    global_widget_registry[key] = widget
