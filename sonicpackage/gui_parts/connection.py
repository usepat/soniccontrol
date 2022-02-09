import tkinter as tk
import tkinter.ttk as ttk
import ttkbootstrap as ttkb

from PIL import Image, ImageTk
from gui_parts.skeleton import SonicFrame
from data import Command


class ConnectionTab(SonicFrame, ttk.Frame):
    
    def __init__(self, parent: object, root: object, serial: object, sonicamp: object, *args, **kwargs) -> None:
        SonicFrame.__init__(self, parent, root, serial, sonicamp)
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        
        self.topframe: object = TopFrame(self, root, serial, sonicamp)
        self.botframe: object = BotFrame(self, root, serial, sonicamp)
            
        self.parent.add(self, 
                        state=tk.NORMAL, 
                        text='Connection', 
                        image=self.parent.root.connection_img, 
                        compound=tk.TOP)
        
        for child in self.children.values():
            child.pack()
    
    def build_for_catch(self) -> None:
        pass
    
    def build_for_wipe(self) -> None:
        pass
                    

class TopFrame(SonicFrame, ttk.Frame):
    
    def __init__(self, parent: object, root: object, serial: object, sonicamp: object, *args, **kwargs) -> None:
        SonicFrame.__init__(self, parent, root, serial, sonicamp)
        ttk.Frame.__init__(self, parent, *args, **kwargs)

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
        self.connect_button = ttkb.Button(self.control_frame, width = 10)
        
        self.ports_menue = ttk.Combobox(
            master=self.control_frame,
            textvariable=self.parent.root.port,
            values=self.parent.serial.device_list,
            width=7,
            style = "dark.TCombobox",
            state=tk.READABLE)
        
        self.refresh_button = ttkb.Button(
            self.control_frame, 
            bootstyle="secondary-outline",
            image=self.parent.root.refresh_img, 
            command = self.refresh)
        
        self.subtitle.grid(row=0, column=0, columnspan=2, sticky=tk.S)
        self.heading1.grid(row=1, column=0, columnspan=1, sticky=tk.E)
        self.heading2.grid(row=1, column=1, columnspan=1, sticky=tk.W)
        self.heading_frame.pack(padx=10, pady=20, expand=True)

        self.ports_menue.grid(row=0, column=0, columnspan=2, pady=10, padx=5, sticky=tk.NSEW)        
        self.connect_button.grid(row=0, column=2,columnspan=1, pady=10, padx=5, sticky=tk.NSEW)
        self.refresh_button.grid(row=0, column=3 ,columnspan=1,  pady=10, padx=5, sticky=tk.NSEW)
        self.control_frame.pack(padx=10, pady=20, expand=True)
        
        if self.parent.serial.is_connected:
            self.build4connected()
        else:
            self.build4notconnected()

        #TODO: Eine Tabelle für genaue information


    def refresh(self):
        self.ports_menue['values'] = self.root.serial.get_ports()
    
    
    def build4connected(self):        
        self.subtitle.configure(text="You are connected to:")
        self.heading1.configure(text = self.sonicamp.amp_type[:5])
        self.heading2.configure(text=self.sonicamp.amp_type[5:])
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
        if self.parent.root.port.get() == '-' or self.parent.root.port.get() == '':
            self.parent.serial.auto_connect()
        
        else:
            self.parent.serial.connect_to_port(port=self.root.port.get())
        
        self.root.initialize_amp()
        self.root.sonic_agent.resume()
        self.root.gui_builder.resume()
        self.build4connected()
        
        
    def disconnect(self):
        self.root.sonic_agent.pause()
        self.serial.disconnect()
        # self.root.gui_builder.pause()
        self.build4notconnected()
        
    def build_for_catch(self) -> None:
        pass
    
    def build_for_wipe(self) -> None:
        pass



class BotFrame(SonicFrame, ttk.Frame):
    
    def __init__(self, parent: object, root: object, serial: object, sonicamp: object, *args, **kwargs) -> None:
        SonicFrame.__init__(self, parent, root, serial, sonicamp)
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        
        label_border = ttk.Labelframe(self, text='Firmware' ,style='dark.TLabelframe')
        self.fw_label = ttk.Label(
            label_border,
            text=self.parent.sonicamp.firmware,
            font=('Consolas', 12),
            padding=10,
            style='dark.TLabel')
        self.fw_label.pack()
        label_border.pack(side=tk.BOTTOM, padx=10, pady=20, expand=True)

    def build_for_catch(self) -> None:
        pass
    
    def build_for_wipe(self) -> None:
        pass
        
        