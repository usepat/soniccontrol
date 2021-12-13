import tkinter as tk
import tkinter.ttk as ttk
import ttkbootstrap as ttkb
from ttkbootstrap import Style
from ttkbootstrap.constants import *
from tkinter import font
from tkinter import *
import threading

from sonicpackage.gui import NotebookMenu#, HomeTab, InfoTab, NotebookMenu, ScriptingTab
from sonicpackage.connection import SonicAmp


class Root(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        
        self.geometry("540x900")
        self.wm_title('SonicControl')
        style = Style(theme='sandstone')
        
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family='Arial', size=12) 
        self.option_add("*Font", default_font)

        self.arial12 = font.Font(family='Arial', size=12, weight=font.BOLD)
        self.qtype12 = font.Font(family='QTypeOT-CondMedium', size=12, weight=font.BOLD)
        
        self.sonicamp = SonicAmp()
        
        self.sonicamp.connect_to_port(auto=True)
        if self.sonicamp.is_connected:  
            self.sonicamp.get_info()
            print(self.sonicamp.info)
        else:
            self.buildwindow()

        self.port = tk.StringVar(value=f"{self.sonicamp.info['port']}")
        self.wiperuns = tk.StringVar()
        self.frequency = tk.StringVar()

        self.status_thread = threading.Thread(target=self.sonicamp.connection_worker)
        self.status_thread.daemon = True
        self.status_thread.start()
        
        self.checkout_amp()
        self.build_window()
    
    
    def checkout_amp(self):
        self.process_incoming()
        if not self.sonicamp.is_connected:
            import sys
            self.status_thread.daemon = False
            sys.exit(1)
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
                    self.status_thread.daemon = False

            except:
                pass
    
    
    def window_updater(self, update_dict):
        pass
    

    def build_window(self):
        self.notebook = NotebookMenu(self)



class GuiBuilder(Root):

    def __init__(self):
        super().__init__()



if __name__ == "__main__":
    gui = GuiBuilder()
    gui.mainloop()
    gui.sonicamp.is_connected = False

        

        
