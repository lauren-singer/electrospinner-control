'''
Purpose:

Collect data from sensor driver
Calculate duty cycle
Make list
Export recent values to sensorgui
'''
from HumiditySensors.DHT_Reader import DHT_Reader
import RPi.GPIO as GPIO
import time
import csv
from tkFileDialog import asksaveasfilename

class SensorAdapter():
	def __init__(self):
		self.dht = DHT_Reader(4)
		self.dht.read_sensor()
		self.dht.start_read_loop()
		
		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)
		GPIO.setup(20,GPIO.OUT)
		
		self.p = GPIO.PWM(20,0.5)
		self.p.start(0)
		
		self.dht_tot = []
		self.datalist = {}
		
		self.timein = time.time()
		
		for name in self.dht.data_names()[0:len(self.dht.data_names())]:
			self.datalist[name] = []

	def save_data(self):
		try:
			filename = asksaveasfilename()
			data_file = open(filename + '.csv', "wb")
			writer = csv.writer(data_file)
			writer.writerow(['Time', 'Temperature', 'Humidity', 'Duty Cycle'])
			writer.writerow(['Start Time: ',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.timein))])
			for i in range(0,len(self.datalist['time'])):
				writer.writerow([self.datalist['time'][i],self.datalist['temperature'][i],self.datalist['humidity'][i],self.datalist['duty cycle'][i]])
			print('Saved')
		except TypeError:
			print('???????????????????????????????????????? ok')
			
	def collect_data(self,dc):
		# grab tth data from sensordriver
		# call in GUI while specifying duty cycle
		if self.dht.last_read_value()[2] < 100:
			self.datalist['time'].append(self.dht.last_read_value()[0])
			self.datalist['temperature'].append(self.dht.last_read_value()[1])
			self.datalist['humidity'].append(self.dht.last_read_value()[2])
			self.datalist['duty cycle'].append(dc)
			
			self.dht_tot.append(self.dht.last_read_value())
			print(self.dht.last_read_value())
			return (self.datalist['time'][-1],self.datalist['temperature'][-1],self.datalist['humidity'][-1])
	
	def calculate_dutycycle(self):
		self.dutycycle = int(round(100 - self.dht.last_read_value()[2]))
		return self.dutycycle
	
	def set_dutycycle(self,dc):
		try:
			self.p.ChangeDutyCycle(dc)
		except ValueError:
			print("that's definitely not a valid value")
	
	def quit_plot(self):
		self.p.stop()
		GPIO.cleanup()
			
