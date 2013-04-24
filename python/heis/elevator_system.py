import pickle

class System:
    def __init__(self, send):

        self.elevators = {}
        self.inactive_elevators = {}

        self.send_to = send

        self.active_orders = {}

        # self.orders = []
        # self.active_orders = {}
        # self.order_queue = []

    def recv(self, msg, src):
        # message contains  whatbutton(in/out/stop/obstruction/floorupdate),whatfloor([1-9]*),others(up/down etc)
        event = msg.rsplit(',')
        # floor = int(event[1])

        if event[0] == 'in':

            self.elevators[src]['work'].append('goto,%i' % int(event[1]))

            #if src in self.active_orders:
                #self.send_to('update,%s' % floor, src)
            #else:
            self.send_to('goto,%i' % int(event[1]), src)

        elif event[0] == 'out':
            direction = 1 if event[2] == 'up' else 0

            if direction == 'up':
                pass
            elif direction == 'down':
                pass

            working_elevator = self.get_elevator(int(event[1]), direction)
            # self.active_orders[working_elevator].append(msg)

            self.send_to('light,%i' % int(event[1]), working_elevator)
            self.send_to('goto,%i' % int(event[1]), working_elevator)

        elif event[0] == 'update':
            print 'I get UPDATE'
            direction = int(event[2])

            self.elevators[src]['direction'] = int(event[1])
            self.elevators[src]['current_floor'] = int(direction)

        elif event[0] == 'stop':
            pass

        elif event[0] == 'obstruction':
            pass

        elif event[0] == 'done':
            work = event[1]+','+event[2]

            if work in self.elevators[src]['work']:
                for i, w in enumerate(self.elevators[src]['work']):
                    if w == work:
                        print "BEFORE DONE"
                        print self.elevators[src]['work']

                        del self.elevators[src]['work'][i]

                        print "AFTER  DONE"
                        print self.elevators[src]['work']

    def remove_event_from_elevator(self):
        pass

    def get_elevator(self, floor, direction):
        my_elevators = iter(self.elevators)
        current_elevator = next(my_elevators)

        for elevator in my_elevators:
            ## do more magic here
            if self.elevators[elevator]['current_floor'] is None or self.elevators[current_elevator]['current_floor'] is None:
                current_elevator = elevator
            else:
                if abs(int(self.elevators[elevator]['current_floor']) - int(floor)) < abs(int(self.elevators[current_elevator]['current_floor']) - int(floor)):
                    # if self.elevators[elevator]['direction'] == self.elevators[current_elevator]['direction'] == direction:
                    current_elevator = elevator

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
        elif src not in self.elevators:
            self.elevators[src] = {'current_floor': None, 'direction': None, 'work': []}

    def get_pickle(self):
        anders = (self.elevators, self.inactive_elevators, self.active_orders)
        return pickle.dumps(anders)

    def put_pickle(self, info):
        anders = pickle.loads(info)
        self.elevators = anders[0]
        self.inactive_elevators = anders[1]
        self.active_orders = anders[2]
