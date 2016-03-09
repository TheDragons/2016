#!/usr/bin/env python3

import wpilib as wp
import robotfuncs as rf
import time as tm
from networktables import NetworkTable as NT

try:
	camServ = wp.CameraServer()
	usbCam = wp.USBCamera()
	usbCam.setExposureManual(50)
	usbCam.setBrightness(80)
	usbCam.updateSettings() # force update before we start thread
	camServ.startAutomaticCapture(usbCam)
except:
	pass
	
class MyRobot(wp.SampleRobot):


	def robotInit(self):
		'''Robot initialization function'''
		
		self.motorFrontRight = wp.VictorSP(1)
		self.motorBackRight = wp.VictorSP(3)
		self.motorMiddleRight = wp.VictorSP(5)
		self.motorFrontLeft = wp.VictorSP(2)
		self.motorBackLeft = wp.VictorSP(4)
		self.motorMiddleLeft = wp.VictorSP(6)
		self.intakeMotor = wp.VictorSP(9)
		self.extIntakeMotor = wp.VictorSP(7) #New 3/8/16
		self.liftMotor = wp.VictorSP(8)  #New 3/8/16
		self.encdLeft = wp.Encoder(0, 1)
		self.encdRight = wp.Encoder(2,3)
		self.gyro = wp.AnalogGyro(0, center = None, offset = None)
		self.compressor = wp.Compressor()
		self.high = wp.Solenoid(1)
		self.low = wp.Solenoid(2)
		self.intakeOut = wp.Solenoid(3)		#New 3/8/16
		self.intakeIn = wp.Solenoid(4)      #New 3/8/16
		self.ptoEngage = wp.Solenoid(5)     #New 3/8/16
		self.ptoDisengage = wp.Solenoid(6)  #New 3/8/16
		self.stick = wp.Joystick(0)
		self.stick2 = wp.Joystick(1)
		self.stick3 = wp.Joystick(2)
		self.intakeSensor = wp.DigitalInput(4)
		self.autoTime = wp.Timer()
		self.intakeTime = wp.Timer()
		#self.intakeLight = wp.Relay(0)  #New 3/8/16
		
		#calibrate gyro
		self.gyro.calibrate() 
		
		auto2 = False   #autoNums are for selecting types of auto
		auto3 = False
		
		wp.SmartDashboard.putBoolean("Auto1:", False)
		
		

	def autonomous(self):
		self.gyro.reset()
		self.encdLeft.reset()
		self.encdRight.reset()
		rSide = 0
		lSide = 0
		straightAngle = 0
		turnAngle = 30
		angleGain = 100	 
		#print(wp.SmartDashboard.getNumber())
		pos1 = 1000
		pos2 = 30
		pos3 = 1000
		intakeMotorSpeed = 0
		stage1 = True
		stage2 = False #stageNums are for the individual stages of auto
		stage3 = False
		auto1 = wp.SmartDashboard.getBoolean("Auto1:", False)
		while self.isAutonomous() and self.isEnabled():
			if(abs(self.encdRight.get()) < pos1 and stage1):  #abs(self.encdLeft.get()) < pos1 and 
				setR, setL = rf.gyroFunc(self.gyro.getAngle(), -0.3, -0.3)
				stage2 = True
			elif(abs(self.encdRight.get()) < pos2 and stage2): #abs(self.encdLeft.get()) < pos2 and
				stage1 = False
				stage3 = True
				setR, setL = rf.angleFunc(self.gyro.getAngle(), turnAngle, angleGain)
				self.encdLeft.reset()
				self.encdRight.reset()
			elif(abs(self.encdRight.get()) < pos3 and stage3): #abs(self.encdLeft.get()) < pos3 and 
				stage2 = False
				setR, setL = rf.gyroFunc(self.gyro.getAngle(), -0.3, -0.3)
			else:
				setR = 0
				setL = 0
				stage3 = False
				if(self.intakeTime.running == False):
					self.intakeTime.start()
				if(self.intakeTime.get() < 0.5):
					intakeMotorSpeed = -1
				else:
					intakeMotorSpeed = 0
					self.intakeTime.stop()
					self.intakeTime.reset()
				
			self.motorFrontRight.set(setR * -1)
			self.motorMiddleRight.set(setR)
			self.motorBackRight.set(setR * -1)	
			self.motorFrontLeft.set(setL)
			self.motorMiddleLeft.set(setL * -1)
			self.motorBackLeft.set(setL)
			self.intakeMotor.set(intakeMotorSpeed)
			wp.SmartDashboard.putNumber("Right Encoder:",self.encdRight.get())
			wp.SmartDashboard.putNumber("Left Encoder:",self.encdLeft.get())
			wp.SmartDashboard.putBoolean("Auton Selection", auto1)
			

	def disabled(self):
		pass

	def operatorControl(self):
		past = False
		driveType = True
		past2 = False
		flipVar = False
		#reset encoders
		self.encdRight.reset()
		self.encdLeft.reset()
		self.gyro.reset()
		dtGain = 0.075 
		encval = 0
		setR = 0
		setL = 0
		compressor = False
		highOn = True
		lowOn = False
		past3 = False
		wantedSpeed = 300
		speedGain = 100
		intakeIsEnabled = False
		previousIntake = False
		self.intakeTime.reset()
		self.intakeTime.stop()
		test = 1
		wp.SmartDashboard.putNumber("TestNumber:", test)
		auto1 = wp.SmartDashboard.getBoolean("Auto1:", False)
		while self.isOperatorControl() and self.isEnabled():
			#output to dashboard
			joyValY = self.stick.getY()
			joyValX = self.stick.getX()
			joyVal2 = self.stick2.getY()
			#driveTypeButton = self.stick2.getRawButton(3)
			driveSideButton = self.stick2.getRawButton(2)
			intakeForward = self.stick3.getRawButton(10) 
			intakeBackward = self.stick3.getRawButton(11)
			gyroButton = self.stick.getRawButton(8)
			highButton = self.stick2.getRawButton(11)
			lowButton = self.stick2.getRawButton(10)
			compressorButton = self.stick3.getRawButton(8)

			#toggle drivetype button
			#if (past == False and driveTypeButton == True):
			#	driveType = not driveType
			#past = driveTypeButton                                 IN CASE WE NEED IT

			#toggle driveside button
			if (past2 == False and driveSideButton == True):
				flipVar = not flipVar
			past2 = driveSideButton
			
			if( driveType):
				rightM, leftM = rf.tank(joyValY, joyVal2)
			else:
				rightM, leftM = rf.arcade(joyValY, joyValX)
				
			rSide, lSide = rf.flip(flipVar, rightM, leftM) 
			
			#Intake
			intakeMotorSpeed = 0
			if( previousIntake == False and intakeForward == True):
				intakeIsEnabled = not intakeIsEnabled

			if( intakeIsEnabled):
				intakeMotorSpeed = .75
				
				if( self.intakeSensor.get() == 1 ):
					if(self.intakeTime.running == False):
						self.intakeTime.start()
					print("Intake Timer: " + str(self.intakeTime.get()))
					if(self.intakeTime.get() > 0.25):
						intakeMotorSpeed = 0
						intakeIsEnabled = False
						self.intakeTime.stop()
						self.intakeTime.reset()
				
			
			if(intakeBackward):
				intakeMotorSpeed = -1 
			
			previousIntake = intakeForward
			
			
			#toggle compressor button
			if (compressor == False and compressorButton == True):
				compressor = not compressor
				
			past3 = compressorButton
			
			#toggle shifting button
			if (highButton == True):
				highOn = True
				lowOn = False
			
			elif (lowButton == True):
				highOn = False
				lowOn = True
			
			##This sets our dead band on the joystick
			if ((rSide <= dtGain*-1) or (rSide >= dtGain)):
				setR = rf.deadband(rSide, dtGain)
			else:
				setR = 0
			
			if ((lSide <= dtGain*-1) or (lSide >= dtGain)):
				setL = rf.deadband(lSide, dtGain)
			else:
				setL = 0
			
			if (gyroButton):
				self.gyro.calibrate()
			setR = setR * 0.9750367
			
			self.motorFrontRight.set(setR * -1)
			self.motorBackRight.set(setR * -1)
			self.motorMiddleRight.set(setR)			# Reversed because of the dynamics of the transmission
			self.motorFrontLeft.set(setL)
			self.motorBackLeft.set(setL)
			self.motorMiddleLeft.set(setL * -1)		# Reversed because of the dynamics of the transmission
			self.intakeMotor.set(intakeMotorSpeed)
			
			intakeMotorSpeed = 0
			
			#smartdashboard
			wp.SmartDashboard.putString("Gyro:",round(self.gyro.getAngle(), 2))
			wp.SmartDashboard.putNumber("Right Encoder:",self.encdRight.get())
			wp.SmartDashboard.putNumber("Left Encoder:",self.encdLeft.get())
			wp.SmartDashboard.putNumber("Right Motor:", setR)
			wp.SmartDashboard.putNumber("Left Motor:", setL)
			wp.SmartDashboard.putBoolean("Sensor:",self.intakeSensor.get())
			wp.SmartDashboard.getNumber("Test the GetNumber:", test)
			wp.SmartDashboard.putNumber("Test of the test:", wp.SmartDashboard.getNumber("TestNumber:", 1))
			wp.SmartDashboard.putBoolean("Auton Selection", auto1)

			wp.Timer.delay(0.005)   # wait 5ms to avoid hogging CPU cycles

if __name__ == '__main__':
    wp.run(MyRobot)
