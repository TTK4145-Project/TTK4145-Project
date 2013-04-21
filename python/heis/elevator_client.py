import elevatorwrapper
from channels import *
from IO import io


class Client:
    def __init__(self, send):

        self.elevator = elevatorwrapper.ElevatorWrapper()

        self.elevator.addButtonListener(self.button_listener())
        self.elevator.addFloorListener(self.floor_listener())

        # addListener(INPUT.STOP, self.stopstruction)
        # addListener(INPUT.OBSTRUCTION, self.stopstruction)

        self.queue = []
        self.current_floor = None
        self.heading = -1

        # only on moveToFloor
        self.current_action = "goto,2"

        self.send_to = send

    # msg = type,floor
    def recv(self, msg):
        msg = msg.rsplit(',')

        if msg[0] == 'light':
            # turn on current floor light
            io.setBit(OUTPUT.FLOOR_LIGHTS[0], (msg[1] - 1) / 2)

        elif msg[0] == 'goto':
            # up: 0 - down: 1
            self.current_action = 'goto,%s' % msg[1]
            self.heading = 0 if msg[1] > self.current_floor else 1
            self.elevator.moveToFloor(msg[1])

        elif msg[0] == 'update':
            self.queue.append(self.current_action)
            self.current_action = 'goto,%s' % msg[1]

    def button_listener(self, where, what, floor, en, to):
        if where == "in":
            self.send_to('in,%s' % floor)

        elif where == "out":
            if what == "up":
                self.send_to('out,%s,up' % floor)
            elif what == "down":
                self.send_to('out,%s,down' % floor)

    def floor_listener(self, floor):
        self.current_floor = floor
        # print "Current floor", self.current_floor
        self.send_to("update,%s,%s" % (floor, self.heading))