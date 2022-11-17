from __future__ import annotations

import time
import tkinter as tk
import tkinter.ttk as ttk
import ttkbootstrap as ttkb

from typing import Union, TYPE_CHECKING
from ttkbootstrap.scrolled import ScrolledFrame
from soniccontrol.sonicamp import SerialConnection, SerialConnectionGUI

if TYPE_CHECKING:
    from soniccontrol.core import Root


class SerialMonitor(ttkb.Frame):

    HELPTEXT: str = """
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
   ?pval             Prints values used for the protocol\n\n"""

    @property
    def root(self) -> Root:
        return self._root

    @property
    def serial(self) -> SerialConnectionGUI:
        return self._serial

    def __init__(self, root: Root, *args, **kwargs) -> None:
        super().__init__(root, *args, **kwargs)
        
        self._root: Root = root
        self._serial: SerialConnectionGUI = root.serial

        self.command_history: list = [""]
        self.index_history: int = 0

        self.output_frame: ttk.Frame = ttk.LabelFrame(self, text='OUTPUT')
        
        self.scrolled_frame: ScrolledFrame = ScrolledFrame(self.output_frame)
        self.scrolled_frame.autohide_scrollbar()
        self.scrolled_frame.enable_scrolling()

        self.input_frame: ttk.LabelFrame = ttk.LabelFrame(self, text='INPUT')
        self.command_field: ttk.Entry = ttk.Entry(self.input_frame, style='dark.TEntry')
        
        self.command_field.bind('<Return>', self.send_command)
        self.command_field.bind('<Up>', self.history_up)
        self.command_field.bind('<Down>', self.history_down)

        self.send_button: ttkb.Button = ttkb.Button(
            self.input_frame,
            text='Send',
            command=self.send_command,
            style='success.TButton',
        )
        
        self.insert_text(self.HELPTEXT)
        self.publish()
        
    def publish(self) -> None:
        self.command_field.pack(anchor=tk.S, padx=10, pady=10, fill=tk.X, expand=True, side=tk.LEFT)
        self.send_button.pack(anchor=tk.S, padx=10, pady=10, side=tk.RIGHT)
        self.scrolled_frame.pack(anchor=tk.N, expand=True, fill=tk.BOTH, padx=10, pady=10, side=tk.TOP)

        self.input_frame.pack(anchor=tk.S, fill=tk.X, side=tk.BOTTOM)
        self.output_frame.pack(anchor=tk.N, expand=True, fill=tk.BOTH, pady=10, side=tk.TOP)

    def send_command(self, event) -> None:
        command: str = self.command_field.get()
        self.command_history.insert(1, command)

        self.insert_text(f">>> {command}")

        if not self.is_internal_command(command=command):
            self.insert_text(f"{self.serial.send_and_get(command)}\n")

        self.scrolled_frame.yview_moveto(1)
        self.command_field.delete(0, tk.END)

    def is_internal_command(self, command: str) -> bool:

        if command == "clear":
            for child in self.scrolled_frame.winfo_children():
                child.destroy()

        elif command == "help":
            self.insert_text(self.HELPTEXT)

        elif command == "exit":
            self.root.publish_serial_monitor()
        
        else:
            return False
        
        return True

    def insert_text(self, text: Union[str, list]) -> None:
        if text is list:
            text = " ".join(text)
        
        ttk.Label(self.scrolled_frame, text=text, font=("Consolas", 10)).pack(
            fill=tk.X, side=tk.TOP, anchor=tk.W
        )
        self.scrolled_frame.update()

    def history_up(self, event) -> None:
        if self.index_history != len(self.command_history) - 1:
            self.index_history += 1
            self.command_field.delete(0, tk.END)
            self.command_field.insert(0, self.command_history[self.index_history])
    
    def history_down(self, event) -> None:
        if self.index_history:
            self.index_history -= 1
            self.command_field.delete(0, tk.END)
            self.command_field.insert(0, self.command_history[self.index_history])


class SerialMonitorCatch(SerialMonitor):

    HELPTEXT: str = """
Welcome to the Help Text for your SonicCatch!
There  are a  variety  of  commands to control your 
SonicCatch under you liking.  Typically, a  command that 
sets up the SonicAmp System starts with an <!>, whereas 
commands that start  with a  <?> ask  the  System  about
something and outputs this data.

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
?pval             Prints values used for the protocol\n\n"""

    def __init__(self, root: Root, *args, **kwargs) -> None:
        super().__init__(root, *args, **kwargs)


