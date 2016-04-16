import sys
sys.path.append('c:\python27\lib')

from mpclient import Client
from time import sleep, time
import pdb
# target upload rate in Hz
targetRate = 13

# according to http://auvsi-suas-competition-interoperability-system.readthedocs.org/en/latest/integration/hints.html
# the server takes at most 0.011 seconds to do its thing
guessServeTime = 0



FEET_PER_METER = 3.28084

url = 'http://localhost:2000'
username = 'lol4'
password = 'lol4'


def main():

	client = None
	try:
		client = Client(url,username,password)
	except Exception:
		pass #except something, not sure what yet

	# try to "fix" the average
	makeUpTime = 0

	retLat = 0
	while True:
		try:

			beforeTelemTime = time()

			lat = float(cs.lat)
			lng = float(cs.lng)
			alt = retLat # float(cs.altoffsethome) / FEET_PER_METER + 22
			retLat += 1
			groundcourse = float(cs.groundcourse)

			print "Time to get telemetry: %f" % (time() - beforeTelemTime)
			telemetry = {'latitude':lat,'longitude':lng,'altitude':alt,'uas_heading':groundcourse}

			beforeServeTime = time()

			afterServeTime,error = client.post_telemetry(telemetry)

			if error:
				print error

			print "Time to send to Django: %f" % (afterServeTime - beforeServeTime)

			telTime = time() - beforeTelTime
			timeToSleep = (1 / float(targetRate)) - telTime - guessServeTime - makeUpTime
			if timeToSleep > 0:
				sleep(timeToSleep)
				makeUpTime = 0
			else:
				makeUpTime = -timeToSleep

		except IOError as e:
		    print "Failed to connect to Django:"
		    print e
		    sleep(1)

main()
