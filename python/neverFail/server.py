import socket, threading, select, pickle, traceback, sys
from time import sleep
from redundancy import redundancy
from mutex import mutex
from collections import deque
from package import package

class server:
	UDPport = redundancy.UDPport
	TCPport = redundancy.TCPport
	bufSize = redundancy.bufSize
	timeout = redundancy.timeout

	broadcast_message = redundancy.broadcast_message
	broadcast_answer  = redundancy.broadcast_answer

	udp = None

	client_list = dict()

	listen_thread_tcp = None
	listen_thread_udp = None
	sending_thread = None
	running = True

	receive_lock = mutex()
	send_lock = mutex()
	send_queue = deque()

	receive_buffer = []

	def delete(self):
		self.running = False
		if self.listen_thread_tcp != None:
			print "Joining"
			self.listen_thread_tcp.join(self.timeout*2)
			if self.listen_thread_tcp.isAlive(): print "Failed to kill thread"
			else: print "Successfully killed thread"
		else:
			if redundancy.DEBUG: print "No thread"

	def start(self):
		self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		self.udp.bind(('', self.UDPport))
		self.udp.setblocking(0)

		address = None

		self.listen_thread_tcp = threading.Thread(target=self.server_tcp_listener)
		self.listen_thread_tcp.start()

		self.listen_thread_udp = threading.Thread(target=self.server_udp_listener)
		self.listen_thread_udp.start()

		while self.running: self.listen_thread_udp.join(0.5) # Temporary

	def server_tcp_listener(self):
		while self.running:
			read, write, error = select.select(self.client_list.values(), [], [], self.timeout)

			if len(read) + len(write) + len(error) != 0: print "Event: ", len(read), len(write), len(error)
			else: 
				sleep(0.1)
				continue

			if not self.receive_lock.testandset():
				sleep(0.05)
				continue

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
					if msg == redundancy.client_request:
						print "Sending client list"
						conn.send(redundancy.client_answer + pickle.dumps(self.client_list.keys()))

				except:
					print "Read fail"
					conn.close()
					del self.client_list[index]

			for buffered in self.receive_buffer:
				conn = self.client_list[buffered[0]]
				msg = buffered[1]

				# call tricode
				if msg == redundancy.client_request:
					conn.send(redundancy.client_answer + pickle.dumps(self.client_list.keys()))


			self.receive_lock.unlock()

	def server_udp_listener(self):
		while self.running:
			result = select.select([self.udp], [], [], self.timeout)
			if len(result[0]) == 0: continue
			msg, address = result[0][0].recvfrom(self.bufSize)
			print msg, " from ", address

			if msg != self.broadcast_message:
				print "Wrong message received, not an elevator"
				continue

			tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			tcp.settimeout(redundancy.timeout)
			try:
				tcp.connect((address[0], self.TCPport))
				self.client_list[address[0]] = tcp

				print "Connected to", address[0]
				tcp.send(self.broadcast_answer)
			except:
				print traceback.print_tb(sys.exc_info()[2])
				print sys.exc_info()[0]
				print "Failed to connect to", address[0]

	def send_message(self, target, prefix, message):
		pass

	def send_queue_processor(self):
		while self.running:
			if not len(self.send_queue):
				sleep(0.1)
				continue

			send_mutex_counter = 0
			recv_mutex_counter = 0
			while not self.send_lock.testandset():
				sleep(0.05) # mutex lock
				send_mutex_counter += 1
			while not self.receive_lock.testandset():
				sleep(0.05) # mutex lock
				recv_mutex_counter += 1

			package = self.send_queue.popleft()

			sender = package[0]
			conn = self.client_list[sender]
			prefix = package[1]
			msg = package[2]

			try:
				conn.send(prefix + pickle.dumps(msg))

				while self.running:
					read, write, error = select.select([conn], [], [], redundancy.timeout / 4.0)

					if len(read):
						msg = conn.recv(redundancy.bufSize)
						if msg.startswith(redundancy.ack_prefix):
							if msg[len(redundancy.ack_prefix):].startswith(prefix):
								# All ok
								if len(msg) > len(redundancy.ack_prefix + prefix):
									# Multiple packets received
									print "Multiple packets received, splitting"
									receive_buffer.append((sender, msg[len(redundancy.ack_prefix + prefix)]))
								break
							else: raise 1
						else:
							receive_buffer.append((sender, msg))
					else:
						raise 1 # lost connection
			except:
				conn.close()
				del self.client_list[package[0]]

			self.receive_lock.unlock() # mutex release
			self.send_lock.unlock() # mutex release
			print "Waited %f seconds for send lock", (send_mutex_counter * 0.05)
			print "Waited %f seconds for recv lock", (recv_mutex_counter * 0.05)


	def event_received(self, event):
		pass

	def message_listener(self):
		pass

	def event_listener(self, event):
		pass