class SerialMonitorWipe(SerialMonitor):
    
    HELPTEXT: str = """
Welcome to the Help text for your SonicWipe!
There are a variety of commands to control your SonicWipe
under you liking.  Typically, a  command that sets up the 
SonicWipe  starts  with  an  <!>,  whereas  commands that
start  with a  <?> ask  the  System  about  something and 
outputs this data.

Here is a list for all commands:

COMMAND:          DESCRIPTION:
!SERIAL           Set your SonicWipe to the serial mode
!f=<Frequency>    Sets the frequency you want to operate on
!ON               Starts the output of the signal
!OFF              Ends the Output of the Signal, Auto 
                  and Wipe
!WIPE             Starts the wiping process with indefinite
                  cycles
!WIPE=<Cycles>    Starts the wiping process with definite 
                  cycles
!prot=<Protocol>  Sets the protocol of your liking
?                 Prints information on the progress State
?info             Prints information on the software
?type             Prints the type of the SonicAmp System
?freq             Prints the current frequency
                  PT100 element
?tpcb             Prints the current temperature in the 
                  case
?prot             Lists the current protocol
?list             Lists all available protocols
"""

    def __init__(self, root: Root, *args, **kwargs) -> None:
        super().__init__(root, *args, **kwargs)


class SerialMonitor40KHZ(SerialMonitor):
    
    HELPTEXT: str = """
Welcome to the Help Page for the Serial Monitor!
There are a variety of commands to control your SonicWipe
under you liking.  Typically, a  command that   sets up a 
SonicWipe  starts  with  an  <!>,  whereas  commands that
start  with a  <?> ask  the  System  about  something and 
outputs this data.

Here is a list for all commands:

COMMAND:          DESCRIPTION:
!g=<Gain>         Sets the Gain to your liking
!ON               Starts the output of the signal
!OFF              Ends the Output of the Signal
?info             Prints the version of the Firmware

clear             Clears the screen of the console
help              Prints out this help text
exit              Exits the Serial Monitor"""

    def __init__(self, root: Root, *args, **kwargs) -> None:
        super().__init__(root, *args, **kwargs)

    def send_command(self, event) -> None:
        command: str = self.command_field.get()
        self.command_history.insert(0, command)
        self.insert_text(f">>> {command}")

        if not self.is_internal_command(command=command):
            
            answer: str = self.serial.send_and_get(command)
            
            if answer.isnumeric():
                answer: int = int(answer)
            
                if command == "!ON" and answer == 1:
                    self.insert_text("Wipe signal set to ON")
                    self.root.status_frame.signal_on()

                elif command == "!OFF" and answer == 0:
                    self.insert_text("Wipe signal set to OFF")
                    self.root.status_frame.signal_off()

                elif command[:3] == "!g=" and answer:
                    self.insert_text(f"Gain set to {answer}")
                    self.root.status_frame.change_values(gain=answer)
                    
            else:
                self.insert_text(answer)
                
                if command == "!ON":
                    self.root.status_frame.signal_on()

                elif command == "!OFF":
                    self.root.status_frame.signal_off()

                elif command[:3] == "!g=":
                    self.root.status_frame.change_values(gain=answer)
        
        self.scrolled_frame.yview_moveto(1)
        self.command_field.delete(0, tk.END)












# from __future__ import annotations

# import tkinter as tk
# import tkinter.ttk as ttk
# import ttkbootstrap as ttkb

# from typing import Union, TYPE_CHECKING

# from soniccontrol.sonicamp import SerialConnectionGUI

# if TYPE_CHECKING:
#     from soniccontrol.core import Root


# class SerialMonitor(ttkb.Frame):

#     HELPTEXT: str = """
# Welcome to the Help Page for SonicAmp Systems!
# There are a variety  of commands to control your SonicAmp
# under you liking.  Typically, a  command that sets up the 
# SonicAmp System starts with an <!>, whereas commands that
# start  with a  <?> ask  the  System  about  something and 
# outputs this data.

# Here is a list for all commands:

