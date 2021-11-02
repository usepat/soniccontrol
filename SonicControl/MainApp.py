# General libraries
import datetime
import time 
import tkinter as tk
from tkinter import font
import tkinter.ttk as ttk
import tkinter.scrolledtext as st
from tkinter import filedialog
from tkinter import messagebox
from tkinter import *
from PIL import Image, ImageTk
# PySerial Libraries
import serial
import serial.tools.list_ports
# Internal libraries
from SonicControl import root
from SonicControl.FunctionHelper import FunctionhelperWidget
from SonicControl.SerialMonitor import SerialMonitorWidget

class WipeApp:
    def __init__(self, master=None):
        #initialize needed variables
        self.tmp = True
        self.ser=serial.Serial()
        self.listdev=[]
        self.logfilepath = ''
        self.reply = '' #answer from amp
        self.kHzFrequency = tk.StringVar(value = '1000000')
        self.Protocol = StringVar()
        self.ProtocolOptions = ("Chirp", "Square", "Ramp", "Multi frequency", "Custom")
        self.WipeRuns = tk.StringVar(value='100')
        self.scriptstatus = tk.StringVar()
        self.connectionstatus = tk.StringVar()
        self.USStatus = tk.StringVar()
        self.style = ttk.Style()
        # self.style.theme_use('clam')
        
        # Styles to configure
        self.style.configure('WIPE.TButton', font=('Futura Md BT', 22), foreground='#0000FF')
        self.style.configure('USActive.TButton', font=('Futura Md BT', 22), foreground = '#4DAF7C')
        self.style.configure('USInActive.TButton', font=('Futura Md BT', 22), foreground = '#ff8080')
        self.style.configure('bigger.TSpinbox', arrowsize=20)
        self.style.configure('bigger.TMenubutton', arrowsize=20)
        self.style.configure('bar.Horizontal.TProgressbar')
        
        self._filetypes = [('Text', '*.txt'),('All files', '*'),]
        self.red = '#ED2839'
        self.green = '#00AD83'
        
        # build ui
        self.SonicControl = ttk.Frame(master)
        self.notebook_1 = ttk.Notebook(self.SonicControl)
        self.tabManual = ttk.Frame(self.notebook_1)
        
         # Frames
        self.TopFrame = ttk.Frame(self.tabManual)
        self.BottomFrame = ttk.Frame(self.tabManual)
        
        self.WipeFrame = ttk.LabelFrame(self.TopFrame, text='Wiping')
        self.FrqFrame = ttk.LabelFrame(self.TopFrame, text='Frequency')
        
        
        # Wiping Frame
        self.ProtocolMenue = ttk.OptionMenu(self.WipeFrame, self.Protocol, self.ProtocolOptions[0], *self.ProtocolOptions, command=self.setProtocol)
        self.ProtocolMenue.config(style="bigger.TMenubutton")
        self.ProtocolMenue.pack(anchor='center', padx=10, pady=10, fill='x')
        
        self.WipeRunsSpinBox = ttk.Spinbox(self.WipeFrame)
        self.WipeRunsSpinBox.config(from_='10', increment='5', justify='left', to='100', textvariable=self.WipeRuns)
        self.WipeRunsSpinBox.config(validate='none', width='5', font=('TkDefaultFont', 14), style='bigger.TSpinbox')
        self.WipeRunsSpinBox.pack(anchor='center', padx=10, pady=10, fill='x')
        
        self.EndlessWipeRunsButton = ttk.Button(self.WipeFrame)
        self.EndlessWipeRunsButton.config(text='Infinite cycles')
        self.EndlessWipeRunsButton.pack(anchor='center', padx=10, pady=10, fill='x')
        self.EndlessWipeRunsButton.configure(command=self.EndlessWipeRuns)
        
        self.WipeProgressBar = ttk.Progressbar(self.WipeFrame, style='bar.Horizontal.TProgressbar')
        self.WipeProgressBar.config(orient='horizontal', length=50, mode='indeterminate')
        self.WipeProgressBar.pack(anchor='center', padx=10, pady=10, fill='x')
        
        self.StartWipeModeButton = ttk.Button(self.WipeFrame)
        self.StartWipeModeButton.config(text='WIPE', style='WIPE.TButton')
        self.StartWipeModeButton.pack(anchor='center', padx=10, pady=10, fill='x', side='bottom')
        self.StartWipeModeButton.configure(command=self.StartWipeMode)
        
        # Frequency Frame
        self.FreqSpinBox = ttk.Spinbox(self.FrqFrame)
        self.FreqSpinBox.config(from_='50000', increment='100', state='normal', to='1200000',  textvariable = self.kHzFrequency)
        self.FreqSpinBox.config(width='10', font=('TkDefaultFont', 14), style = 'bigger.TSpinbox')
        self.FreqSpinBox.pack(anchor='center', padx=10, pady=10, fill='x')
        self.FreqSpinBox.configure(command=self.setkHzFrequency)
        
        self.ScrollDigitSpinbox = ttk.Spinbox(self.FrqFrame)
        self.ScrollDigitSpinbox.config(from_='1', increment='1', state='normal', to='6')
        self.ScrollDigitSpinbox.config(validate='none', width=5,font=('TkDefaultFont', 14), )#style = 'bigger.TSpinbox')
        self.ScrollDigit = tk.StringVar(value='''3''')
        self.ScrollDigitSpinbox.insert('0', self.ScrollDigit.get())
        self.ScrollDigitSpinbox.pack(anchor='center', padx=10, pady=10, fill='x')
        self.ScrollDigitSpinbox.configure(command=self.setScrollDigit)
        
        self.SetkHzFreqButton = ttk.Button(self.FrqFrame)
        self.SetkHzFreqButton.config(text='Set frequency')
        self.SetkHzFreqButton.pack(anchor='center', padx=10, pady=10, fill='x')
        self.SetkHzFreqButton.configure(command=self.setkHzFrequency)
        
        self.setUSActiveButton = ttk.Button(self.FrqFrame)
        self.setUSActiveButton.config(text='ON', style='USActive.TButton')
        self.setUSActiveButton.pack(anchor='center', padx=10, pady=10, fill='x', side='bottom')
        self.setUSActiveButton.configure(command=self.setUSActive)
        
        
        # packing frames
        self.WipeFrame.pack(anchor='center', padx=10, pady=10, side='left', expand=True, fill='both')
        self.FrqFrame.pack(anchor='center', padx=10, pady=10, side='right', expand=True, fill='both')
        
        
        
        self.SetUSInActiveButton = ttk.Button(self.BottomFrame)
        self.SetUSInActiveButton.config(text='OFF', style = 'USInActive.TButton', width=10)
        self.SetUSInActiveButton.pack(anchor='n', padx=10, pady=10, side='top', fill='x')
        self.SetUSInActiveButton.configure(command=self.SetUSInActive)
        
        
        
        self.OutputFrame = ttk.Labelframe(self.BottomFrame, text='Feedback', width=10)
        self.OutputText = st.ScrolledText(self.OutputFrame, wrap=tk.WORD, height=10, font=("Consolas",10), state='normal')
        self.OutputText.pack(anchor='center', expand=True, fill='both', padx=10, pady=10,)
        self.tabManual.rowconfigure(2, weight=3)
        self.OutputFrame.pack(anchor='center', padx=10, pady=10, side='top', fill='both')
        
        self.TopFrame.pack(anchor='n',  expand=True, side='top', fill='both')
        self.BottomFrame.pack(anchor='s', expand=True, side='bottom', fill='both')
        
        self.tabManual.config(height='200', width='200')
        self.tabManual.pack(side='top')
        
        
        self.notebook_1.add(self.tabManual, padding='0', state='normal', sticky='nsew', text='Manual')
        self.tabScripting = ttk.Frame(self.notebook_1)
        self.ButtonsAuto = ttk.Frame(self.tabScripting)
        self.LoadScriptButton = ttk.Button(self.ButtonsAuto)
        self.LoadScriptButton.config(text='Load Script File')
        self.LoadScriptButton.pack(pady='5', side='top')
        self.LoadScriptButton.configure(command=self.loadFile)
        self.SaveScriptButton = ttk.Button(self.ButtonsAuto)
        self.SaveScriptButton.config(text='Save Script File')
        self.SaveScriptButton.pack(pady='5', side='top')
        self.SaveScriptButton.configure(command=self.saveFile)
        self.SaveLogButton = ttk.Button(self.ButtonsAuto)
        self.SaveLogButton.config(text='Save Log File to')
        self.SaveLogButton.pack(padx='5', pady='5', side='top')
        self.SaveLogButton.configure(command=self.openLogFile)
        self.FunctionHelperButton = ttk.Button(self.ButtonsAuto)
        self.FunctionHelperButton.config(text='Function Helper')
        self.FunctionHelperButton.pack(padx='5', pady='5', side='top')
        self.FunctionHelperButton.bind("<Button>", lambda e: FunctionhelperWidget(master, self.scriptText)) 
        #self.FunctionHelperButton.configure(command=self.openHelperWindow)
        self.StopScriptButton = ttk.Button(self.ButtonsAuto)
        self.StopScriptButton.config(text='Stop Script')
        self.StopScriptButton.pack(padx='5', pady='5', side='bottom')
        self.StopScriptButton['state'] = 'disabled'
        self.StopScriptButton.configure(command=self.closeFile)
        self.StartScriptButton = ttk.Button(self.ButtonsAuto)
        self.StartScriptButton.config(text='Start Script')
        self.StartScriptButton.pack(padx='5', pady='5', side='bottom')
        self.StartScriptButton.configure(command=self.readFile)
        self.ButtonsAuto.config(height='200', width='200')
        self.ButtonsAuto.pack(anchor='w', fill='y', side='left')
        self.ScriptFrame = ttk.Labelframe(self.tabScripting)
        self.scriptText = tk.Text(self.ScriptFrame)
        self.scriptText.config(autoseparators='false', background='white') #height='10') #font='TkDefaultFont', height='10', insertunfocussed='solid'
        self.scriptText.config(setgrid='false', width='30')
        _text_ = '''Enter tasks here...'''
        self.scriptText.insert('0.0', _text_)
        self.scriptText.pack(anchor='nw', expand='true', fill='both', padx='3', pady='3', side='left')
        self.scrollbar = ttk.Scrollbar(self.ScriptFrame, command=self.scriptText.yview)
        self.scrollbar.config(orient='vertical')
        self.scrollbar.pack(anchor='n', expand='false', fill='y', side='left')
        self.scriptText.config(yscrollcommand=self.scrollbar.set)
        self.scriptText.tag_configure("misspelled", foreground="red", underline=True) #Tag for the Spellcheck
        self.scriptText.bind("<space>", self.Spellcheck) #Executes the Spellcheck with the press of space
        self.ScriptFrame.config(height='200', text='Script Editor', width='200')
        self.ScriptFrame.pack(anchor='nw', expand='true', fill='both', padx='3', pady='5', side='top')
        self.ScriptFrame.bind('<1>', self.callback, add='')
        self.framePrevious = ttk.Frame(self.tabScripting)
        self.framePrevious.pack(fill='x')
        self.label_2 = ttk.Label(self.framePrevious)
        self.label_2.config(font='{Futura Md BT} 10 {}', text='Previous task:')
        self.label_2.pack(side='left')
        self.PTaskLabel = ttk.Label(self.framePrevious)
        self.PreviousTask = tk.StringVar('')
        self.PreviousTask.set('Idle')
        self.PTaskLabel.config(font='{Futura Md BT} 10 {}', textvariable=self.PreviousTask)
        self.PTaskLabel.pack(side='top')
        self.label_1 = ttk.Label(self.tabScripting)
        self.label_1.config(font='{Futura Md BT} 12 {}', text='Current task:')
        self.label_1.pack(side='left')
        self.TaskLabel = ttk.Label(self.tabScripting)
        self.CurrentTask = tk.StringVar('')
        self.CurrentTask.set('Idle')
        self.TaskLabel.config(font='{Futura Md BT} 12 {}', textvariable=self.CurrentTask)
        self.TaskLabel.pack(side='top')
        self.ScriptProgressbar = ttk.Progressbar(self.tabScripting)
        self.ScriptProgressbar.config(orient='horizontal', mode='indeterminate')
        self.ScriptProgressbar.pack(anchor='s', fill='x', side='bottom')
        self.tabScripting.config(height='200', width='200')
        self.tabScripting.pack(side='top')
        self.notebook_1.add(self.tabScripting, text='Scripting')
        
        #! Connection Tab
        self.tabConnection = ttk.Frame(self.notebook_1)
        self.COMPortsFrame = ttk.Labelframe(self.tabConnection)
        self.comboB1 = ttk.Combobox(self.COMPortsFrame)
        self.varPort = tk.StringVar()
        self.comboB1.config(textvariable=self.varPort, values=self.listdev, width='10')
        self.comboB1.pack(padx='5', side='left')
        self.RefreshButton = ttk.Button(self.COMPortsFrame)
        self.RefreshButton.config(text='Refresh')
        self.RefreshButton.pack(padx='5', side='left')
        self.RefreshButton.configure(command=self.getPorts)
        self.ConnectButton = ttk.Button(self.COMPortsFrame)
        self.ConnectButton.config(text='Connect Device')
        self.ConnectButton.pack(padx='5', side='top')
        self.ConnectButton.configure(command=self.connectPort)
        self.ClosePortButton = ttk.Button(self.COMPortsFrame)
        self.ClosePortButton.config(text='Close Device')
        self.ClosePortButton.pack(padx='5', pady='5', side='top')
        self.ClosePortButton.configure(command=self.closePorts)
        self.COMPortsFrame.config(height='200', text='SonicAmp COM Port', width='200')
        self.COMPortsFrame.pack(fill='x', padx='10', pady='10', side='top')
        self.FirmwareFrame = ttk.Labelframe(self.tabConnection)
        self.FirmwareInfo = ttk.Label(self.FirmwareFrame)
        self.FirmwareInfoText = tk.StringVar('')
        self.FirmwareInfo.config(text='No SonicAmp connected', textvariable=self.FirmwareInfoText)
        self.FirmwareInfo.pack(padx='10', pady='10', side='top')
        self.FirmwareFrame.config(height='200', text='SonicAmp Firmware Info', width='200')
        self.FirmwareFrame.pack(pady='30', side='top')
        self.FirmwareFrame.pack_propagate(0)
        # Button that opens the Serial Monitor Widget
        self.SerialMonitorButton = ttk.Button(self.tabConnection)
        self.SerialMonitorButton.config(text='Serial Monitor')
        self.SerialMonitorButton.pack(anchor='s', padx=10, pady=10, side='bottom')
        self.SerialMonitorButton.configure(state='disabled')
        self.SerialMonitorButton.bind("<Button>", lambda e: SerialMonitorWidget(master, self.ser))
        self.tabConnection.config(height='200', width='200')
        self.tabConnection.pack(side='top')
        self.notebook_1.add(self.tabConnection, text='Connection')
        
        self.getPorts()
        
        self.tabInfo = ttk.Frame(self.notebook_1)
        self.DisclaimerFrame = ttk.Labelframe(self.tabInfo)
        self.DisclaimerLabel = ttk.Label(self.DisclaimerFrame)
        self.DisclaimerLabel.config(borderwidth='5', font='TkDefaultFont', justify='left', padding='20')
        self.DisclaimerLabel.config(text='''SonicWipeControl v1.1

A lightweight GUI for remote control of sonicwipe over
the serial interface.
Allows automation of processes through the scripting editor.

(c) usePAT GmbH''')
        self.DisclaimerLabel.pack(anchor='center', fill='both', padx='10', pady='10', side='top')
        self.DisclaimerFrame.config(height='200', text='Disclaimer', width='200')
        self.DisclaimerFrame.pack(anchor='center', fill='both', padx='20', pady='20', side='top')
        self.tabInfo.config(height='200', width='200')
        self.tabInfo.pack(side='top')
        self.notebook_1.add(self.tabInfo, text='Info')
        self.notebook_1.config(height='680', width='530')
        self.notebook_1.pack(expand='true', fill='both', side='top')
        self.notebook_1.select(self.tabConnection) #select the connection tab as starting tab
        self.notebook_1.tab(self.tabManual, state='disabled') # let the user only use the Manual and Script tab when Amp is connected
        self.notebook_1.tab(self.tabScripting, state='disabled')
        self.statusframe = ttk.Frame(self.SonicControl)
        self.statusframe.config(height='90', relief='ridge', width='200')
        self.statusframe.pack(fill='both', padx='1', pady='1', side='top')
        self.statusframe.pack_propagate(0)
        self.canvas = tk.Canvas(self.statusframe,)
        self.canvas.pack(fill='both', padx='3', pady='3', side='top')
        self.LEDtextAmp = self.canvas.create_text(85, 20, text="sonicamp Status", anchor='center')
        self.LEDAmp = self.canvas.create_oval(70, 40, 100, 70, fill=self.red, width = 0)
        self.LEDtextUS = self.canvas.create_text(260, 20, text="US Status", anchor='center')
        self.LEDUS = self.canvas.create_oval(245, 40, 275, 70, fill=self.red, width = 0)
        self.LEDtextSeq = self.canvas.create_text(435, 20, text="Sequence Status", anchor='center')
        self.LEDSeq = self.canvas.create_oval(420, 40, 450, 70, fill=self.red, width = 0)
        
        self.USStateLabel = ttk.Label(self.statusframe)
        self.USStateLabel.config(background='#ff8080', justify='center', text='US emission off', textvariable=self.USStatus)
        self.USStateLabel.pack(padx='60', side='left')
        self.USStatus.set('US emission off')
        self.WaveFrame = ttk.Frame(self.SonicControl)
        self.WaveFrame.config(height='37')
        self.WaveFrame.pack(fill='both', padx='1', pady='2', side='top')
        # self.img = ImageTk.PhotoImage(Image.open(r'D:\Christoph\usePAT\technology\software\Python\SonicControl\pygubu\tkinter_wave.png'))  
        # self.img = ImageTk.PhotoImage(Image.open(r'D:\usePAT\technology\software\Python\SonicControl\pygubu\tkinter_wave.png'))
        self.img = ImageTk.PhotoImage(Image.open('tkinter_wave.png'))
        self.WaveLabel = tk.Label(self.WaveFrame, image=self.img, bg = 'white')
        self.WaveLabel.pack(fill='both', side='top')
        self.SonicControl.config(borderwidth='0', height='900', width='540')
        self.SonicControl.pack(side='top')

        # self.setButtonState('MHz') # This should be replaced with a check which state is active and set accordingly
        
        # Main widget
        self.mainwindow = self.SonicControl
        
       
    def setkHzFrequency(self):
        self.sendMessage('!f='+self.kHzFrequency.get()+'\n', read = True)
        
    
    def setProtocol(self, protocol):
        if protocol == "Chirp":
            self.sendMessage("!prot=0")
        elif protocol == "Ramp":
            self.sendMessage("!prot=1")
        elif protocol == "Square":
            self.sendMessage("!prot=2")
        elif protocol == "Multi frequency":
            self.sendMessage("!prot=3")
        elif protocol == "Custom":
            self.sendMessage("!prot=4")
        else:
            messagebox.showerror("There is apparently and error with the values you have given")
    
        
    def EndlessWipeRuns(self):
        state = str(self.WipeRunsSpinBox['state'])
        if state == 'normal':
            self.WipeRunsSpinBox.configure(state='disabled')
            self.EndlessWipeRunsButton.config(text='Set up cycles')
        else:
            self.WipeRunsSpinBox.configure(state='normal')
            self.EndlessWipeRunsButton.config(text='Infinite cycles')


    def StartWipeMode(self):
        self.StartWipeModeButton.configure(state='disabled')
        self.WipeProgressBar.start()
        state = str(self.WipeRunsSpinBox['state'])
        if state == 'normal':
            self.sendMessage(f'!WIPE={self.WipeRunsSpinBox.get()}\n')
        else:
            self.sendMessage('!WIPE\n')
        self.canvas.itemconfig(self.LEDUS, fill=self.green)


    def setUSActive(self):
        self.sendMessage('!ON'+'\n', read = True)
        if self.reply[:len("!ON")] == "!ON":
            self.canvas.itemconfig(self.LEDUS, fill=self.green)
        # else:
        #     messagebox.showerror("Error", "It seems either your device is not connected or it is not in Serial mode! To activate the Serial mode, make sure that the mechanic switch is set on \"External mode\"!")


    def SetUSInActive(self):
        self.StartWipeModeButton.configure(state='normal')
        self.WipeProgressBar.stop()
        self.sendMessage('!OFF'+'\n', read = True)
        self.canvas.itemconfig(self.LEDUS, fill=self.red)


    def setScrollDigit(self):
        self.FreqSpinBox.config(increment=str(10**(int(self.ScrollDigitSpinbox.get())-1)))

