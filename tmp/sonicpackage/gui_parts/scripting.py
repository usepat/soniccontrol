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
    
    def __init__(self, parent, sonicamp, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        
        self._parent = parent
        self._sonicamp = sonicamp
        
        self.prev_task = tk.StringVar().set('Idle')
        self.current_task = tk.StringVar().set('Idle')
        
        self.button_frame = ttk.Frame(self)
        self.load_script_btn = ttk.Button(
            self.button_frame,
            text='Load script file',
            style='',
            command=self.load_file,
        )
        
        self.save_script_btn = ttk.Button(
            self.button_frame,
            text='Save script file',
            style='',
            command=self.save_file
        )
        
        self.save_log_btn = ttk.Button(
            self.button_frame,
            text='Save log file to',
            style='',
            command=self.open_logfile
        )
        
        self.script_guide_btn = ttk.Button(
            self.button_frame,
            text='Scripting Guide',
            style='',
            command=lambda e: ScriptingGuide(parent.root, self.scripttext)
        )

        self.stop_script_btn = ttk.Button(
            self.button_frame,
            text='Stop Script',
            style='',
            command=self.close_file
        )
        
        self.start_script_btn = ttk.Button(
            self.button_frame,
            text='Start Script',
            style='',
            command=self.read_file
        )
        
        self.scripting_frame = ttk.Labelframe(
            self,
            height=200,
            width=200,
            text='Script Editor'
        )
        
        self.scripttext = tk.Text(
            self.scripting_frame,
            autoseparators=False,
            background='white',
            setgrid=False,
            width=30,
        )
        _text = '''Enter Tasks here...'''
        self.scripttext.insert(0.0, _text)
        
        self.scrollbar = ttk.Scrollbar(
            self.scripting_frame,
            orient='vertical',
            command=self.scripttext.yview
        )
        
        self.scripttext.configure(yscrollcommand=self.scrollbar.set)
        
        self.task_frame = ttk.Frame(self)
        self.static_prevtask_label = ttk.Label(
            self.task_frame,
            font=parent.root.arial12,
            text='Previous Task:'
        )
        
        self.prev_task_label = ttk.Label(
            self.task_frame,
            font=parent.root.arial12,
            textvariable=self.prev_task,
        )
        
        
        self.static_curtask_label = ttk.Label(
            self.task_frame,
            font=parent.root.arial12,
            text='Current Task:'
        )
        
        self.cur_task_label = ttk.Label(
            self.task_frame,
            font=parent.root.arial12,
            textvariable=self.current_task
        )
        
        
        self.script_progressbar = ttk.Progressbar(
            self,
            orient='horizontal',
            mode='indeterminate'
        )
        
        self.config(height=200, width=200)
        parent.add(self, text='Scripting', image=parent.root.script_img, compound=tk.TOP)
        
    
    def load_file(self):
        pass
    
    def save_file(self):
        pass
    
    def open_logfile(self):
        pass
    
    def close_file(self):
        pass
    
    def read_file(self):
        pass
    
    
    
    
class ScriptingGuide(tk.Toplevel):
    
    def __init__(self, root, *args, **kwargs):
        tk.Toplevel.__init__(self, root, *args, **kwargs)
        pass
    
