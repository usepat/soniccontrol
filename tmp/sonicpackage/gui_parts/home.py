import tkinter as tk
import tkinter.ttk as ttk
import ttkbootstrap as ttkb

class HomeTab(ttk.Frame):
    
    @property
    def parent(self):
        return self._parent
    
    @property
    def root(self):
        return self._root
    
    @property
    def sonicamp(self):
        return self._sonicamp    
    
    @property
    def serial(self):
        return self._serial    
    
    def __init__(self, parent, root, serial, sonicamp, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        
        self._parent = parent
        self._root = root
        self._serial = serial
        self._sonicamp = sonicamp
        
        if sonicamp.info['type'] == 'soniccatch':
            self.build4catch()
        elif sonicamp.info['type'] == 'sonicwipe':
            self.build4wipe()
        else:
            pass
        
        self.control_header_frame = ttk.Frame(self)
        self.topframe = ttk.Frame(self)
        self.botframe = ttk.Frame(self)
        
        self.utilframe = ttk.Labelframe(self.topframe)
        
       
        self.frq_mode_button = ttk.Button(
            self.control_header_frame,
            text=self.root.frq_mode,
            style='',
            command=self.set_frq_mode
        )
        
        self.sonic_measure_button = ttk.Button(
            self.control_header_frame,
            text='Sonic measure',
            style='',
            command=lambda e: SonicMeasure(self.parent.root)
        )
        
        self.wipe_runs_spinbox = ttk.Spinbox(
            self.utilframe,
            from_ = 10,
            increment = 5,
            justify = tk.LEFT,
            to = 100,
            textvariable = self.parent.root.wiperuns,
            validate = None,
            width = 5,
            style = 'primary.TButton'   
        )
        
        self.wipemode_button = ttk.Button(
            self.utilframe,
            text='Infinite Cycles',
            command=self.set_wipemode
        )
        
        self.wipe_progressbar = ttk.Progressbar(
            self.utilframe,
            orient=tk.HORIZONTAL,
            length=50,
            mode='indeterminate',
            style=''
        )
        
        self.start_wiping_button = ttk.Button(
            self.utilframe,
            text='WIPE',
            command=self.start_wiping,
            style=''
        )
        
        self.freq_frame = ttk.Labelframe(self.topframe)
        self.frq_spinbox = ttk.Spinbox(
            self.freq_frame,
            from_=50000,
            increment=100,
            to=1200000,
            textvariable=self.root.frequency,
            width=10,
            style='primary.TSpinbox',
            command=self.set_frequency
        )
        
        self.scroll_digit = ttk.Spinbox(
            self.freq_frame,
            from_=1,
            increment=1,
            to=6,
            validate=None,
            width=5,
            style='secondary.TSpinbox',
            command=self.set_scrolldigit
        )
        
        self.set_frq_button = ttk.Button(
            self.freq_frame,
            text='Set Frequency',
            command=self.set_frequency,
            style='',
        )
    
        self.us_on_button = ttk.Button(
            self.freq_frame,
            text='ON',
            style='success.TButton',
            command=self.turn_us_on
        )
        
        self.us_off_button = ttk.Button(
            self.botframe,
            text='OFF',
            style='danger.TButton',
            width=10,
            command=self.turn_us_off
        )
        
        self.config(height=200, width=200)
        self.parent.add(self, text='Home', image=self.parent.root.home_img, compound=tk.TOP)
    
    def build4catch(self):
        pass
    
    def build4wipe(self):
        pass
    
    def set_frq_mode(self):
        pass
    
    def start_wiping(self):
        pass
    
    
    def set_wipemode(self):
        pass
    
    
    def set_frequency(self):
        pass
    
    
    def set_scrolldigit(self):
        pass
    
    
    def turn_us_on(self):
        pass
    
    def turn_us_off(self):
        pass
    

class SonicMeasure(tk.Toplevel):
    
    def __init__(self, root, *args, **kwargs):
        tk.Toplevel.__init__(self, root, *args, **kwargs)
        pass