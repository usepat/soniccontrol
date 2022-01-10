import tkinter as tk
import tkinter.ttk as ttk
import ttkbootstrap as ttkb

import tkinter.scrolledtext as st
import time 

class InfoTab(ttk.Frame):
    
    infotext = (
        "Welcome to soniccontrol, a light-weight application to\n" 
        "control sonicamp systems over the serial interface. \n"
        "For help, click the \"Manual\" button below\n"
        "\n"
        "(c) usePAT G.m.b.H\n"
    )
    
    @property
    def parent(self):
        return self._parent
    
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        
        self._parent = parent
        
        self.soniccontrol_logo_frame = ttk.Frame(self)
        self.soniccontrol_logo1 = ttk.Label(
            self.soniccontrol_logo_frame,
            text = self.parent.sonicamp.info['type'][:5],
            padding=(10,0,0,10),
            font = "QTypeOT-CondLight 30")
        self.soniccontrol_logo1.grid(row=0, column=0)
        
        self.soniccontrol_logo2 = ttk.Label(
            self.soniccontrol_logo_frame,
            text = 'control',
            padding=(0,0,0,10),
            font = "QTypeOT-CondBook 30 bold")
        self.soniccontrol_logo2.grid(row=0, column=1)
        
        self.soniccontrol_logo_frame.pack(padx=20, pady=20)
        
        self.info_label = ttk.Label(
            self,
            text=InfoTab.infotext
        )
        self.info_label.pack()
        
        self.controlframe = ttk.Frame(self)
        self.manual_btn = ttk.Button(
            self.controlframe,
            text='Manual',
            command=self.open_manual,
        )
        self.manual_btn.grid(row=0, column=0, padx=5, pady=10)
        
        self.dev_btn = ttk.Button(
            self.controlframe,
            text='I\'m a developer...',
            command=self.serial_monitor,
            style='outline.TButton'
        )
        self.dev_btn.grid(row=0, column=1, padx=5, pady=10)
        
        self.controlframe.pack()
        
        parent.add(self, text='Info', image=parent.root.info_img, compound=tk.TOP)
        
    
    def open_manual(self):
        pass
    
    
    def serial_monitor(self):
        if self.parent.root.winfo_width() == 540:
            self.parent.root.geometry("1080x900")
            self.serial_monitor = SerialMonitor(self.parent.root)
            self.serial_monitor.grid(row=0, column=1, padx=5, pady=5)
            
        else:
            self.parent.root.geometry("540x900")
            self.serial_monitor.grid_forget()
            

