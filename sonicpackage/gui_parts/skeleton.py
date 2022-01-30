from abc import ABC, abstractclassmethod
import tkinter as tk
import tkinter.ttk as ttk
import ttkbootstrap as ttkb

class SonicFrame(ABC):
    
    @property
    def parent(self) -> object:
        return self._parent
    
    @property
    def root(self) -> object:
        return self._root
    
    @property
    def sonicamp(self) -> object:
        return self._sonicamp
    
    @property
    def serial(self) -> object:
        return self._serial    

    @property
    def frame(self) -> object:
        return self._frame
    
    def __init__(self, parent: object, root: object, serial: object, sonicamp: object) -> None:    
        self._parent: object = parent
        self._root: object = root
        self._serial: object = serial
        self._sonicamp: object = sonicamp
        self._frame: object = ttk.Frame()
    
    def build_for_catch(self) -> None:
        pass

    def build_for_wipe(self) -> None:
        pass
    



