import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame

from soniccontrol import const
from soniccontrol import soniccontrol_logger as logger
from soniccontrol.interfaces.view import TabView


class Notebook(ttk.Notebook):
    def __init__(self, master: ttk.Window, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self._images_on: bool = False
        self._titles_on: bool = False

    def add_tabs(self, tabs: list[TabView], keep_tabs: bool = False, **kwargs) -> None:
        if not keep_tabs:
            for tab in self.tabs():
                self.forget(tab)
        for tab in tabs:
            self.add(
                tab,
                text=tab.tab_title if self._titles_on else "",
                image=tab.image if self._images_on else None,
                compound=ttk.TOP if self._images_on else ttk.RIGHT,
            )

    def configure_tabs(
        self, show_titles: bool = False, show_images: bool = False
    ) -> None:
        for tab in self.tabs():
            self.tab(
                tab,
                text=tab.tab_title if show_titles else "",
                image=tab.image if show_images else None,
                compound=ttk.TOP if show_images else ttk.RIGHT,
            )
