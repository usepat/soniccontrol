import tkinter as tk
import tkinter.ttk as ttk
import ttkbootstrap as ttkb

from PIL import Image, ImageTk



class ConnectionTab(ttk.Frame):
    
    @property
    def parent(self):
        return self._parent

    @property
    def root(self):
        return self._root
    
    @property
    def sonicamp(self):
        return self._sonicamp
    
    def __init__(self, parent, root, sonicamp, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        
        self._sonicamp = sonicamp
        self._parent = parent
        self._root = root
        self.topframe =TopFrame(self)
        self.botframe = BotFrame(self)

        if sonicamp.is_connected:
            self.connected()
        else:
            self.not_connected()
            
        parent.add(self, state=tk.NORMAL, text='Connection', image=parent.root.connection_img, compound=tk.TOP)
        


    def not_connected(self):
        pass


    def connected(self):
        for child in self.children.values():
            child.pack()
                    


class TopFrame(ttk.Frame):

    @property
    def parent(self):
        return self._parent
    
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self._parent = parent

        self['padding'] = (10,10,10,10)

        #Heading Frame
        self.heading_frame = ttk.Frame(self)
        self.subtitle = ttk.Label(self.heading_frame, padding=(0,10,0,0))
        self.heading1 = ttk.Label(
            self.heading_frame, 
            padding=(10,0,0,10),
            font = "QTypeOT-CondLight 30")
        self.heading2 = ttk.Label(
            self.heading_frame,
            padding=(0,0,10,10),
            font= "QTypeOT-CondBook 30 bold")
        
        self.control_frame = ttk.Frame(self)
        self.connect_button = ttk.Button(self.control_frame, width = 10)
        self.ports_menue = ttk.OptionMenu(
            self.control_frame,
            self.parent.root.port,
            self.parent.sonicamp.device_list[0],
            self.parent.sonicamp.device_list,
            style = "primary.TOption")
        self.refresh_button = ttkb.Button(
            self.control_frame, 
            bootstyle="secondary-outline",
            image=self.parent.root.refresh_img, 
            command = self.parent.sonicamp.get_ports)
        
        self.subtitle.grid(row=0, column=0, columnspan=2, sticky=tk.S)
        self.heading1.grid(row=1, column=0, columnspan=1, sticky=tk.E)
        self.heading2.grid(row=1, column=1, columnspan=1, sticky=tk.W)
        self.heading_frame.pack(pady=10, padx=10)

        self.ports_menue.grid(row=0, column=0, columnspan=2, pady=10, padx=5, sticky=tk.NSEW)        
        self.connect_button.grid(row=0, column=2,columnspan=1, pady=10, padx=5, sticky=tk.NSEW)
        self.refresh_button.grid(row=0, column=3 ,columnspan=1,  pady=10, padx=5, sticky=tk.NSEW)
        self.control_frame.pack(padx=10, pady=10)
        
        if self.parent.sonicamp.is_connected:
            self.build4connected()
        else:
            self.build4notconnected()

        #TODO: Eine Tabelle für genaue information


    def build4connected(self):        
        self.subtitle.configure(text="You are connected to:")
        self.heading1.configure(text = self.parent.sonicamp.info['type'][:5])
        self.heading2.configure(text=self.parent.sonicamp.info['type'][5:])
        self.connect_button.configure( 
            text = 'Disconnect', 
            command = self.disconnect, 
            style = "danger.TButton")


    def build4notconnected(self):
        self.subtitle.configure(text="Please connect to your sonicamp system:")
        self.heading1.configure(text="not ")
        self.heading2.configure(text="connected")
        self.connect_button.configure(
            text="Connect",
            style="success.TButton",
            command=self.connect)
        
    
    def connect(self):
        self.build4connected()
        self.parent.sonicamp.connect_to_port()

    def disconnect(self):
        self.build4notconnected()
        self.parent.sonicamp.disconnect()

class BotFrame(ttk.Frame):
    
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        