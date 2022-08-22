from __future__ import annotations

import tkinter as tk
import tkinter.ttk as ttk

from typing import TYPE_CHECKING
from tkinter import TclError

if TYPE_CHECKING:
    from soniccontrol.core import Root

from soniccontrol.hometab import (
    Hometab,
    HometabCatch,
    HometabWipe,
    HometabDutyWipe,
    HometabOldCatch,
    HometabOldWipe,
)
from soniccontrol.scriptingtab import ScriptingTab
from soniccontrol.connectiontab import ConnectionTab
from soniccontrol.infotab import InfoTab
from soniccontrol.helpers import logger




###########################################################################
#### SonicContorl Notebook Menue - Composits all the tabs from the GUI ####
###########################################################################

class ScNotebook(ttk.Notebook):
    """
    ScNotebook is a class that defines the ttk.Notebook
    in the Tkinter GUI SonicControl. The most important
    aspect is that it has methods, that change the
    appearence of the Notebook based on the connection
    to the existing/ non-existing sonicamp.

    Furthermore, it adapts it's HomeTab dynamically based
    on the information, that of the sonicamp. By Default
    the hometab is the HomeTabCatch(), that is initialized
    even if there is no connection, because it is in a
    disabled state either way

    Inheritance:
        ttk (tkinter.ttk.Notebook): The ttk.Notebook class
    """

    @property
    def root(self) -> Root:
        return self._root

    def __init__(self, parent: ttk.Frame, root: Root, *args, **kwargs) -> None:

        super().__init__(parent, *args, **kwargs)
        self._root: Root = root
        self.config(height=560, width=540)
        self["style"] = "light.TNotebook"

        self.hometab: Hometab = Hometab(self, self.root)
        self.scriptingtab: ScriptingTab = ScriptingTab(self, self.root)
        self.connectiontab: ConnectionTab = ConnectionTab(self, self.root)
        self.infotab: InfoTab = InfoTab(self, self.root)

    def attach_data(self) -> None:
        """
        Attaches data to the notebookmenue and its children
        """
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
        self.config(height=560)
        self._add_children()
        self.enable_children()
        self.connectiontab.attach_data()
        self._after_publish()

    def _after_publish(self) -> None:
        """
        Internal method that does the needed work for publishing
        the children of ScNotebook
        """
        self.reorder_tabs()
        self.publish_children()
        self.select(self.connectiontab)
        self.pack(padx=5, pady=5)

    def publish_for_old_catch(self) -> None:
        """
        Builds children and displayes menue for a soniccatch
        """
        self.hometab.destroy()
        self.hometab: Hometab = HometabOldCatch(self, self.root)

        self._publish()

    def publish_for_old_wipe(self) -> None:
        """
        Builds children and displayes menue for a sonicwipe
        """
        self.hometab.destroy()
        self.hometab: Hometab = HometabOldWipe(self, self.root)

        self._publish()

    def publish_for_dutywipe(self) -> None:
        """
        Builds children and displayes menue for a sonicwipe 40kHz Duty Cycle amp
        """
        self.hometab.destroy()
        self.hometab: Hometab = HometabDutyWipe(self, self.root)

        self._publish()

    def publish_for_catch(self) -> None:
        """
        Publishing building method for SonicCatch Revision 2.1
        """
        self.hometab.destroy()
        self.hometab: Hometab = HometabCatch(self, self.root)

        self._publish()

    def publish_for_wipe(self) -> None:
        """
        Publishing building method for SonicWipe Revision 2.1
        """
        self.hometab.destroy()
        self.hometab: Hometab = HometabWipe(self, self.root)

        self._publish()

    def publish_disconnected(self) -> None:
        """
        Publishes children in the case that there is no connection
        """
        self.config(height=850)
        self._add_children()
        self.select(self.connectiontab)
        self.connectiontab.abolish_data()
        self.disable_children(self.connectiontab)
        self._after_publish()

    def reorder_tabs(self) -> None:
        """
        Just a function for making sure, that the tabs are ordered right
        """
        self.insert(0, self.hometab)
        self.insert(1, self.scriptingtab)
        self.insert(2, self.connectiontab)
        self.insert(3, self.infotab)

    def publish_children(self) -> None:
        """
        Publishes children
        """
        for child in self.children.values():
            child.publish()

    def disable_children(self, focused_child: ttk.Frame) -> None:
        """
        Disables childen and selects connection tab (case: not connected)
        """
        if not self.root.config_data['dev_mode']:
            for child in self.children.values():

                try:
                    if child != focused_child:
                        self.tab(child, state=tk.DISABLED)

                except Exception as e:
                    logger.info(f"{e}")

        self.select(focused_child)

    def enable_children(self) -> None:
        """Enables all children for use"""
        for child in self.children.values():

            try:
                self.tab(child, state=tk.NORMAL)

            except TclError as e:
                logger.warning(f"{e}")
