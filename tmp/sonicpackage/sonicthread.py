import re
import threading, time

class SonicAgent(threading.Thread):
    
    @property
    def _run(self):
        return self.run
    
    @property
    def serial(self):
        return self._serial
    
    def __init__(self, serial, *args, **kwargs):
        threading.Thread.__init__(self, target=self._run, *args, **kwargs)
        
        self._serial = serial
        
        #flag to pause thread
        self.paused = False
        
        self.pause_cond = threading.Condition(threading.Lock())
        
    
    def run(self):
        while True:
            with self.pause_cond:
                while self.paused:
                    print('Ich bin hier')
                    self.pause_cond.wait()
                
                #thread should not try to do something if paused
                #not paused
                if self.serial.is_connected:
                    raw_data = self.serial.send_message('-', flush=True)
                    list_data = raw_data.split('-')
                    status = [int(statuspart) for statuspart in list_data]
                    if len(status) > 1:
                        self.serial.queue.put(status)
                
                else:
                    self.pause_cond.wait()
    
    
    def pause(self):
        self.paused = True
        # If in sleep, we acquire immediately, otherwise we wait for thread
        # to release condition. In race, worker will still see self.paused
        # and begin waiting until it's set back to False
        self.pause_cond.acquire()
        
        
    def resume(self):
        self.paused = False
        # Notify so thread will wake after lock released
        self.pause_cond.notify()
        # Now release the lock
        self.pause_cond.release()
                
                
            
