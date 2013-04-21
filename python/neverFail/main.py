from server import server
from client import client
import sys
import traceback
from time import sleep

import signal
def killer(a=None,b=None):
    """Signal handler for Ctrl+C interrupt. Stops elevator before exiting."""
    exit(0)

signal.signal(signal.SIGINT, killer)

def main():
	#print "[b]roadcast or [l]isten? Why not both!"

	print "Looking for already existing network of elevators"

	heis = client()
	try:
		result = 0
		for i in range(1): # Try 3 times to connect
			result = heis.start()

			if result == 2: # 
				print "DURR"
				break

			elif result == 0:
				while heis.alive: sleep(0.2)
				print "Server died, my turn to take over"
				synch = heis.server_synch
				ip = heis.my_address
				heis = server(synch[0], synch[1], ip)
				break

		if result == 1:
			print "I am now master"
			heis = server()
			heis.start()

	except:
		print "FAIL"
		print traceback.print_tb(sys.exc_info()[2])
	heis.delete()
	exit()

main()