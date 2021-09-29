import tkinter.ttk as ttk
import tkinter as tk
from ttkthemes import ThemedStyle
from PIL import Image, ImageTk



root = tk.Tk()
style = ThemedStyle(root)
style.set_theme("breeze")
root.maxsize(540,900)
root.iconbitmap('SonicControl/welle.ico')
root.wm_title('SonicControl')

#

from SonicControl.MainApp import SonicControlApp
