import pickle

class System:
    def __init__(self, send):
        self.elevators = {}
        self.inactive_elevators = {}
        self.send_to = send
        self.active_orders = {}

    def recv(self, msg, src):
        # message contains  whatbutton(in/out/stop/obstruction/floorupdate),whatfloor([1-9]*),others(up/down etc)
        event = msg.rsplit(',')

        if event[0] == 'in':
            self.elevators[src]['work'].append('goto,%i' % int(event[1]))

            # light up in_light
            self.send_to('light_in_on,%s' % event[1], src)

            if self.elevators[src]['running'] is False:
                self.send_to('goto,%i' % int(event[1]), src)
                self.elevators[src]['destination'] = int(event[1])
            else:
                e_current_floor = int(self.elevators[src]['current_floor'])

                # if order is between destination and current floor -> prioritize it first
                if e_current_floor < int(event[1]):
                    if int(self.elevators[src]['destination']) > int(event[1]):
                        self.send_to('goto,%i' % int(event[1]), src)
                        self.elevators[src]['destination'] = int(event[1])
                elif e_current_floor > int(event[1]):
                    if int(self.elevators[src]['destination']) < int(event[1]):
                        self.send_to('goto,%i' % int(event[1]), src)
                        self.elevators[src]['destination'] = int(event[1])

            self.elevators[src]['running'] = True

        elif event[0] == 'out':
            direction = 1 if event[2] == 'up' else 0

            working_elevator = self.get_elevator(int(event[1]), int(direction))

            self.elevators[working_elevator]['work'].append('goto,%i' % int(event[1]))

            # turn light on for all clients on given floor
            for elevator in self.elevators:
                self.send_to('lighton,%i' % int(event[1]), elevator)

            self.send_to('goto,%i' % int(event[1]), working_elevator)
            self.elevators[working_elevator]['destination'] = int(event[1])
            self.elevators[working_elevator]['running'] = True

        elif event[0] == 'update':
            self.elevators[src]['direction'] = int(event[2])
            self.elevators[src]['current_floor'] = int(event[1])

        elif event[0] == 'done':
            work = event[1]+','+event[2]

            # turn light off for all clients on given floor
            for elevator in self.elevators:
                self.send_to('lightoff,%i' % int(event[2]), elevator)

            if work in self.elevators[src]['work']:
                self.elevators[src]['work'] = filter (lambda w: w != work, self.elevators[src]['work'])
                #for i, w in enumerate(self.elevators[src['work']]):
                #    if w == work:
                #        del self.elevators[src]['work'][i]
                # delete any records of finished work (removes duplicates from queue/history)
                # del self.elevators[src]['work'][self.elevators[src]['work'].index(work)]

            # if work list is empty - set the running variable to False, else do next task
            if len(self.elevators[src]['work']) == 0:
                self.elevators[src]['running'] = False
                self.elevators[src]['destination'] = -1
            else:
                self.send_to(self.elevators[src]['work'][-1], src)
                self.elevators[src]['destination'] = int(self.elevators[src]['work'][-1].rsplit(',')[1])

    def get_elevator(self, floor, direction):
        my_elevators = iter(self.elevators)
        current_elevator = next(my_elevators)

        for elevator in my_elevators:
            ## do more magic here
            if self.elevators[elevator]['current_floor'] is None or self.elevators[current_elevator]['current_floor'] is None:
                current_elevator = elevator
            else:
                diff_elevator = abs(int(self.elevators[elevator]['current_floor']) - int(floor))
                diff_current_elevator = abs(int(self.elevators[current_elevator]['current_floor']) - int(floor))

                if diff_elevator < diff_current_elevator:
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
            self.elevators[src] = {'current_floor': -1, 'direction': None, 'destination': -1, 'running': False, 'work': []}

    def get_pickle(self):
        p = (self.elevators, self.inactive_elevators, self.active_orders)
        return pickle.dumps(p)

    def put_pickle(self, info):
        p = pickle.loads(info)
        self.elevators = p[0]
        self.inactive_elevators = p[1]
        self.active_orders = p[2]
