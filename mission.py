"""
Interoperability component that loads missions

PLEASE refer to libinterop/types.py for auvsi provided objects
objects refered:
	Mission which is made up of other objects
	...
"""

from libinterop import MissionInterop
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("server",help="ip:port pair for django")
parser.add_argument("username",help="username for django")
parser.add_argument("password", help="password for django")
args = parser.parse_args()
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



mission_client = MissionInterop(proxy_info)

#gets mission from server right away
missions,error = mission_client.start()

if error !=None:
	raise Exception(error)

print(missions)

#TODO: Load missions into mavproxy/dronekit/missionplanner

