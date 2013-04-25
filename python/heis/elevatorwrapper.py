from driver import Driver
from channels import *
from functools import partial
from time import sleep


class ElevatorWrapper:
    topFloor = 3
    botFloor = 0

    def __init__(self):
        self.elevator = Driver()

        self.direction = 0
        self.lastFloor = self.getFloor() if self.getFloor() != None else -1
        self.destination = 0
        self.externalFloorListener = None
        self.stop = self.elevator.stop

        for i, floor in enumerate(INPUT.SENSORS):
            self.elevator.addListener(floor, partial(self.floorListener, i))

        addListener = self.elevator.addListener

        addListener(INPUT.STOP, self.stopstruction)
        addListener(INPUT.OBSTRUCTION, self.stopstruction)

    def moveToFloor(self, floor):
        if self.elevator.readChannel(INPUT.OBSTRUCTION):
            print "Obstruction"
            return
        if floor > self.topFloor:
            print "Too much floor: %i > %i , WAT" % (floor, self.topFloor)
            return
        print "Moving to floor", floor
        if floor > self.lastFloor:
            print "Going up"
            self.elevator.move(OUTPUT.MOTOR_UP)
            self.direction = 1
        elif floor < self.lastFloor:
            print "Going down"
            self.elevator.move(OUTPUT.MOTOR_DOWN)
            self.direction = 0
        else:
            print "Open doors"
        self.destination = floor

    def floorListener(self, floor, en, to): # TODO: en, to
        print "At floor", floor

        if floor == self.destination and self.floorListener == None:
            print "At destination"
            self.elevator.stop()
        elif floor >= self.topFloor and self.direction == 1:
            print "Stop it! (top)", floor, self.topFloor, self.direction
            self.elevator.stop()
        elif floor <= self.botFloor and self.direction == 0:
            print "Stop it! (bot)", floor, self.botFloor, self.direction
            self.elevator.stop()

        """if self.lastFloor < floor: self.direction = 1
        elif self.lastFloor > floor: self.direction = 0
        else: print "derp" """

        self.lastFloor = floor;
	
	print type(floor)
	self.elevator.setFloorIndicator(floor)

        self.externalFloorListener(floor)

    def buttonListener(self, where, what, floor, en, to): #TODO en, to
        print where, what, floor
        if where == "in":
            self.moveToFloor(floor)
        elif where == "out":
            if what == "up":
                self.moveToFloor(floor)
            elif what == "down":
                self.moveToFloor(floor)
        else:
            raise ValueError("Invalid \"where\"")

    def stopstruction(self, en, to): # TODO: en, to
        self.elevator.stop()
        self.lastFloor = self.lastFloor + (0.5 if self.direction else -0.5)
        print "Stopped, now at", self.lastFloor

    def isObstructed(self):
        return self.elevator.readChannel(INPUT.OBSTRUCTION)

    def down(self):
        self.elevator.move(OUTPUT.MOTOR_DOWN)
        sleep(2.0)
        self.elevator.stop()

    def getFloor(self):
        return self.elevator.getCurrentFloor()

    def addButtonListener(self, listener):
        addListener = self.elevator.addListener
        addListener(INPUT.FLOOR_UP1, partial(listener, "out", "up", 0))
        addListener(INPUT.FLOOR_UP2, partial(listener, "out", "up", 1))
        addListener(INPUT.FLOOR_UP3, partial(listener, "out", "up", 2))

        addListener(INPUT.FLOOR_DOWN2, partial(listener, "out", "down", 1))
        addListener(INPUT.FLOOR_DOWN3, partial(listener, "out", "down", 2))
        addListener(INPUT.FLOOR_DOWN4, partial(listener, "out", "down", 3))

        addListener(INPUT.FLOOR_COMMAND1, partial(listener, "in", "", 0))
        addListener(INPUT.FLOOR_COMMAND2, partial(listener, "in", "", 1))
        addListener(INPUT.FLOOR_COMMAND3, partial(listener, "in", "", 2))
        addListener(INPUT.FLOOR_COMMAND4, partial(listener, "in", "", 3))

    def addFloorListener(self, listener):
        self.externalFloorListener = listener
		
