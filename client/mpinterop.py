import sys

from mpclient import Client
from time import sleep, time
from dronekit import connect
import pdb
# target upload rate in Hz
targetRate = 13

# according to http://auvsi-suas-competition-interoperability-system.readthedocs.org/en/latest/integration/hints.html
# the server takes at most 0.011 seconds to do its thing
guessServeTime = 0



FEET_PER_METER = 3.28084

url = 'http://192.168.43.100:2000'
username = 'telemuser'
password = 'ruautonomous'


def main():

	pdb.set_trace()
	client = None
	try:
		client = Client(url,username,password)
	except Exception:
		pass #except something, not sure what yet

	try:
		drone = connect('127.0.0.1:14550',wait_ready=True)
	except Exception as e:
		print e


	# try to "fix" the average
	makeUpTime = 0

	retLat = 0
	while True:
		try:

			beforeTelem = time()

			lat = float(drone.location.global_frame.lat)
			lng = float(drone.location.global_frame.lon)
			alt = float(drone.location.global_frame.alt)
			groundcourse = float(drone.heading)

		
			telemetry = {'latitude':lat,'longitude':lng,'altitude_msl':alt,'uas_heading':groundcourse}


			fut= client.post_telemetry(telemetry)
			afterServeTime,error = fut.result()

			if error:
				print error

			afterTelem = time()
			#sleep(.05)
						
			timeToSleep = (1 / float(targetRate)) -(afterTelem-beforeTelem)
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
