import Tkinter as tk
import ttk
import time
from HumiditySensors.DHT import DHT
from PumpAdapters.OSPump import PrintedPump
'''
runmotor = Process(target=MotorGui)
runmotor.start()
runsensor = Process(target=SensorGui)
runsensor.start()
runmotor.join()
runsensor.join()

'''
class RunGUI(object):
	def __init__(self):
		self.root = tk.Tk()
		
		self.horizframe = tk.Frame(self.root)
		self.horizframe.pack(side=tk.TOP)
		self.frame1 = tk.LabelFrame(self.horizframe,text="Humidity Controls",labelanchor='n')
		self.frame1.pack(side=tk.LEFT,fill=tk.Y,padx=5)

		self.frame2 = tk.LabelFrame(self.horizframe,text="Syringe Pump Controls",labelanchor='n')
		self.frame2.pack(side=tk.LEFT,fill=tk.Y,padx=5)
		
		self.setup_sensorframe()
		self.setup_motorframe()
		
		ttk.Button(self.root,text="QUIT",command=self.quit_gui).pack(anchor=tk.S)
		
		self.root.mainloop()
	
	def setup_sensorframe(self):
		self.sensor_adapter = DHT()
		self.radiobutton_frame = tk.Frame(self.frame1)
		self.radiobutton_frame.pack()
		
		self.dutycycle_choices = tk.StringVar()
		self.dutycycle_choices.set("4")
		self.dutycycle_buttons = {
			"manual humidifying": "1",
			"automatic humidifying": "2",
			"max humidifying": "3",
			"no humidifying": "4"}
		self.dutycycle_functions = [
			self.manual_dc,
			self.auto_dc,
			self.full_dc,
			self.no_dc]
		for num in range(1,5):
			for k,value in self.dutycycle_buttons.iteritems():
				if value==str(num):
					key = k
					break
			tk.Radiobutton(
				self.radiobutton_frame,text=key,
				command=self.dutycycle_functions[num-1],
				variable=self.dutycycle_choices,
				value=self.dutycycle_buttons[key],
				indicatoron=0).pack(side=tk.LEFT)

		tk.Label(self.frame1,text="\n Time: ").pack(side=tk.TOP)
		self.time_value1 = tk.StringVar()
		self.time_label = tk.Label(self.frame1,textvariable=self.time_value1)
		self.time_label.pack(side=tk.TOP)
		
		tk.Label(self.frame1,text="\n Temperature (C): ").pack(side=tk.TOP)
		self.temperature_value = tk.StringVar()
		self.temperature_label = tk.Label(self.frame1,textvariable=self.temperature_value)
		self.temperature_label.pack(side=tk.TOP)
		
		tk.Label(self.frame1,text="\n Relative Humidity (%): ").pack(side=tk.TOP)
		self.humidity_value = tk.StringVar()
		self.humidity_label = tk.Label(self.frame1,textvariable=self.humidity_value)
		self.humidity_label.pack(side=tk.TOP)
		
		tk.Label(self.frame1,text="\n % of Time Humidifying: ").pack(side=tk.TOP)
		self.dutycycle_value = tk.StringVar()
		self.dutycycle_value.set("0")
		self.dutycycle_label = tk.Label(self.frame1,textvariable=self.dutycycle_value)
		self.dutycycle_label.pack(side=tk.TOP)
		
		# for input box
		self.input_frame = tk.Frame(self.frame1)
		self.input_frame.pack()
		
		# for Save, Quit buttons
		self.button_frame = tk.Frame(self.frame1)
		self.button_frame.pack()
		
		ttk.Button(self.button_frame,text="SAVE",command=self.sensor_adapter.save_data).pack()
		
		
		self.continue_auto = False
		self.destroy_input_box = False
		self.dc_value = 0
		
		self.print_sensor_data()
	
	def manual_dc(self):
		self.continue_auto = False
		if self.destroy_input_box is False:
			self.text_label = tk.Label(self.input_frame,text="Percentage?")
			self.text_label.pack(side=tk.LEFT)
			
			self.entry_value = tk.StringVar()
			self.entry_box = tk.Entry(self.input_frame,textvariable=self.entry_value)
			self.entry_box.pack(side=tk.LEFT)
			
			self.enter_button = ttk.Button(self.input_frame,text="Enter",command=self.clicked_enter)
			self.enter_button.pack(side=tk.LEFT)
			
			self.destroy_input_box = True
		
	def auto_dc(self):
		if self.destroy_input_box:
			self.entry_box.destroy()
			self.enter_button.destroy()
			self.text_label.destroy()
			self.destroy_input_box = False
		self.continue_auto = True
	
	def full_dc(self):
		self.continue_auto = False
		if self.destroy_input_box:
			self.entry_box.destroy()
			self.enter_button.destroy()
			self.text_label.destroy()
			self.destroy_input_box = False
		self.dc_value = 100
		self.sensor_adapter.set_dutycycle(self.dc_value)
		
	def no_dc(self):
		self.continue_auto = False
		if self.destroy_input_box:
			self.entry_box.destroy()
			self.enter_button.destroy()
			self.text_label.destroy()
			self.destroy_input_box = False
		self.dc_value = 0
		self.sensor_adapter.set_dutycycle(self.dc_value)

	def clicked_enter(self):
		self.dc_value = int(float(self.entry_value.get()))
		self.sensor_adapter.set_dutycycle(self.dc_value)

	def print_sensor_data(self):
		if self.continue_auto:
			self.dc_value = self.sensor_adapter.calculate_dutycycle()
			self.sensor_adapter.set_dutycycle(self.dc_value)
		self.dutycycle_value.set(self.dc_value)
		timeval,tempval,humval = self.sensor_adapter.collect_data(self.dc_value)
		time_ = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timeval))
		temperature = '%.3f'%(tempval)
		humidity = '%.3f'%(humval)
		self.time_value1.set(time_)
		self.temperature_value.set(temperature)
		self.humidity_value.set(humidity)
		
		self.frame1.after(500,self.print_sensor_data)

	def setup_motorframe(self):
		self.motor_adapter = PrintedPump()
		
		self.notebook = ttk.Notebook(self.frame2)
		self.run_frame = ttk.Frame(self.notebook)
		self.cal_frame = ttk.Frame(self.notebook)
		self.notebook.pack()
		self.notebook.add(self.run_frame,text='Run Pump')
		self.notebook.add(self.cal_frame,text='Calibrate')
		
		self.cal_label1 = tk.Label(self.cal_frame, text='Desired Volume:')
		self.cal_label1.pack(side=tk.TOP)
		self.cal_text1 = tk.StringVar()
		self.cal_box1 = tk.Entry(self.cal_frame,textvariable=self.cal_text1)
		self.cal_box1.pack(side=tk.TOP)

		self.cal_label2 = tk.Label(self.cal_frame, text='Experimental Volume:')
		self.cal_label2.pack(side=tk.TOP)
		self.cal_text2 = tk.StringVar()
		self.cal_box2 = tk.Entry(self.cal_frame,textvariable=self.cal_text2)
		self.cal_box2.pack(side=tk.TOP)
		
		ttk.Button(self.cal_frame, text="CALIBRATE", command=self.calibrate_pump).pack(side=tk.TOP)
		ttk.Button(self.cal_frame, text="RESET", command=self.reset_calibration).pack(side=tk.TOP)
		
		# will contain dropdown menu
		self.menu_frame = tk.Frame(self.run_frame)
		self.menu_frame.configure()
		self.menu_frame.pack()
		
		# dropdown menu
		self.v = tk.StringVar()
		self.v.set("choose:")
		self.options = [
			"choose:",
			"run indefinitely",
			"input run time",
			"input total run volume"]
		ttk.OptionMenu(self.menu_frame,self.v,*self.options,command=self.basic_setup).pack()
		
		# will contain boxes, labels, enter button
		self.entry_frame = tk.Frame(self.run_frame)
		self.entry_frame.configure()
		self.buttons = []  
		self.entry_frame.pack()

		# INFO_FRAME: time, paused, withdrawing/pumping, total vol
		self.info_frame = tk.Frame(self.run_frame)
		self.info_frame.configure()
		self.info_frame.pack()
		
		self.timetext = tk.StringVar()
		self.timelabel = tk.Label(self.info_frame, textvariable=self.timetext).pack()

		self.voltext1 = tk.StringVar()
		self.vollabel1 = tk.Label(self.info_frame, textvariable=self.voltext1).pack()
		
		self.voltext2 = tk.StringVar()
		self.vollabel2 = tk.Label(self.info_frame, textvariable=self.voltext2).pack()
		
		self.statustext = tk.StringVar()
		self.statuslabel = tk.Label(self.info_frame, textvariable=self.statustext).pack()
		
		self.pausetext = tk.StringVar()
		self.pauselabel = tk.Label(self.info_frame,textvariable=self.pausetext).pack()
	
	def calibrate_pump(self):
		trueval = float(self.cal_text1.get())
		expval = float(self.cal_text2.get())
		self.motor_adapter.calibration(trueval,expval,0)
	
	def reset_calibration(self):
		self.motor_adapter.calibration(1,1,1)
	
	def basic_setup(self,choice):
		# erase previous stuff and start again
		self.entry_frame.destroy()
		self.entry_frame = tk.Frame(self.run_frame)
		self.entry_frame.configure()
		self.buttons = [] 
		self.entry_frame.pack(side=tk.TOP)
		
		if choice == "run indefinitely":
			self.time_input_exists = False
			self.volume_input_exists = False
		elif choice == "input run time":
			self.time_input_exists = True
			self.volume_input_exists = False
		elif choice == "input total run volume":
			self.time_input_exists = False
			self.volume_input_exists = True
			
		# create boxes & labels
		self.input_data()
		
		# pause, reverse, & quit buttons
		ttk.Button(self.entry_frame, text="PAUSE/UNPAUSE", command=self.motor_adapter.pause_adapter).pack(side=tk.TOP)
		ttk.Button(self.entry_frame, text="REVERSE", command=self.motor_adapter.reverse_adapter).pack(side=tk.TOP)
		ttk.Button(self.entry_frame, text="RESET", command=self.motor_adapter.reset_adapter).pack(side=tk.TOP)	
		
	def input_data(self):
		self.entrytext = {}
		if self.volume_input_exists:
			self.userinput = {
				  "total volume (mL)": "3",
				  "volumetric flow rate (mL/hr)": "2",
				  "inner diameter (cm)": "1"}
			self.lastnum = 4
		elif self.time_input_exists:
			self.userinput = {
				  "total time (min)": "3",
				  "volumetric flow rate (mL/hr)": "2",
				  "inner diameter (cm)": "1"}
			self.lastnum = 4	
		else:
			self.userinput = {
				  "volumetric flow rate (mL/hr)": "2",
				  "inner diameter (cm)": "1"} 	
			self.lastnum = 3		
		for num in range(1,self.lastnum):
			for k,value in self.userinput.iteritems():
				if value==str(num):
					key = k
					break
			self.label = tk.Label(self.entry_frame, text=key)
			self.label.pack(side=tk.TOP)
			self.entrytext[key] = tk.StringVar()
			self.entry_box = tk.Entry(self.entry_frame,textvariable=self.entrytext[key])
			self.entry_box.pack(side=tk.TOP)
		ttk.Button(self.entry_frame, text="Enter", command=self.enter_function).pack(side=tk.TOP)
		self.blank_label = tk.Label(self.entry_frame, text="")
		self.blank_label.pack()
		
	def enter_function(self):
		self.flowrate = float(self.entrytext["volumetric flow rate (mL/hr)"].get())
		self.diameter = float(self.entrytext["inner diameter (cm)"].get())
		
		self.timetext.set("00:00:00")
		self.voltext1.set("Volume dispensed (mL):")
		
		self.motor_adapter.freq_calc(self.flowrate,self.diameter)
		self.print_motor_data()

	def get_time(self):
		# called by adapter.data_return
		if self.time_input_exists:
			try:
				self.time_value2 = int(self.entrytext["total time (min)"].get())*60
				#if not self.time_value:
					#raise ValueError('empty string')
			except ValueError:
				self.time_value2 = -1
		else:
			self.time_value2 = -1
		return self.time_value2
		
	def get_vol(self):
		# called by adapter.data_return
		if self.volume_input_exists:
			try:
				self.vol_value = int(self.entrytext["total volume (mL)"].get())
				#if not self.vol_value:
					#raise ValueError('empty string')
			except ValueError:
				self.vol_value = -1
		else:
			self.vol_value = -1
		return self.vol_value
	
	def print_motor_data(self):
		try:
			self.time_input = self.get_time()
			self.volume_input = self.get_vol()
			
			self.new_timelabel, self.new_vollabel = self.motor_adapter.data_return(self.time_input,self.volume_input)
			self.timetext.set(self.new_timelabel)
			self.voltext2.set('%.2f'%(self.new_vollabel))

			self.pausecheck, self.statuscheck = self.motor_adapter.status_return()
			
			if self.statuscheck:
				self.statustext.set("Pumping")
			else:
				self.statustext.set("Withdrawing")
			
			if self.pausecheck:
				self.pausetext.set("")
			else:
				self.pausetext.set("Paused")
			
			self.root.after(500,self.print_motor_data)
		except TypeError:
			print('done')
	
	def quit_gui(self):
		self.sensor_adapter.quit_plot()
		self.motor_adapter.quit_adapter()
		self.root.destroy()
RunGUI()