### Here the functions for the Script part are starting                                   

 
    def loadFile(self):
        self.filepath = filedialog.askopenfilename(defaultextension='.txt', filetypes=self._filetypes)
        if not self.filepath:
            pass
        else:
            # print(self.filepath)
            with open(self.filepath, 'r') as f:
                self.scriptText.delete('1.0', tk.END)
                self.scriptText.insert(tk.INSERT, f.read())


    def saveFile(self):
        self.filename = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=self._filetypes)
        if not self.filename:
            pass
        else:
            f = open(self.filename, 'w')
            f.write(self.scriptText.get('1.0', 'end'))
            f.close()


    def openLogFile(self):
        self.logfilepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=self._filetypes)
        # print(self.logfilepath)


    def closeFile(self):
        self.run = False
        self.CurrentTask.set('Idle')
        self.PreviousTask.set('Idle')
        self.scriptText.config(state='normal', background='white')
        self.LoadScriptButton.config(state='normal')
        self.SaveScriptButton.config(state='normal')
        self.SaveLogButton.config(state='normal')
        self.StartScriptButton.config(state='normal')
        self.FunctionHelperButton.config(state='normal')
        self.notebook_1.tab(self.tabManual, state='normal')
        self.notebook_1.tab(self.tabConnection, state='normal')
        self.canvas.itemconfig(self.LEDSeq, fill=self.red)
        self.ScriptProgressbar.stop()
        self.sendMessage('!OFF'+'\n', read = False)
        self.StopScriptButton['state'] = 'disabled'


    def readFile(self):
        '''
        Starts the script. First we disable all unnecessary buttons. Then we
        create a list, where every command is parsed with their respective
        arguments and time duration. Loops are flattened. The command list can then be
        iteratively passed to the sonicamp.

        Returns
        -------
        None.

        '''
        # all Buttons are disabled
        self.scriptText.config(state='disabled', background='#d6d6d6')   
        self.LoadScriptButton.config(state='disabled')
        self.SaveScriptButton.config(state='disabled')
        self.SaveLogButton.config(state='disabled')
        self.StartScriptButton.config(state='disabled')
        self.FunctionHelperButton.config(state='disabled')
        self.notebook_1.tab(self.tabManual, state='disabled')
        self.notebook_1.tab(self.tabConnection, state='disabled')
        self.canvas.itemconfig(self.LEDSeq, fill=self.green)
        self.StopScriptButton['state'] = 'normal'
        
        self.run = True
        
        # Check if the user has created a logfile
        try:
            self.logfilehandle=open(self.logfilepath, 'w')
            self.logfilehandle.write("Timestamp"+"\t"+"Datetime"+"\t"+"Action"+"\n")
            self.logfilehandle.close()
            self.startSequence()
        except:
            messagebox.showerror("Error", "No logfile is specified. Please specify a file.")
            self.logfilepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=(("Text file", "*.txt"),))
            if not self.logfilepath:
                self.closeFile()
            else:
                self.logfilehandle=open(self.logfilepath, 'w')
                self.logfilehandle.write("Timestamp"+"\t"+"Datetime"+"\t"+"Action"+"\n")
                self.logfilehandle.close()
                self.startSequence()
            # print(self.logfilepath)
        
        
    def startSequence(self):
        self.Commands = []
        self.Arguments = []
        self.Durations = []
        self.loops = []
        self.loopindex = 0
        commandList = self.scriptText.get('1.0', 'end-1c').splitlines()
        
        #Putting the commands and arguments into seperate lists with the same index.
        self.parseCommands(commandList)   
        # Loop through commands and register every loop, find its beginning and ending index, put those into a nested list
        for i, command in enumerate(self.Commands):
            # the index of the start and argument of the loop - list looks: [[start index, argument] [start index, argument] [...]...]            
            if command == "startloop":
                if self.Arguments[i][0] == 'inf':
                    loopdata = [i, 'inf']
                else:
                    loopdata = [i, int(self.Arguments[i][0])]                       
                self.loops.insert(i, loopdata)
            # If end found, insert the index into a nested list, that indicates the nearest possible start index (Find the correspodent beginning of the loop)
            # list looks: [[start index, argument, end index] [start index, argument, end index] [...] ...]    
            elif command == "endloop":
                self.loops.insert(i, [])
                for loop in reversed(self.loops):
                    if len(loop) == 2:
                        loop.insert(2, i)
                        break
                    else:
                        continue 
            
            elif command == 'hold':
                # insert an empty list every time its not a startloop, to keep the original index
                self.loops.insert(i, [])
                self.Durations.append(float(self.Arguments[i][0]))
            
            elif command == 'ramp':
                self.loops.insert(i, [])
                
                start = int(self.Arguments[i][0])
                stop = int(self.Arguments[i][1])
                step = int(self.Arguments[i][2])
                delay = int(self.Arguments[i][3])
                
                if start > stop:
                    freq_list = list(range(stop, start+step, step))
                else:
                    freq_list = list(range(start, stop+step, step))
                
                self.Durations.append(len(freq_list)*float(delay))                
            
            else: 
                self.loops.insert(i, [])
                self.Durations.append(0.5)
        
        #print(self.loops)
        # MSGBox = messagebox.askokcancel("Info", "The script you are about to run will take "
        #                                    +str(datetime.timedelta(seconds=sum(self.Durations)))+
        #                                    '\n'+'Do you want to continue?')
        
        # if MSGBox == False:
        #     self.closeFile()
        # else:
            
        i = 0
        while i < len(self.Commands) and self.run is True:
            self.ScriptProgressbar.start()
            if self.Commands[i] == 'startloop': 
                # If the Arguments are not 0, go trough the content of the loop and edit the Arguments to remember 
                if self.loops[i][1] != 0 and isinstance(self.loops[i][1], int) :
                    #print(f"found a startloop now only {self.loops[i][1]}-1 cycles")
                    self.loops[i][1] = self.loops[i][1] - 1
                    i = i + 1
                # If it's 0, then there is nothing more to run in that loop, jump to the end and go on with the other commands
                elif self.loops[i][1] == 'inf':
                    i = i + 1
                else:
                    # Jump to the end +1 of course
                    #print(f"Found startloop with 0 arguments, jumping to {self.loops[i][2]}+1")
                    i = self.loops[i][2] + 1
                       
            elif self.Commands[i] == 'endloop':
                # Go through the Loop list, if you find the current index in the end index field, search for the beginning of that loop
                for loop in self.loops:
                    if bool(loop):
                        if loop[2] == i:
                            #print(f"Endloop! Found corresponding start at {loop[0]}, now checking for nested loops...")
                            # Check if there are nested loops in between, if yes -> set Argument to the original Argument
                            for k in range(loop[0]+1,loop[2]):
                                if bool(self.loops[k]):     # Ignoring empty lists
                                    #print(f"Found nested loop at {self.loops[k][0]}, reseting arguments...")
                                    self.loops[k][1] = int(self.Arguments[k][0])
                            # Jump to the Beginning, If loop found
                            i = loop[0]
                        else:
                            continue
                    else:
                        continue    
            # if nothing else, it must be a command. Proceed with command specific processes
            else:
                #print(f"Command: {self.Commands[i]}")
                self.readit(i)
                i = i + 1
        # Close file if everything ends.
        self.ScriptProgressbar.stop()            
        self.closeFile()
            

    def parseCommands(self, commandList):
        # Check if an argument was given, if so append the command to one list, the argument to another with the same index
        for line in commandList:
            if ' ' in line:
                self.Commands.append(line.split(' ')[0])
                self.Arguments.append(line.split(' ')[1].split(','))
            else:
                self.Commands.append(line)
                self.Arguments.append('')
                

    def readit(self, counter):
        self.CurrentTask.set(str(self.Commands[counter])+' '+str(self.Arguments[counter]))
        root.update()
        
        if counter > 0:
            self.PreviousTask.set(str(self.Commands[counter-1])+' '+str(self.Arguments[counter-1]))
            
        self.logfilehandle=open(self.logfilepath, 'a')
        self.logfilehandle.write(str(time.time())+"\t"+time.strftime("%d-%m-%Y %H:%M:%S", time.localtime())+"\t"
                                 +str(self.Commands[counter])+' '+str(self.Arguments[counter])+'\n')
        self.logfilehandle.close()
        
        if self.Commands[counter] == 'frequency':
            self.setFrequency(self.Arguments[counter])
            
        elif self.Commands[counter] == 'ramp':
            self.startRamp(self.Arguments[counter])
            
        elif self.Commands[counter] == 'hold':
            self.now = datetime.datetime.now()
            self.target = self.now+datetime.timedelta(seconds=int(self.Arguments[counter][0]))
            
            while(self.now < self.target):
                time.sleep(0.02)
                self.now = datetime.datetime.now()
                root.update()

        elif self.Commands[counter] == 'on':
            if self.ser.is_open:
                self.sendMessage('!ON\n', delay=0.0)
                self.canvas.itemconfig(self.LEDUS, fill=self.green)
                root.update()
            else:
                messagebox.showerror("Error", "No connection is established, please recheck all connections and try to reconnect in the Connection Tab. Make sure the instrument is in Serial Mode.")
        
        elif self.Commands[counter] == 'off':
            if self.ser.is_open:
                self.sendMessage('!OFF\n', delay=0.0)
                self.canvas.itemconfig(self.LEDUS, fill=self.red)
                root.update()
            else:
                messagebox.showerror("Error", "No connection is established, please recheck all connections and try to reconnect in the Connection Tab. Make sure the instrument is in Serial Mode.")
       
        elif self.Commands[counter] == 'autotune':
            self.sendMessage('!AUTO\n', read = True, wait=0.1)

            
