import socket, threading, select, pickle
from time import sleep

class redundancy:
	UDPport = 54545
	TCPport = 54544
	bufSize = 1024
	timeout = 1.0

	broadcast_message = "I am elevator"
	broadcast_answer  = "We are elevators"

	udp = None
	tcp = None

	client_list = dict()

	listen_thread = None
	running = True

	def __init__(self):
		self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	def delete(self):
		self.running = False
		if self.listen_thread != None:
			print "Joining"
			self.listen_thread.join(self.timeout*2)
			if self.listen_thread.isAlive(): print "Failed to kill thread"
			else: print "Successfully killed thread"
		else: print "No thread"


	def server(self):
		self.udp.bind(('', self.UDPport))
		self.udp.setblocking(0)

		address = None

		self.listen_thread = threading.Thread(target=self.server_listener)
		self.listen_thread.start()

		while self.running:
			result = select.select([self.udp], [], [], self.timeout)
			if len(result[0]) == 0: continue
			msg, address = result[0][0].recvfrom(self.bufSize)
			print msg, " from ", address

			if msg != self.broadcast_message:
				print "Wrong message received, not an elevator"
				continue

			tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			tcp.connect((address[0], self.TCPport))
			self.client_list[address[0]] = tcp

			print "Connected to", address[0]
			tcp.send(self.broadcast_answer)




		# print "Connecting"
		# self.tcp.connect((address[0], self.TCPport))
		# print "Sending to "
		# self.tcp.send("Hello there!")
		# self.tcp.close()

	def client(self): # Trying to connect to existing network

		self.udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

		self.tcp.bind(('', self.TCPport))
		self.tcp.listen(1)

		self.udp.sendto(self.broadcast_message, ('255.255.255.255', self.UDPport)) # Broadcast to see if there are other elevators

		for i in range(3):
			read, write, error = select.select([self.tcp], [], [], self.timeout)
			if len(read) > 0: break

		if len(read) == 0: return 1 # Noone answered

		connaddr = [None, None]

		accept_thread = threading.Thread(target=self.client_listener, args=(connaddr,))
		accept_thread.start()
		accept_thread.join(self.timeout)

		if connaddr[0] == None: return 2 # We encountered an error, restart program?

		conn, addr = connaddr[0], connaddr[1]

		#print "Receiving"
		msg = conn.recv(self.bufSize)
		#print "Received:", msg, "from", addr

		if msg != self.broadcast_answer: return 1 # Wrong message received, they are not elevators

		# Enter client code

		# Ask for client list
		conn.send("clients")
		clients = conn.recv(self.bufSize)
		print pickle.loads(clients)



		conn.close()
		return 0

	def server_listener(self):
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
					if msg == "clients":
						conn.send(pickle.dumps(self.client_list.keys()))

				except:
					print "Read fail"
					conn.close()
					del self.client_list[index]


	def client_listener(self, connaddr):

		conn, addr = None, None

		print "Listening"
		conn, addr = self.tcp.accept()

		connaddr[0] = conn
		connaddr[1] = addr

	def message_listener(self):
		pass

	def event_listener(self, event):
		pass

def main():
	print "[b]roadcast or [l]isten? Why not both!"

	heis = redundancy()
	try:
		result = heis.client()
		if result == 1:
			print "Okay, just listen"
			heis = redundancy()
			heis.server()
		elif result == 2: print "DURR"
		else: print "Finished successfully"
	except: print "FAIL"
	heis.delete()
	exit()

main()
