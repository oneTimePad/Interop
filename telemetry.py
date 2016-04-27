import sys

from client import Client
from time import sleep, time
from dronekit import connect
import argparse
import pdb

# target upload rate in Hz
TARGET_RATE = 13
FEET_PER_METER = 3.28084
MAV_SERVER = '127.0.0.1:14550'

#print unicode colors
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

if __name__ == "__main__"
	parser = arg.ArgumentParser()
	parser.add_argument("url",help="url for django server (http://ip:port)",type=str)
	parser.add_argument("username",help="username for django server",type=str)
	parser.add_argument("password",help="password for django server",type=str)

	args = parser.parse_args()

	url = args.url
	username = args.username
	password = args.password

	client = None
	#connect to django
	try:
		client = Client(url,username,password)
	except Exception:
		print bcolors.FAIL+"Received Exception while contacting Django"+bcolors.ENDC+"\n"
		print e
		sys.exit(1)

	#connect to maxproxy
	try:
		drone = connect(MAV_SERVER,wait_ready=True)
	except Exception as e:
		print bcolors.FAIL+"Received Exception while contacting MaxProxy"+bcolors.ENDC+"\n"
		print e
		sys.exit(1)


	# try to "fix" the average
	makeUpTime = 0
	while True:
		try:

			beforeTelem = time()

			#get data from maxproxy (Dronekit)
			lat = float(drone.location.global_frame.lat)
			lng = float(drone.location.global_frame.lon)
			alt = float(drone.location.global_frame.alt)
			groundcourse = float(drone.heading)

			#forumlate json of data
			telemetry = {'latitude':lat,'longitude':lng,'altitude_msl':alt,'uas_heading':groundcourse}

			#post to django
			fut= client.post_telemetry(telemetry)
			#wait for response
			afterServeTime,error = fut.result()

			if error:
				print bcolors.FAIL+"Continuing but recieved an error from Django:"+bcolors.ENDC+"\n"
				print error

			afterTelem = time()

			timeToSleep = (1 / float(TARGET_RATE)) -(afterTelem-beforeTelem)
			if timeToSleep > 0:
				sleep(timeToSleep)
				makeUpTime = 0
			else:
				makeUpTime = -timeToSleep


		except IOError as e:
		    print  bcolors.FAIL+"Failed to connect to Django:"+bcolors.ENDC+"\n"
		    print e
		    sleep(1)