import socket, threading, select, pickle, traceback, sys
from time import sleep
from redundancy import redundancy
from mutex import mutex
from collections import deque
from package import package
import elevator_system
import elevator_client

class server:
	UDPport = redundancy.UDPport
	TCPport = redundancy.TCPport
	bufSize = redundancy.bufSize
	timeout = redundancy.timeout

	broadcast_message = redundancy.broadcast_message
	broadcast_answer  = redundancy.broadcast_answer

	udp = None

	client_mutex = mutex()
	client_list = dict()
	client_synch = dict()

	listen_thread_udp = None
	ticker_thread = None
	running = True

	send_queue = dict()
	self_recv_queue = []

	my_ip = None

	elevators = None
	elevator_hardware = None

	def __init__(self, client_list=[], client_synch=dict(), my_ip=None, elevators=None, elevator_hardware=None):
		for key in client_list:
			self.client_list[key] = None
			self.send_queue[key] = []
		self.client_synch = client_synch
		self.my_ip = my_ip
		self.elevators = elevator_system.System(self.send_to)
		if elevators == None:
			print "Setting up new system"
		else:
			print "Restoring old system"
			self.elevators.put_pickle(elevators)

		# Reuse already initialized driver
		if elevator_hardware == None:
			self.elevator_hardware = elevator_client.Client(self.send)
		else:
			self.elevator_hardware = elevator_hardware
			self.elevator_hardware.set_send(self.send)

	def delete(self): # Method for stopping threads properly
		self.running = False
		if self.listen_thread_udp != None:
			print "Joining"
			self.listen_thread_udp.join(self.timeout*2)
			if self.listen_thread_udp.isAlive(): print "Failed to kill thread"
			else: print "Successfully killed thread"
		else:
			if redundancy.DEBUG: print "No thread"

	def delete_driver(self):
		if self.elevator_hardware:
			self.elevator_hardware.delete()

	def start(self):
		self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		self.udp.bind(('', self.UDPport))								# Listen on all addresses, on port UDPport
		self.udp.setblocking(0)

		self.listen_thread_udp = threading.Thread(target=self.server_udp_listener) # Initialize the UDP listener thread
		self.listen_thread_udp.start()									# Start the UDP listener thread

		self.ticker_thread = threading.Thread(target=self.ticker) 		# Initialize the ticker thread
		self.ticker_thread.start() 										# Start the ticker thread

		while self.running: self.listen_thread_udp.join(0.5) 			# Block

	def server_udp_listener(self):
		while self.running:
			result = select.select([self.udp], [], [], self.timeout)	# Wait for buffered UDP input
			if len(result[0]) == 0: continue 							# Timeout, start listening again

			msg, address = result[0][0].recvfrom(self.bufSize)			# Get address of sender and message

			if address[0] in self.client_list != None and False:
				print "Already connected to", address[0]
				continue

			if address[0] == self.my_ip: continue 						# Received from myself, ignore

			if msg != self.broadcast_message:							# The UDP message was not from our software, ignore
				print "Wrong message received, not an elevator"
				continue

			tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			tcp.settimeout(redundancy.timeout)
			while not self.client_mutex.testandset(): sleep(0.1)
			try:
				tcp.connect((address[0], self.TCPport))					# Connect with tcp to the broadcasting client

				print "Connected to", address[0]
				tcp.send(self.broadcast_answer)							# Send answer to the broadcast
				self.client_synch[address[0]] = False					# Set connected client as not synchronized

				# Block used to get the ip-address used on the interface we received our first
				# message on.
				if self.my_ip == None:
					self.my_ip = tcp.getsockname()[0]					# Get our ip-address from the current connection
					self.client_list[self.my_ip] = None					# Add ourselves to the list of connected clients
					self.client_synch[self.my_ip] = True				# List that we are synchronized (obviously)
					self.send_queue[self.my_ip] = []					# Initialize our send_queue
					self.elevators.client_reconnected(self.my_ip)		# Notify master node (us) that we are connected

				self.send_queue[address[0]] = []						# Initialize send queue for connected client
				self.client_list[address[0]] = tcp 						# Associate the new connection with the client in the list of clients
				self.elevators.client_reconnected(address[0]) 			# Notify master node (us) that client is connected
				self.client_mutex.unlock() 								# Unlock the client list mutex
			except:
				self.client_mutex.unlock() 								# Unlock the client list mutex in case we failed
				print traceback.print_tb(sys.exc_info()[2])
				print sys.exc_info()[0]
				print "Failed to connect to", address[0]
				continue

	def ticker(self):
		while self.running:
			sleep(0.5) # TODO: Try without delay
			if not len(self.client_list.values()): continue

			while not self.client_mutex.testandset(): sleep(0.1) 	# Get mutex for client list before iteration

			synch_package = pickle.dumps((self.client_synch, self.elevators.get_pickle())) # Information to be synchronized to all clients

			for client in self.client_list:							# Iterate over all previously and currently connected clients
				try:
					if client == self.my_ip: 						# Client is local, we can just use local buffers
						for command in self.send_queue[client]:		# Go through all locally buffered commands
							self.elevator_hardware.recv(command)	# Send command to elevator
						self.send_queue[client] = []				# Empty the buffer
						continue									# Continue to next client (no network necessary)

					conn = self.client_list[client]

					if conn == None: continue 						# Disconnected client, do nothing

					if not len(self.send_queue[client]): 			# If there are no pending commands
						conn.send(redundancy.synchronize_prefix + synch_package
					else:
						msg = redundancy.synchronize_prefix + synch_package + redundancy.command_prefix

						for command in self.send_queue[client]: 	# Add all pending commands, pad with splitter string
							msg += command + redundancy.command_split

						msg = msg[:-len(redundancy.command_split)] 	# Remove last splitter string
						conn.send(msg)								# Send message
						self.send_queue[client] = []				# Empty send queue for client

					msg = conn.recv(redundancy.bufSize)				# Receive answer from client

					if not msg.startswith(redundancy.ack_prefix):	# Check if we received correct package
						print "Received:", msg
						raise Exception("Not ack")					# Throw exception if wrong package was received

					if len(msg) > len(redundancy.ack_prefix):		# Check if ack is padded with events
						msg = msg[len(redundancy.ack_prefix):]
						for event in msg.split(redundancy.event_split): # Iterate over all received events
							self.elevators.recv(event, client)		# Call main node with events

					self.client_synch[client] = True				# Mark current connection as synchronized (used when selecting new host)
				except:
					self.client_list[client] = None					# Remove reference to lost connection
					self.client_synch[client] = False				# Mark client as not being synched with server
					print "Client dropped: ", client, "Cause:", sys.exc_info()[0], traceback.print_tb(sys.exc_info()[2])
					print sys.exc_info()[1]
					self.elevators.client_disconnected(client)		# Notify the master node of the disconnected elevator
			
			for message in self.self_recv_queue:					# Iterate over locally buffered events
				self.elevators.recv(message, self.my_ip)			# Send events to local master node
			self.self_recv_queue = []								# Empty local event buffer

			self.client_mutex.unlock() 								# Unlock client list mutex

	def send(self, message):
		self.self_recv_queue.append(message) 						# Add local elevator event to receive queue

	def send_to(self, message, to):
		self.send_queue[to].append(message) 						# Add command from master node to corresponding send queue

