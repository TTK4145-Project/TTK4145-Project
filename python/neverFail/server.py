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
		if elevators == None:
			print "Setting up new system"
			self.elevators = elevator_system.System(self.send_to)
		else:
			print "Restoring old system"
			self.elevators = elevators
			self.elevators.set_send(self.send_to)

		if elevator_hardware == None:
			self.elevator_hardware = elevator_client.Client(self.send)
		else:
			self.elevator_hardware = elevator_hardware

	def delete(self):
		self.running = False
		if self.listen_thread_udp != None:
			print "Joining"
			self.listen_thread_udp.join(self.timeout*2)
			if self.listen_thread_udp.isAlive(): print "Failed to kill thread"
			else: print "Successfully killed thread"
		else:
			if redundancy.DEBUG: print "No thread"

	def start(self):
		self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		self.udp.bind(('', self.UDPport))
		self.udp.setblocking(0)

		self.listen_thread_udp = threading.Thread(target=self.server_udp_listener)
		self.listen_thread_udp.start()

		self.ticker_thread = threading.Thread(target=self.ticker)
		self.ticker_thread.start()

		while self.running: self.listen_thread_udp.join(0.5) # Temporary

	def server_udp_listener(self):
		while self.running:
			result = select.select([self.udp], [], [], self.timeout)
			if len(result[0]) == 0: continue
			msg, address = result[0][0].recvfrom(self.bufSize)
			print msg, " from ", address

			if address[0] == self.my_ip: continue

			if msg != self.broadcast_message:
				print "Wrong message received, not an elevator"
				continue

			tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			tcp.settimeout(redundancy.timeout)
			while not self.client_mutex.testandset(): sleep(0.1)
			try:
				tcp.connect((address[0], self.TCPport))

				print "Connected to", address[0]
				tcp.send(self.broadcast_answer)
				print "Client_synch:", self.client_synch
				print "address:", address
				self.client_synch[address[0]] = False
				if self.my_ip == None:
					self.my_ip = tcp.getsockname()[0]
					self.client_list[self.my_ip] = None
					self.client_synch[self.my_ip] = True
					self.send_queue[self.my_ip] = []
				self.send_queue[address[0]] = []
				self.client_list[address[0]] = tcp
				self.elevators.client_reconnected(address[0]) # Call tricode client connected
				self.client_mutex.unlock()
			except:
				self.client_mutex.unlock()
				print traceback.print_tb(sys.exc_info()[2])
				print sys.exc_info()[0]
				print "Failed to connect to", address[0]
				continue

	def ticker(self):
		while self.running:
			sleep(0.5)
			if not len(self.client_list.values()): continue
			# Synchronize

			while not self.client_mutex.testandset(): sleep(0.1)
			for client in self.client_list:
				if client == self.my_ip: # No synchronization required
					try:
						for command in self.send_queue[client]:
							self.elevator_hardware.recv(msg)
							pass # Call tricode recv(msg)
					except AttributeError:
						print "NoneType again :("
					continue

				conn = self.client_list[client]

				if conn == None: continue

				try:
					# If commands, pad with those in send
					if not len(self.send_queue[client]): conn.send(redundancy.synchronize_prefix + pickle.dumps((self.client_synch, self.elevators)))
					else: 
						msg = redundancy.synchronize_prefix + pickle.dumps((self.client_synch, self.elevators)) + redundancy.command_prefix
						for command in self.send_queue[client]:
							msg += command + redundancy.command_split
						msg = msg[:-len(redundancy.command_split)]
						conn.send(msg)
						self.send_queue[client] = []
					msg = conn.recv(redundancy.bufSize)
					if not msg.startswith(redundancy.ack_prefix):
						print "Received:", msg
						raise Exception("Not ack")
					if len(msg) > len(redundancy.ack_prefix):
						msg = msg[len(redundancy.ack_prefix):]
						for event in msg.split(redundancy.event_split):
							self.elevators.recv(event, client)
							pass # Call tricode recv(msg, client)
					self.client_synch[client] = True
				except:
					self.client_list[client] = None
					self.client_synch[client] = False
					print "Client dropped: ", client, "Cause:", sys.exc_info()[0], traceback.print_tb(sys.exc_info()[2])
					self.elevators.client_disconnected(client)
					# Call tricode client dropped
			for message in self.self_recv_queue:
				self.elevators.recv(message, self.my_ip)
			self.client_mutex.unlock()

	def send(self, message):
		self.self_recv_queue.append(message)
		pass # Call tricode recv(msg)

	def send_to(self, message, to):
		self.send_queue[to].append(message)

