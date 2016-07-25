'''

'''
from MotorDrivers.a4988 import a4988_Driver
import math
import datetime
import time

class PrintedPump():
	def __init__(self):
		
		self.driver = a4988_Driver()
		
		self.is_motor_running = True
		self.motor_pause = True
		self.motor_direction = True
		
		self.time_now = 0
		self.time_duration = 0
		self.time_list = []
		self.calibration_factor = 1
		self.val_ratio = 1
	
	def pause_adapter(self):
		# called by pause button in gui
		self.motor_pause = self.driver.pause_motor()
		if self.motor_pause is False:
			self.time_duration = self.time_now
			self.time_now = 0
		elif self.motor_pause:
			self.time_initial = time.time()

	def reverse_adapter(self):
		# called by reverse button in gui
		self.motor_direction = self.driver.reverse_motor()
		if self.motor_direction is False:
			self.time_duration = self.time_now
			self.time_now = 0
		elif self.motor_direction:
			self.time_initial = time.time()
	
	def reset_adapter(self):
		self.time_initial = time.time()
		self.time_duration = 0
	
	def calibration(self,setval,expval,reset):
		self.setval = setval
		self.expval = expval
		if reset==0:
			self.calibration_factor = self.setval/self.expval
			self.val_ratio = self.val_ratio*self.calibration_factor
		elif reset==1:
			self.val_ratio = 1
		print self.val_ratio
	
	def return_calval(self):
		return self.val_ratio
	
	def freq_calc(self,flowrate,diameter):
		self.time_initial = time.time()
		
		self.flowrate = flowrate/3600
		self.diameter = diameter
		val_ratio = self.return_calval()

		self.stepsize = self.driver.return_stepsize()
		self.pitch = self.driver.return_pitch()
		
		# calc freq
		self.frequency = float((4*self.flowrate*self.stepsize*val_ratio)/(math.pi*(self.diameter**2)*self.pitch))
		self.motor_pause = True
		self.is_motor_running = True
		
		# changes frequency
		self.driver.set_freq(self.frequency)
		print self.frequency
	
	def _stopwatch(self):
		# calculate running time
		# called with time_return
		if self.motor_pause and self.motor_direction:
			self.time_now = time.time() - self.time_initial + self.time_duration
		if self.time_now is not 0:
			self.time_list.append(self.time_now)
			return self.time_now
		else:
			return self.time_list[-1]
			

	def data_return(self,maxtime,maxvol):
		if self.is_motor_running:
			# run stopwatch, export timestring & volume to motorgui
			time_now = int(self._stopwatch())
			self.timestring = str(datetime.timedelta(seconds=time_now))
			
			#self.timeval = (self.timer[2]/10) + (self.timer[1]*10) + (self.timer[0]*600)
			self.volnow = (self.flowrate * time_now)
			
			if int(time_now) == int(maxtime) or int(self.volnow) == int(maxvol):
				self.pause_adapter()
				self.is_motor_running = False

			return (self.timestring,self.volnow)
	
	def status_return(self):
		return (self.motor_pause,self.motor_direction)
	
	def quit_adapter(self):
		# called by gui.quit_function, time_return, and vol_return
		self.driver.quit_motor()
