"""
main program for SDA and interop related to SDA
this should be the first program started for sda
PLEASE refer to libinterop/types.py for information on the auvsi provided
objects
objects that used are:
	MovingObstacle
	StationaryObstacle
"""

from libinterop import ObstacleInterop
from sda import handle_response,main_routine

"""
These configurations are defaults. Please edit proxy_info and poll_info and
DEBUG to meet your needs
"""
#prox_info is the information for the ground station
proxy_info ={
	"host": "192.168.1.171",
	"port"  : "8000",
	"username": "telemuser",
	"password": "ruautonomous"

}

#poll_sec is the time between requests for obstacles
#print_sec is the time between prints for debugging (i.e. not used if debugging
#is off
poll_info = {
	"poll_sec" : 0.1,
	"print_sec": 10
}


DEBUG = False # set to true to enable debug info


obstacles_client = ObstacleInterop(
	proxy_info,
	poll_info,
	handle_response,
	status_debug=DEBUG)


obstacles_client.start()

main_routine()

