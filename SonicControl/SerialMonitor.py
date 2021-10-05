# genereral libraries
import time 
# Tkinter libraries
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.scrolledtext as st
from tkinter import messagebox
from tkinter import *
# PySerial Library
import serial
import serial.tools.list_ports
# Internal libraries
from SonicControl import root


class SerialMonitorWidget(tk.Toplevel):
      def __init__(self, master, ser):
         # Widget configuration
         super().__init__(master = master)   
         self.ser = ser
         self.title('Serial Monitor')
         x = root.winfo_x()
         dx = root.winfo_width()
         y = root.winfo_y()
         self.geometry("%dx%d+%d+%d" % (500, 850, x + dx, y))
         
         self.SMFrame = ttk.Frame(self)
         
         # Setting up the output frame
         self.OutputFrame = ttk.LabelFrame(self.SMFrame)
         self.OutputText = st.ScrolledText(self.OutputFrame, wrap=tk.WORD, height=45, font=("Consolas",10), state='normal') # Configuration for the Output Textwindow
         self.OutputText.pack(anchor='center', expand=True, fill='both', padx=10, pady=10)
         self.inittext = self.ser.read(255).decode("ASCII")                                                                                # For the initialazation text from the microcontroller
         self.OutputText.insert(END, "Type <help> to output the command-cheatsheet!\n")
         self.OutputText.insert(END, "Type <clear> to clear the screen!\n\n")
         self.OutputText.insert(END, self.inittext)                                                                         # Where to put it
         self.OutputFrame.config(text='OUTPUT')#, width='450', height='700')
         self.OutputFrame.pack(anchor='n',fill='both', padx='10', pady='10', side='top')
         
         # Setting up the input frame
         self.InputFrame = ttk.LabelFrame(self.SMFrame)
         self.CommandField = ttk.Entry(self.InputFrame)
         self.CommandField.config()
         self.CommandField.pack(anchor='s', padx=10, pady=10, fill='x', expand=True, side='left')
         # Bindings for features
         self.CommandField.bind('<Return>', self.SendCommand)
         self.CommandField.bind('<Up>', self.CommandHistoryUP)
         self.CommandField.bind('<Down>', self.CommandHistoryDOWN)
         # Variables for the storing of commands and going through them
         self.CommandHistory = []
         self.IndexHistory = -1
         # Send Button
         self.SendButton = ttk.Button(self.InputFrame, text='Send')
         self.SendButton.config()
         self.SendButton.pack(anchor='s', padx=10, pady=10, side='right')
         self.SendButton.bind('<Button-1>', self.SendCommand)
         self.InputFrame.config(text='INPUT')#, width='450', height='100')
         self.InputFrame.pack(anchor='s',fill='x', padx='10', pady='10', side='bottom')
         
         self.SMFrame.pack(fill='both', side='top')
      
      def SendCommand(self, event):
         self.command, self.commandlen = self.CommandField.get(), len(self.CommandField.get())  # Getting the Command, and the Legnth of it
         self.CommandHistory.insert(0, self.command)                                            # Storing the Command in the History List
         self.IndexHistory = -1                                                                 # Reseting the History Index, because a command was just sent
         
         # Internal Commands
         if self.command == "clear":
            self.OutputText.delete('1.0', END)
         elif self.command == "exit":
            self.destroy()
         elif self.command == "help":
            self.OutputText.insert(END, f'>>> {self.command}')
            self.help()
         else: # External Commands (Sent to the microcontroller)
            self.sendMessage(self.command)
            # Slicing the Reply into the Command and the Data that the Arduino has sent
            self.CommandReply, self.DataReply = self.reply[:self.commandlen], self.reply[self.commandlen:]
            self.OutputText.insert(END, f'>>> {self.CommandReply}\n')
            self.OutputText.insert(END, f'{self.DataReply}\n')
            
         self.OutputText.see(END)            # Autoscroll
         self.CommandField.delete(0, END)    # Deleting the Input for new commands
         
         
      def sendMessage(self, message, read = True, flush=False, delay=0.0, wait=0.0):
        if self.ser.is_open:
            if flush == True:
                self.ser.flushInput() 
            self.ser.write(f'{message}\n'.encode())
            time.sleep(delay)
            if read == True:
                self.reply = self.ser.read(255).rstrip().decode('ASCII')
            time.sleep(wait)
        else:
            messagebox.showerror("Error", "No connection is established, please recheck all connections and try to reconnect in the Connection Tab. Make sure the instrument is in Serial Mode.")
            
      def CommandHistoryUP(self, event):
         if self.IndexHistory != len(self.CommandHistory) - 1:
            self.IndexHistory += 1
            self.CommandField.delete(0, END)
            self.CommandField.insert(0, self.CommandHistory[self.IndexHistory])
         
      def CommandHistoryDOWN(self, event):
         if self.IndexHistory != -1:
            self.IndexHistory -= 1
            self.CommandField.delete(0, END)
            self.CommandField.insert(0, self.CommandHistory[self.IndexHistory])
         else:
            self.CommandField.delete(0, END)
            
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
         self.OutputText.insert(END, self.helptext)