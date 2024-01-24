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
    ) -> str:

        if with_image:
            kwargs.update({
                key: value for key, value in {
                    const.misc.IMAGE: tab.image
                    const.misc.COMPOUND: ttk.TOP,
                }.items() if key not in kwargs
            })

        if with_image:
            if kwargs.get(const.misc.IMAGE) is None:
                kwargs[const.misc.IMAGE] = tab.image
            if kwargs.get(const.misc.COMPOUND) is None:
                kwargs[const.misc.COMPOUND] = ttk.TOP
        else:
            if kwargs.get(const.misc.IMAGE) is not None:
                kwargs.pop(const.misc.IMAGE)
        if with_title:
            if kwargs.get(const.misc.TEXT) is None:
                kwargs[const.misc.TEXT] = tab.tab_title

        kwargs["image"] = (
            tab.image if kwargs.get("image") is None else kwargs.get("image")
        )
        kwargs["compound"] = (
            ttk.TOP if kwargs.get("compound") is None else kwargs.get("compound")
        )
        kwargs["text"] = (
            tab.tab_title if kwargs.get("text") is None else kwargs.get("title")
        )
        return self.add(
            tab.container if isinstance(frame, ScrolledFrame) else tab,
        )

    def add_tabs(
        self,
        tabs: list[TabView],
        with_image: bool = True,
        with_title: bool = True,
        **kwargs
    ) -> None:
        pass
