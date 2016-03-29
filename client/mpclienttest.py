import sys
sys.path.append('c:\python27\lib')

import xmlrpclib
from time import sleep, time

# target upload rate in Hz
targetRate = 12

# according to http://auvsi-suas-competition-interoperability-system.readthedocs.org/en/latest/integration/hints.html
# the server takes at most 0.011 seconds to do its thing
serveTime = 0

def main():
	while True:
		try:
		    server = xmlrpclib.ServerProxy('http://127.0.0.1:9000')
		    alt = 0
		    while True:
		    	initTime = time()
		        alt+=1

		        server.telemetry(float(cs.lat), float(cs.lng),alt,float(cs.groundcourse))

		        telTime = time() - initTime
		        print("Time to send telemetry: %f" % telTime)

		        timeToSleep = (1 / float(targetRate)) - telTime - serveTime
		        if timeToSleep > 0:
		        	sleep(timeToSleep)
		except IOError as e:
		    print "Failed to connect to RPC:"
		    print e
		    sys.exit(1)

main()