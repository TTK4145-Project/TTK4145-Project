import socket, select
from time import sleep

UDPport = 54545
TCPport = 54544
bufSize = 1024

broadcast = raw_input("[b]roadcast or [l]isten? ")

cs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

if broadcast == "b":
	cs.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	cs.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

	tcp.bind(('', TCPport))
	tcp.listen(1)
	#tcp.setblocking(0)

	cs.sendto('This is a test', ('255.255.255.255', UDPport))

	conn, addr = None, None

	connected = False
	for i in range(10):
		try:
			print "Listening"
			conn, addr = tcp.accept()
			if conn != None:
				connected = True
				break
			sleep(0.5)
		except: pass
	if connected:
		print "Receiving"
		msg = conn.recv(bufSize)
		print msg
		conn.close()

elif broadcast == "l":
	cs.bind(('', UDPport))
	cs.setblocking(0)

	address = None

	#while True:
	result = select.select([cs], [], [])
	msg, address = result[0][0].recvfrom(bufSize)
	print msg, " from ", address

	#sleep(1.0)
	print "Connecting"
	tcp.connect((address[0], TCPport))
	print "Sending to "
	tcp.send("Hello there!")
	tcp.close()
