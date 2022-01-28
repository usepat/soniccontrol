import queue
import re
import threading, time

from sonicpackage.connection import Command, SerialConnection

class SonicAgent(threading.Thread):
    
    @property
    def _run(self):
        return self.run
    
    @property
    def serial(self):
        return self._serial
    
    def __init__(self, serial, *args, **kwargs):
        threading.Thread.__init__(self, target=self._run, *args, **kwargs)
        
        self._serial: object = serial
        self.paused: bool = False
        self.pause_cond: object = threading.Condition(threading.Lock())
        self.queue = queue.Queue()
        
    
    def run(self):
        while True:
            with self.pause_cond:
                while self.paused:
                    self.pause_cond.wait()
                
                #thread should not try to do something if paused
                #not paused
                if self.serial.is_connected:
                    try:
                        raw_data = self.serial.send_and_get(Command.GET_STATUS)
                        list_data = raw_data.split('-')
                        status = [int(statuspart) for statuspart in list_data]
                        if len(status) > 1:
                            self.queue.put(status)
                    except:
                        print("Not the value I was looking for")
                
                else:
                    self.pause_cond.wait()
    
    
    def pause(self):
        self.paused = True
        self.pause_cond.acquire()
        
        
    def resume(self):
        self.paused = False
        self.pause_cond.notify()
        self.pause_cond.release()