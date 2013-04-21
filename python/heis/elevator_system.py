class System:
    def __init__(self, send):

        self.elevators = []
        self.inactive_elevators = []
        self.send_to = send

        self.active_orders = {}

        # self.orders = []
        # self.active_orders = {}

    def recv(self, msg, src):
        if src not in self.elevators:
            self.elevators.append(src)

        # message contains  whatbutton(in/out/stop/obstruction/floorupdate),whatfloor([1-9]*),others(up/down etc)
        msg = msg.rsplit(',')

        if msg[0] == 'in':
            floor = msg[1]

            if src in self.active_orders:
                self.send_to('update,%s' % floor)
            else:
                self.send_to('goto,%s' % floor, src)

        elif msg[0] == 'out':
            floor = msg[1]
            direction = 1 if msg[2] == 'up' else 0

            if direction == 'up':
                pass
            elif direction == 'down':
                pass

            working_elevator = self.get_elevator(floor, direction)

            self.send_to('light,%s' % floor, working_elevator)
            self.send_to('goto,%s' % floor, working_elevator)

        elif msg[0] == 'update':
            pass

        elif msg[0] == 'stop':
            pass

        elif msg[0] == 'obstruction':
            pass

            # self.send_to("light,floor", src)
            # self.send_to("goto,floor", src)

    def get_elevator(self, floor, direction):
        current_elevator = None
        for elevator in self.elevators:
            if current_elevator is None:
                current_elevator = elevator
                continue

            #if abs(elevator.lastFloor - floor) < abs(current_elevator.lastFloor - floor):
            #    if elevator.direction == current_elevator.direction == direction:
            #        current_elevator = elevator






    def client_disconnected(self, src):
        if src in self.elevators:
            self.inactive_elevators.append = src
            del self.elevators[self.elevators.index(src)]

    def client_reconnected(self, src):
        if src in self.inactive_elevators:
            self.elevators.append(src)
            del self.inactive_elevators[self.inactive_elevators.index(src)]