import tkinter as tk
import tkinter.ttk as ttk
import ttkbootstrap as ttkb
from ttkbootstrap import Style
from ttkbootstrap.constants import *
from tkinter import font
from PIL import ImageTk, Image
import threading

from sonicpackage.gui_parts.home import HomeTab
from sonicpackage.gui_parts.scripting import ScriptingTab
from sonicpackage.gui_parts.connection import ConnectionTab
from sonicpackage.gui_parts.info import InfoTab
from sonicpackage.utils.img import resize_img
from sonicpackage.connection import SonicAmp
from sonicpackage.sonicthread import SonicAgent


class Root(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        
        self.geometry("540x900")
        self.minsize(540, 900)
        self.maxsize(1080,900)
        self.wm_title('SonicControl')
        style = Style(theme='sandstone')        
        
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family='Arial', size=12) 
        self.option_add("*Font", default_font)

        self.arial12 = font.Font(family='Arial', size=12, weight=font.BOLD)
        self.qtype12 = font.Font(family='QTypeOT-CondMedium', size=12, weight=font.BOLD)
        
        self.refresh_img = ImageTk.PhotoImage(
            resize_img('sonicpackage//pictures//refresh_icon.png', (20, 20)))
        self.home_img = ImageTk.PhotoImage(
            resize_img('sonicpackage//pictures//home_icon.png', (30, 30)))
        self.script_img = ImageTk.PhotoImage(
            resize_img('sonicpackage//pictures//script_icon.png', (30, 30)))
        self.connection_img = ImageTk.PhotoImage(
            resize_img('sonicpackage//pictures//connection_icon.png', (30, 30)))
        self.info_img = ImageTk.PhotoImage(
            resize_img('sonicpackage//pictures//info_icon.png', (30, 30)))
        self.play_img = ImageTk.PhotoImage(
            resize_img('sonicpackage//pictures//play_icon.png', (30, 30)))
        self.pause_img = ImageTk.PhotoImage(
            resize_img('sonicpackage//pictures//pause_icon.png', (30, 30)))

        self.sonicamp = SonicAmp()
        
        self.sonicamp.connect_to_port(auto=True)
        # if self.sonicamp.is_connected:  
        self.sonicamp.get_info()
        
        print(self.sonicamp.device_list)
        print(self.sonicamp.info)
        # else:
        # self.build_window()

        self.port = tk.StringVar(value=f"{self.sonicamp.info['port']}")
        self.wiperuns = tk.StringVar()
        self.frequency = tk.StringVar()
        
        #TODO: KHZ und MHZ synchronisation
        self.frq_mode = 'KHZ'
        # if self.sonicamp.modules['RELAIS'] is True:
        #     self.frq_mode = self.sonicamp.send_message()

        
        self.status_thread = SonicAgent( self.sonicamp, target=SonicAgent.run)
        self.status_thread.daemon = True
        self.status_thread.start()
        
        if not self.sonicamp.is_connected:
            self.status_thread.pause()
        
        self.checkout_amp()
        self.build_window()
    
    
    def checkout_amp(self):
        self.process_incoming()
        if not self.sonicamp.is_connected:
            self.status_thread.pause()
        else:
            pass
        self.after(50, self.checkout_amp)


    def process_incoming(self):
        while self.sonicamp.queue.qsize():
            try:
                status = self.sonicamp.queue.get(0)
                print(self.sonicamp.get_status(status))
                
                if self.sonicamp.info['status']['error'] == 0:
                    self.window_updater(self.sonicamp.info['status'])
                else:
                    self.sonicamp.is_connected = False

            except:
                pass
    
    
    def window_updater(self, update_dict):
        pass
    

    def build_window(self):
        self.notebook = NotebookMenu(self, self.sonicamp)



class GuiBuilder(Root):

    def __init__(self):
        super().__init__()



class NotebookMenu(ttk.Notebook):
    
    @property
    def root(self):
        return self._root
    
    @property
    def sonicamp(self):
        return self._sonicamp
    
    def __init__(self, root, sonicamp, *args, **kwargs):
        ttk.Notebook.__init__(self, root, *args, **kwargs)
        self._root = root
        self._sonicamp = sonicamp
        
        self.config(height=680, width=530)
        
        self.home_tab = HomeTab(self, self.root, self.sonicamp)
        self.script_tab = ScriptingTab(self, self.sonicamp)
        self.connection_tab = ConnectionTab(self, self.root, self.sonicamp)
        self.info_tab = InfoTab(self)
        
        if not sonicamp.is_connected:
            for child in self.children.values():
                if child != self.connection_tab:
                    self.tab(child, state=tk.DISABLED)
                
        self.select(self.connection_tab)
        
        self.publish()


    def publish(self):
        self.grid(row=0, column=0, padx=2.5, pady=2.5)



if __name__ == "__main__":
    gui = GuiBuilder()
    gui.mainloop()
    gui.sonicamp.is_connected = False

        

    
