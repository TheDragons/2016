#!/usr/bin/env python3

import wpilib as wp
import robotfuncs as rf
import time as tm
from networktables import NetworkTable as NT
from threading import Timer
import wpiJoystickOverlay as joy

#this is an experment, this will run reguardless of robot state, teleop, auto, disabled, test any state but off.
def update_dash(roboSelf, pastAuto1, pastAuto2, right = 0.0, left = 0.0): 
	wp.SmartDashboard.putNumber("Gyro:",round(roboSelf.gyro.getAngle(), 2))
	wp.SmartDashboard.putNumber("Right Encoder:",roboSelf.encdRight.get())
	wp.SmartDashboard.putNumber("Left Encoder:",roboSelf.encdLeft.get())
	wp.SmartDashboard.putBoolean("Sensor:",roboSelf.intakeSensor.get())
	wp.SmartDashboard.putNumber("Stick X",roboSelf.stick.getX())
	wp.SmartDashboard.putNumber("Stick Y:",roboSelf.stick.getY())
	wp.SmartDashboard.putNumber("Stick2 X:",roboSelf.stick2.getX())
	wp.SmartDashboard.putNumber("Stick2 Y:",roboSelf.stick2.getY())
			
	wp.SmartDashboard.putNumber("Right Motor:", right)
	wp.SmartDashboard.putNumber("Left Motor:", left)
	
	auto1 = wp.SmartDashboard.getBoolean("Auto1:", True)
	auto2 = wp.SmartDashboard.getBoolean("Auto2:", True)
	calGyro = wp.SmartDashboard.getBoolean("calGyro:", True)
	resetGyro = wp.SmartDashboard.getBoolean("resetGyro:", True)
	encodeReset = wp.SmartDashboard.getBoolean("resetEnc:", True)
	
	if(not pastAuto1 and auto1):
		wp.SmartDashboard.putBoolean("Auto2:", False)
		auto2 = False
	
	if(not pastAuto2 and auto2):
		wp.SmartDashboard.putBoolean("Auto1:", False)
		auto1 = False
	
	if(auto1 and auto2):
		wp.SmartDashboard.putBoolean("Auto1:", False)
		wp.SmartDashboard.putBoolean("calGyro:", False)
		
	if(resetGyro):
		roboSelf.gyro.reset()
		wp.SmartDashboard.putBoolean("resetGyro:", False)
		
	if(calGyro):
		roboSelf.gyro.calibrate()
		wp.SmartDashboard.putBoolean("calGyro:", False)
		
	if(encodeReset):
		roboSelf.encdRight.reset()
		roboSelf.encdLeft.reset()
		wp.SmartDashboard.putBoolean("resetEnc:", False)
		
	return auto1, auto2

