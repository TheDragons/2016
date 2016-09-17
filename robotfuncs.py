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

def gyroFunc(currentAngle, holdAngle, speed, gain):
	R = speed + ((currentAngle - holdAngle)/ gain)
	L = speed - ((currentAngle - holdAngle)/ gain)
		
	return R, L
	
def angleFunc(angle, wantedAngle, gain):
	position = (angle - wantedAngle) / gain
	
	if( position < 0.15 and position > 0):
		position = 0.15
		
	if( position > -0.15 and position < 0):
		position = -0.15
		
	return position, (position * -1)
	
def deadband(side, dtGain):
	if ((side <= dtGain*-1) or (side >= dtGain)):
		setSide = (side/abs(side))*((1/(1-dtGain))*(abs(side)-dtGain))
	else:
		setSide = 0
		
	return setSide

def speedHold(encdRate, wantedRate, gain):
	motSpeed = (encdRate - wantedRate) / gain
	return motSpeed