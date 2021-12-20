import tkinter as tk
import tkinter.ttk as ttk
import ttkbootstrap as ttkb

class InfoTab(ttk.Frame):
    
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        parent.add(self, text='Info', image=parent.root.info_img, compound=tk.TOP)