class System:
    def __init__(self, send):

        self.elevators = {}
        self.inactive_elevators = {}

        self.send_to = send

        # self.order_queue = []
        self.active_orders = {}

        # self.orders = []
        # self.active_orders = {}

    def recv(self, msg, src):
        if src not in self.elevators:
            self.elevators[src]= {'current_floor': None, 'direction': None, 'work': []}

        # message contains  whatbutton(in/out/stop/obstruction/floorupdate),whatfloor([1-9]*),others(up/down etc)
        msg = msg.rsplit(',')

        if msg[0] == 'in':
            floor = msg[1]

            self.elevators[src]['work'].append(msg)

            if src in self.active_orders:
                self.send_to('update,%s' % floor, src)
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
            # self.active_orders[working_elevator].append(msg)

            self.send_to('light,%s' % floor, working_elevator)
            self.send_to('goto,%s' % floor, working_elevator)

        elif msg[0] == 'update':
            self.elevators[src]['direction'] = msg[1]
            self.elevators[src]['current_floor'] = msg[2]

        elif msg[0] == 'stop':
            pass

        elif msg[0] == 'obstruction':
            pass

        elif msg[0] == 'done':
            if src in self.elevators | msg[1] in self.elevators[src]['work']:
                if msg[1] in self.elevators[src]['work']:
                    for i, w in enumerate(self.elevators[src]['work']):
                        if w == msg[1]:
                            del self.elevators[src]['work'][i]



        #self.send_to(current_event, working_elevator)


    def get_elevator(self, floor, direction):
        current_elevator = None
        for elevator in self.elevators:
            if current_elevator is None:
                current_elevator = elevator
                continue

            ## do more magic here
            #if abs(elevator.lastFloor - floor) < abs(current_elevator.lastFloor - floor):
            #    if elevator.direction == current_elevator.direction == direction:
            #        current_elevator = elevator

        return current_elevator

    def set_send(self, send):
        self.send_to = send

    def get_elevator_task(self, elevator):
        pass

    def client_disconnected(self, src):
        if src in self.elevators:
            self.inactive_elevators[src] = self.elevators[src]
            del self.elevators[src]

    def client_reconnected(self, src):
        if src in self.inactive_elevators:
            self.elevators[src] = self.inactive_elevators[src]
            del self.inactive_elevators[src]
        else:
            self.elevators = {'current_floor': None, 'direction': None, 'work': []}