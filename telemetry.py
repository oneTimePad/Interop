import sys

from interop import Client
from interop import Telemetry
from time import sleep, time
from dronekit import connect
import argparse
import pdb

# target upload rate in Hz
TARGET_RATE = 10
FEET_PER_METER = 3.28084
MAV_SERVER = '192.168.1.162:14550'

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

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("url",help="url for django server (http://ip:port)",type=str)
	parser.add_argument("username",help="username for django server",type=str)
	parser.add_argument("password",help="password for django server",type=str)

	args = parser.parse_args()
	#pdb.set_trace()
	url = args.url
	username = args.username
	password = args.password

	client = None
	#connect to django
	try:
		client = Client(url,username,password)
	except Exception as e:
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

	#pdb.set_trace()
	# try to "fix" the average
	makeUpTime = 0
	while True:
		try:

			beforeTelem = time()

			#get data from maxproxy (Dronekit)
			lat = float(drone.location.global_frame.lat)
			lon = float(drone.location.global_frame.lon)
			alt = float(drone.location.global_frame.alt)
			print drone.heading
			groundcourse = float(drone.heading if drone.heading != None else  0)
			heading = groundcourse

			latdeg = round(lat)
			latmin = round((lat-latdeg)*60)
			latsec = round(((lat-latdeg)*60-latmin)*3600)

			londeg = round(lon)
			lonmin = round((lon-londeg)*60)
			lonsec = round(((lon-londeg)*60-lonmin)*3600)
			now = time()
			print(now- beforeTelem)

			print "----------TIME STAMP-------------\n"
			print "         "+str(beforeTelem)+"        \n"
			print bcolors.OKBLUE+"Telemtry Data:\n" \
			"Latitude: "+ str(latdeg)+"deg "+str(latmin)+"min "+str(latsec)+"sec\n"+ \
		               "Longitude: "+str(londeg)+"deg "+str(lonmin)+"min "+str(lonsec)+"sec\n"+ \
		               "Altitude: "+str(alt*3.28084)+"ft\n"+ \
		               "Heading: "+str(heading)+"deg"+bcolors.ENDC+"\n" 

			beforeRequest = time()
			#forumlate json of data
			telemetry = Telemetry(latitude=lat,
						 longitude=lon,
						 altitude_msl=alt,
						 uas_heading=groundcourse)

			#post to django
			fut= client.post_telemetry(telemetry)
			#wait for response
			afterServeTime,error = fut.result()
			now = time()
			print(now-beforeRequest)

			if error:
				print bcolors.FAIL+"Continuing but recieved an error from Django:"+bcolors.ENDC+"\n"
				print error
				print bcolors.OKGREEN+"--------------Telemtry Posted----------------"+bcolors.ENDC+"\n"

			afterTelem = time()

			timeToSleep = (1 / float(TARGET_RATE)) -(afterTelem-beforeTelem)
			if timeToSleep > 0:
				sleep(timeToSleep)
				makeUpTime = 0
			else:
				makeUpTime = -timeToSleep
			print(1/(afterTelem-beforeTelem+timeToSleep))


		except IOError as e:
		    print  bcolors.FAIL+"Failed to connect to Django:"+bcolors.ENDC+"\n"
		    print e
		    sleep(1)