#    COMMAND:          DESCRIPTION:
#    !SERIAL           Set your SonicAmp to the serial mode
#    !f=<Frequency>    Sets the frequency you want to operate on
#    !g=<Gain>         Sets the Gain to your liking
#    !cur1=<mAmpere>   Sets the current of the 1st Interface
#    !cur2=<mAmpere>   Sets the current of the 2nd Interface
#    !KHZ              Sets the Frequency range to KHz
#    !MHZ              Sets the Frequency range to MHz
#    !ON               Starts the output of the signal
#    !OFF              Ends the Output of the Signal, Auto 
#                      and Wipe
#    !WIPE             [WIPE ONLY] Starts the wiping process 
#                      with indefinite cycles
#    !WIPE=<Cycles>    [WIPE ONLY] Starts the wiping process 
#                      with definite cycles
#    !prot=<Protocol>  Sets the protocol of your liking
#    !rang=<Frequency> Sets the frequency range for protocols
#    !step=<Range>     Sets the step range for protocols
#    !sing=<Seconds>   Sets the time, the Signal should be 
#                      turned
#                      on during protocols
#    !paus=<Seconds>   Sets the time, the Signal shoudl be 
#                      turned off during protocols
#    !AUTO             Starts the Auto mode
#    !atf1=<Frequency> Sets the Frequency for the 1st protocol
#    !atf2=<Frequency> Sets the Frequency for the 2nd protocol
#    !atf3=<Frequency> Sets the Frequency for the 3rd protocol
#    !tust=<Hertz>     Sets the tuning steps in Hz
#    !tutm=<mseconds>  Sets the tuning pause in milliseconds
#    !scst=<Hertz>     Sets the scaning steps in Hz    
   
#    ?                 Prints information on the progress State
#    ?info             Prints information on the software
#    ?type             Prints the type of the SonicAmp System
#    ?freq             Prints the current frequency
#    ?gain             Prints the current gain
#    ?temp             Prints the current temperature of the 
#                      PT100 element
#    ?tpcb             Prints the current temperature in the 
#                      case
#    ?cur1             Prints the Current of the 1st Interface                     
#    ?cur2             Prints the Current of the 2nd Interface
#    ?sens             Prints the values of the measurement chip
#    ?prot             Lists the current protocol
#    ?list             Lists all available protocols
#    ?atf1             Prints the frequency of the 1st protocol                     
#    ?atf2             Prints the frequency of the 2nd protocol                     
#    ?atf3             Prints the frequency of the 3rd protocol
#    ?pval             Prints values used for the protocol\n\n"""

#     @property
#     def root(self) -> Root:
#         return self._root

#     @property
#     def serial(self) -> SerialConnectionGUI:
#         return self._serial

#     def __init__(self, root: Root, *args, **kwargs) -> None:
#         super().__init__(root, *args, **kwargs)
#         self._root: Root = root
#         self._serial: SerialConnectionGUI = root.serial

#         self.command_history: list[str] = []
#         self.index_history: int = -1

#         self.output_frame: ttk.Frame = ttk.LabelFrame(self, text="OUTPUT")

#         container: ttk.Frame = ttk.Frame(self.output_frame)
#         self.canvas: tk.Canvas = tk.Canvas(container)
#         scrollbar: ttk.Scrollbar = ttk.Scrollbar(
#             container, orient=tk.VERTICAL, command=self.canvas.yview
#         )
#         self.scrollable_frame: ttk.Frame = ttk.Frame(self.canvas)

#         self.scrollable_frame.bind(
#             "<Configure>",
#             lambda x: self.canvas.configure(scrollregion=self.canvas.bbox(tk.ALL)),
#         )

#         self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor=tk.NW)
#         self.canvas.configure(yscrollcommand=scrollbar.set)

#         container.pack(
#             anchor=tk.N, expand=True, fill=tk.BOTH, padx=5, pady=5, side=tk.TOP
#         )
#         self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
#         scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

#         self.input_frame: ttk.Frame = ttk.LabelFrame(self, text="INPUT")

#         self.command_field: ttk.Entry = ttk.Entry(self.input_frame, style="dark.TEntry")
#         self.command_field.bind("<Return>", self.send_command)
#         self.command_field.bind("<Up>", self.history_up)
#         self.command_field.bind("<Down>", self.history_down)

#         self.send_button: ttk.Button = ttk.Button(
#             self.input_frame,
#             text="Send",
#             command=self.send_command,
#             style="success.TButton",
#         )
#         self.send_button.bind("<Button-1>", self.send_command)

