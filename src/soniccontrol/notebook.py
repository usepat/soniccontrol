from __future__ import annotations

import typing
import tkinter as tk
import tkinter.ttk as ttk

if typing.TYPE_CHECKING:
    from soniccontrol.core import Root

from soniccontrol.hometab import (
    Hometab,
    HometabCatch,
    HometabWipe,
    HometabWipe40KHZ,
    HometabOldCatch,
    HometabOldWipe,
)

from soniccontrol.scriptingtab import ScriptingTab
from soniccontrol.connectiontab import ConnectionTab
from soniccontrol.infotab import InfoTab
from soniccontrol.helpers import logger


class ScNotebook(ttk.Notebook):
    @property
    def root(self) -> Root:
        return self._root

    def __init__(self, parent: ttk.Frame, root: Root, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self._root: Root = root

        # self.config(height=560, width=540)
        self["style"] = "light.TNotebook"

        self.hometab: Hometab = ttk.Frame()
        self.scriptingtab: ScriptingTab = ttk.Frame()
        self.connectiontab: ConnectionTab = ConnectionTab(self, self.root)
        self.infotab: InfoTab = InfoTab(self, self.root)

        logger.debug("Initialized Notebook")

    def attach_data(self) -> None:
        for child in self.children.values():
            child.attach_data()

    def _add_children(self) -> None:
        """
        publishes default children of the notebook
        """
        self.add(
            self.hometab,
            state=tk.NORMAL,
            text="Home",
            image=self.root.HOME_IMG,
            compound=tk.TOP,
        )
        self.add(
            self.scriptingtab,
            text="Scripting",
            image=self.root.SCRIPT_IMG,
            compound=tk.TOP,
        )
        self.add(
            self.connectiontab,
            text="Connection",
            image=self.root.CONNECTION_IMG,
            compound=tk.TOP,
        )
        self.add(self.infotab, text="Info", image=self.root.INFO_IMG, compound=tk.TOP)

    def _publish(self) -> None:
        # self.config(height=560)
        self._add_children()
        self.enable_children()
        self.connectiontab.attach_data()
        self._after_publish()

    def _after_publish(self) -> None:
        self._reorder_tabs()
        self._publish_children()
        self.select(self.connectiontab)
        self.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)

    def _rescue_or_disconnected(
        self, disconnected: bool = False, rescue: bool = False
    ) -> None:
        assert not (disconnected and rescue)

        self.config(height=850)
        self._add_children()
        self.select(self.connectiontab)

        if disconnected:
            self.connectiontab.abolish_data()
        else:
            self.connectiontab.attach_data(rescue=True)

        self.disable_children(self.connectiontab)
        self.tab(self.infotab, state=tk.NORMAL)
        self._after_publish()

    def abolish_data(self) -> None:
        pass

    def publish_disconnected(self) -> None:
        self._rescue_or_disconnected(disconnected=True)

    def publish_rescue_mode(self) -> None:
        self._rescue_or_disconnected(rescue=True)

    def publish_for_old_catch(self) -> None:
        self.hometab.destroy()
        self.scriptingtab.destroy()
        self.hometab: Hometab = HometabOldCatch(self, self.root)
        self.scriptingtab: ScriptingTab = ScriptingTab(self, self.root)
        self._publish()

    def publish_for_old_wipe(self) -> None:
        self.hometab.destroy()
        self.scriptingtab.destroy()
        self.hometab: Hometab = HometabOldWipe(self, self.root)
        self.scriptingtab: ScriptingTab = ScriptingTab(self, self.root)
        self._publish()

    def publish_for_wipe(self) -> None:
        self.hometab.destroy()
        self.scriptingtab.destroy()
        self.hometab: Hometab = HometabWipe(self, self.root)
        self.scriptingtab: ScriptingTab = ScriptingTab(self, self.root)
        self._publish()

    def publish_for_wipe40khz(self) -> None:
        self.hometab.destroy()
        self.scriptingtab.destroy()
        self.hometab: Hometab = HometabWipe40KHZ(self, self.root)
        self.scriptingtab: ScriptingTab = ScriptingTab(self, self.root)
        self._publish()

    def _reorder_tabs(self) -> None:
        self.insert(0, self.hometab)
        self.insert(1, self.scriptingtab)
        self.insert(2, self.connectiontab)
        self.insert(3, self.infotab)

    def _publish_children(self) -> None:
        for child in self.children.values():
            child.publish()

    def disable_children(self, focused_child: ttk.Frame) -> None:
        for child in self.children.values():
            if child == focused_child:
                continue
            self.tab(child, state=tk.DISABLED)

        self.select(focused_child)

    def enable_children(self) -> None:
        for child in self.children.values():
            self.tab(child, state=tk.NORMAL)


if __name__ == "__main__":
    pass
