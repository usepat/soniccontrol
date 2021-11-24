# Tkinter libraries
import tkinter as tk
import tkinter.ttk as ttk
# PySerial libraries
import serial
import serial.tools.list_ports
# Internal libraries
from SonicControl import root

class FunctionhelperWidget(tk.Toplevel):
    def __init__(self, master, scriptText):
        super().__init__(master = master) 
        self.title('Function Helper')
        x = root.winfo_x()
        dx = root.winfo_width()
        # dy = root.winfo_height()
        y = root.winfo_y()
        self.geometry("%dx%d+%d+%d" % (850, 400, x + dx, y))
        self.scriptText = scriptText
        # tk.Toplevel.__init__(self, master, **kw)
        self.HelperFrame = ttk.Frame(self)
        self.label_1 = ttk.Label(self.HelperFrame)
        self.label_1.config(anchor='w', font='{Bahnschrift} 12 {}', justify='center', text='Command')
        self.label_1.grid(column='0', columnspan='1', padx='20', pady='0', row='1')
        self.label_2 = ttk.Label(self.HelperFrame)
        self.label_2.config(font='{Bahnschrift} 12 {}', text='Arguments')
        self.label_2.grid(column='1', padx='20', row='1')
        self.label_3 = ttk.Label(self.HelperFrame)
        self.label_3.config(font='{Bahnschrift} 12 {}', text='Description')
        self.label_3.grid(column='2', padx='20', row='1')
        
        self.HoldButton = ttk.Button(self.HelperFrame)
        self.HoldButton.config(state='normal', text='hold', command = self.insertHold)
        self.HoldButton.grid(column='0', ipady='0', pady='5', row='2')
        self.label_4 = ttk.Label(self.HelperFrame)
        self.label_4.config(text='[1-100.000] in [seconds]')
        self.label_4.grid(column='1', padx='10', row='2')
        self.label_5 = ttk.Label(self.HelperFrame)
        self.label_5.config(text='Hold the last state for X seconds')
        self.label_5.grid(column='2', padx='10', row='2')
        
        self.FreqButton = ttk.Button(self.HelperFrame)
        self.FreqButton.config(text='frequency', command = self.insertFrequency)
        self.FreqButton.grid(column='0', pady='5', row='3')
        self.label_6 = ttk.Label(self.HelperFrame)
        self.label_6.config(text='[50.000-1.200.000] in [Hz]')
        self.label_6.grid(column='1', row='3')
        self.label_7 = ttk.Label(self.HelperFrame)
        self.label_7.config(text='Change to the indicated frequency in Hz')
        self.label_7.grid(column='2', padx='5', row='3')

        self.OnButton = ttk.Button(self.HelperFrame)
        self.OnButton.config(text='on', command = self.insertOn)
        self.OnButton.grid(column='0', pady='5', row='4')
        self.label_14 = ttk.Label(self.HelperFrame)
        self.label_14.config(text='None')
        self.label_14.grid(column='1', row='4')
        self.label_15 = ttk.Label(self.HelperFrame)
        self.label_15.config(text='Activate US emission')
        self.label_15.grid(column='2', row='4')
        
        self.OffButton = ttk.Button(self.HelperFrame)
        self.OffButton.config(text='off', command = self.insertOff)
        self.OffButton.grid(column='0', pady='5', row='5')
        self.label_16 = ttk.Label(self.HelperFrame)
        self.label_16.config(text='None')
        self.label_16.grid(column='1', row='5')
        self.label_17 = ttk.Label(self.HelperFrame)
        self.label_17.config(text='Deactivate US emission')
        self.label_17.grid(column='2', row='5')
        
        self.StartLoopButton = ttk.Button(self.HelperFrame)
        self.StartLoopButton.config(text='startloop', command = self.insertStartloop)
        self.StartLoopButton.grid(column='0', pady='5', row='6')
        self.label_18 = ttk.Label(self.HelperFrame)
        self.label_18.config(text='[2-10.000] as an [integer]')
        self.label_18.grid(column='1', row='6')
        self.label_19 = ttk.Label(self.HelperFrame)
        self.label_19.config(text='Start a loop for X times')
        self.label_19.grid(column='2', row='6')
        
        self.EndLoopButton = ttk.Button(self.HelperFrame)
        self.EndLoopButton.config(text='endloop', command = self.insertEndloop)
        self.EndLoopButton.grid(column='0', pady='5', row='7')
        self.label_20 = ttk.Label(self.HelperFrame)
        self.label_20.config(text='None')
        self.label_20.grid(column='1', row='7')
        self.label_21 = ttk.Label(self.HelperFrame)
        self.label_21.config(text='End the loop here')
        self.label_21.grid(column='2', row='7')
        
        self.RampButton = ttk.Button(self.HelperFrame)
        self.RampButton.config(text='ramp', command = self.insertRamp)
        self.RampButton.grid(column='0', pady='5', row='8')
        self.label_24 = ttk.Label(self.HelperFrame)
        self.label_24.config(text='start f [Hz], stop f [Hz], step size [Hz], delay [ms]')
        self.label_24.grid(column='1', row='8')
        self.label_23 = ttk.Label(self.HelperFrame)
        self.label_23.config(text='Create a frequency ramp with a start frequency, a stop frequency,\n a step size and a delay between steps')
        self.label_23.grid(column='2', row='8')
        
        # self.AutotuneButton = ttk.Button(self.HelperFrame)
        # self.AutotuneButton.config(text='autotune', command = self.insertAutotune)
        # self.AutotuneButton.grid(column='0', pady='5', row='9')
        # self.label_26 = ttk.Label(self.HelperFrame)
        # self.label_26.config(text='None')
        # self.label_26.grid(column='1', row='9')
        # self.label_25 = ttk.Label(self.HelperFrame)
        # self.label_25.config(text='Start the autotune protocol. This should be followed by "hold"\n commands, otherwise the function will be stopped.')
        # self.label_25.grid(column='2', row='9')
        
        self.label_22 = ttk.Label(self.HelperFrame)
        self.label_22.config(text='To insert a function at the cursor position, click on the respective button', font=('TkDefaultFont', 11, 'bold'))
        self.label_22.grid(column='0', columnspan='3', padx='5', pady='5', row='9')
        self.HelperFrame.config(height='250', width='400')
        self.HelperFrame.pack(side='top')

    def insertHold(self):
        self.scriptText.insert(self.scriptText.index(tk.INSERT), 'hold X\n')
        
    def insertFrequency(self):
        self.scriptText.insert(self.scriptText.index(tk.INSERT), 'frequency XXXXXXXX\n')
        
    def insertOn(self):
        self.scriptText.insert(self.scriptText.index(tk.INSERT), 'on\n')
        
    def insertOff(self):
        self.scriptText.insert(self.scriptText.index(tk.INSERT), 'off\n')
        
    def insertStartloop(self):
        self.scriptText.insert(self.scriptText.index(tk.INSERT), 'startloop X\n')
        
    def insertEndloop(self):
        self.scriptText.insert(self.scriptText.index(tk.INSERT), 'endloop\n')
        
    def insertRamp(self):
        self.scriptText.insert(self.scriptText.index(tk.INSERT), 'ramp XXXXXXX,XXXXXXX,XXXX,XX\n')
    
    def insertAutotune(self):
        self.scriptText.insert(self.scriptText.index(tk.INSERT), 'autotune\n')
        