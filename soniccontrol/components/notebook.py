import ttkbootstrap as ttk
from _typeshed import NoneType
from ttkbootstrap.scrolled import ScrolledFrame

from soniccontrol import const
from soniccontrol.interfaces.view import TabView


class Notebook(ttk.Notebook):
    def __init__(self, master: ttk.Window, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self._images_on: bool = False
        self._titles_on: bool = False

    def add_tab(
        self, tab: TabView, with_image: bool, with_title: bool, **kwargs
    ) -> None:
        kwargs.update(
            {
                key: value
                for key, value in {
                    const.misc.IMAGE: tab.image,
                    const.misc.COMPOUND: ttk.TOP,
                }.items()
                if key not in kwargs
            }
            if with_image
            else {}
        )
        kwargs.update(
            {
                key: value
                for key, value in {const.misc.TEXT: tab.tab_title}.items()
                if key not in kwargs
            }
            if with_title
            else {}
        )
        self.add(tab.container if isinstance(tab, ScrolledFrame) else tab, **kwargs)

    def add_tabs(
        self,
        tabs: list[TabView],
        with_image: bool = True,
        with_title: bool = True,
        **kwargs
    ) -> None:
        for tab in tabs:
            self.add_tab(tab, with_image=with_image, with_title=with_title, **kwargs)
