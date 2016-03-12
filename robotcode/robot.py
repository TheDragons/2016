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
		#self.high = wp.Solenoid(0)
		#self.low = wp.Solenoid(1)
		self.shifter = wp.DoubleSolenoid(0,1)
		#self.intakeA = wp.Solenoid(2)		#New 3/8/16
		#self.intakeB = wp.Solenoid(3)  		#New 3/8/16
		self.extIntakeSol = wp.DoubleSolenoid(2,3)
		#self.ptoEngage = wp.Solenoid(4)     #New 3/8/16
		#self.ptoDisengage = wp.Solenoid(5)  #New 3/8/16
		self.ptoSol = wp.DoubleSolenoid(4,5)
		self.stick = wp.Joystick(0)
		self.stick2 = wp.Joystick(1)
		self.stick3 = wp.Joystick(2)
		self.intakeSensor = wp.DigitalInput(4)
		self.autoTime = wp.Timer()
		self.intakeTime = wp.Timer()
		#self.intakeLight = wp.Relay(0)  #New 3/8/16
		
		#calibrate gyro
		self.gyro.calibrate() 
		
		autoDesc1 = "Auto1 goes under lowbar and into goal, Might not work!"
		autoDesc2 = "Auto2 just goes straight for a couple seconds, usefull for crossing defences."
		
		wp.SmartDashboard.putBoolean("Auto1:", False)
		wp.SmartDashboard.putBoolean("Auto2:", False)
		wp.SmartDashboard.putBoolean("Auto2:", False)
		wp.SmartDashboard.putNumber("pos 1:", 9825)
		wp.SmartDashboard.putNumber("pos 2:", 40)
		wp.SmartDashboard.putNumber("pos 3:", 6550)
		wp.SmartDashboard.putNumber("pos 5:", 6000)
		wp.SmartDashboard.putString("Auton 1 Description:", autoDesc1)
		wp.SmartDashboard.putString("Auton 2 Description:", autoDesc2)
	def autonomous(self):
		self.gyro.calibrate()
		self.encdLeft.reset()
		self.encdRight.reset()
		rSide = 0
		lSide = 0
		straightAngle = 0
		
		angleGain = 40
		#print(wp.SmartDashboard.getNumber())
		pos1 = wp.SmartDashboard.getNumber("pos 1:", 9825)
		pos2 = wp.SmartDashboard.getNumber("pos 2:", 40)
		pos3 = wp.SmartDashboard.getNumber("pos 3:", 6550)
		pos5 = wp.SmartDashboard.getNumber("pos 5:", 6000)
		intakeMotorSpeed = 0
		stage1 = True
		stage2 = False #stageNums are for the individual stages of auto
		stage3 = False
		auto1 = wp.SmartDashboard.getBoolean("Auto1:", False)
		auto2 = wp.SmartDashboard.getBoolean("Auto2:", False)
		setR = 0
		setL = 0
		self.ptoSol.set(1)
		extIntakeSet = 1
		while self.isAutonomous() and self.isEnabled():
			if(auto1):
				if(abs(self.encdLeft.get()) < pos1 and abs(self.encdRight.get()) < pos1 and stage1):  # 
					setR, setL = rf.gyroFunc(self.gyro.getAngle(), -0.65, -0.65)
					extIntakeSet = 2
					stage2 = True
				elif(self.gyro.getAngle() < pos2 and stage2): #abs(self.encdLeft.get()) < pos2 and
					stage1 = False
					setR, setL = rf.angleFunc(self.gyro.getAngle(), pos2, angleGain)
					self.encdLeft.reset()
					self.encdRight.reset()
					stage3 = True
				elif(abs(self.encdLeft.get()) < pos3 and abs(self.encdRight.get()) < pos3 and stage3):
					if(stage2):
						self.gyro.reset()
						
					stage2 = False
					setR, setL = rf.gyroFunc(self.gyro.getAngle(), -0.65, -0.65)
					extIntakeSet = 1
				else:
					setR = 0
					setL = 0
					stage3 = False
					#if(self.intakeTime.running == False):
					#	self.intakeTime.start()
					#if(self.intakeTime.get() < 0.5):
					#	intakeMotorSpeed = -1
					#else:                                                 #auton intake code
					#	intakeMotorSpeed = 0
					#	self.intakeTime.stop()
					#	self.intakeTime.reset()
				self.extIntakeSol.set(extIntakeSet)
				wp.SmartDashboard.putBoolean("Auto2:", False)
				
			if(auto2):
				if(abs(self.encdRight.get()) < pos5): 
				#if(self.gyro.getAngle() < 41):                                                #ANGLE TEST IF STATEMENT
					setR, setL = rf.gyroFunc(self.gyro.getAngle(), -0.9, -0.9)                 #USE FOR DRIVING STRAIGHT OVER DEFENCE
					#setR, setL = rf.angleFunc(self.gyro.getAngle(), turnAngle, angleGain)     #USE FOR ANGLE TESTING
				else:
					setR = 0
					setL = 0
				wp.SmartDashboard.putBoolean("Auto1:", False)
				
			self.motorFrontRight.set(setR * -1)
			self.motorMiddleRight.set(setR)
			self.motorBackRight.set(setR * -1)	
			self.motorFrontLeft.set(setL)
			self.motorMiddleLeft.set(setL * -1)
			self.motorBackLeft.set(setL)
			self.intakeMotor.set(intakeMotorSpeed)
			self.ptoSol.set(1)
			
			wp.SmartDashboard.putNumber("Right Encoder:",self.encdRight.get())
			wp.SmartDashboard.putNumber("Left Encoder:",self.encdLeft.get())
			wp.SmartDashboard.putNumber("Right Motor:", setR)
			wp.SmartDashboard.putNumber("Left Motor:", setL)
			wp.SmartDashboard.putString("Gyro:",round(self.gyro.getAngle(), 2))
			
			

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
		shiftSet = 2
		extIntakeSet = 1
		ptoSet = 1
		extIntakeMotorSpeed = 0
		while self.isOperatorControl() and self.isEnabled():
			#output to dashboard
			joyValY = self.stick.getY()
			joyValX = self.stick.getX()
			joyVal2 = self.stick2.getY()
			#driveTypeButton = self.stick2.getRawButton(3)
			driveSideButton = self.stick2.getRawButton(2)
			intakeForward = self.stick3.getRawButton(10) 
			intakeBackward = self.stick3.getRawButton(11)
			extIntakeBackward = self.stick3.getRawButton(1)
			gyroButton = self.stick.getRawButton(8)
			highButton = self.stick2.getRawButton(11)
			lowButton = self.stick2.getRawButton(10)
			extIntakeInButton = self.stick3.getRawButton(7)
			extIntakeOutButton = self.stick3.getRawButton(6)
			compressorButton = self.stick3.getRawButton(8)
			ptoEngage = self.stick.getRawButton(11)
			ptoDisengage = self.stick.getRawButton(10)

			#toggle drivetype button
			#if (past == False and driveTypeButton == True):
			#	driveType = not driveType
			#past = driveTypeButton                                 IN CASE WE NEED IT

			#toggle driveside button
			if (past2 == False and driveSideButton == True):
				flipVar = not flipVar
			past2 = driveSideButton
			
			rightM, leftM = rf.tank(joyValY, joyVal2)
				
			rSide, lSide = rf.flip(flipVar, rightM, leftM) 
			
			#Intake
			intakeMotorSpeed = 0
			if( previousIntake == False and intakeForward == True):
				intakeIsEnabled = not intakeIsEnabled

			if( intakeIsEnabled):
				intakeMotorSpeed = 0.75
				extIntakeMotorSpeed = -0.75
				
				if( self.intakeSensor.get() == 1 ):
					if(self.intakeTime.running == False):
						self.intakeTime.start()
					
					if(self.intakeTime.get() > 0.25):
						intakeMotorSpeed = 0
						extIntakeMotorSpeed = 0
						extIntakeSet = 1
						intakeIsEnabled = False
						self.intakeTime.stop()
						self.intakeTime.reset()
				
			if(intakeBackward):
				intakeMotorSpeed = -1 
				
			if(extIntakeBackward):
				extIntakeMotorSpeed = 1
			
			
			
			previousIntake = intakeForward
			
			if(extIntakeInButton or (self.stick3.getY() <= -0.85)):
				extIntakeSet = 2
				
			if(extIntakeOutButton or (self.stick3.getY() >= 0.85)):
				extIntakeSet = 1
			
			#toggle compressor button
			if (compressor == False and compressorButton == True):
				compressor = not compressor
				
			past3 = compressorButton
			
			if(compressor == False and compressorButton):
				self.compressor.start()
			if(compressor == True and compressorButton):
				self.compressor.stop()
			
			#toggle shifting button
			#if (highButton == True):
			#	highOn = True
			#	lowOn = False
			
			#elif (lowButton == True):
			#	highOn = False
			#	lowOn = True
			if(highButton and shiftSet == 2):
				shiftSet = 1
			if(lowButton and shiftSet == 1):
				shiftSet = 2
			
			 
			#pto engage/disengage
			if(ptoEngage and ptoSet == 2):
				ptoSet = 1
			if(ptoDisengage and ptoSet == 1):
				ptoSet = 2
				
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
				
			#drivetrain compensation
			setR = setR * 1
			
			self.motorFrontRight.set(setR * -1)
			self.motorBackRight.set(setR * -1)
			self.motorMiddleRight.set(setR)			# Reversed because of the dynamics of the transmission
			self.motorFrontLeft.set(setL)
			self.motorBackLeft.set(setL)
			self.motorMiddleLeft.set(setL * -1)		# Reversed because of the dynamics of the transmission
			self.intakeMotor.set(intakeMotorSpeed)
			self.extIntakeMotor.set(extIntakeMotorSpeed)
			self.shifter.set(shiftSet)
			self.extIntakeSol.set(extIntakeSet)
			self.ptoSol.set(ptoSet)
			intakeMotorSpeed = 0
			
			#smartdashboard
			wp.SmartDashboard.putString("Gyro:",round(self.gyro.getAngle(), 2))
			wp.SmartDashboard.putNumber("Right Encoder:",self.encdRight.get())
			wp.SmartDashboard.putNumber("Left Encoder:",self.encdLeft.get())
			wp.SmartDashboard.putNumber("Right Motor:", setR)
			wp.SmartDashboard.putNumber("Left Motor:", setL)
			wp.SmartDashboard.putBoolean("Sensor:",self.intakeSensor.get())

			wp.Timer.delay(0.005)   # wait 5ms to avoid hogging CPU cycles

if __name__ == '__main__':
    wp.run(MyRobot)
