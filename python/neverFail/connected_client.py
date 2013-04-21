from redundancy import redundancy
import package_manager
import threading
from collections import deque

class connected_client:
	conn = None
	recv_buffer = deque()
	running = True
	manager = None
	connected = True

	listen_thread = None

	def __init__(self, conn):
		self.conn = conn
		self.manager = package_manager.package_manager(self.recv_buffer)
		self.start()

	def start(self):
		self.running = True
		self.listen_thread = threading.Thread(target=self.listener)
		self.listen_thread.start()

	def listener(self):
		while self.running:
			read, write, error = select.select([conn], [], [], redundancy.timeout)
			if not len(read): continue

			try:
				msg = self.conn.recv(redundancy.bufSize)
				if not len(msg): raise 1
				print "Received", self.manager.raw_parse(msg), "package(s)"
			except:
				self.connected = False
				self.running = False


