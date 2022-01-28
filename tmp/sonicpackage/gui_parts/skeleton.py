import tkinter.ttk as ttk

class Tab(ttk.Frame):
    
    @property
    def parent(self):
        return self._parent
    
    @property
    def root(self):
        return self._root
    
    @property
    def sonicamp(self):
        return self._sonicamp
    
    @property
    def serial(self):
        return self._serial    
    
    def __init__(self, parent, root, serial, sonicamp, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        
        self._parent = parent
        self._root = root
        self._serial = serial
        self._sonicamp = sonicamp
    
    # @classmethod
    # def for_wipe(cls, parent, root, serial, sonicamp, *args, **kwargs):
    #     obj = cls.__new__(cls)
    #     super(Tab, obj).__init__()

    # @classmethod
    # def for_catch(cls, parent, root, serial, sonicamp, *args, **kwargs):
    #     obj = cls.__new__(cls)
    #     super(Tab, obj).__init__()

        
