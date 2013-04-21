from elevatorwrapper import ElevatorWrapper
from time import sleep


class ElevatorSystem:
    def __init__(self):
        self.elevator = ElevatorWrapper()
        self.upOrders = []
        self.downOrders = []
        self.inOrders = []
        self.queue = []
        self.heading = -1
        self.floor = -1

        self.elevator.addButtonListener(self.buttonListener)
        self.elevator.addFloorListener(self.floorListener)

    def buttonListener(self, where, what, floor, en, to): # TODO: en, to
        if where == "in":
            if not floor in self.inOrders:
                if self.heading == 1 and floor > self.floor:
                    if not floor in self.queue:
                        self.queue.append(floor)
                elif self.heading == 0 and floor < self.floor:
                    if not order in self.queue:
                        self.queue.append(floor)
                else:
                    self.inOrders.append(floor)
                    self.inOrders.sort()
        elif where == "out":
            if what == "up":
                if not floor in self.upOrders:
                    if self.heading == 1 and floor > self.floor:
                        if not floor in self.queue:
                            self.queue.append(floor)
                    else:
                        self.upOrders.append(floor)
                        self.upOrders.sort()
            elif what == "down":
                if not floor in self.downOrders:
                    if self.heading == 0 and floor < self.floor:
                        if not floor in self.queue:
                            self.queue.append(floor)
                    else:
                        self.downOrders.append(floor)
                        self.downOrders.sort()
        self.updateOrders()

    def updateOrders(self):
        if self.heading == 1:
            for order in self.inOrders:
                if order > self.floor:
                    if order in self.queue:
                        self.inOrders.remove(order)
                    else:
                        self.queue.append(order)
                        self.inOrders.remove(order)
            for order in self.upOrders:
                if order > self.floor:
                    if order in self.queue:
                        self.upOrders.remove(order)
                    else:
                        self.queue.append(order)
                        self.upOrders.remove(order)
        elif self.heading == 0:
            for order in self.inOrders:
                if order < self.floor:
                    if order in self.queue:
                        self.inOrders.remove(order)
                    else:
                        self.queue.append(order)
                        self.inOrders.remove(order)
            for order in self.downOrders:
                if order < self.floor:
                    if order in self.queue:
                        self.downOrders.remove(order)
                    else:
                        self.queue.append(order)
                        self.downOrders.remove(order)
        elif self.heading == -1:
            if len(self.inOrders):
                self.queue.append(self.inOrders.pop(0))
            elif len(self.upOrders):
                self.queue.append(self.upOrders.pop(0))
            elif len(self.downOrders):
                self.queue.append(self.downOrders.pop(0))

        self.queue.sort()

        if self.heading == 0: self.queue.reverse()

        if len(self.queue):
            self.elevator.moveToFloor(self.queue[0])
            self.heading = 0 if self.floor > self.queue[0] else 1

        print self.upOrders, self.downOrders, self.inOrders, self.queue
        print "Heading:", self.heading

    def floorListener(self, floor):
        self.floor = floor
        print "Floor:", floor
        if len(self.queue) and floor == self.queue[0]:
            self.queue.pop(0)

            self.elevator.stop()

            sleep(1.0)

            if len(self.queue):
                self.elevator.moveToFloor(self.queue[0])
                self.heading = 0 if self.floor > self.queue[0] else 1
            else:
                self.heading = -1
                self.updateOrders()
        elif not self.elevator.elevator.moving:
            print "Recovery"
            if len(self.queue): self.elevator.moveToFloor(self.queue[0])
