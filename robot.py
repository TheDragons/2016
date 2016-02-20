#!/usr/bin/env python3

import wpilib as wp
import robotfuncs as rf
import time as tm
from networktables import NetworkTable as NT
	
class MyRobot(wp.SampleRobot):


	def robotInit(self):
		'''Robot initialization function'''
		self.motorFrontRight = wp.VictorSP(1)
		self.motorBackRight = wp.VictorSP(3)
		self.motorMiddleRight = wp.VictorSP(5)
		self.motorFrontLeft = wp.VictorSP(2)
		self.motorBackLeft = wp.VictorSP(4)
		self.motorMiddleLeft = wp.VictorSP(6)
		self.intakeMotor = wp.VictorSP(7)
		self.encd = wp.Encoder(1, 2)
		self.gyro = wp.AnalogGyro(0, center = None, offset = None)
		self.compressor = wp.Compressor()
		self.high = wp.Solenoid(1)
		self.low = wp.Solenoid(2)
		self.stick = wp.Joystick(1)
		self.stick2 = wp.Joystick(2)
		self.autoTime = wp.Timer()
		self.sd = NT.getTable('SmartDashboard') #the smart dashboard communication

	def autonomous(self):
		self.autoTime.start()
		self.autoTime.reset()
		self.gyro.calibrate()
		rSide = 0
		lSide = 0
		while self.isAutonomous() and self.isEnabled():
			
			if(self.autoTime.get() <= 5):
				print(self.gyro.getAngle())
				rSide, lSide = rf.gyroFunc(self.gyro.getAngle(), 0.5, 0.5)
			else:
				rSide = 0
				lSide = 0
				
			self.motorFrontRight.set(rSide)
			self.motorBackRight.set(rSide)	
			self.motorFrontLeft.set(lSide * -1)
			self.motorBackLeft.set(lSide * -1)

	def disabled(self):
		pass

	def operatorControl(self):
		past = False
		driveType = True
		past2 = False
		flipVar = False
		#reset encoder
		self.encd.reset()
		#calibrate gyro
		self.gyro.calibrate() 
		encval = 0
		dtGain = 0.05
		setR = 0
		setL = 0
		compressor = False
		highOn = True
		lowOn = False
		past3 = False
		while self.isOperatorControl() and self.isEnabled():
			#output to dashboard
			joyValY = self.stick.getY()
			joyValX = self.stick.getX()
			joyVal2 = self.stick2.getY()
			driveTypeButton = self.stick.getRawButton(3)
			driveSideButton = self.stick.getRawButton(2)
			intakeForward = self.stick.getRawButton(11)
			intakeBackward = self.stick.getRawButton(10)
			gyroButton = self.stick.getRawButton(8)
			highButton = self.stick.getRawButton(6)
			lowButton = self.stick.getRawButton(7)
			compressorButton = self.stick.getRawButton(9)

			#toggle drivetype button
			if (past == False and driveTypeButton == True):
				driveType = not driveType
			past = driveTypeButton

			#toggle driveside button
			if (past2 == False and driveSideButton == True):
				flipVar = not flipVar
			past2 = driveSideButton
			
			if( driveType):
				rightM, leftM = rf.tank(joyValY, joyVal2)
			else:
				rightM, leftM = rf.arcade(joyValY, joyValX)
				
			rSide, lSide = rf.flip(flipVar, rightM, leftM) 
			
			#decide which way the intake motor goes
			intakeMotorSpeed = 0
			if( intakeForward):
				intakeMotorSpeed = 0.75
			elif( intakeBackward):
				intakeMotorSpeed = -1
			
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
			
			#reset gyro button
			if(gyroButton):
				self.gyro.calibrate()
		
			self.motorFrontRight.set(setR * -1)
			self.motorBackRight.set(setR * -1)
			self.motorMiddleRight.set(setR)			# Reversed because of the dynamics of the transmission
			self.motorFrontLeft.set(setL)
			self.motorBackLeft.set(setL)
			self.motorMiddleLeft.set(setL * -1)		# Reversed because of the dynamics of the transmission
			self.intakeMotor.set(intakeMotorSpeed)
			
			#smartdashboard
			self.sd.putString("DB/String 0", str(self.encd.get()))
			print("encd: " + str(self.encd.get())) 
			print("gyro: " + str(self.gyro.getAngle()))

			wp.Timer.delay(0.005)   # wait 5ms to avoid hogging CPU cycles

if __name__ == '__main__':
    wp.run(MyRobot)