###### Functions needed for scripts
    def setFrequency(self, frequency):
        if self.ser.is_open:
            self.sendMessage('!f='+str(frequency[0])+'\n', read=True)
        else:
            messagebox.showerror("Error", "No connection is established, please recheck all connections and try to reconnect in the Connection Tab. Make sure the instrument is in Serial Mode.")


    def startRamp(self, arglist):
        start = int(arglist[0])
        stop = int(arglist[1])
        step = int(arglist[2])
        delay = int(arglist[3])
        # The following is to distinguish between rising or falling ramps
        if start > stop:
            freq_list = list(range(stop, start+step, step))
            freq_list.sort(reverse=True)
        else:
            freq_list = list(range(start, stop+step, step))
        # print(freq_list)    
        for frequency in freq_list:
            if self.run == 1:
                if self.ser.is_open:
                    self.sendMessage('!f='+str(frequency)+'\n', read=True)
                    self.CurrentTask.set('ramp is now @ '+str(frequency)+' Hz')
                    self.logfilehandle=open(self.logfilepath, 'a')
                    self.logfilehandle.write(str(time.time())+"\t"+time.strftime("%d-%m-%Y %H:%M:%S", time.localtime())+"\t"
                                     +'ramp is now @ '+' '+str(frequency)+'Hz\n')
                    self.logfilehandle.close()
                    self.now = datetime.datetime.now()
                    print(self.now)
                    self.target = self.now+datetime.timedelta(seconds=int(delay))
                    while(self.now < self.target):
                        time.sleep(0.02)
                        self.now = datetime.datetime.now()
                        root.update()
                    print('wait finished @'+str(self.now))
                else:
                    messagebox.showerror("Error", "No connection is established, please recheck all connections and try to reconnect in the Connection Tab. Make sure the instrument is in Serial Mode.")
            else:
                pass


    def callback(self, event=None):
        pass


    def getPorts(self):
        self.listdev=[]
        for self.index,self.port in enumerate(serial.tools.list_ports.comports(),start=0):  
            self.listdev.append(self.port.device)
        # print(self.listdev)
        self.comboB1.config(values=self.listdev)
        


    def connectPort(self):
        if self.varPort.get()=="":
            messagebox.showerror("Error", "No COM Port is selected. Please select the correct COM Port and reconnect.")       
        else:
            self.ser=serial.Serial(self.varPort.get(), 115200, timeout=0.3)
            time.sleep(5)
            self.sendMessage('!SERIAL\n', read = False, flush = True, delay=0.05)
            time.sleep(1)
            self.sendMessage('?info\n', flush = True, delay=0.05)
            # print(self.reply)
            FirmwareText = ''
            # for line in self.reply[1:-1]:
            #     # print(line)
            #     # print(line.decode())
            #     FirmwareText = FirmwareText + str(line.decode())
            FirmwareText = self.DataReply
            # print(FirmwareText)
            self.FirmwareInfoText.set(FirmwareText)
            self.canvas.itemconfig(self.LEDAmp, fill=self.green)
            self.SerialMonitorButton.configure(state='normal')
            self.notebook_1.tab(self.tabManual, state='normal')
            self.notebook_1.tab(self.tabScripting, state='normal')
            # check initial kHz/MHz state
            self.sendMessage('?\n', flush = True, delay=0.05)
                
            
    def closePorts(self):
        self.ser.close()
        time.sleep(0.1)             
        self.canvas.itemconfig(self.LEDAmp, fill=self.red)
        self.notebook_1.tab(self.tabManual, state='disabled')
        self.notebook_1.tab(self.tabScripting, state='disabled')
        self.FirmwareInfoText.set('')
        
        
    def sendMessage(self, message, read = True, flush=False, delay=0.0, wait=0.0):
        if self.ser.is_open:
            # self.ser.flush()
            messageLen = len(message)
            if flush == True:
                self.ser.flushInput() #it works best with this flush
            # print('Command to amp: '+str(message))
            self.ser.write(message.encode())
            time.sleep(delay)
            if read == True:
                self.reply = self.ser.read(255).rstrip().decode()
                self.DataReply = self.reply[messageLen:]
                self.OutputText.insert(END, f'{self.DataReply}\n\n')
                self.OutputText.see(END)
                
                if "Wipe ended!" in self.DataReply:
                    self.StartWipeModeButton.configure(state='normal')
                    self.WipeProgressBar.stop()
                    self.sendMessage('!OFF'+'\n', read = True)
                    self.canvas.itemconfig(self.LEDUS, fill=self.red)
                    
            time.sleep(wait)
        else:
            messagebox.showerror("Error", "No connection is established, please recheck all connections and try to reconnect in the Connection Tab. Make sure the instrument is in Serial Mode.")
        # while self.ser.is_open:
        #     self.OutputText.insert(END, f'{self.reply}')

            
    # A spellcheck for the functions we use
    def Spellcheck(self, event):
        '''Spellcheck the word preceeding the insertion point'''
        index = self.scriptText.search(r'\s', "insert", regexp=True)
        if '1.' in index:
            index ="1.0"
        else:
            index = self.scriptText.index("%s linestart" % index)
        word = self.scriptText.get(index, "insert")
        functions = ['hold', 'frequency', 'on', 'off', 'startloop', 'endloop', 'ramp', 'autotune']
        if word in functions:
            self.scriptText.tag_remove("misspelled", index, "%s+%dc" % (index, len(word)))
        else:
            self.scriptText.tag_add("misspelled", index, "%s+%dc" % (index, len(word)))
        # print('\n')


    def run(self):
        self.mainwindow.mainloop()