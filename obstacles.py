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
from sda import async_routine,sync_routine
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("server",help="ip:port pair for django")
parser.add_argument("username",help="username for django")
parser.add_argument("password", help="password for django")

"""
These configurations are defaults. Please edit proxy_info and poll_info and
DEBUG to meet your needs
"""
#prox_info is the information for the ground station
proxy_info ={
	"host": args.server.split(':')[0],
	"port"  : args.server.split(':')[1],
	"username":args.username,
	"password": args.password

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
