import socket, threading, select, pickle, sys
from time import sleep
from redundancy import redundancy
import elevator_client
import time
import traceback

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

	elevator_hardware = None

	def __init__(self):
		self.elevator_hardware = elevator_client.Client(self.send)

	def delete(self):
		self.running = False
		if self.listen_thread != None:
			print "Joining"
			self.listen_thread.join(self.timeout*2)
			if self.listen_thread.isAlive(): print "Failed to kill thread"
			else: print "Successfully killed thread"
		else: print "No thread"

	def delete_driver(self):
		if self.elevator_hardware:
			self.elevator_hardware.delete()

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
			print "Already running?"
			return 2 # Probably already running


		# Listen for answer for 5 * timeout seconds
		for i in range(5):
			# Broadcast message
			self.udp.sendto(self.broadcast_message, ('255.255.255.255', self.UDPport)) # Broadcast to see if there are other elevators

			read, write, error = select.select([self.tcp], [], [], self.timeout/3)
			if len(read) > 0: break

		if len(read) == 0:
			print "No answer"
			return 1 # Noone answered

		connaddr = [None, None]

		# Someone is waiting to connect, start a thread to accept the connection
		accept_thread = threading.Thread(target=self.client_listener, args=(connaddr,))
		accept_thread.start()
		accept_thread.join(self.timeout)

		if connaddr[0] == None:
			print "Server did not connect to me"
			return 2 # Could not establish a connection to the other end

		conn, addr = connaddr[0], connaddr[1]

		msg = conn.recv(self.bufSize)
		print "Received:", msg, "from", addr

		if msg != self.broadcast_answer:
			print "Wrong message received:", msg
			return 1 # Wrong message received, they are not elevators
		self.server[0] = addr[0]
		self.server[1] = conn

		conn.settimeout(redundancy.timeout)

		self.my_address = conn.getsockname()[0]
		print "My address:", self.my_address

		print "Connected"

		self.tcp.close() # Stop listening for connections

		# Enter client code
		self.running = True
		self.listen_thread = threading.Thread(target=self.message_listener)
		self.listen_thread.start()

		while self.running: self.listen_thread.join(0.5)

		return 0

	def client_listener(self, connaddr):

		conn, addr = None, None

		print "Listening"
		try:
			conn, addr = self.tcp.accept()
		except:
			print "Fail accept:"
			print sys.exc_info()[0]
			print traceback.print_tb(sys.exc_info()[2])

		connaddr[0] = conn
		connaddr[1] = addr

	def message_listener(self):
		idletime = time.time()
		while self.running:
			if time.time() - idletime > redundancy.timeout * 2.0:			# Checking for server timeout
				print "Timeout!"
				self.running = False										# Make loop stop at next iteration
				threading.Thread(target=self.relocate_server).start()		# Start thread for reconnection / relocation of server
				break
			sleep(0.1)
			try:
				read, write, error = select.select([self.server[1]], [], [], self.timeout)

				if not len(read): continue

				conn = read[0] 												# Convenience variable

				msg = conn.recv(self.bufSize)
				if not len(msg): 
					conn.close()
					raise Exception("Empty message received")

				if not msg.startswith(redundancy.synchronize_prefix):		# Check that we are receiving a synchronization
					conn.close()
					raise Exception("Not a synchronization")

				msg = msg[len(redundancy.synchronize_prefix):] 				# Strip away the prefix

				synch = None
				commands = None

				if msg.find(redundancy.command_prefix) != -1:				# If message contains commands
					synch, commands = msg.split(redundancy.command_prefix) 	# Split message
				else:
					synch = msg 											# There were no commands, only synch
				self.server_synch = pickle.loads(synch) 					# Save the synchronized data

				if commands != None:										# If we got commands
					for command in commands.split(redundancy.command_split):# Iterate over commands
						self.elevator_hardware.recv(command) 				# Send commands to local elevator

				if not len(self.send_queue): 								# If we have no pending events from local elevator
					conn.send(redundancy.ack_prefix)						# Just send a basic ack
				else:
					msg = redundancy.ack_prefix
					for event in self.send_queue:							# For each pending event from local elevator
						msg += event + redundancy.event_split 				# Pad message with event and splitter
					msg = msg[:-len(redundancy.event_split)]				# Remove last splitter

					conn.send(msg)											# Send ack with events to server
					self.send_queue = []									# Empty the send queue
				idletime = time.time() 										# Reset the timeout counter
			except:
				print "Read fail:", sys.exc_info()[1]
				print traceback.print_tb(sys.exc_info()[2])
				print sys.exc_info()[1]
				self.running = False 										# Make the loop end next iteration
				threading.Thread(target=self.relocate_server).start() 		# Start a thread for reconnection / relocation of server

	def relocate_server(self):
		# First just try to reconnect
		print "Lost connection, trying to reconnect"
		status = self.start()
		if status:
			# No connection, restore mode
			self.delete()
			client_synch = self.server_synch[0]

			for client in client_synch:										# Iterate over connected clients
				if client_synch[client] and client != self.server[0]: 		# Check that client is synchronized and not the server that crashed
					if client == self.my_address: 							# Is it me?
						self.alive = False									# Killing me(client), trying to take over as server in main.py
						break
					else:
						status = self.start() 								# Trying to connect to new server
						if status:
							print "Failed to connect, trying next in line", status
							self.delete()
						else: 
							break

	def send(self, message):
		self.send_queue.append(message) 									# Append event to outgoing queue to be processed by message_listener