#         self.command_field.pack(
#             anchor=tk.S, padx=10, pady=10, fill=tk.X, expand=True, side=tk.LEFT
#         )
#         self.send_button.pack(anchor=tk.S, padx=10, pady=10, side=tk.RIGHT)

#         self.input_frame.pack(anchor=tk.S, fill=tk.X, side=tk.BOTTOM)
#         self.output_frame.pack(
#             anchor=tk.N, expand=True, fill=tk.BOTH, pady=10, side=tk.TOP
#         )

#         self.insert_text(self.HELPTEXT)
#         self.output_frame.pack_propagate(False)

#     def send_command(self, event) -> None:
#         """Sends the command written in the input field"""
#         command: str = self.command_field.get()
#         self.command_history.insert(0, command)
#         self.insert_text(f">>> {command}")

#         if not self._internal_command(command=command):
#             self.insert_text(self.serial.send_and_get(command))
        
#         self.canvas.yview_moveto(1)
#         self.command_field.delete(0, tk.END)
        
#     def _internal_command(self, command: str) -> bool:
#         if command == "clear":

#             for child in self.scrollable_frame.children.values():
#                 child.destroy()

#             return True

#         elif command == "help":
#             self.insert_text(SerialMonitor.HELPTEXT)
#             return True

#         elif command == "exit":
#             self.root.publish_serial_monitor()
#             return True

#         else:
#             return False

#     def insert_text(self, text: Union[str, list]) -> None:
#         """Inserts text in the output frame"""
#         if text is list:
#             text = " ".join(text)

#         ttk.Label(self.scrollable_frame, text=text, font=("Consolas", 10)).pack(
#             fill=tk.X, side=tk.TOP, anchor=tk.W
#         )
#         self.canvas.update()

#     def history_up(self, event) -> None:
#         """function to go through the history of commands upwards"""
#         if self.index_history != len(self.command_history) - 1:
#             self.index_history += 1
#             self.command_field.delete(0, tk.END)
#             self.command_field.insert(0, self.command_history[self.index_history])

#     def history_down(self, event) -> None:
#         """function to go through the history of commands downwards"""
#         if self.index_history != -1:
#             self.index_history -= 1
#             self.command_field.delete(0, tk.END)
#             self.command_field.insert(0, self.command_history[self.index_history])

#         else:
#             self.command_field.delete(0, tk.END)
     


# class SerialMonitorCatch(SerialMonitor):
    
#     HELPTEXT: str = """
# Welcome to the Help Text for your SonicCatch!
# There  are a  variety  of  commands to control your 
# SonicCatch under you liking.  Typically, a  command that 
# sets up the SonicAmp System starts with an <!>, whereas 
# commands that start  with a  <?> ask  the  System  about
# something and outputs this data.

# Here is a list for all commands:

# COMMAND:          DESCRIPTION:
# !SERIAL           Set your SonicAmp to the serial mode
# !f=<Frequency>    Sets the frequency you want to operate on
# !g=<Gain>         Sets the Gain to your liking
# !cur1=<mAmpere>   Sets the current of the 1st Interface
# !cur2=<mAmpere>   Sets the current of the 2nd Interface
# !KHZ              Sets the Frequency range to KHz
# !MHZ              Sets the Frequency range to MHz
# !ON               Starts the output of the signal
# !OFF              Ends the Output of the Signal, Auto 
#                   and Wipe
# !rang=<Frequency> Sets the frequency range for protocols
# !step=<Range>     Sets the step range for protocols
# !sing=<Seconds>   Sets the time, the Signal should be 
#                   turned
#                   on during protocols
# !paus=<Seconds>   Sets the time, the Signal shoudl be 
#                   turned off during protocols
# !AUTO             Starts the Auto mode
# !atf1=<Frequency> Sets the Frequency for the 1st protocol
# !atf2=<Frequency> Sets the Frequency for the 2nd protocol
# !atf3=<Frequency> Sets the Frequency for the 3rd protocol
# !tust=<Hertz>     Sets the tuning steps in Hz
# !tutm=<mseconds>  Sets the tuning pause in milliseconds
# !scst=<Hertz>     Sets the scaning steps in Hz    

