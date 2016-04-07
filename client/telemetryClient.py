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
After asking, we will just drop data
'''
# def tryAgain(reconnect,TOO_MANY):
# 	reconnect = [reconnect]
# 	def tryTelemAgain(t,client):

# 		while True:
# 			if reconnect[0] == TOO_MANY:
# 				print "Stopping to conserve...Server must be in critical state."
# 				sys.exit(1)

# 			try:

# 				res =client.post_telemetry(t).result()
# 				yield res
# 			except InteropError as e:
# 				reconnect[0]+=1
# 				yield e
# 			except requests.ConnectionError as e:
# 				reconnect[0] += 1
# 				yield e

# 	return tryTelemAgain

'''
class for allowing communication to mission planner
'''
class RelayService:
	def __init__(self,client):
		self.client = client

	#mission planner calls for telemetry post
	def telemetry(self,lat,lon,alt,heading):
			startTime = time()
			# telemAgain = tryAgain(0,10)
			#telementry object
			t = Telemetry(latitude=lat,
            		longitude=lon,
					altitude_msl=alt,
					uas_heading=heading)
			print "hi"
			#post it
			#@RUAutonomous-autopilot
			#might be where exception catching goes, look for a InteropError obj
			successful = False
			while not successful:
				try:
					postTime = time()
					self.client.post_telemetry(t).result()
					print "Time to post: %f" % (time() - postTime)
					successful = True
				except InteropError as e:
					#@RUAutonomous-autopilot
					#We might need more exceptions here and below
					code,reason,text = e.errorData()
					print "POST /api/telmetry has failed."
					print "Error code : %d Error Reason: %s" %(code,reason)
					print "Text Reason: \n%s" %(text)

					if code == 400:
						print "Invalid telemetry data. Stopping."
						sys.exit(1)

					elif code == 404:
						print "Server Might be down.\n Trying again at 1Hz"
						sleep(1)

					elif code == 405 or code == 500:
						print "Internal error (code: %s). Stopping." % (str(code))
						sys.exit(1)

					elif code == 403:
						#@RUAutonomous-autopilot
						# TODO: Ask to reenter credentials after n tries or reset that mysterious cookie
						print "Server has not authenticated this login. Attempting to relogin."
						username = os.getenv('INTEROP_USER','testuser')
						password = os.getenv('INTEROP_PASS','testpass')
						#@RUAutonomous-autopilot --> self.post doesn't exist, self.client.post?
						self.post('/api/login', data={'username': username, 'password': password})

				except requests.ConnectionError:
					print "A server at %s was not found. Waiting for a second, then retrying." % (server)
					sleep(1)

				except requests.Timeout:
					print "The server timed out. Waiting for a second, then retrying."
					sleep(1)

				except requests.TooManyRedirects:
					print "The URL redirects to itself; reenter the address:"
					enterAUVSIServerAddress()
					self.client.url = os.getenv('INTEROP_SERVER')
					sleep(1)

				except requests.URLRequired:
					print "The URL is invalid; reenter the address:"
					enterAUVSIServerAddress()
					self.client.url = os.getenv('INTEROP_SERVER')
					sleep(1)

				except requests.RequestException as e:
					# catastrophic error. bail.
					print e
					sys.exit(1)

				except concurrent.futures.CancelledError:
					print "Multithreading failed. Waiting for a second, then retrying."
					sleep(1)

				except concurrent.futures.TimeoutError:
					print "Multithreading timed out. Waiting for a second, then retrying."
					sleep(1)

				except:
					print "Unknown error: %s" % (sys.exc_info()[0])
					sys.exit(1)

			return startTime

'''
wraps around AsyncClient for exception catching
'''
class TelemetryClient:

	def __init__(self,server,username,password):
		self.client = None
		while not self.client:
			try:
				self.client = AsyncClient(server,username,password)
			except InteropError as serverExp:
				#@RUAutonomous-autopilot
				#We might need more exceptions here and below
				code,reason,text =  serverExp.errorData()
				print "Error code : %d Error Reason: %s" %(code,reason)
				print "Reason: \n%s" %(text)

				if code == 400:
					print "The current user/pass combo (%s, %s) is wrong. Please try again." % (username,password)
					enterLoginCredentials()
					username = os.getenv('INTEROP_USER','testuser')
					password = os.getenv('INTEROP_PASS','testpass')

				elif code == 404:
					print "A server at %s was not found. Please reenter the server IP address." % (server)
					enterAUVSIServerAddress()
					server = os.getenv('INTEROP_SERVER','http://localhost')

				elif code == 500:
					print "Internal issues with their code. Stopping."
					sys.exit(1)
			#deals with timeout error
			except requests.ConnectionError:
				print "A server at %s was not found. Please reenter the server IP address." % (server)
				enterAUVSIServerAddress()
				server = os.getenv('INTEROP_SERVER','http://localhost')

			except requests.Timeout:
				print "The server timed out. Waiting for a second, then retrying."
				sleep(1)

			except requests.TooManyRedirects:
				print "The URL redirects to itself; reenter the address:"
				enterAUVSIServerAddress()
				server = os.getenv('INTEROP_SERVER','http://localhost')

			except requests.URLRequired:
				print "The URL is invalid; reenter the address:"
				enterAUVSIServerAddress()
				server = os.getenv('INTEROP_SERVER','http://localhost')

			except requests.RequestException as e:
				# catastrophic error. bail.
				print e
				sys.exit(1)

			except concurrent.futures.CancelledError:
				print "Multithreading failed. Waiting for a second, then retrying."
				sleep(1)

			except concurrent.futures.TimeoutError:
				print "Multithreading timed out. Waiting for a second, then retrying."
				sleep(1)

			except:
				print "Unknown error: %s" % (sys.exc_info()[0])
				sys.exit(1)

		print "[DEBUG]: Server successfully connected to %s." % (server)
		print "[DEBUG]: Logged in as %s." % (username)

	def __enter__(self):
		return self

	#ends nicely
	def __exit__(self,type,value,traceback):
			print "Quit"
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

def enterAUVSIServerAddress():
	baseURL = raw_input('Enter base URL (default when nothing is found is localhost): ')
	if not baseURL:
		baseURL = 'localhost'
	port = raw_input('Enter port (default is none): ')

	fullURL = 'http://' + baseURL + (':' + port if port else '')

	os.environ['INTEROP_SERVER'] = fullURL

	# print '[DEBUG] Server address: %s' % (os.getenv('INTEROP_SERVER', 'Default'))

def enterLoginCredentials():
	username = raw_input('Enter username (default when nothing is found is testuser): ')
	password = raw_input('Enter password (default is testpass): ')

	if username:
		os.environ['INTEROP_USER'] = username
	elif not os.getenv('INTEROP_USER'):
		os.environ['INTEROP_USER'] = 'testuser'

	if password:
		os.environ['INTEROP_PASS'] = password
	elif not os.getenv('INTEROP_PASS'):
		os.environ['INTEROP_PASS'] = 'testpass'

	# print '[DEBUG] User/pass: (%s/%s)' % (os.getenv('INTEROP_USER', 'Default'), os.getenv('INTEROP_PASS', 'Default'))

if __name__ == '__main__':
	enterLoginCredentials()

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
