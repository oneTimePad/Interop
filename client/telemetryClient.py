import os
import requests
from SimpleXMLRPCServer import SimpleXMLRPCServer
import sys
from time import time
from . import Client, AsyncClient, InteropError, Target, Telemetry
import argparse


'''
@RUAutonomous-autopilot

Below is a basic TelemetryClient I made by adding my own code and using there code.
I caught some exceptions, but wee need to catch things like:
	if server dies, we need to reconnect [might need to test with server and mp to catch this. since without mp to requestsare made]
	other stuff
	make sure the timing rate is ok.
Timing can be tested by running mission planner with auvsi_np.py, and the server and this program
Although you MIGHT need a pixhawk since you need to generate the data at 10Hz. Contact me if you attempt this.

If you run this you'll see I caught an exception and it prints it


don't cd into client to run this. It is a package so run it from outside client.

This program is also a server. It sets up an RPC server for mission planner to use to send the
telemetry to this program.

python -m "client.telemetryClient" --host (rpc server ip to setup) --port (rpc server port)

if you leave the host/port out it just uses ('127.0.0.1','9000')
use ports above 1020 to avoid superuser permissions

'''

'''
class for allowing communication to mission planner
'''
class RelayService:
	def __init__(self,client):
		self.client = client

	#mission planner calls for telemetry post
	def telementry(self,lat,lon,alt,heading):
			#telementry object
			t = Telemetry(latitude=lat,
            		longitude=lon,
					altitude_msl=alt,
					uas_heading=heading)

			#post it
			#@RUAutonomous-autopilot
			#might be where exception catching goes, look for a InteropError obj
			self.client.post_telemetry(t)

			#calc time between consecutive posts
			new_time = time()
			print 1 / (new_time - self.last_telemetry)
			self.last_telemetry = new_time

			return True


'''
wraps around AsyncClient for exception catching
'''
class TelemetryClient:

	def __init__(self,server,username,password):
		self.client = None
		try:
			self.client = AsyncClient(server,username,password)
		#deals with login error
		except InteropError as serverExp:
			code,reason,text =  serverExp.errorData()

			if text == "Invalid Credentials.":
				print "Error code : %d Error Reason: %s" %(code,reason)
				print "Exiting wrong username/password combo"
				print "Current user:%s pass:%s" %(username,password)
				#sys.exit(1)


			elif code ==404:
				print "Server not found return 404\n"
				print "Reason: \n%s" %(text)
				#sys.exit(1)
			#@RUAutonomous-autopilot
			#We might need more exceptions here and below


		#deals with timeout error
		except requests.ConnectionError:
			print "Error: Connection to server failed"
			#sys.exit(1)


	def __enter__(self):
		pass

	#ends nicely
	def __exit__(self,type,value,traceback):
			if self.client:
				self.client.session.close()
			#if an exception caused this, explain
			#@RUAutonomous-autopilot : might need to be more specifc? Right now it's good
			if isinstance(value,Exception):
				print("Ended with Exception: \n")
				print(value)
				return False
			return True

if __name__ == '__main__':
	#get paramters from environment variables
	server = os.getenv('INTEROP_SERVER','http://localhost')
	username = os.getenv('INTEROP_USER','testuser')
	password = os.getenv('INTEROP_PASS','testpass')
	'''
	take args for RPC server host/port
	'''
	parser = argparse.ArgumentParser(
		description='Telemetry Client')
	parser.add_argument(
		'--host',
		dest='host',
		help='RPC server ip')
	parser.add_argument(
		'--port',
		dest='port',
		help='RPC server ip')

	args = parser.parse_args()



	#helps end nicely -- calls __enter__ and __exit__
	with TelemetryClient(server,username,password) as client:
		#start RPCserver for Mission planner
		'''@RUAutonomous-autopilot
		---> works with auvsi_mp.py
		---> auvsi_mp.py runs in mp space and calls telemetry_post via rpc
		'''
		#set RPC server interface
		serverface = (args.host,args.port) if (args.host is not None and args.port is not None) else ('127.0.0.1','9000')

		relay = RelayService(client.client)
		server = SimpleXMLRPCServer(
			serverface,
			logRequests=True,
			allow_none = True)
		# allow mission planner to call post_telemetry
		server.register_instance(relay)

		#start
		server.serve_forever()
