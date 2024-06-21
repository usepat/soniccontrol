from typing import List
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame, ScrolledText
from soniccontrol.tkintergui.utils.constants import tk_const
from soniccontrol.tkintergui.utils.types import ScriptingGuideCardDataDict
from soniccontrol.tkintergui.widgets.card import Card


class ScriptingGuide(ttk.Toplevel):
    def __init__(self, root: ttk.Window, editor_text: ScrolledText, cards_data: List[ScriptingGuideCardDataDict], *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self._editor_text: ScrolledText = editor_text
        self._scrolled_frame: ScrolledFrame = ScrolledFrame(self)
        self._cards_data: List[ScriptingGuideCardDataDict] = cards_data

        KEYWORD = "keyword"
        EXAMPLE = "example"
        for data in self._cards_data:
            card: Card = Card(
                self._scrolled_frame,
                heading=data[KEYWORD],
                data=dict(list(data.items())[1:]),
                command=lambda _, text=data[EXAMPLE]: self.insert_text(text),
            )
            card.pack(side=ttk.TOP, fill=ttk.X, padx=15, pady=15)
        self._scrolled_frame.pack(side=ttk.TOP, fill=ttk.BOTH, expand=True)
        self.protocol(tk_const.DELETE_WINDOW, self.destroy)

    def insert_text(self, text: str) -> None:
        self._editor_text.insert(self._editor_text.index(ttk.INSERT), f"{text}\n")
