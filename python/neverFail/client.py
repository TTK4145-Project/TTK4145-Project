import socket, threading, select, pickle, sys
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

	client_list = []
	server = [None, None]
	my_address = None

	listen_thread = None
	running = True

	server_synch = None

	send_queue = []

	alive = True

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


		# Listen for answer for 3 * timeout seconds
		for i in range(3):
			# Broadcast message
			self.udp.sendto(self.broadcast_message, ('255.255.255.255', self.UDPport)) # Broadcast to see if there are other elevators

			read, write, error = select.select([self.tcp], [], [], self.timeout/3)
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
		self.server[0] = addr[0]
		self.server[1] = conn

		self.my_address = conn.getsockname()[0]
		print "My address:", self.my_address

		print "Connected"

		# Enter client code
		self.running = True
		self.listen_thread = threading.Thread(target=self.message_listener)
		self.listen_thread.start()

		# Ask for client list
		#conn.send(redundancy.client_request)
		#clients = conn.recv(self.bufSize)
		#print pickle.loads(clients)

		while self.running: self.listen_thread.join(0.5)

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
			try:
				#print "Server:", self.server
				read, write, error = select.select([self.server[1]], [], [], self.timeout)

				if len(read):
					#print "Event: ", len(read)
					pass
				else: continue

				conn = read[0]

				index = conn.getpeername()[0]
				msg = conn.recv(self.bufSize)
				if len(msg): 
					#print "Received command \"", msg, "\""
					pass
				else:
					conn.close()
					# TODO: Try to take over
					#del self.client_list[index]
					continue

				# call tricode
				if msg.startswith(redundancy.synchronize_prefix):
					try:
						msg = msg[len(redundancy.synchronize_prefix):]
						synch = None
						commands = None
						if msg.find(redundancy.command_prefix) != -1:
							synch, commands = msg.split(redundancy.command_prefix)
						else:
							synch = msg
						self.server_synch = pickle.loads(synch)
						#print "Server synch:", self.server_synch

						if commands != None:
							for command in commands.split(redundancy.command_split):
								pass # Call tricode recv(command)

						if  not len(self.send_queue):
							#print "Sending:", redundancy.ack_prefix
							conn.send(redundancy.ack_prefix)
						else:
							msg = redundancy.ack_prefix
							for event in self.send_queue:
								msg += event + redundancy.event_split
							msg = msg[:-redundancy.event_split]
							print "Sending:", msg
							conn.send(msg)
							self.send_queue = []
						print "Synchronized"
					except:
						# Something failed, try to take over?
						print "Fail inner:", sys.exc_info()[1]
						print traceback.print_tb(sys.exc_info()[2])
						self.running = False
						threading.Thread(target=self.relocate_server).start()
						continue


			except:
				print "Read fail"
				self.running = False
				threading.Thread(target=self.relocate_server).start()
				# TODO: Try to take over
				#del self.client_list[index]

	def relocate_server(self):
		# First just try to reconnect
		print "Lost connection, trying to reconnect"
		status = self.start()
		if status:
			# No connection, restore mode
			client_synch = self.server_synch[0]

			for client in client_synch:
				if client_synch[client]:
					if client == self.my_address:
						alive = False
					else:
						status = self.start()
						if status: print "Failed to connect, trying next in line"





