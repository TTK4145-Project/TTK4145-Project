import package
from redundancy import redundancy

class State:
	START = 0
	CONTENT = 1

class package_manager:
	buf = ""

	state = State.START
	buffer_list = None

	def __init__(self, buffer_list):
		self.buffer_list = buffer_list

	def raw_parse(self, message):
		self.buf += message
		count = 0
		while True:
			if self.state == State.START:
				index = self.buf.find(redundancy.package_start)
				if index == 0:
					self.state = State.CONTENT
					self.buf = self.buf[len(redundancy.package_start):]
				elif index == -1: return count
				else:
					self.buf = self.buf[index:]
			if self.state == State.CONTENT:
				index = self.buf.find(redundancy.package_end)
				if index == -1: return count
				if self.package_parse(self.buf[:index]): pass # Error
				else: count += 1
				self.buf = self.buf[index+len(redundancy.package_end):]
				self.state = State.START
			
	def package_parse(self, pack):
		ack = False
		if pack.startswith(redundancy.ack_prefix):
			ack = True
			pack = pack[len(redundancy.ack_prefix):]
		prefix = None
		for index in redundancy.messages:
			if pack.startswith(redundancy.messages[index]):
				prefix = index
				pack = pack[len(redundancy.messages[index]):]
				break
		if prefix == None: return 1 # Fatal error

		pkg = package.package(ack, prefix, pack)
		self.buffer_list.append(pkg)
		return 0
