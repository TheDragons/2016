import wpilib as wp

class joyClass():
    def __init__(self, joystickPort, deadZone = 0.05):
        self._joystickObj = wp.Joystick(joystickPort)
        self._buttonCount = 12 # if (self._joystickObj.getButtonCount() == 0) else self._joystickObj.getButtonCount()
        self._axisCount = 2 # if (self._joystickObj.getAxisCount() == 0) else self._joystickObj.getAxisCount()
        self._deadZone = deadZone
        self._currentVal = self._lastVal = self._lastValueJoy()
        self._currentValJoy = self._lastValJoy = self._lastValueJoystick()
        
    def _inWindow(self, value, window):
        return (value < window) and (value > (-1)*window)
    
    def _smartDeadZone(self, jostickValue, deadZoneWindow, setMotor = 0.0):
        if (jostickValue <= deadZoneWindow*-1):
            return (-1*((1/(1-deadZoneWindow))*(abs(jostickValue)-deadZoneWindow)))
        if (jostickValue >= deadZoneWindow):
            return ((1/(1-deadZoneWindow))*(abs(jostickValue)-deadZoneWindow))
        
        return setMotor
    
    def _lastValueJoy(self):
        lastValues = [0]*(self._buttonCount + 1)
        
        for i in range(1, self._buttonCount):
            lastValues[i] = self._joystickObj.getRawButton(i)

        return lastValues
    
    def _lastValueJoystick(self):
        lastValues = [0]*(self._axisCount)
        
        for i in range(0, self._axisCount):
            lastValues[i] = self.inDeadZoneRawAxis(i)

        return lastValues
    
    def updateClause(self):
        self._lastVal = self._currentVal
        self._currentVal = self._lastValueJoy()
        self._lastValJoy = self._currentValJoy
        self._currentValJoy = self._lastValueJoystick()

    def getButton(self, buttonNum):
        currentVal = self._currentVal[buttonNum] # self._joystickObj.getRawButton(buttonNum)
        return (currentVal == True)
       
    def getButtonEvent(self, buttonNum):
        return (self._lastVal[buttonNum] != self.getButton(buttonNum))
       
    def getButtonRise(self, buttonNum):
        val = ((self._lastVal[buttonNum] == False) and self.getButton(buttonNum))
        return val

    def getButtonFall(self, buttonNum):
        val = ((self._lastVal[buttonNum]) and (self.getButton(buttonNum) == False))
        return val

    def getY(self):
        return self._smartDeadZone(self._joystickObj.getY(), self._deadZone)
    
    def getX(self):
        return self._smartDeadZone(self._joystickObj.getX(), self._deadZone)
    
    def getZ(self):
        return self._smartDeadZone(self._joystickObj.getZ(), self._deadZone)
    
    def getThrottle(self):
        return self._smartDeadZone(self._joystickObj.getThrottle(), self._deadZone)
    
    def getTwist(self):
        return self._smartDeadZone(self._joystickObj.getTwist(), self._deadZone)
    
    def getAxis(self,axis):
        return self._smartDeadZone(self._joystickObj.getAxis(axis), self._deadZone)
    
    def getRawAxis(self,axis):
        return self._smartDeadZone(self._joystickObj.getRawAxis(axis), self._deadZone)
    
    def getEventX(self):
        val = (self._currentValJoy[0] != self._lastValJoy[0])
        return val
        
    def getEventY(self):
        val = (self._currentValJoy[1] != self._lastValJoy[1])
        return val
    
    def getEventZ(self):
        val = (self._currentValJoy[2] != self._lastValJoy[2])
        return val
    
    def getEventTwist(self):
        val = (self._currentValJoy[2] != self._lastValJoy[2])
        return val
    
    def getEventThrottle(self):
        val = (self._currentValJoy[3] != self._lastValJoy[3])
        return val
    
    def getEventAxis(self,axis):
        val = (self._currentValJoy[axis] != self._lastValJoy[axis])
        return val
    
    def getEventRawAxis(self,axis):
        return self.getEventAxis(axis)
    
    def inDeadZoneX(self):
        return self._inWindow(self._joystickObj.getX(), self._deadZone)
    
    def inDeadZoneY(self):
        return self._inWindow(self._joystickObj.getY(), self._deadZone)
    
    def inDeadZoneZ(self):
        return self._inWindow(self._joystickObj.getZ(), self._deadZone)
    
    def inDeadZoneThrottle(self):
        return self._inWindow(self._joystickObj.getThrottle(), self._deadZone)
    
    def inDeadZoneTwist(self):
        return self._inWindow(self._joystickObj.getTwist(), self._deadZone)
    
    def inDeadZoneRawAxis(self, axis):
        return self._inWindow(self._joystickObj.getRawAxis(axis), self._deadZone)
    
    def inDeadZoneAxis(self, axis):
        return self._inWindow(self._joystickObj.getAxis(axis), self._deadZone)
    
    def setDeadZone(self, deadZone):
        self._deadZone = deadZone
        