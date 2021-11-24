
import tkinter as tk
from ttkbootstrap import Style
import tkinter.ttk as ttk

root = tk.Tk()

style = Style(theme='sandstone')

root.geometry("1200x640")
root.maxsize(1200, 640)
root.iconbitmap('welle.ico')
root.wm_title('SonicControl')