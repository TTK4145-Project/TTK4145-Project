import socket, sys, thread, time
listenClient, clientConnected = 0, 0
def server(sock, value):
	global clientConnected, listenClient
	thread.start_new_thread(listener, (sock,))
	while 1:
		if clientConnected:
			try: listenClient.send(str(value))
			except: clientConnected = 0
		print value
		value += 1
		time.sleep(1.0)
def listener(sock):
	global clientConnected, listenClient
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	while 1:
		try: 
			sock.bind(('', 1234))
			break
		except socket.error as e: print "Failbind: ", e.strerror
	sock.listen(1)
	while 1:
		if clientConnected == 0:
			try:
				conn, addr = sock.accept()
				listenClient, clientConnected = conn, 1
			except: print "Failconnect"
		else: time.sleep(0.5)
def client(sock, value = -1):
	lastTime = time.time()
	while 1:
		try:
			if time.time() - lastTime > 1.5: break
			temp = sock.recv(1024)
			if len(temp) > 0: lastTime, value = time.time(), int(temp)
		except socket.error: break
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	if value < 0: server(sock, 0)
	server(sock, value + 1)
def main():
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try: sock.connect(("127.0.0.1", 1234))
	except:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server(sock, 0)
		return
	client(sock)
main()