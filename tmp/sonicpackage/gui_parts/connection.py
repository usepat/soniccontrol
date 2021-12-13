import tkinter as tk
import tkinter.ttk as ttk
import ttkbootstrap as ttkb

class ConnectionTab(ttk.Frame):
    
    @property
    def parent(self):
        return self._parent
    
    @property
    def sonicamp(self):
        return self._sonicamp
    
    def __init__(self, parent, sonicamp, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        
        self._sonicamp = sonicamp
        self._parent = parent
        self.topframe =TopFrame(self)
        self.botframe = BotFrame(self)

        if sonicamp.is_connected:
            self.connected()
        else:
            self.not_connected()
            
        parent.add(self, state=tk.NORMAL, text='Connection')
        


    def not_connected(self):
        pass


    def connected(self):
        for child in self.children.values():
            child.pack()
            for grandchild in child.children.values():
                grandchild.pack()
                for gandgrandchild in grandchild.children.values():
                    gandgrandchild.pack()
                    


class TopFrame(ttk.Frame):
    
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        
        self.heading_frame = ttk.Frame(self)
        
        self.subtitle = ttk.Label(
            self.heading_frame, 
            text="You are connected to:"
        )
        
        self.heading = ttk.Label(
            self.heading_frame, 
            text = parent.sonicamp.info['type'],
            font = "QTypeOT-CondBook 30 bold",
        )
        
        self.control_frame = ttk.Frame(self)
        self.ports_menue = ttk.OptionMenu(
            self.control_frame,
            parent.parent.root.port,
            parent.sonicamp.device_list[0],
            parent.sonicamp.device_list,
            style = "primary.TOption"
        )
        
        self.connect_button = ttk.Button(
            self.control_frame, 
            text = 'Connect', 
            command = parent.sonicamp.connect_to_port, 
            style = "success.TButton",
            width = 10
        )
        
        self.refresh_button = ttk.Button(
            self.control_frame, 
            text = 'Refresh', 
            command = parent.sonicamp.get_ports, 
            style = "outline.TButton"
        )
        
        self.disconnect_button = ttk.Button(
            self.control_frame, 
            text='Disconnect', 
            command=parent.sonicamp.disconnect, 
            style="danger.TButton", 
            width=10
        )


class BotFrame(ttk.Frame):
    
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        