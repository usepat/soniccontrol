from __future__ import annotations

import tkinter as tk
import tkinter.ttk as ttk

from typing import TYPE_CHECKING
from tkinter import TclError

if TYPE_CHECKING:
    from soniccontrol.core import Root

from sonicpackage import SonicWipeDuty
from soniccontrol.hometab import HomeTabCatch, HomeTabWipe, HometabDutyWipe
from soniccontrol.scriptingtab import ScriptingTab
from soniccontrol.connectiontab import ConnectionTab
from soniccontrol.infotab import InfoTab
from soniccontrol.helpers import logger



class ScNotebook(ttk.Notebook):

    @property
    def root(self) -> Root:
        return self._root

    def __init__(self, parent: ttk.Frame, root: Root, *args, **kwargs) -> None:
        """ Notebook object """
        super().__init__(parent, *args, **kwargs)
        self._root: Root = root
        self.config(height=560, width=540)
        self['style'] = 'light.TNotebook'
        
        self.hometab: HomeTabCatch = HomeTabCatch(self, self.root, name='hometabcatch')
        self.hometabwipe: HomeTabWipe = HomeTabWipe(self, self.root, name='hometabwipe')
        self.hometabdutywipe: HometabDutyWipe = HometabDutyWipe(self, self.root)
        self.scriptingtab: ScriptingTab = ScriptingTab(self, self.root)
        self.connectiontab: ConnectionTab = ConnectionTab(self, self.root)
        self.infotab: InfoTab = InfoTab(self, self.root)
        logger.info("Notebook initialized object")
        
    def attach_data(self) -> None:
        """Attaches data to the notebookmenue and its children"""
        
        for child in self.children.values():
            child.attach_data()
    
    def _publish(self) -> None:
        """publishes default children of the notebook"""
        self.add(self.hometab, state=tk.NORMAL, text="Home", image=self.root.home_img, compound=tk.TOP)
        self.add(self.hometabwipe, state=tk.HIDDEN,text="Home", image=self.root.home_img, compound=tk.TOP)
        self.add(self.hometabdutywipe, state=tk.HIDDEN,text="Home", image=self.root.home_img, compound=tk.TOP)
        self.add(self.scriptingtab, text="Scripting", image=self.root.script_img, compound=tk.TOP)
        self.add(self.connectiontab, text="Connection", image=self.root.connection_img, compound=tk.TOP)
        self.add(self.infotab, text="Info", image=self.root.info_img, compound=tk.TOP)
    
    def publish_for_catch(self) -> None:
        """ Builds children and displayes menue for a soniccatch """
        self._publish()
        self.reorder_tabs()
        self.forget(self.hometabwipe)
        self.forget(self.hometabdutywipe)
        self.select(self.connectiontab)
        self.enable_children()
        self.connectiontab.attach_data()
        self.publish_children()
        self.pack(padx=5, pady=5)
        
    def publish_for_wipe(self) -> None:
        """ Builds children and displayes menue for a sonicwipe """
        self._publish()
        self.reorder_tabs()
        self.forget(self.hometab)
        self.forget(self.hometabdutywipe)
        self.select(self.connectiontab)
        self.enable_children()
        self.connectiontab.attach_data()
        self.publish_children()
        self.pack(padx=5, pady=5)
        
    def publish_for_dutywipe(self) -> None:
        
        self._publish()
        self.reorder_tabs()
        self.forget(self.hometab)
        self.forget(self.hometabwipe)
        self.select(self.connectiontab)
        self.enable_children()
        self.connectiontab.attach_data()
        self.publish_children()
        self.pack(padx=5, pady=5)
    
    def publish_disconnected(self) -> None:
        """Publishes children in the case that there is no connection"""
        self.config(height=850)
        self._publish()
        self.forget(self.hometabwipe)
        self.forget(self.hometabdutywipe)
        self.select(self.connectiontab)
        self.connectiontab.abolish_data()
        self.publish_children()
        self.disable_children(self.connectiontab)
        self.pack(padx=5, pady=5)
    
    def reorder_tabs(self) -> None:
        """Just a function for making sure, that the tabs are ordered right"""
        self.config(height=560)
        
        if self.root.sonicamp.type_ == 'soniccatch':
            self.hometabwipe.forget()
            self.hometabdutywipe.forget()
            self.insert(0, self.hometab)
        
        elif self.root.sonicamp.type_ == 'sonicwipe' and not isinstance(self.root.sonicamp, SonicWipeDuty):
            self.hometab.forget()
            self.hometabdutywipe.forget()
            self.insert(0, self.hometabwipe)
        
        else:
            self.hometab.forget()
            self.hometabwipe.forget()
            self.insert(0, self.hometabdutywipe)
        
        self.insert(1, self.scriptingtab)
        self.insert(2, self.connectiontab)
        self.insert(3, self.infotab)
    
    def publish_children(self) -> None:
        """ Publishes children """
        for child in self.children.values():
            child.publish()
                
    def disable_children(self, focused_child: ttk.Frame) -> None:
        """ Disables childen and selects connection tab (case: not connected)"""
        for child in self.children.values():
            
            try:
                if child != focused_child:
                    self.tab(child, state=tk.DISABLED)    
            
            except Exception as e:
                logger.info(f"{e}")                
        
        self.select(focused_child)
    
    def enable_children(self) -> None:
        """ Enables all children for use """
        for child in self.children.values():
            
            try:
                self.tab(child, state=tk.NORMAL)
            
            except TclError:
                # logger.info("Something went wrong in enabling children")
                pass