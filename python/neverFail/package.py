from redundancy import redundancy

class package:

	def __init__(self, ack, prefix, message):
		self.ack = ack
		self.prefix = prefix
		self.message = message

	def pack(self):
		return redundancy.package_start + ( redundancy.ack_prefix if self.ack else "" ) + redundancy.messages[self.prefix] + self.message + redundancy.package_end

