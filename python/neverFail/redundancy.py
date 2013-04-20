
class redundancy:
	UDPport = 54545
	TCPport = 54544
	bufSize = 4096
	timeout = 1.0

	broadcast_message = "I am elevator"
	broadcast_answer  = "We are elevators"

	messages = {
		'client_request' : "I can haz clients?",
		'client_answer' : "Here are the clients:"
	}

	ack_prefix = "Done :)"

	package_start = "^&%pkg_start%&^"
	package_end = "^&%pkg_end%&^"

	DEBUG = True