import tkinter as tk
import tkinter.ttk as ttk
import ttkbootstrap as ttkb

class ScriptingTab(ttk.Frame):
    
    @property
    def parent(self):
        return self._parent
    
    @property
    def sonicamp(self):
        return self._sonicamp
    
    @property
    def serial(self):
        return self._serial    
    
    #TODO: Eh klar, was hier das problem ist
    def __init__(self, parent, serial, sonicamp, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        
        self._parent = parent
        self._serial = serial
        self._sonicamp = sonicamp
        
        self.prev_task = tk.StringVar().set('Idle')
        self.current_task = tk.StringVar().set('Idle')
        
        self.button_frame = ttk.Frame(self)
        
        self.start_script_btn = ttk.Button(
            self.button_frame,
            text='Run',
            style='success.TButton',
            width=11,
            image=self.parent.root.play_img,
            compound=tk.RIGHT,
            command=self.read_file
        )
        self.start_script_btn.pack(side=tk.TOP, padx=5, pady=5)#grid(row=0, column=0, padx=5, pady=5)
        
        self.load_script_btn = ttk.Button(
            self.button_frame,
            text='Open script file',
            style='',
            width=15,
            command=self.load_file,
        )
        self.load_script_btn.pack(side=tk.TOP, padx=5, pady=5)#grid(row=1, column=0, padx=5, pady=5)
        
        self.save_script_btn = ttk.Button(
            self.button_frame,
            text='Save script file',
            style='',
            width=15,
            command=self.save_file
        )
        self.save_script_btn.pack(side=tk.TOP, padx=5, pady=5)#grid(row=2, column=0, padx=5, pady=5)
        
        self.save_log_btn = ttk.Button(
            self.button_frame,
            text='Specify logfile path',
            style='',
            width=15,
            command=self.open_logfile
        )
        self.save_log_btn.pack(side=tk.TOP, padx=5, pady=5)#grid(row=3, column=0, padx=5, pady=5)
        
        self.sequence_status = ttkb.Floodgauge(
            self.button_frame,
            font=self.parent.root.qtype12,
            length=160,
            mode=ttkb.INDETERMINATE,
            orient=ttkb.HORIZONTAL,
            bootstyle=ttkb.DARK,
            text=self.current_task
        )
        self.sequence_status.pack(side=tk.LEFT, padx=5, pady=30)
        
        self.button_frame.pack(anchor=tk.N, side=tk.LEFT, padx=5, pady=5)
        
        self.scripting_frame = ttk.Labelframe(
            self,
            text='Script Editor',
            padding=(5,5,5,5)
        )
        
        self.scripttext = tk.Text(
            self.scripting_frame,
            autoseparators=False,
            background='white',
            setgrid=False,
            width=35,
            padx=5,
            pady=5,
            font=("Consolas", 12)
        )
        self.scripttext.grid(row=0, column=0, columnspan=2)

        _text = '''Enter Tasks here...'''
        self.scripttext.insert(0.0, _text)
        
        self.scrollbar = ttk.Scrollbar(
            self.scripting_frame,
            orient='vertical',
            command=self.scripttext.yview
        )        
        self.scripttext.configure(yscrollcommand=self.scrollbar.set)
        
        self.show_log_console = ttk.Button(
            self.scripting_frame,
            text='Show log console',
            command=self.show_console
        )
        self.show_log_console.grid(row=1, column=0, padx=5, pady=5)
        
        self.script_guide_btn = ttk.Button(
            self.scripting_frame,
            text='Scripting Guide',
            style='',
            command=lambda e: ScriptingGuide(self.parent.root, self.scripttext)
        )
        self.script_guide_btn.grid(row=1, column=1, padx=5, pady=5)
        
        self.scripting_frame.pack(anchor=tk.N ,side=tk.RIGHT ,padx=5, pady=5, expand=True, fill=tk.X)
        
        
        
        self.task_frame = ttk.Frame(self)
        self.static_prevtask_label = ttk.Label(
            self.task_frame,
            font=self.parent.root.arial12,
            text='Previous Task:'
        )
        self.static_prevtask_label.grid(row=0, column=0)
        
        self.prev_task_label = ttk.Label(
            self.task_frame,
            font=self.parent.root.arial12,
            textvariable=self.prev_task,
        )
        self.prev_task_label.grid(row=1, column=0)
        
        
        self.static_curtask_label = ttk.Label(
            self.task_frame,
            font=self.parent.root.arial12,
            text='Current Task:'
        )
        self.static_curtask_label.grid(row=0, column=1)
        
        self.cur_task_label = ttk.Label(
            self.task_frame,
            font=self.parent.root.arial12,
            textvariable=self.current_task
        )
        self.cur_task_label.grid(row=1, column=1)
        
        self.task_frame.pack(side=tk.BOTTOM, padx=10, pady=10)
        
        self.script_progressbar = ttk.Progressbar(
            self,
            orient='horizontal',
            mode='indeterminate'
        )
        self.script_progressbar.pack(side=tk.BOTTOM, padx=10, pady=10)
        
        
        self.config(height=200, width=200)
        self.parent.add(self, text='Scripting', image=self.parent.root.script_img, compound=tk.TOP)
        
    def show_console(self):
        pass
    
    def load_file(self):
        pass
    
    def save_file(self):
        pass
    
    def open_logfile(self):
        pass
    
    def close_file(self):
        self.start_script_btn.configure(
            text='Run',
            style='success.TButton',
            image=self.parent.root.play_img,
            command=self.read_file
        )
    
    def read_file(self):
        self.start_script_btn.configure(
            text='Stop',
            style='danger.TButton',
            image=self.parent.root.pause_img,
            command=self.close_file
        )
    
    
    
    
class ScriptingGuide(tk.Toplevel):
    
    def __init__(self, root, *args, **kwargs):
        tk.Toplevel.__init__(self, root, *args, **kwargs)
        pass
    
