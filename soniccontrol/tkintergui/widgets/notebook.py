from typing import Any

import ttkbootstrap as ttk

from soniccontrol.interfaces.view import TabView


class Notebook(ttk.Notebook):
    def __init__(self, master: ttk.Window | ttk.tk.Widget, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self._images_on: bool = False
        self._titles_on: bool = False

    def add_tab(self, tab: TabView, index: int | None = None, **kwargs) -> None:
        return (
            self.add(
                tab,
                text=tab.tab_title if self._titles_on else "",
                image=tab.image if self._images_on else {},
                compound=ttk.TOP if self._images_on else ttk.RIGHT,
                **kwargs
            )
            if index is None
            else self.insert(
                index,
                tab,
                text=tab.tab_title if self._titles_on else "",
                image=tab.image if self._images_on else {},
                compound=ttk.TOP if self._images_on else ttk.RIGHT,
                **kwargs
            )
        )

    def add_tabs(
        self,
        tabs: list[TabView | tuple[int, TabView]],
        keep_tabs: bool = False,
        show_titles: bool = True,
        show_images: bool = False,
        **kwargs
    ) -> None:
        if not keep_tabs:
            for tab in self.tabs():
                self.forget(tab)
        self._images_on = show_images
        self._titles_on = show_titles
        for tab in tabs:
            self.add_tab(
                tab if isinstance(tab, TabView) else tab[1],
                index=None if isinstance(tab, TabView) else tab[0],
                **kwargs
            )

    def configure_tabs(
        self, show_titles: bool = False, show_images: bool = False
    ) -> None:
        for tab_name in self.tabs():
            tab: Any = self.nametowidget(tab_name)
            self.tab(
                tab,
                text=tab.tab_title if show_titles else "",
                image=tab.image if show_images else None,
                compound=ttk.TOP if show_images else ttk.RIGHT,
            )
        self._images_on = show_images
        self._titles_on = show_titles