class SerialMonitor(ttk.Frame):
    #TODO: Das funktioniert noch immer nicht, schaus da an
    @property
    def root(self):
        return self._root
    
    def __init__(self, root, *args, **kwargs):
        ttk.Frame.__init__(self, root, *args, **kwargs)
        
        self._root = root
        
        self.grid_propagate(0)
        self.root.grid_propagate(0)
        
        self.configure(
            height=10,
            width=10,
            # style='primary.TFrame'
        )
        
        self.text_array = [
            "Type <help> to output the command-cheatsheet!",
            "Type <help> to output the command-cheatsheet!"]
        
        self.command_history = []
        self.index_history = -1
        
        self.output_frame = ttk.LabelFrame(self, text='OUTPUT', height=10, width=10)
        self.output_text = ttk.Label(
            self.output_frame,
            font=("Consolas",12), 
            state='normal',
            style="primary.TLabel"
        )
        self.output_text.pack(
            anchor='center',
            expand=True,
            fill=tk.BOTH, 
            padx=10, 
            pady=10
        )
        self.inittext = f"{self.root.serial.send_message('?', 'block')}"                                                                                # For the initialazation text from the microcontroller
        self.text_array.append(self.inittext)
        
        self.output_text['text'] = '\n'.join(self.text_array)
        
        self.output_frame.pack(
            anchor=tk.N, 
            padx=10, 
            pady=10, 
            side=tk.TOP, 
            expand=True, 
            fill=tk.BOTH)
        
        self.input_field = ttk.LabelFrame(
            self, 
            text='INPUT', 
            # font=("QTypeOT-CondMedium", 12),
            style="primary.TLabelframe")
        
        self.command_field = ttk.Entry(self.input_field, font=("Consolas", 12))
        self.command_field.pack(anchor='s', padx=10, pady=10, fill='x', expand=True, side='left')
        
        self.command_field.bind('<Return>', self.send_command)
        self.command_field.bind('<Up>', self.cmd_history_up)
        self.command_field.bind('<Down>', self.cmd_history_down)
        
        self.send_button = ttk.Button(self.input_field, text='Send')
        self.send_button.pack(anchor='s', padx=10, pady=10, side='right')
        self.send_button.bind('<Button-1>', self.send_command)
        
        self.input_field.pack(anchor='s',fill='x', padx='10', pady='10', side='bottom')

    
    def send_command(self, event):
        self.command, self.commandlen = self.command_field.get(), len(self.command_field.get())  # Getting the Command, and the Legnth of it
        self.command_history.insert(0, self.command)                                            # Storing the Command in the History List
        self.index_history = -1                                                                 # Reseting the History Index, because a command was just sent
        
        # Internal Commands
        if self.command == "clear":
           self.output_text.delete('1.0', tk.END)
        elif self.command == "exit":
           self.destroy()
        elif self.command == "help":
           self.output_text.insert(tk.END, f'>>> {self.command}')
           self.help()
        else: # External Commands (Sent to the microcontroller)
           reply = self.root.serial.send_message(self.command, 'block')
           self.text_array.append(reply)
           self.output_text['text'] = '\n'.join(self.text_array)
    
        self.command_field.delete(0, tk.END)    # Deleting the Input for new commands
            
    def cmd_history_up(self, event):
       if self.index_history != len(self.command_history) - 1:
          self.index_history += 1
          self.command_field.delete(0, tk.END)
          self.command_field.insert(0, self.command_history[self.index_history])
         
    def cmd_history_down(self, event):
        if self.index_history != -1:
           self.index_history -= 1
           self.command_field.delete(0, tk.END)
           self.command_field.insert(0, self.command_history[self.index_history])
        else:
           self.command_field.delete(0, tk.END)
            
    def help(self):
         # Help Page, that can be accessed by typing <help> into the command line
        self.helptext = '''
Welcome to the Help Page for SonicAmp Systems!
There are a variety  of commands to control your SonicAmp
under you liking.  Typically, a  command that sets up the 
SonicAmp System starts with an <!>, whereas commands that
start  with a  <?> ask  the  System  about  something and 
outputs this data.

Here is a list for all commands:

   COMMAND:          DESCRIPTION:
   !SERIAL           Set your SonicAmp to the serial mode
   !f=<Frequency>    Sets the frequency you want to operate on
   !g=<Gain>         Sets the Gain to your liking
   !cur1=<mAmpere>   Sets the current of the 1st Interface
   !cur2=<mAmpere>   Sets the current of the 2nd Interface
   !KHZ              Sets the Frequency range to KHz
   !MHZ              Sets the Frequency range to MHz
   !ON               Starts the output of the signal
   !OFF              Ends the Output of the Signal, Auto 
                     and Wipe
   !WIPE             [WIPE ONLY] Starts the wiping process 
                     with indefinite cycles
   !WIPE=<Cycles>    [WIPE ONLY] Starts the wiping process 
                     with definite cycles
   !prot=<Protocol>  Sets the protocol of your liking
   !rang=<Frequency> Sets the frequency range for protocols
   !step=<Range>     Sets the step range for protocols
   !sing=<Seconds>   Sets the time, the Signal should be 
                     turned
                     on during protocols
   !paus=<Seconds>   Sets the time, the Signal shoudl be 
                     turned off during protocols
   !AUTO             Starts the Auto mode
   !atf1=<Frequency> Sets the Frequency for the 1st protocol
   !atf2=<Frequency> Sets the Frequency for the 2nd protocol
   !atf3=<Frequency> Sets the Frequency for the 3rd protocol
   !tust=<Hertz>     Sets the tuning steps in Hz
   !tutm=<mseconds>  Sets the tuning pause in milliseconds
   !scst=<Hertz>     Sets the scaning steps in Hz    
   
   ?                 Prints information on the progress State
   ?info             Prints information on the software
   ?type             Prints the type of the SonicAmp System
   ?freq             Prints the current frequency
   ?gain             Prints the current gain
   ?temp             Prints the current temperature of the 
                     PT100 element
   ?tpcb             Prints the current temperature in the 
                     case
   ?cur1             Prints the Current of the 1st Interface                     
   ?cur2             Prints the Current of the 2nd Interface
   ?sens             Prints the values of the measurement chip
   ?prot             Lists the current protocol
   ?list             Lists all available protocols
   ?atf1             Prints the frequency of the 1st protocol                     
   ?atf2             Prints the frequency of the 2nd protocol                     
   ?atf3             Prints the frequency of the 3rd protocol
   ?pval             Prints values used for the protocol\n\n'''
        self.output_text.insert(tk.END, self.helptext)