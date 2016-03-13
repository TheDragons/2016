#!/usr/bin/env python3

import wpilib as wp
import robotfuncs as rf
import time as tm
from networktables import NetworkTable as NT
from threading import Timer

#this is an experment, this will run reguardless of robot state, teleop, auto, disabled, test any state but off.
def update_dash(roboSelf): 
	wp.SmartDashboard.putNumber("Gyro:",round(roboSelf.gyro.getAngle(), 2))
	wp.SmartDashboard.putNumber("Right Encoder:",roboSelf.encdRight.get())
	wp.SmartDashboard.putNumber("Left Encoder:",roboSelf.encdLeft.get())
	wp.SmartDashboard.putBoolean("Sensor:",roboSelf.intakeSensor.get())
	Timer(0.1, update_dash, [roboSelf]).start()

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
		self.extIntakeMotor = wp.VictorSP(7)
		self.liftMotor = wp.VictorSP(8)
		self.encdLeft = wp.Encoder(0, 1)
		self.encdRight = wp.Encoder(2,3)
		self.gyro = wp.AnalogGyro(0, center = None, offset = None)
		self.compressor = wp.Compressor()
		self.shifter = wp.DoubleSolenoid(0,1)
		self.extIntakeSol = wp.DoubleSolenoid(2,3)
		self.ptoSol = wp.DoubleSolenoid(4,5)
		self.stick = wp.Joystick(0)
		self.stick2 = wp.Joystick(1)
		self.stick3 = wp.Joystick(2)
		self.intakeSensor = wp.DigitalInput(4)
		self.autoTime = wp.Timer()
		self.intakeTime = wp.Timer()
		
		#calibrate gyro
		self.gyro.calibrate() 
		
		#update dashboard
		update_dash(self)
				
		wp.SmartDashboard.putBoolean("Auto1:", False)
		wp.SmartDashboard.putBoolean("Auto2:", False)
		wp.SmartDashboard.putNumber("pos 1:", 9825)
		wp.SmartDashboard.putNumber("pos 2:", 40)
		wp.SmartDashboard.putNumber("pos 3:", 6550)
		wp.SmartDashboard.putNumber("pos 5:", 6000)
	def autonomous(self):
		self.gyro.reset()
		self.encdLeft.reset()
		self.encdRight.reset()
		rSide = 0
		lSide = 0
		straightAngle = 0
		
		turnGain = 40
		straitGain = 43
		
		pos1 = wp.SmartDashboard.getNumber("pos 1:", 9825)
		pos2 = wp.SmartDashboard.getNumber("pos 2:", 40)
		pos3 = wp.SmartDashboard.getNumber("pos 3:", 6550)
		pos5 = wp.SmartDashboard.getNumber("pos 5:", 6000)
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
		while self.isAutonomous() and self.isEnabled():
			if(auto1):
				if(abs(self.encdLeft.get()) < pos1 and abs(self.encdRight.get()) < pos1 and stage1):  # 
					setR, setL = rf.gyroFunc(self.gyro.getAngle(), 0, -0.65, straitGain)
					extIntakeSet = 2
					stage2 = True
				elif(self.gyro.getAngle() < pos2 and stage2): #abs(self.encdLeft.get()) < pos2 and
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
					stage3 = False
				self.extIntakeSol.set(extIntakeSet)
				wp.SmartDashboard.putBoolean("Auto2:", False)
				
			if(auto2):
				if(abs(self.encdRight.get()) < pos5): 
					setR, setL = rf.gyroFunc(self.gyro.getAngle(), 0, -0.9, straitGain)                 #USE FOR DRIVING STRAIGHT OVER DEFENCE
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
			
			wp.SmartDashboard.putNumber("Right Motor:", setR)
			wp.SmartDashboard.putNumber("Left Motor:", setL)
			
	def disabled(self):
		pass

	def operatorControl(self):
		past2 = False #used for fliping drive train
		flipVar = False
		
		#reset encoders
		self.encdRight.reset()
		self.encdLeft.reset()
		self.gyro.reset()
		
		#Gain Tuning
		dtGain = 0.075 
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
		while self.isOperatorControl() and self.isEnabled():
			#output to dashboard
			joyValY = self.stick.getY()
			joyValX = self.stick.getX()
			gyroButton = self.stick.getRawButton(8)
			ptoDisengage = self.stick.getRawButton(10)
			ptoEngage = self.stick.getRawButton(11)
			
			joyVal2 = self.stick2.getY()
			driveSideButton = self.stick2.getRawButton(2)
			lowButton = self.stick2.getRawButton(10)
			highButton = self.stick2.getRawButton(11)
			
			extIntakeBackward = self.stick3.getRawButton(1)
			extIntakeOutButton = self.stick3.getRawButton(6)
			extIntakeInButton = self.stick3.getRawButton(7)
			compressorButton = self.stick3.getRawButton(8)
			intakeForward = self.stick3.getRawButton(10) 
			intakeBackward = self.stick3.getRawButton(11)

			if (past2 == False and driveSideButton == True):
				flipVar = not flipVar
			past2 = driveSideButton
			
			#Used to run tank drive
			rightM, leftM = rf.tank(joyValY, joyVal2)
			
			#used to flip side of tank
			rSide, lSide = rf.flip(flipVar, rightM, leftM) 
			
			#Intake
			intakeMotorSpeed = 0
			
			if( previousIntake == False and intakeForward == True):
				intakeIsEnabled = not intakeIsEnabled

			if(intakeIsEnabled):
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
				
			##This sets our dead band on the joystick
			setR = rf.deadband(rSide, dtGain)
			setL = rf.deadband(lSide, dtGain)
			
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
			wp.SmartDashboard.putNumber("Right Motor:", setR)
			wp.SmartDashboard.putNumber("Left Motor:", setL)

			wp.Timer.delay(0.005)   # wait 5ms to avoid hogging CPU cycles

if __name__ == '__main__':
    wp.run(MyRobot)
