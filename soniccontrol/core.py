import tkinter as tk
import tkinter.ttk as ttk
import ttkbootstrap as ttkb
from tkinter import font
from ttkbootstrap import Style
from PIL import ImageTk

from helpers import resize_img

class Root(tk.Tk):
    """
    The class Root defines the whole GUI application named soniccontrol. 
    It composites all the tkinter objects of the window.
    """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(self, *args, **kwargs)

        # setting up root window, configurations
        self.geometry("540x900")
        self.minsize(540, 900)
        self.maxsize(1080,900)
        self.wm_title('SonicControl')
        style = Style(theme="sandstone") 

        # default font in GUI and custom Fonts
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family='Arial', size=12) 
        self.option_add("*Font", default_font)

        self.arial12: font.Font = font.Font(
            family="Arial", 
            size=12, 
            weight=tk.font.BOLD)
        
        self.qtype12: font.Font = font.Font(
            family="QTypeOT-CondMedium", 
            size=12, 
            weight=tk.font.BOLD)

        # Defining images
        # Uses custom resize funtion in helpers file
        self.refresh_img: object = ImageTk.PhotoImage(resize_img('sonicpackage//pictures//refresh_icon.png', (20, 20)))
        self.home_img: object = ImageTk.PhotoImage(resize_img('sonicpackage//pictures//home_icon.png', (30, 30)))
        self.script_img: object = ImageTk.PhotoImage(resize_img('sonicpackage//pictures//script_icon.png', (30, 30)))
        self.connection_img: object = ImageTk.PhotoImage(resize_img('sonicpackage//pictures//connection_icon.png', (30, 30)))
        self.info_img: object = ImageTk.PhotoImage(resize_img('sonicpackage//pictures//info_icon.png', (30, 30)))
        self.play_img: object = ImageTk.PhotoImage(resize_img('sonicpackage//pictures//play_icon.png', (30, 30)))
        self.pause_img: object = ImageTk.PhotoImage(resize_img('sonicpackage//pictures//pause_icon.png', (30, 30)))
        self.wave_bg: object = ImageTk.PhotoImage(resize_img('sonicpackage//pictures//wave_bg.png', (540,440)))
        self.graph_img: object = ImageTk.PhotoImage(resize_img('sonicpackage//pictures//graph.png', (100,100)))
        self.led_green_img: object = ImageTk.PhotoImage(resize_img('sonicpackage//pictures//led_green.png', (35,35)))
        self.led_red_img: object = ImageTk.PhotoImage(resize_img('sonicpackage//pictures//led_red.png', (35,35)))
        
        
