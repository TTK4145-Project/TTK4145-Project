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
            self.send_to()

            if src in self.active_orders:
                self.send_to('update,%s' % msg[1])
            else:
                self.send_to('goto,%s' % msg[1], src)

        elif msg[0] == 'out':
            # pick an elevat0r
            working_elevator = self.get_closest_elevator(msg[1])

            self.send_to('light,%s' % msg[1], working_elevator)

            self.send_to('goto,%s' % msg[1], working_elevator)

        elif msg[0] == 'update':
            pass

        elif msg[0] == 'stop':
            pass

        elif msg[0] == 'obstruction':
            pass

            # self.send_to("light,floor", src)
            # self.send_to("goto,floor", src)

    def get_closest_elevator(self, floor):
        pass

    def client_disconnected(self, src):
        if src in self.elevators:
            self.inactive_elevators.append = src
            del self.elevators[self.elevators.index(src)]

    def client_reconnected(self, src):
        if src in self.inactive_elevators:
            self.elevators.append(src)
            del self.inactive_elevators[self.inactive_elevators.index(src)]