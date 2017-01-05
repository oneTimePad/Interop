"""
Interoperability component that loads missions

PLEASE refer to libinterop/types.py for auvsi provided objects
objects refered:
	Mission which is made up of other objects
	...
"""

from libinterop import MissionInterop

"""
change this configuration of the proxy info to meet your needs
proxy_info is the information for our groundstation
"""
proxy_info ={
	"host": "192.168.1.171",
	"port"  : "8000",
	"username": "telemuser",
	"password": "ruautonomous"

}


mission_client = MissionInterop(proxy_info)

#gets mission from server right away
missions,error = mission_client.start()

if error !=None:
	raise Exception(error)

print(missions[0])

#TODO: Load missions into mavproxy/dronekit/missionplanner

