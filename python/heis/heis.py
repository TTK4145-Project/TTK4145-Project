import driver
from channels import *

snu = 0

def flip(en, to):
	global snu
	snu = 0 if snu else 1

heis = driver.Driver()
heis.addListener(INPUT.SENSOR1, flip)
heis.addListener(INPUT.SENSOR4, flip)

while 1:
	heis.move(OUTPUT.MOTOR_UP, 1000)
	while not snu: pass
	snu = 0
	heis.move(OUTPUT.MOTOR_DOWN, 1000)
	while not snu: pass
	snu = 0
