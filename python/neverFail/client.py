import socket, threading, select, pickle
from time import sleep
from redundancy import redundancy

class client:
	UDPport = redundancy.UDPport
	TCPport = redundancy.TCPport
	bufSize = redundancy.bufSize
	timeout = redundancy.timeout

	broadcast_message = redundancy.broadcast_message
	broadcast_answer  = redundancy.broadcast_answer

	udp = None
	tcp = None

	client_list = dict()

	listen_thread = None
	running = True

	def delete(self):
		self.running = False
		if self.listen_thread != None:
			print "Joining"
			self.listen_thread.join(self.timeout*2)
			if self.listen_thread.isAlive(): print "Failed to kill thread"
			else: print "Successfully killed thread"
		else: print "No thread"

	def start(self): # Trying to connect to existing network
		# Initialize sockets
		self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		# Enable broadcast on UDP socket
		self.udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

		# Start listening for answers before sending broadcast
		try:
			self.tcp.bind(('', self.TCPport))
			self.tcp.listen(1)
		except:
			return 2 # Probably already running

		# Broadcast message
		self.udp.sendto(self.broadcast_message, ('255.255.255.255', self.UDPport)) # Broadcast to see if there are other elevators

		# Listen for answer for 3 * timeout seconds
		for i in range(3):
			read, write, error = select.select([self.tcp], [], [], self.timeout)
			if len(read) > 0: break

		if len(read) == 0: return 1 # Noone answered

		connaddr = [None, None]

		# Someone is waiting to connect, start a thread to accept the connection
		accept_thread = threading.Thread(target=self.client_listener, args=(connaddr,))
		accept_thread.start()
		accept_thread.join(self.timeout)

		if connaddr[0] == None: return 2 # Could not establish a connection to the other end

		conn, addr = connaddr[0], connaddr[1]

		#print "Receiving"
		msg = conn.recv(self.bufSize)
		#print "Received:", msg, "from", addr

		if msg != self.broadcast_answer: return 1 # Wrong message received, they are not elevators
		self.client_list[addr[0]] = conn

		print "Connected"

		# Enter client code
		self.listen_thread = threading.Thread(target=self.message_listener)
		self.listen_thread.start()

		# Ask for client list
		conn.send(redundancy.client_request)
		#clients = conn.recv(self.bufSize)
		#print pickle.loads(clients)

		while self.running: self.listen_thread.join(0.5)

		conn.close()
		return 0

	def client_listener(self, connaddr):

		conn, addr = None, None

		print "Listening"
		conn, addr = self.tcp.accept()

		connaddr[0] = conn
		connaddr[1] = addr

	def message_listener(self):
		while self.running:
			sleep(0.1)
			read, write, error = select.select(self.client_list.values(), [], [], self.timeout)

			if len(read) + len(write) + len(error) != 0: print "Event: ", len(read), len(write), len(error)

			for conn in error:
				try:
					index = conn.getpeername()[0]
					del client_list[index]
				except: print "Error fail"

			for conn in read:
				try:
					index = conn.getpeername()[0]
					msg = conn.recv(self.bufSize)
					if len(msg): print "Received command \"", msg, "\""
					else:
						conn.close()
						del self.client_list[index]
						continue

					# call tricode
					if msg.startswith(redundancy.client_answer):
						try:
							msg = msg[len(redundancy.client_answer):]
							clients = pickle.loads(msg)
							for client in clients:
								if not client in self.client_list:
									self.client_list[client] = None
							conn.send(redundancy.ack_prefix + redundancy.client_answer)
							if redundancy.DEBUG: print "Client list:\n", self.client_list
						except: # Failed to interpret client list
							pass

				except:
					print "Read fail"
					conn.close()
					del self.client_list[index]

	def event_listener(self, event):
		pass




