import socket, thread, time

class Defaults:
    MIN_PORT = 5000
    MAX_PORT = 5010
    HOST_ADDR = '127.0.0.1'

class Network:

    host_addr = Defaults.HOST_ADDR
    port = Defaults.MIN_PORT
    left, left_connected = 0, 0


    def __init__(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        thread.start_new_thread(self.listener, (sock,))

        while 1:
            if self.left_connected:
                try: self.left.send(str(self.port))
                except: self.left_connected = 0
            print self.port
            time.sleep(1.0)


    def listener(self, sock):
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        while True:
            try:
                sock.bind(('', self.port))
                break
            except:
                self.port = self.port + 1 if self.port + 1 <= Defaults.MAX_PORT else Defaults.MIN_PORT

        sock.listen(1)

        while True:
            if self.left_connected == 0:
                try:
                    conn, addr = sock.accept()
                    self.left, self.left_connected = conn, 1
                except:
                    print "bæsj"








    def ping(self, port):
        pass



n = Network()