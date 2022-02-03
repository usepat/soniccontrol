import threading
import queue
import enum
from abc import ABC, abstractclassmethod
import tkinter as tk
from data import Status, Command


class SonicThread(ABC):
    
    @property
    def _run(self):
        return self.run
    
    def __init__(self) -> None:
        self.thread = threading.Thread(target=self._run)

        self.paused: bool = False
        self.pause_cond: object = threading.Condition(threading.Lock())
        self.queue: object = queue.Queue()
        
    @abstractclassmethod
    def run(self) -> None:
        pass
    
    def pause(self):
        self.paused = True
        self.pause_cond.acquire()
        
        
    def resume(self):
        self.paused = False
        self.pause_cond.notify()
        self.pause_cond.release()



class SonicAgent(SonicThread):
    
    @property
    def serial(self):
        return self._serial
    
    def __init__(self, serial: object) -> None:
        SonicThread.__init__(self)
        self._serial: object = serial
        
    
    def run(self) -> None:
        while True:
            with self.pause_cond:
                while self.paused:
                    self.pause_cond.wait()
                
                #thread should not try to do something if paused
                #not paused
                if self.serial.is_connected:
                    try:
                        data_str = self.serial.send_and_get(Command.GET_STATUS)
                        if len(data_str) > 1:
                            self.queue.put(data_str)
                    except:
                        print("Not the value I was looking for")
                
                else:
                    self.pause_cond.wait()


class GuiBuilder(SonicThread):
    
    @property
    def root(self):
        return self._root
    
    def __init__(self, root: object):
        SonicThread.__init__(self)
        self._root: object = root
        
    def run(self):
        while True:
            with self.pause_cond:
                while self.paused:
                    self.pause_cond.wait()
                
                #thread should not try to do something if paused
                #not paused
                print("Going through run...")
                if self.root.serial.is_connected:
                    print("connected...changing values")
                    self.root.sonicamp.connection = "connected"
                    self.root.status_frame.con_status_label.configure(text=self.root.sonicamp.connection,
                                                                      image=self.root.led_green_img)
                    self.root.status_frame.frq_meter["amountused"] = self.root.sonicamp.status.frequency / 1000000
                    self.root.status_frame.gain_meter["amountused"] = self.root.sonicamp.status.gain
            
                    if self.root.sonicamp.status.frequency:
                        print("detected signal, changing values...")
                        self.root.sonicamp.signal = "signal on"
                        self.root.notebook.home_tab.input_frequency.set(self.root.sonicamp.status.frequency)
                        self.root.status_frame.sig_status_label.configure(text=self.root.sonicamp.signal,
                                                                          image=self.root.led_green_img)
                    else:
                        self.root.sonicamp.signal = "signal off"
                        self.root.status_frame.sig_status_label.configure(text=self.root.sonicamp.signal,
                                                                          image=self.root.led_red_img)
                    if self.root.sonicamp.status.error:
                        print("detected error")
                        self.root.sonicamp.error = "critical error"
                        self.root.status_frame.con_status_label.grid_forget()
                        self.root.status_frame.sig_status_label.grid_forget()
                        self.root.status_frame.configure(style="inverse.danger.TFrame")
                        self.root.status_frame.err_status_label.grid(row=0, column=0, columnspan=3, 
                                                                     padx=10, pady=10, sticky=tk.NSEW)

                    else:
                        self.root.sonicamp.error = "everything fine"

                else:
                    print("window updater not connected")
                    # setting all values to None
                    self.root.sonicamp.connection = "not connected"
                    self.root.sonicamp.signal = "signal off"
                    self.root.sonicamp.status = Status(0, 0, 0, 0, 0)

                    self.root.status_frame.con_status_label.configure(text=self.root.sonicamp.connection,
                                                                 image=self.root.led_red_img)
                    self.root.status_frame.sig_status_label.configure(text=self.root.sonicamp.signal,
                                                                 image=self.root.led_red_img)
                    self.root.status_frame.frq_meter["amountused"] = self.root.sonicamp.status.frequency / 1000000
                    self.root.status_frame.gain_meter["amountused"] = self.root.sonicamp.status.gain
