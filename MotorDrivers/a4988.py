'''
16*200 s/r
'''

import RPi.GPIO as GPIO

class a4988_Driver():
	def __init__(self):

		# turn on motor (18) and driver (6)
		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)
		GPIO.setup(21,GPIO.OUT)
		GPIO.setup(18,GPIO.OUT)
		GPIO.setup(16,GPIO.OUT)
		GPIO.setup(12,GPIO.OUT)
		GPIO.setup(6,GPIO.OUT)
		self.p = GPIO.PWM(18,10) # GPIO, frequency
		self.sixteenth_step()
		self.p.start(0) # duty cycle
		
		GPIO.output(6,GPIO.HIGH)
		
		# tells reverse_motor whether to withdraw or pump
		self.make_motor_reverse = True # make_motor_reverse	
		
		# tells pause_motor whether to pause or play
		self.make_motor_pause = True
	
	def full_step(self):
		GPIO.output(12,GPIO.LOW)
		GPIO.output(16,GPIO.LOW)
		GPIO.output(21,GPIO.LOW)
		self.step_multiply = 1
	
	def half_step(self):
		GPIO.output(12,GPIO.LOW)
		GPIO.output(16,GPIO.LOW)
		GPIO.output(21,GPIO.HIGH)
		self.step_multiply = 2

	def quarter_step(self):
		GPIO.output(12,GPIO.LOW)
		GPIO.output(16,GPIO.HIGH)
		GPIO.output(21,GPIO.LOW)
		self.step_multiply = 4
		
	def eighth_step(self):
		GPIO.output(12,GPIO.LOW)
		GPIO.output(16,GPIO.HIGH)
		GPIO.output(21,GPIO.HIGH)
		self.step_multiply = 8

	def sixteenth_step(self):
		GPIO.output(12,GPIO.HIGH)
		GPIO.output(16,GPIO.HIGH)
		GPIO.output(21,GPIO.HIGH)
		self.step_multiply = 16	
	
	def pause_motor(self):
		# called with "pause/unpause" button in motorgui
		if self.make_motor_pause:
			self.p.ChangeDutyCycle(0)
		else:
			self.p.ChangeDutyCycle(50)
		self.make_motor_pause = not self.make_motor_pause
		return self.make_motor_pause
		
	def reverse_motor(self):
		# called with "reverse" button in motorgui
		if self.make_motor_reverse:
			GPIO.output(6,GPIO.LOW)
		else:
			GPIO.output(6,GPIO.HIGH)
		self.make_motor_reverse = not self.make_motor_reverse
		return self.make_motor_reverse
	
	def return_stepsize(self):
		# called by adapter.freq_calc
		self.stepsize = 200*self.step_multiply #steps/rev
		return self.stepsize
	
	def return_pitch(self):
		# called by adapter.freq_calc
		self.pitch = 0.08 #cm/rev
		return self.pitch
	
	def set_freq(self,frequency):
		# this will be called with the "enter" button in motorgui
		self.p.ChangeDutyCycle(50)
		self.p.ChangeFrequency(frequency)
	
	def quit_motor(self):
		# called when "quit" is pressed or when time import has run up
		self.p.stop()
		GPIO.cleanup()
		print('cool')
