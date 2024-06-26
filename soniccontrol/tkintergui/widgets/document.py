from pathlib import Path
from typing import List, Tuple

import attrs
import ttkbootstrap as ttk

from soniccontrol import __version__
from soniccontrol.interfaces.ui_component import UIComponent
from soniccontrol.interfaces.view import View
from soniccontrol.tkintergui.utils.constants import fonts, sizes
from soniccontrol.tkintergui.utils.image_loader import ImageLoader


@attrs.define()
class Text:
    text: str = attrs.field()
    font: str = attrs.field(default=fonts.QTYPE_OT)
    font_size: int = attrs.field(default=fonts.TEXT_SIZE)

@attrs.define()
class Image:
    image_path: Path = attrs.field()
    image_size: Tuple[int, int] = attrs.field()


class Document(UIComponent):
    def __init__(
            self, 
            parent: UIComponent, 
            parent_view: View,
            content: List[str | Text | Image], 
            paragraph_padding: int = sizes.MEDIUM_PADDING,
            wraplength: int = 0
        ) -> None:
        self._view = DocumentView(parent_view, content, paragraph_padding, wraplength)
        super().__init__(parent, self._view)


class DocumentView(View):
    def __init__(
        self,
        master: ttk.tk.Widget,
        content: List[str | Text | Image],
        paragraph_padding: int = sizes.MEDIUM_PADDING,
        wraplength: int = 0,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(master, *args, **kwargs)
        self._master: ttk.tk.Widget = master
        self._wraplength: int = wraplength
        self._paragraph_padding: int = paragraph_padding
        
        for index, element in enumerate(content):
            if isinstance(element, str):
                uielement = ttk.Label(
                    self, 
                    text=element,
                    wraplength=self._wraplength,
                    anchor=ttk.W,
                    justify=ttk.LEFT
                )
            elif isinstance(element, Text):
                uielement = ttk.Label(
                    self, 
                    text=element.text,
                    font=(element.font, element.font_size),
                    wraplength=self._wraplength,
                    anchor=ttk.W,
                    justify=ttk.LEFT
                )
            elif isinstance(element, Image):
                uielement = ttk.Label(
                    self, 
                    text="",
                    wraplength=self._wraplength,
                    anchor=ttk.CENTER,
                    justify=ttk.CENTER,
                    image=ImageLoader.load_image(element.image_path, element.image_size)
                )
            uielement.grid(
                row=index + 1,
                column=0,
                sticky=ttk.EW,
                pady=self._paragraph_padding,
                padx=sizes.LARGE_PADDING,
            )
            self.rowconfigure(index + 1, weight=sizes.DONT_EXPAND)

