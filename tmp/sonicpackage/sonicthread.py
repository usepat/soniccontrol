import threading, time

class SonicAgent(threading.Thread):
    def __init__(self, sonicamp, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.sonicamp = sonicamp
        
        #flag to pause thread
        self.paused = False
        
        self.pause_cond = threading.Condition(threading.Lock())
        
    
    def run(self):
        while True:
            with self.pause_cond:
                while self.paused:
                    self.pause_cond.wait()
                
                #thread should not try to do something if paused
                #not paused
                if self.sonicamp.is_connected:
                    raw_data = self.sonicamp.send_message('-')
                    list_data = raw_data.split('-')
                    status = [int(statuspart) for statuspart in raw_data]
                    if len(status) > 1:
                        self.sonicamp.queue.put(status)
                
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
                
                
            
