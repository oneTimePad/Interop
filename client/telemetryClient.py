import os
import requests
from SimpleXMLRPCServer import SimpleXMLRPCServer
from concurrent.futures import ThreadPoolExecutor
import sys
from time import time,sleep
from . import Client, AsyncClient, InteropError, Target, Telemetry
import argparse
import pdb


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
allows for retry of telemetry sending if server dies
telemetry post tries to send last failed attempt. Then continue to sends next telem
'''
def tryAgain(reconnect,TOO_MANY):
	reconnect = [reconnect]
	def tryTelemAgain(t,client):

		while True:
			if reconnect[0] == TOO_MANY:
				print "Stopping to conserve...Server must be in critical state."
				sys.exit(1)

			try:

				res =client.post_telemetry(t).result()
				yield res
			except InteropError as e:
				reconnect[0]+=1
				yield e


	return tryTelemAgain

'''
class for allowing communication to mission planner
'''
class RelayService:
	def __init__(self,client):
		self.client = client

	#mission planner calls for telemetry post
	def telemetry(self,lat,lon,alt,heading):
			telemAgain = tryAgain(0,10)
			#telementry object
			t = Telemetry(latitude=lat,
            		longitude=lon,
					altitude_msl=alt,
					uas_heading=heading)
			print lat
			#post it
			#@RUAutonomous-autopilot
			#might be where exception catching goes, look for a InteropError obj
			#If the server dies, should it resend the data?
			print "[DEBUG] posting telementry"
			try:
				self.client.post_telemetry(t).result()
			except InteropError as e:
					print "POST resulting in Server error response:"
					print e
					print "Server Might be down.\n Trying again at 1Hz"
					#rtry sending after 1Hz
					for result in telemAgain(t,self.client):
						if result == None:
							break
						print "Request Results in"
						print result
						sleep(1)



			print "Fixed"
			#calc time between consecutive posts
			#new_time = time()
			#print 1 / (new_time - self.last_telemetry)
			#self.last_telemetry = new_time

			return True


'''
wraps around AsyncClient for exception catching
'''
class TelemetryClient:

	def __init__(self,server,username,password):
		self.client = None
		try:


			self.client = AsyncClient(server,username,password)
			print "[DEBUG]: Server connection success"
		#deals with login error
		except InteropError as serverExp:

			code,reason,text =  serverExp.errorData()

			if text == "Invalid Credentials.":
				print "Error code : %d Error Reason: %s" %(code,reason)
				print "Exiting wrong username/password combo"
				print "Current user:%s pass:%s" %(username,password)
				sys.exit(1)


			elif code ==404:
				print "Server not found return 404\n"
				print "Reason: \n%s" %(text)
				sys.exit(1)
			#@RUAutonomous-autopilot
			#We might need more exceptions here and below


		#deals with timeout error
		except requests.ConnectionError:

			print "Error: Connection to server failed"
			sys.exit(1)



	def __enter__(self):
		return self

	#ends nicely
	def __exit__(self,type,value,traceback):
			print "HEERE"
			if self.client:
				self.client.client.session.close()
			#if an exception caused this, explain
			#@RUAutonomous-autopilot : might need to be more specifc? Right now it's good
			if isinstance(value,Exception):
				print("Ended with Exception: \n")
				print(value)

				return False
			return True

#start RPC server
def start_server(args):
	#start RPCserver for Mission planner
	'''@RUAutonomous-autopilot
	---> works with auvsi_mp.py
	---> auvsi_mp.py runs in mp space and calls telemetry_post via rpc
	'''
	#set RPC server interface
	serverface = (args.host,int(args.port)) if (args.host is not None and args.port is not None) else ('127.0.0.1',int('9000'))

	relay = RelayService(client.client)
	server = SimpleXMLRPCServer(
		serverface,
		logRequests=True,
		allow_none = True)
	# allow mission planner to call post_telemetry
	server.register_instance(relay)
	print "[DEBUG]: Server Started"
	#start
	server.serve_forever()

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
		start_server(args)

		#for testing purposes only
		'''
		def exc():
			while 1:
				#pdb.set_trace()
				t = Telemetry(latitude=2,
	            		longitude=3,
						altitude_msl=4,
						uas_heading=5)
				try:
					print client.client.post_telemetry(t).result()

				except Exception as e:
					print "Error"
					print e
					client.client.client.session.close()
					client.client.client.session=None
				sleep(2)

		with ThreadPoolExecutor(max_workers=2) as executor:
			executor.submit(exc)
			executor.submit(start_server)
		'''
