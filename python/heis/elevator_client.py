import elevatorwrapper
from channels import *
from IO import io


class Client:
    def __init__(self, send):
        self.send_event = send

        self.elevator = elevatorwrapper.ElevatorWrapper()

        self.elevator.addButtonListener(self.button_listener)
        self.elevator.addFloorListener(self.floor_listener)

        # addListener(INPUT.STOP, self.stopstruction)
        self.elevator.addListener(INPUT.OBSTRUCTION, self.stopstruction)


        self.current_floor = None
        self.direction = -1

        # only on moveToFloor
        self.current_action = "goto,2,1"

        # reset elevator position on startup
        self.startup()

    def switch_lighting(self, channels, val):
        for chan in channels:
            io.setBit(chan, val)

    def stopstruction(self, en, to): # TODO: en, to
        self.elevator.stop()

    def startup(self):
        self.elevator.moveToFloor(1)

    def delete(self):
        self.elevator.elevator.__del__()

    def recv(self, msg):
        # msg[0]: type - msg[1]: floor
        msg = msg.rsplit(',')

        if msg[0] == 'lighton':
            # turn on floor light
            self.elevator.elevator.setButtonIndicator(int(msg[1]), int(msg[2]), 1)
            pass
        elif msg[0] == 'lightoff':
            # turn off floor light
            self.elevator.elevator.setButtonIndicator(int(msg[1]), int(msg[2]), 0)
            pass
        elif msg[0] == 'light_in_on':
            if int(msg[1]) == 0:
                io.setBit(OUTPUT.LIGHT_COMMAND1, 1)
            elif int(msg[1]) == 1:
                io.setBit(OUTPUT.LIGHT_COMMAND2, 1)
            elif int(msg[1]) == 2:
                io.setBit(OUTPUT.LIGHT_COMMAND3, 1)
            elif int(msg[1]) == 3:
                io.setBit(OUTPUT.LIGHT_COMMAND4, 1)

        elif msg[0] == 'goto':
            io.setBit(OUTPUT.DOOR_OPEN, 0)
            # up: 1 - down: 0
            self.direction = 1 if msg[1] > self.current_floor else 0
            self.current_action = 'goto,%s,%i' % (int(msg[1]), self.direction)
            self.elevator.moveToFloor(int(msg[1]))

            if self.current_floor == int(msg[1]):
                print 'I will not move to %s' % self.current_action
                self.send_event('done,%s' % self.current_action)

    def button_listener(self, where, what, floor, en, to):
        if where == "in":
            self.send_event('in,%s' % floor)
        elif where == "out":
            if what == "up":
                self.send_event('out,%s,up' % floor)
            elif what == "down":
                self.send_event('out,%s,down' % floor)

    def floor_listener(self, floor):
        print "Current floor:", self.current_floor
        if self.current_floor != floor:
            self.current_floor = floor
            self.send_event("update,%s,%s" % (floor, self.direction))
        print "New current floor:", self.current_floor


        # check if current floor is destination and poke system
        if floor == int(self.current_action.rsplit(',')[1]):
            io.setBit(OUTPUT.DOOR_OPEN, 1)

            if floor == 0:
                io.setBit(OUTPUT.LIGHT_COMMAND1, 0)
            elif floor == 1:
                io.setBit(OUTPUT.LIGHT_COMMAND2, 0)
            elif floor == 2:
                io.setBit(OUTPUT.LIGHT_COMMAND3, 0)
            elif floor == 3:
                io.setBit(OUTPUT.LIGHT_COMMAND4, 0)

            print 'I has done work %s' % self.current_action
            self.elevator.stop()
            self.send_event('done,%s' % self.current_action)

    def set_send(self, send):
        self.send_event = send
