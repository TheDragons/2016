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

def gyroFunc(angle, rSide, lSide):
	gain = 20
<<<<<<< HEAD
	R = rSide - (angle / gain)
	L = lSide + (angle / gain)
=======
	R = rSide + (angle / gain)
	L = lSide - (angle / gain)
>>>>>>> 4735bcba74d929739cdf4bb70566b6e0a2eed7a6
	return R, L

def deadband(side, dtGain):
	setSide = (side/abs(side))*((1/(1-dtGain))*(abs(side)-dtGain))
	return setSide

def speedHold(encdRate, wantedRate, gain):
	motSpeed = (encdRate - wantedRate) / gain
	return motSpeed