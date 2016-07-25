import Adafruit_DHT
import threading
import time


class DHT_Reader():
    def __init__(self,pin,sensor=Adafruit_DHT.AM2302):
        self.pin = pin
        self.sensor = sensor
        self.thread = None
        self.continue_loop = False
        self.data = {}
        self.data_list = []
        
    def read_sensor(self):
        humidity, temperature = Adafruit_DHT.read_retry(
              self.sensor,self.pin,
              delay_seconds=0.5)
        read_time = time.time()
        self.data = [read_time,temperature,humidity]
        return self.data
    
    def _read_loop(self):
        while self.continue_loop:
            # take self.data & make it a list of lists
            # append self.read_sensor onto self.data
            self.data = self.read_sensor()
            self.data_list.append(self.data)
            time.sleep(0.5)
            
    def start_read_loop(self):
        self.continue_loop = True
        self.thread = threading.Thread(target=self._read_loop,args=())
        self.thread.start()
    
    def _stop_read_loop(self):
        self.continue_loop = False
    
    def _is_loop_alive(self):
        if self.thread:
            return self.thread.isAlive()
        else:
            return False
         
    def data_names(self):
        return ['time','temperature','humidity','duty cycle']
           
    def last_read_value(self):
        return self.data

    

if __name__ == '__main__':
    dht = DHT_Reader(4)
    dht.read_sensor()
    dht.start_read_loop()

    while True:
        # prints time, temperature, humidity
        print(dht.last_read_value())
        time.sleep(1)


