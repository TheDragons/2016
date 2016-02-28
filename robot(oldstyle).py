#!/usr/bin/env python3

import wpilib as wp
import time as tm


#arcade function
def tank(joyValY, joyVal2):
	return joyValY, joyVal2 
def arcade(joyValY, joyValX):
	L = joyValY - joyValX
	R = joyValY + joyValX
	return L, R
def gyroFunc(angle, rside, lside):
	gain = 20
	R = rside + (angle / gain)
	L = lside - (angle / gain)
	return R, L

class MyRobot(wp.SimpleRobot):


	def RobotInit(self):
		'''Robot initialization function'''
		self.motorFrontRight = wp.Jaguar(1)
		self.motorBackRight = wp.Jaguar(3)
		self.motorFrontLeft = wp.Jaguar(2)
		self.motorBackLeft = wp.Jaguar(4)
		
		self.gyro = wp.Gyro(1)
		self.encd = wp.Encoder(5, 6)
		self.stick = wp.Joystick(1)
		self.stick2 = wp.Joystick(2)
		self.autoTime = wp.Timer()
		#self.smartDs = wp.SmartDashboard() #the smart dashboard communication

	def Autonomous(self):
		self.autoTime.Start()
		self.autoTime.Reset()
		self.gyro.Reset()
		rSide = 0
		lSide = 0
		while self.IsAutonomous() and self.IsEnabled():
			
			if(self.autoTime.Get() <= 5):
				print(self.gyro.GetAngle())
				rSide, lSide = gyroFunc(self.gyro.GetAngle(), 0.5, 0.5)
			else:
				rSide = 0
				lSide = 0
				
			self.motorFrontRight.Set(rSide)
			self.motorBackRight.Set(rSide)	
			self.motorFrontLeft.Set(lSide * -1)
			self.motorBackLeft.Set(lSide * -1)

	def Disabled(self):
		pass

	def OperatorControl(self):
		past = False
		driveType = False
		past2 = False
		flip = False
		

		while self.IsOperatorControl() and self.IsEnabled():
			#output to dashboard
			joyValY = self.stick.GetY()
			joyValX = self.stick.GetX()
			joyVal2 = self.stick2.GetY()
			driveTypeButton = self.stick.GetRawButton(3)
			driveSideButton = self.stick.GetRawButton(2)
			
			
			
			#toggle drivetype button
			if (past == False and driveTypeButton == True):
				driveType = not driveType
			past = driveTypeButton

			#toggle driveside button
			if (past2 == False and driveSideButton == True):
				flip = not flip
			past2 = driveSideButton
			if (flip == True):
				joyValY = joyValY * -1
				joyVal2 = joyVal2 * -1
				joyValX = joyValX * -1
				
			if(flip == True and driveType == True):
				temp = joyValY
				joyValY = joyVal2
				joyVal2 = temp

			if(flip and driveType == False):
				aR, aL = arcade(joyValY, joyValX)
			if(flip == False and driveType == False):
				aR, aL = arcade(joyValX, joyValY)
			
			if (driveType):
				tR, tL = tank(joyValY, joyVal2)
				self.motorFrontRight.Set(tR)
				self.motorBackRight.Set(tR)
				self.motorFrontLeft.Set(tL * -1)
				self.motorBackLeft.Set(tL * -1)
			else:
				self.motorFrontRight.Set(aR)
				self.motorBackRight.Set(aR)
				self.motorFrontLeft.Set(aL * -1)
				self.motorBackLeft.Set(aL * -1)

			


			wp.Wait(0.005)   # wait 5ms to avoid hogging CPU cycles

def run():
        robot = MyRobot()
        robot.StartCompetition()