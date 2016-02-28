#!/usr/bin/env python3

import wpilib as wp
import time as tm
from networktables import NetworkTable

def tank(joyValY, joyValX):
	return joyValY, joyValX

def arcade(joyValY, joyValX):
	L = joyValY - joyValX
	R = joyValY + joyValX
	return L, R

def flip(flip, jY1, jY2):
	if (flip):
		jY1 = jY1 * -1
		jY2 = jY2 * -1
		return jY2, jY1
		
	return jY1, jY2

def driveTypeFunc(past, driveType, driveTypeButton):
	if (past == False and driveTypeButton):
		driveType = not driveType
		
	past = driveTypeButton
	
def goToArmPos(currentPos, wantedPos, gain):
	motSpeed = (currentPos - wantedPos) / gain
	return motSpeed
	
class MyRobot(wp.SampleRobot):


	def robotInit(self):
		'''Robot initialization function'''
		self.motorFrontRight = wp.VictorSP(1)
		self.motorBackRight = wp.VictorSP(3)
		self.motorMiddleRight = wp.VictorSP(5)
		self.motorFrontLeft = wp.VictorSP(2)
		self.motorBackLeft = wp.VictorSP(4)
		self.motorMiddleLeft = wp.VictorSP(6)
		self.arm = wp.VictorSP(7)
		self.encd = wp.Encoder(1, 2)
		self.stick = wp.Joystick(1)
		self.stick2 = wp.Joystick(2)
		self.compressor = wp.Compressor()
		self.high = wp.Solenoid(1)
		self.low = wp.Solenoid(2)
		self.smartDs = wp.SmartDashboard() #the smart dashboard communication

	def autonomous(self):
		begin = tm.clock()
		while self.isAutonomous() and self.isEnabled():
			while(tm.clock() <= (begin + 5) ):
				self.motorFrontRight.set(.5)
				self.motorBackRight.set(.5)
				self.motorMiddleRight.set(.5)
				self.motorBackLeft.set(-.5)
				self.motorFrontLeft.set(-.5)
				self.motorMiddleLeft.set(-.5)
				
			self.motorFrontRight.set(0)
			self.motorBackRight.set(0)
			self.motorMiddleRight.set(0)
			self.motorFrontLeft.set(0)
			self.motorBackLeft.set(0)
			self.motorMiddleLeft.set(0)
			'''Put robot aton hereish'''

	def disabled(self):
		pass

	def operatorControl(self):
		past = False
		driveType = False
		past2 = False
		flipVar = False
		past3 = False
		compressor = False
		highOn = True
		lowOn = False
		self.encd.reset()
		gain = 100
		wantedArmPos = 90
		encval = 0
		
		while self.isOperatorControl() and self.isEnabled():
			#output to dashboard
			currentArmPos = self.encd.get() 
			joyValY = self.stick.getY()
			joyValX = self.stick.getX()
			joyVal2 = self.stick2.getY()
			driveTypeButton = self.stick.getRawButton(3)
			driveSideButton = self.stick.getRawButton(2)
			compressorButton = self.stick.getRawButton(4)
			highButton = self.stick.getRawButton(6)
			lowButton = self.stick.getRawButton(7)
			
			#toggle drivetype button
			if (past == False and driveTypeButton == True):
				driveType = not driveType
				
			past = driveTypeButton

			#toggle driveside button
			if (past2 == False and driveSideButton == True):
				flipVar = not flipVar
				
			past2 = driveSideButton
			
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
				
			
			if( driveType):
				rightM, leftM = tank(joyValY, joyVal2)
			else:
				rightM, leftM = arcade(joyValY, joyValX)
			
			print (self.encd.get()) 
			armSpeed = goToArmPos(currentArmPos, wantedArmPos, gain)
			rSide, lSide = flip(flipVar, rightM, leftM)
			self.motorFrontRight.set(rSide)
			self.motorBackRight.set(rSide)
			self.motorMiddleRight.set(rSide)
			self.motorFrontLeft.set(lSide * -1)
			self.motorBackLeft.set(lSide * -1)
			self.motorMiddleLeft.set(lSide * -1)
			self.arm.set(armSpeed)
			self.high.set(highOn)
			self.low.set(lowOn)
			#smartdashboard
			self.smartDs.putString("SmartDashboard/DB/String 0", "Encoder Value: " + str(self.encd.get()))
			self.smartDs.putString("SmartDashboard/DB/String 1", "testing thing: " + "whatever")
			wp.Timer.delay(0.005)   # wait 5ms to avoid hogging CPU cycles

if __name__ == '__main__':
    wp.run(MyRobot)
