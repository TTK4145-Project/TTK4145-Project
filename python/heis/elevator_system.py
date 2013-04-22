import pickle

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
        # if src not in self.elevators:
            # self.elevators[src]= {'current_floor': None, 'direction': None, 'work': []}

        # message contains  whatbutton(in/out/stop/obstruction/floorupdate),whatfloor([1-9]*),others(up/down etc)
        msg = msg.rsplit(',')

        if msg[0] == 'in':
            floor = msg[1]

            self.elevators[src]['work'].append('goto,%s' % floor)

            #if src in self.active_orders:
                #self.send_to('update,%s' % floor, src)
            #else:
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
            print 'I get UPDATE'
            self.elevators[src]['direction'] = int(msg[1])
            self.elevators[src]['current_floor'] = int(msg[2])

        elif msg[0] == 'stop':
            pass

        elif msg[0] == 'obstruction':
            pass

        elif msg[0] == 'done':
            print "FRIST:",src
            if src in self.elevators and msg[1]+','+msg[2] in self.elevators[src]['work']:
                for i, w in enumerate(self.elevators[src]['work']):
                    if w == msg[1]+','+msg[2]:
                        print "BEFORE DONE"
                        print self.elevators[src]['work']
                        del self.elevators[src]['work'][i]
                        print "AFTER  DONE"
                        print self.elevators[src]['work']


        #self.send_to(current_event, working_elevator)


    def get_elevator(self, floor, direction):
        current_elevator = None

        for elevator in self.elevators:

            if current_elevator is None:
                current_elevator = elevator
                continue

            print self.elevators
            # print self.elevators[elevator]['current_floor']

            ## do more magic here
            if self.elevators[elevator]['current_floor'] == None:
                current_elevator = elevator
            else:
                if abs(int(self.elevators[elevator]['current_floor']) - floor) < abs(int(self.elevators[current_elevator]['current_floor']) - floor):
                    if self.elevators[elevator]['direction'] == self.elevators[current_elevator]['direction'] == direction:
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