#try:
#	camServ = wp.CameraServer()
#	usbCam = wp.USBCamera()
#	usbCam.setExposureManual(50)
#	usbCam.setBrightness(80)
#	usbCam.updateSettings() # force update before we start thread
#	camServ.startAutomaticCapture(usbCam)
#except:
#	pass
	
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
		self.extIntakeMotor = wp.VictorSP(7)
		self.liftMotor = wp.VictorSP(8)
		
		self.encdLeft = wp.Encoder(0, 1)
		self.encdRight = wp.Encoder(2,3)
		
		self.gyro = wp.AnalogGyro(0, center = None, offset = None)
		
		self.compressor = wp.Compressor()
		self.shifter = wp.DoubleSolenoid(0,1)
		self.extIntakeSol = wp.DoubleSolenoid(2,3)
		self.ptoSol = wp.DoubleSolenoid(4,5)
		
		self.stick = joy.joyClass(0)
		self.stick2 = joy.joyClass(1)
		self.stick3 = joy.joyClass(2)
		
		self.intakeSensor = wp.DigitalInput(4)
		self.autoTime = wp.Timer()
		self.intakeTime = wp.Timer()
		
		self.spike = wp.Relay(0) 
		
		#calibrate gyro
		self.gyro.calibrate() 
		
		#update dashboard
		update_dash(self, True, True)
		
	def autonomous(self):
		self.gyro.reset()
		self.encdLeft.reset()
		self.encdRight.reset()
		rSide = 0
		lSide = 0
		straightAngle = 0

		turnGain = 70
		straitGain = 43
		
		pos1 = wp.SmartDashboard.getNumber("pos 1:", 4000)
		pos2 = wp.SmartDashboard.getNumber("pos 2:", 41)
		pos3 = wp.SmartDashboard.getNumber("pos 3:", 5000)
		pos5 = wp.SmartDashboard.getNumber("pos 5:", 5000)
		auto1 = wp.SmartDashboard.getBoolean("Auto1:", False)
		auto2 = wp.SmartDashboard.getBoolean("Auto2:", False)
		
		intakeMotorSpeed = 0
		stage1 = True
		stage2 = False #stageNums are for the individual stages of auto
		stage3 = False
		setR = 0
		setL = 0
		self.ptoSol.set(1)
		extIntakeSet = 1
		p1 = True
		p2 = True
		p1, p2 = update_dash(self, p1, p2)
		self.compressor.stop()
		while self.isAutonomous() and self.isEnabled():
			p1, p2 = update_dash(self, p1, p2, setR, setL)
			
			if(auto1):
				if(abs(self.encdLeft.get()) < pos1 and abs(self.encdRight.get()) < pos1 and stage1):  # 
					setR, setL = rf.gyroFunc(self.gyro.getAngle(), 0, -0.65, straitGain)
					extIntakeSet = 2
					stage2 = True
				elif(abs(self.gyro.getAngle()) < (pos2 -.05) and stage2): #abs(self.encdLeft.get()) < pos2 and
					stage1 = False
					setR, setL = rf.angleFunc(self.gyro.getAngle(), pos2, turnGain)
					self.encdLeft.reset()
					self.encdRight.reset()
					stage3 = True
				elif(abs(self.encdLeft.get()) < pos3 and abs(self.encdRight.get()) < pos3 and stage3):
					stage2 = False
					setR, setL = rf.gyroFunc(self.gyro.getAngle(), pos2, -0.65, straitGain)
					extIntakeSet = 1
				else:
					setR = 0
					setL = 0
					intakeMotorSpeed = 1
					stage3 = False
				self.extIntakeSol.set(extIntakeSet)
				
			if(auto2):
				if(abs(self.encdRight.get()) < pos5 or abs(self.encdLeft.get()) < pos5): 
					setR, setL = rf.gyroFunc(self.gyro.getAngle(), 0, -0.9, straitGain)                 #USE FOR DRIVING STRAIGHT OVER DEFENCE
				else:
					setR = 0
					setL = 0
							
			self.motorFrontRight.set(setR * -1)
			self.motorMiddleRight.set(setR)
			self.motorBackRight.set(setR * -1)	
			self.motorFrontLeft.set(setL)
			self.motorMiddleLeft.set(setL * -1)
			self.motorBackLeft.set(setL)
			self.intakeMotor.set(intakeMotorSpeed)
			self.ptoSol.set(1)
			wp.Timer.delay(0.015)   # wait 5ms to avoid hogging CPU cycles
			
	def disabled(self):
		p1, p2 = update_dash(self, True, True)
		while self.isDisabled():
			p1, p2 = update_dash(self, p1, p2)
			wp.Timer.delay(0.015)   # wait 5ms to avoid hogging CPU cycles

	def operatorControl(self):
		flipVar = False
		
		#reset encoders
		self.encdRight.reset()
		self.encdLeft.reset()
		self.gyro.reset()
		
		#Gain Tuning
		dtGain = 0.11
		wantedSpeed = 300
		speedGain = 100
		
		setR = 0
		setL = 0
		intakeIsEnabled = False
		previousIntake = False
		self.intakeTime.reset()
		self.intakeTime.stop()
		shiftSet = 2
		extIntakeSet = 1
		ptoSet = 1
		extIntakeMotorSpeed = 0
		liftMotorSpeed = 0
		p1, p2 = update_dash(self, True, True)
		self.compressor.start()
		while self.isOperatorControl() and self.isEnabled():
			#output to dashboard
			p1, p2 = update_dash(self, p1, p2, setR, setL)
			joyValY = self.stick.getY()
			joyValX = self.stick.getX()
			gyroButton = self.stick.getButtonRise(8)
			ptoDisengage = self.stick.getButtonRise(10)
			ptoEngage = self.stick.getButtonRise(11)
			
			joyVal2 = self.stick.getRawAxis(5)
			driveSideButton = self.stick2.getButtonRise(2)
			lowButton = self.stick2.getButtonRise(10)
			highButton = self.stick2.getButtonRise(5)
			
			extIntakeBackward = self.stick3.getButton(1)
			lifterUp = self.stick3.getButton(6)
			lifterDown = self.stick3.getButton(7)
			compressorButton = self.stick3.getButtonRise(8)
			intakeForward = self.stick3.getButtonRise(10) 
			intakeBackward = self.stick3.getButton(9)
			
			if (driveSideButton):
				flipVar = not flipVar
			
			#Used to run tank drive
			rightM, leftM = rf.tank(joyValY, joyVal2)
			
			#used to flip side of tank
			setR, setL = rf.flip(flipVar, rightM, leftM) 
			
			#Intake
			intakeMotorSpeed = 0
			extIntakeMotorSpeed = 0
			
			if(intakeForward):
				intakeIsEnabled = not intakeIsEnabled
			
			if(intakeIsEnabled):
				intakeMotorSpeed = -0.8
				extIntakeMotorSpeed = -1
				
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
				intakeMotorSpeed = 1
				
			if(extIntakeBackward):
				extIntakeMotorSpeed = 1
			
			if(self.stick3.getY() <= -0.85):
				extIntakeSet = 2
				
			if(self.stick3.getY() >= 0.85):
				extIntakeSet = 1
				
			if(self.intakeSensor.get() == 1):
				self.spike.set(3)
			else:
				self.spike.set(0)
				
			#lifter
			liftMotorSpeed = 0
			if(lifterUp):
				liftMotorSpeed = 1
			if(lifterDown):
				liftMotorSpeed = -1
						
			#toggle shifting button
			if(highButton and shiftSet == 2):
				shiftSet = 1
			if(lowButton and shiftSet == 1):
				shiftSet = 2
			
			#pto engage/disengage
			if(ptoEngage and ptoSet == 2):
				ptoSet = 1
			if(ptoDisengage and ptoSet == 1):
				ptoSet = 2
			
			#Calibrate the Gyro
			if (gyroButton):
				self.gyro.calibrate()
				
			#drivetrain compensation
			setR = setR * .935
			
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
			
			self.liftMotor.set(liftMotorSpeed)
			
			self.stick.updateClause()
			self.stick2.updateClause()
			self.stick3.updateClause()
			
			intakeMotorSpeed = 0                                                                                                                                                              
			
			#smartdashboard
			wp.Timer.delay(0.015)   # wait 5ms to avoid hogging CPU cycles

if __name__ == '__main__':
    wp.run(MyRobot)
