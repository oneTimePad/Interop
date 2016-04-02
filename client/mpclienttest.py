import sys
sys.path.append('c:\python27\lib')

import xmlrpclib
from time import sleep, time

# target upload rate in Hz
targetRate = 10

# according to http://auvsi-suas-competition-interoperability-system.readthedocs.org/en/latest/integration/hints.html
# the server takes at most 0.011 seconds to do its thing
guessServeTime = 0

# server ip
host = '127.0.0.1'
port = '9000'

FEET_PER_METER = 3.28084

def main():
	server = xmlrpclib.ServerProxy('http://' + host + ':' + port)

	# try to "fix" the average
	makeUpTime = 0

	while True:
		try:
			beforeTelTime = time()
			beforeTelemTime = time()

			lat = float(cs.lat)
			lng = float(cs.lng)
			alt = float(cs.altoffsethome) / FEET_PER_METER + 22
			groundcourse = float(cs.groundcourse)

			print "Time to get telemetry: %f" % (time() - beforeTelemTime)

			beforeServeTime = time()
			afterServeTime = server.telemetry(lat, lng, alt, groundcourse)

			print "Time to send to RPC: %f" % (afterServeTime - beforeServeTime)				

			telTime = time() - beforeTelTime
			timeToSleep = (1 / float(targetRate)) - telTime - guessServeTime - makeUpTime
			if timeToSleep > 0:
				sleep(timeToSleep)
				makeUpTime = 0
			else:
				makeUpTime = -timeToSleep

		except IOError as e:
		    print "Failed to connect to RPC:"
		    print e
		    sleep(1)

main()