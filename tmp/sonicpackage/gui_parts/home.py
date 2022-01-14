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
        
        # if sonicamp.info['type'] == 'soniccatch':
        #     self.build4catch()
        # elif sonicamp.info['type'] == 'sonicwipe':
        #     self.build4wipe()
        # else:
        #     pass
        
        self.topframe = ttk.LabelFrame(self, text='Manual control')
        self.botframe = ttk.Frame(self)
        
        self.control_frame = ttk.Frame(self.topframe) 
        self.freq_frame = ttk.Label(self.control_frame)
        self.frq_rng_frame = ttk.Label(self.control_frame)
        
        self.frq_spinbox = ttk.Spinbox(
            self.freq_frame,
            from_=self.sonicamp.info.get('frq rng start'),
            increment=100,
            to=self.sonicamp.info.get('frq rng stop'),
            textvariable=self.root.frequency,
            width=16,
            style='dark.TSpinbox',
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
        
        self.khz_button = ttkb.Radiobutton(
            self.frq_rng_frame,
            text='KHz',
            bootstyle='dark-outline-toolbutton',
            width=12,
            command=self.set_khz_mode
        )
        
        self.mhz_button = ttkb.Radiobutton(
            self.frq_rng_frame,
            text='MHz',
            bootstyle='dark-outline-toolbutton',
            width=12,
            command=self.set_mhz_mode
        )
        
        self.set_frq_button = ttk.Button(
            self.control_frame,
            text='Set Frequency',
            command=self.set_frequency,
            bootstyle='dark.TButton',
        )
        
        
        self.sonic_measure_button = ttk.Button(
            self.topframe,
            text='Sonic measure',
            style='dark.TButton',
            image=self.root.graph_img,
            compound=tk.TOP,
            command=lambda e: SonicMeasure(self.parent.root)
        )
        
        
        self.us_on_button = ttk.Button(
            self.botframe,
            text='ON',
            style='success.TButton',
            width=10,
            command=self.turn_us_on
        )
        
        self.us_off_button = ttk.Button(
            self.botframe,
            text='OFF',
            style='danger.TButton',
            width=10,
            command=self.turn_us_off
        )
        
        self.build4catch()
        self.config(height=200, width=200)
        self.parent.add(self, text='Home', image=self.parent.root.home_img, compound=tk.TOP)
    
    
    def build4catch(self):
        self.frq_spinbox.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.scroll_digit.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)
        
        self.khz_button.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.mhz_button.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)
        
        self.freq_frame.pack(side=tk.TOP, expand=True, fill=tk.X)
        self.frq_rng_frame.pack(side=tk.TOP, expand=True, fill=tk.X)
        self.set_frq_button.pack(side=tk.TOP, expand=True, fill=tk.X, padx=10, pady=10)
        
        self.control_frame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.sonic_measure_button.grid(row=0, column=1, padx=20, pady=20, sticky=tk.NSEW)

        self.us_on_button.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.us_off_button.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)

        self.topframe.pack(side=tk.TOP, padx=20, pady=20)
        self.botframe.pack(side=tk.TOP)
    
    def build4wipe(self):
        pass
    
    def set_khz_mode(self):
        pass

    def set_mhz_mode(self):
        pass
    
    def start_wiping(self):
        pass
    
    
    def set_wipemode(self):
        pass
    
    
    def set_frequency(self):
        self.serial.send_message(f"!f={self.root.frequency}")
    
    
    def set_scrolldigit(self):
        pass
    
    
    def turn_us_on(self):
        self.serial.send_message(f"!ON")
    
    def turn_us_off(self):
        pass
    

class SonicMeasure(tk.Toplevel):
    
    def __init__(self, root, *args, **kwargs):
        tk.Toplevel.__init__(self, root, *args, **kwargs)
        pass
    

# self.wipe_runs_spinbox = ttk.Spinbox(
#             self.utilframe,
#             from_ = 10,
#             increment = 5,
#             justify = tk.LEFT,
#             to = 100,
#             textvariable = self.parent.root.wiperuns,
#             validate = None,
#             width = 5,
#             style = 'primary.TButton'   
#         )
        
#         self.wipemode_button = ttk.Button(
#             self.utilframe,
#             text='Infinite Cycles',
#             command=self.set_wipemode
#         )
        
#         self.wipe_progressbar = ttk.Progressbar(
#             self.utilframe,
#             orient=tk.HORIZONTAL,
#             length=50,
#             mode='indeterminate',
#             style=''
#         )
        
#         self.start_wiping_button = ttk.Button(
#             self.utilframe,
#             text='WIPE',
#             command=self.start_wiping,
#             style=''
#         )