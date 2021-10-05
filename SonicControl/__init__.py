# Tkinter libraries
import tkinter.ttk as ttk
import tkinter as tk
from ttkthemes import ThemedStyle

root = tk.Tk()
style = ThemedStyle(root)
style.set_theme("breeze")
root.maxsize(540,900)
root.iconbitmap('welle.ico')
root.wm_title('SonicControl')

