from baseclients import AsyncClient
from types import Telemetry
import binascii
import time
import threading
import datetime
import logging
import sys
from proxy_mavlink import *

"""
	Clients that implement the actual functionality specific to each interop task
"""

class InteropClient(AsyncClient):
	"""
		Implements certain functionality that is useful through some of the interop tasks
		such as debugging and registering handlers for the clients that use futures
		for piplining
	"""

	def __init__(self,proxy_info,poll_info,callback=None,status_debug = True):
		"""
			args := poll_info = { POLL_SEC , PRINT_SEC}  (dictionary containng poll time and print time)
					proxy_info =  { host, port, username, password} (all for proxy interop server (imaging server)

		"""
		if not all(key in proxy_info for key in("username","password","host","port")):
			raise Exception("HandlerInteropClient<Bad argument>: prox_info = \
				   dict('username','password','host','port')")
		#register a callback to be executed when client receives response from server
		self.future_callback = callback
		#whether debugging is enable (prints debug statements)
		self.status_debug = status_debug
		if status_debug:

			self.status_lock = threading.Lock()
			#number of requests sent since we last printed a debug statement
			self.sent_since_print = 0
			#use now as the start time
			self.last_print = datetime.datetime.now()
		self.POLL_SEC = poll_info["poll_sec"]
		self.PRINT_SEC = poll_info["print_sec"] if ("print_sec" in poll_info)else 0


		super(InteropClient,self).__init__("http://"+proxy_info["host"]+":"+proxy_info["port"],proxy_info["username"],proxy_info["password"])

	def handler_contact_callback(self,future):
		"""
			default callback registered for all clients using futures
			prints debug statments, check for errors and calls the other callback registered in the arg to __init__
		"""
		if future.exception():
			print("WARNING: Request Failed with %s" % (str(future.exception())))
		else:
			if self.status_debug:
				#print("DEBUG: Request result %s" %(str(future.result())))

				with self.status_lock:
					self.sent_since_print+=1
			# if the client has a registered callback passed in the constructor, call it now
			if self.future_callback:
				try:
					self.future_callback(*future.result())
				except Exception as e:
					print("WARNING: Registered callback Failed with %s" % (str(e)))

	def _make_request(self):
		"""
			the actual request method that must be overriden by subclasses
		"""
		raise NotImplementedError("_make_request must be overridden")

	def start(self,THREADING_ENABLED=True):
		"""
			starts up the requesting and multithreads if needed
			args := THREADING_ENABLED (optional should the requesting be ran in a separate thread)
		"""
		#call synchronously
		if not THREADING_ENABLED:
			self._start()
		else:
			#thread and deamonize
			self.thread = threading.Thread(target=self._start)
			self.thread.daemon = True
			self.thread.start()


	def _start(self):
		"""
			starts the requesting process
		"""
		while True:
			# try to call the subclasses request method and add the callback to the future
			try:
				self._make_request().add_done_callback(self.handler_contact_callback)
			except Exception as e:
				raise Exception("WARNING: Request for Object Failed with %s" % (str(e)))
			if not self.status_debug:
				pass
			else:
				#if we are debugging, print debug statments and times
				now = datetime.datetime.now()
				since_print = (now-self.last_print).total_seconds()

				if since_print >= self.PRINT_SEC:
					with self.status_lock:
						local_sent_since_print = self.sent_since_print
						self.sent_since_print = 0
						print("DEBUG: Upload Rate %f" %(local_sent_since_print/since_print))
						self.last_print = now
			#attempt to achieve the request request rate
			time.sleep(self.POLL_SEC)




class TelemetryInterop(InteropClient):
	"""
			posting UAV current telemetry interop task

	"""
	def __init__(self,proxy_info,poll_info,mav_info,status_debug=True):
		if not all(key in mav_info for key in ("host","port")):
			raise Exception("TelemtryInterop required mav_info=dict('host','port') to contact mavproxy")
		#connects to MAVProxy via Dronekit over udp 
		self.mav_endpoint = mav_info["host"] +":"+mav_info["port"]
		try:
			#make the dronekit connection
			self.drone = mavutil.mavlink_connection("udp:"+self.mav_endpoint, autoreconnect=True)
		except Exception as e:
			raise Exception("TelemetryInterop failed to setup mav connection, Failed with %s" %(str(e)))
		if not self.drone:
			raise Exception("Failed to connect via %s\n" %str(self.mav_endpoint))
		#create an initial telemetry
		self.last_telemetry = Telemetry(0,0,0,0)
		self.logger = logging.getLogger(__name__)

		super(TelemetryInterop,self).__init__(proxy_info,poll_info,status_debug=status_debug)

	def _make_request(self):
		"""
			post the current telemetry
		"""
		drone = self.drone
		# Get packet
		msg = drone.recv_match(type='GLOBAL_POSITION_INT',
								blocking=True,
								timeout=10.0)
		if msg is None:
			self.logger.critical(
			'Did not receive MAVLink packet for over 10 seconds.')
			sys.exit(-1)
		# fetch the current telemetry from dronekit (lat,lon,altitude MSL, heading)
		telemetry = Telemetry(latitude=mavlink_latlon(msg.lat),
							longitude=mavlink_latlon(msg.lon),
							  altitude_msl=mavlink_alt(msg.alt),
							  uas_heading=mavlink_heading(msg.hdg))

		#only send if telemtry has changed
		if telemetry != self.last_telemetry:
			#print("telemtry:"+str(telemetry))
			return self.post_telemetry(telemetry)
		


class ObstacleInterop(InteropClient):
	"""
		requesting obstacle locations for SDA

	"""
	def _make_request(self):
		return self.get_obstacles()

class MissionInterop(AsyncClient):

	"""
		request the mission
	"""
	def __init__(self,proxy_info):
		#no need for callbacks or looping requests (only need to grab the mission once)
		super(MissionInterop,self).__init__("http://"+proxy_info["host"]+":"+proxy_info["port"],
									  proxy_info["username"],
									  proxy_info["password"])

	def start(self):
		return self.get_mission().result()
