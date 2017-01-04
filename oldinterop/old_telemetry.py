import sys
#sys.path.append(".")
from libinterop import Client
from libinterop import Telemetry
import time
import dronekit
import argparse
import pdb
import datetime
import threading
import binascii
# target upload rate in Hz
TARGET_RATE = 10
FEET_PER_METER = 3.28084
POLL_SEC = 0.1
PRINT_SEC = 10
MAV_SERVER = "192.168.1.162:14550"

send_lock = threading.Lock()
last_print = datetime.datetime.now()
sent_since_print = 0
def handle_upload_result(future):
	global sent_since_print
	#print "handler"
	if future.exception():
		print("Request Failed. Exception %s" % (str(future.exception())))
	else:
		with send_lock:
		#send_lock.acquire()
		#print "updated",sent_since_print
		#print str(sent_since_print)
			sent_since_print += 1
		#send_lock.release()
		#sent_since_print = 5

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

while True:
	try:
		client = Client(url,username,password)
		break
	except (TypeError,binascii.Error):
		continue
	#except Exception as e:
	#	print "Received Exception while contacting Django"+"\n"
	#	print e
	#	sys.exit(1)

#connect to maxproxy
try:
	drone = dronekit.connect(MAV_SERVER,wait_ready=True)

except Exception as e:
	print "Received Exception while contacting MaxProxy"+"\n"
	print e
	sys.exit(1)




last_telemetry = Telemetry(0,0,0,0)
while True:
	telemetry = Telemetry(latitude =float(drone.location.global_frame.lat),
					longitude=float(drone.location.global_frame.lon),
					altitude_msl = float(drone.location.global_frame.alt),
					uas_heading = 0)

	if telemetry != last_telemetry:
		client.post_telemetry(telemetry).add_done_callback(
			handle_upload_result)
		last_telemtry = telemetry
	else:
		print "DUP\n"

	now = datetime.datetime.now()
	since_print = (now-last_print).total_seconds()
	if since_print >= PRINT_SEC:
		#print "ATTEMPTING LOCK"
		with send_lock:
		#send_lock.acquire()
		#print "GOT"
			local_sent_since_print = sent_since_print
		#print str(sent_since_print)
			sent_since_print = 0
		#send_lock.release()
		print "Upload Rate: %f" % (local_sent_since_print/ since_print)
		last_print = now
	time.sleep(POLL_SEC)
