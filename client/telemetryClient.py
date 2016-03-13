import os
import requests

from SimpleXMLRPCServer import SimpleXMLRPCServer
import sys
from . import Client, AsyncClient, InteropError, Target, Telemetry


server = os.getenv('INTEROP_SERVER','http://localhost')
username = os.getenv('INTEROP_USER','testuser')
password = os.getenv('INTEROP_PASS','testpass')


'''
class for allowing communication to mission planner
'''
class RelayService:
	def __init__(self,client):
		self.client = client
	#mission planner calls for telemetry post
	def telementry(self,lat,lon,alt,heading):
	        t = Telemetry(latitude=lat,
                      longitude=lon,
                      altitude_msl=alt,
                      uas_heading=heading)
        	self.client.post_telemetry(t)

        	new_time = time()
        	print 1 / (new_time - self.last_telemetry)
        	self.last_telemetry = new_time

        	return True

#creates client
class clientCreate:
	def __enter__(self):
		global server
		global username
		global password
		try:
			return AsyncClient(server,username,password)
		#deals with login error
		except InteropError as serverExp:
			code,reason,text =  serverExp.errorData()
			
			if text == "Invalid Credentials.":
				print "Error code : %d Error Reason: %s" %(code,reason)
				print "Exiting wrong username/password combo"
				print "Current user:%s pass:%s" %(username,password)
				sys.exit(1)
		#deals with timeout error
		except requests.ConnectionError:
			print "Error: Connection to server failed"
			sys.exit(1)
	#ends nicely
	def __exit__(self,type,value,traceback):
		print "Exception"			



if __name__ == '__main__':
	
	with clientCreate() as client:
		#start RPCserver for Mission planner
		relay = RelayService(client)
		server = SimpleXMLRPCServer(
			('127.0.0.1',9000),
			logRequests=True,
			allow_none = True)
		
		server.register_instance(relay)
		
		server.serve_forever()
