"""
main program for SDA and interop related to SDA
this should be the first program started for sda

"""

from libinterop import ObstacleInterop
import time
"""
These configurations are defaults. Please edit proxy_info and poll_info and
DEBUG to meet your needs
"""
proxy_info ={
	"host": "192.168.1.160",
	"port"  : "8000",
	"username": "telemuser",
	"password": "ruautonomous"

}


poll_info = {
	"poll_sec" : 0.1,
	"print_sec": 10
}


DEBUG = True # set to false to disable debug info
def handle_response(moving,stationary,error):
	"""
	moving:= list of moving obstacles in object format
	stationary:= list of stationary obstacles in object format
	NOTE: see libinterop/types.py for the structure of the object format
	moving = [MovingObstacle(...),MovingObstacle(...),...]
	same for stationary
	error:=an error is returned from the server when not equal to None

	NOTE OF Caution: be careful when editing global variables here,
	execution of this function is asynchronous of everything outside it.
	This means that is can happen at anytime. Thus you need to lock any global
	data using the following:

		import threading
		lock = threading.Lock()

		...
		# area where global variable is edited
		def handle_response(...):
			no lock
			with lock:
				do stuff with global variable
			no lock
		#stuff outside of handle_response where global variable is edited
		no lock
		with lock:
			do stuff with same global variable
		no lock
	"""

	if error:
		print("error: %s" %(str(error)))
	"""
		all the work that gets done when receiving obstacle updates goes
		hanle_response
	"""
	#Example
	print("updating obstacle status ...")

obstacles_client = ObstacleInterop(
	proxy_info,
	poll_info,
	handle_response,
	status_debug=DEBUG)


obstacles_client.start()

#EVERYTHING ABOVE HERE IS REQUIRED

#TODO: add synchronus work here (everything that happens while waiting for
#obstacle position updates (i.e. rest of the SDA code [function, routines, etc]
#EXAMPLE:
while True:
	print("Do some SDA stuff")
	time.sleep(2)


