from pyfrc.physics import drivetrains
from config import *
import time
from pprint import pprint

class PhysicsEngine(object):
	'''
	   Simulates a 4-wheel mecanum robot using Tank Drive joystick control 
	'''
	
	def __init__(self, physics_controller):
		'''
			:param physics_controller: `pyfrc.physics.core.Physics` object
									   to communicate simulation effects to
		'''
		self.physics_controller = physics_controller
		physics_controller.add_gyro_channel(0)
		self.lcount = 0 
		self.rcount = 0 
		self.lcountP = 0 
		self.rcountP = 0 
		
		self.pastTime = 0
		self.currentTime = 0
		self.loopTime = 0
		
		self.encodeLRate = 0
		self.encodeRRate = 0
		self.robot_enabled = False
		
	def update_sim(self, hal_data, now, tm_diff):
		# Simulate the drivetrain
		# -> Remember, in the constructor we inverted the left motors, so
		#	invert the motor values here too!
			
		if(self.currentTime != self.pastTime):
			self.loopTime = self.currentTime - self.pastTime
			
		self.pastTime = self.currentTime
		self.currentTime = time.process_time()
		
		#if(not self.robot_enabled):
		#	hal_data['pwm'][backLeftPort]['value'] = 0
		#	hal_data['pwm'][backRightPort]['value'] = 0
		#	hal_data['pwm'][frontLeftPort]['value'] = 0
		#	hal_data['pwm'][frontRightPort]['value'] = 0
		#	hal_data['pwm'][middleLeftPort]['value'] = 0
		#	hal_data['pwm'][middleRightPort]['value'] = 0
		
		lf_motor = -hal_data['pwm'][backLeftPort]['value']
		rf_motor = hal_data['pwm'][backRightPort]['value']
		
		lr_motor = -hal_data['pwm'][frontLeftPort]['value']
		rr_motor = hal_data['pwm'][frontRightPort]['value']
		
		lm_motor = hal_data['pwm'][middleLeftPort]['value']
		rm_motor = -hal_data['pwm'][middleRightPort]['value']
			
		lcountP = self.lcount 
		rcountP = self.rcount 

		self.lcount += (lf_motor + lr_motor + lm_motor)/4
		self.rcount += (rf_motor + rr_motor + rm_motor)/4
		
		if(self.lcountP == self.lcount):
			self.encodeLRate = 0
		elif(self.loopTime != 0):
			self.encodeLRate = (self.lcount - self.lcountP)/self.loopTime
		
		if(self.rcountP == self.rcount):
			self.encodeRRate = 0
		elif(self.loopTime != 0):
			self.encodeRRate = (self.rcount - self.rcountP)/self.loopTime
		
		self.encodeLRate = 0
		self.encodeRRate = 0

		hal_data['encoder'][0]['initialized'] = True
		hal_data['encoder'][1]['initialized'] = True

		hal_data['encoder'][0]['has_source'] = True
		hal_data['encoder'][0]['count'] = int(self.lcount)
		hal_data['encoder'][0]['rate'] = self.encodeLRate

		hal_data['encoder'][1]['has_source'] = True
		hal_data['encoder'][1]['count'] = int(self.rcount)
		hal_data['encoder'][1]['rate'] = self.encodeRRate

		rside = (rf_motor + rr_motor + rm_motor)/3
		lside = (lf_motor + lr_motor + lm_motor)/3
		
		vx, vy = drivetrains.two_motor_drivetrain(-rside, lside)
		
		self.physics_controller.drive(vx, -vy, tm_diff)