# ?                 Prints information on the progress State
# ?info             Prints information on the software
# ?type             Prints the type of the SonicAmp System
# ?freq             Prints the current frequency
# ?gain             Prints the current gain
# ?temp             Prints the current temperature of the 
#                   PT100 element
# ?tpcb             Prints the current temperature in the 
#                   case
# ?cur1             Prints the Current of the 1st Interface                     
# ?cur2             Prints the Current of the 2nd Interface
# ?sens             Prints the values of the measurement chip
# ?prot             Lists the current protocol
# ?list             Lists all available protocols
# ?atf1             Prints the frequency of the 1st protocol                     
# ?atf2             Prints the frequency of the 2nd protocol                     
# ?atf3             Prints the frequency of the 3rd protocol
# ?pval             Prints values used for the protocol\n\n"""

#     def __init__(self, root: Root, *args, **kwargs) -> None:
#         super().__init__(root, *args, **kwargs)



# class SerialMonitorWipe(SerialMonitor):
    
#     HELPTEXT: str = """
# Welcome to the Help text for your SonicWipe!
# There are a variety of commands to control your SonicWipe
# under you liking.  Typically, a  command that sets up the 
# SonicWipe  starts  with  an  <!>,  whereas  commands that
# start  with a  <?> ask  the  System  about  something and 
# outputs this data.

# Here is a list for all commands:

# COMMAND:          DESCRIPTION:
# !SERIAL           Set your SonicWipe to the serial mode
# !f=<Frequency>    Sets the frequency you want to operate on
# !ON               Starts the output of the signal
# !OFF              Ends the Output of the Signal, Auto 
#                   and Wipe
# !WIPE             Starts the wiping process with indefinite
#                   cycles
# !WIPE=<Cycles>    Starts the wiping process with definite 
#                   cycles
# !prot=<Protocol>  Sets the protocol of your liking
# ?                 Prints information on the progress State
# ?info             Prints information on the software
# ?type             Prints the type of the SonicAmp System
# ?freq             Prints the current frequency
#                   PT100 element
# ?tpcb             Prints the current temperature in the 
#                   case
# ?prot             Lists the current protocol
# ?list             Lists all available protocols
# """

#     def __init__(self, root: Root, *args, **kwargs) -> None:
#         super().__init__(root, *args, **kwargs)


            
# class SerialMonitor40KHZ(SerialMonitor):
    
#     HELPTEXT: str = """
# Welcome to the Help Page for the Serial Monitor!
# There are a variety of commands to control your SonicWipe
# under you liking.  Typically, a  command that   sets up a 
# SonicWipe  starts  with  an  <!>,  whereas  commands that
# start  with a  <?> ask  the  System  about  something and 
# outputs this data.

# Here is a list for all commands:

# COMMAND:          DESCRIPTION:
# !g=<Gain>         Sets the Gain to your liking
# !ON               Starts the output of the signal
# !OFF              Ends the Output of the Signal
# ?info             Prints the version of the Firmware

# clear             Clears the screen of the console
# help              Prints out this help text
# exit              Exits the Serial Monitor"""
    
#     def __init__(self, root: Root, *args, **kwargs) -> None:
#         super().__init__(root, *args, **kwargs)
        
#     def send_command(self, event) -> None:
#         """
#         Sends the command written in the input field
#         """
#         command: str = self.command_field.get()
#         self.command_history.insert(0, command)
#         self.insert_text(f">>> {command}")

#         if not self._internal_command(command=command):
            
#             answer: str = self.serial.send_and_get(command)
            
#             if answer.isnumeric():
#                 answer: int = int(answer)
            
#                 if command == "!ON" and answer == 1:
#                     self.insert_text("Wipe signal set to ON")
#                     self.root.status_frame.signal_on()

#                 elif command == "!OFF" and answer == 0:
#                     self.insert_text("Wipe signal set to OFF")
#                     self.root.status_frame.signal_off()

#                 elif command[:3] == "!g=" and answer:
#                     self.insert_text(f"Gain set to {answer}")
#                     self.root.status_frame.change_values(gain=answer)
                    
#             else:
#                 self.insert_text(answer)
                
#                 if command == "!ON":
#                     self.root.status_frame.signal_on()

#                 elif command == "!OFF":
#                     self.root.status_frame.signal_off()

#                 elif command[:3] == "!g=":
#                     self.root.status_frame.change_values(gain=answer)
        
#         self.canvas.yview_moveto(1)
#         self.command_field.delete(0, tk.END)
